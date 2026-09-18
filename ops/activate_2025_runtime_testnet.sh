#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE="/opt/leantrader/rpb-unified-20260917"
LEGACY="/opt/leantrader/leantrader-2025-c7f9327"
ANCHOR="c7f9327b44cbeedd91046dcdaed57e55ea360db3"
CURRENT_RPB="leantrader-rpb-testnet"
CURRENT_INTEL="leantrader-intelligence-only"
LEGACY_CONTAINER="leantrader-2025-testnet"
ENV_FILE="/opt/leantrader/leantrader-2025-testnet.env"

cd "$SOURCE"

echo "=== 2025 LEANTRADER RESTORE ==="
echo "anchor=$ANCHOR"
echo "source=$SOURCE"
echo "runtime=$LEGACY"

git fetch --no-tags origin

if [ ! -d "$LEGACY/.git" ] && [ ! -f "$LEGACY/.git" ]; then
  rm -rf "$LEGACY"
  git worktree add --detach "$LEGACY" "$ANCHOR"
fi

if [ "$(git -C "$LEGACY" rev-parse HEAD)" != "$ANCHOR" ]; then
  echo "Refusing to use a non-2025 runtime worktree."
  exit 1
fi

echo
echo "=== PRESERVE EXACT 2025 BRAIN ==="
git -C "$LEGACY" status --short
echo "legacy_head=$(git -C "$LEGACY" rev-parse HEAD)"
echo "legacy_date=$(git -C "$LEGACY" show -s --format=%cI HEAD)"

# Keep the 2025 controller/queues/scouts/scalper/decision/evolution logic.
# Overlay only the already-proven authenticated execution plumbing so the
# historical brain does not fall back to simulated trades or synthetic closes.
rsync -a --delete "$SOURCE/src/leantrader/" "$LEGACY/src/leantrader/"
cp "$SOURCE/EXECUTION_ORCHESTRATOR.py" "$LEGACY/EXECUTION_ORCHESTRATOR.py"

# Avoid a second independent order owner. RPB remains instantiated/available
# to the historical system, but the unified 2025 controller owns execution.
python3 - "$LEGACY/COMPLETE_ULTIMATE_ORCHESTRATOR.py" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text()
old = """        # START REAL PROFIT BOT - 35 Pairs Trading!
        if hasattr(self, 'real_profit_bot') and self.real_profit_bot:
            # Wrap sync run() in async
            async def run_real_profit_loop():
                await asyncio.to_thread(self.real_profit_bot.run)

            tasks.append(asyncio.create_task(run_real_profit_loop()))
            logger.info("✅ 💰 REAL PROFIT BOT STARTED - Trading 35 pairs!")
"""
new = """        # REAL_PROFIT_BOT remains part of the historical system, but it is
        # not launched as an independent order owner here. Signals and
        # decisions execute through the unified ExecutionOrchestrator.
        if hasattr(self, 'real_profit_bot') and self.real_profit_bot:
            logger.info("✅ 💰 REAL PROFIT BOT PRESENT - unified controller owns execution")
"""
if old in s:
    s = s.replace(old, new)
p.write_text(s)
PY

echo
echo "=== BUILD TESTNET ENV WITHOUT REUSING TRACKED 2025 SECRETS ==="
: > "$ENV_FILE"

docker inspect "$CURRENT_RPB"   --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null   | grep -E '^(BYBIT_|EXECUTION_|ACCOUNT_|TELEGRAM_|NEWS|CRYPTOPANIC|OPENAI_|ANTHROPIC_|HUGGINGFACE_|QISKIT_|ETHERSCAN_|COINGECKO_|CRYPTOCOMPARE_)'   >> "$ENV_FILE" || true

cat >> "$ENV_FILE" <<'EOF'
TRADING_MODE=testnet
EXECUTION_MODE=testnet
USE_TESTNET=true
ENABLE_LIVE=false
GATEIO_MODE=testnet
PYTHONUNBUFFERED=1
EOF

chmod 600 "$ENV_FILE"

for key in ANTHROPIC_API_KEY OPENAI_API_KEY HUGGINGFACE_TOKEN QISKIT_IBM_TOKEN; do
  if grep -q "^\${key}=." "$ENV_FILE"; then
    echo "$key=SET"
  else
    echo "$key=UNSET"
  fi
done

IMAGE="$(docker inspect "$CURRENT_RPB" --format '{{.Config.Image}}')"
echo "runtime_image=$IMAGE"

echo
echo "=== IMPORT SMOKE TEST — NO TRADING ==="
docker run --rm   --name leantrader-2025-import-smoke   --env-file "$ENV_FILE"   -v "$LEGACY:/app"   -w /app   "$IMAGE"   python -c 'from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator; print("LEGACY_2025_IMPORT_OK")'

echo
echo "=== CUTOVER TO 2025 CONTROLLER ==="
docker rm -f "$LEGACY_CONTAINER" >/dev/null 2>&1 || true
docker stop "$CURRENT_RPB" >/dev/null 2>&1 || true

docker run -d   --name "$LEGACY_CONTAINER"   --restart unless-stopped   --env-file "$ENV_FILE"   -v "$LEGACY:/app"   -w /app   "$IMAGE"   python RUN_BOT.py --testnet >/dev/null

sleep 25

if ! docker ps --format '{{.Names}}' | grep -qx "$LEGACY_CONTAINER"; then
  echo "2025 runtime exited during startup. Restoring previous RPB."
  docker logs --tail 220 "$LEGACY_CONTAINER" 2>&1 || true
  docker start "$CURRENT_RPB" >/dev/null 2>&1 || true
  exit 1
fi

docker stop "$CURRENT_INTEL" >/dev/null 2>&1 || true

echo
echo "=== 2025 RUNTIME STATUS ==="
docker ps --filter "name=$LEGACY_CONTAINER"   --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'

echo
echo "=== ENGINE START EVIDENCE ==="
docker logs --since 3m "$LEGACY_CONTAINER" 2>&1   | grep -E 'Decision loop started|EXECUTION LOOP STARTED|SMART SCALPING LOOP STARTED|Scalper generated|Published .* signals|Decision:|EXECUTING:|SUBMITTING|ORDER ACKNOWLEDGED|Trade executed|Evolution|Sentient|Swarm|Learning loop started|Scouting loop started|ERROR|Traceback'   | tail -n 240 || true

echo
echo "=== CONTAINER MODE EVIDENCE ==="
docker exec "$LEGACY_CONTAINER" python - <<'PY'
import os
print({
    "TRADING_MODE": os.getenv("TRADING_MODE"),
    "EXECUTION_MODE": os.getenv("EXECUTION_MODE"),
    "USE_TESTNET": os.getenv("USE_TESTNET"),
    "ENABLE_LIVE": os.getenv("ENABLE_LIVE"),
    "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
    "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
    "HUGGINGFACE_TOKEN": bool(os.getenv("HUGGINGFACE_TOKEN")),
})
PY

echo
echo "2025 controller is now the active Testnet runtime."
