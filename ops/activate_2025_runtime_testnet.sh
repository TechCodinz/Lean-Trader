#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE="/opt/leantrader/rpb-unified-20260917"
LEGACY="/opt/leantrader/leantrader-2025-c7f9327"
ANCHOR="c7f9327b44cbeedd91046dcdaed57e55ea360db3"
CURRENT_RPB="leantrader-rpb-testnet"
CURRENT_INTEL="leantrader-intelligence-only"
LEGACY_CONTAINER="leantrader-2025-testnet"
ENV_FILE="/opt/leantrader/leantrader-2025-testnet.env"
LEGACY_IMAGE="leantrader-2025-runtime:local"
STATE_ROOT="/opt/leantrader/runtime/leantrader-2025-state"
WORKSPACE_STATE="$STATE_ROOT/workspace"

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
echo "=== RESTORE EXACT 2025 BRAIN BEFORE OVERLAYS ==="
git -C "$LEGACY" reset --hard "$ANCHOR"
git -C "$LEGACY" clean -fd
mkdir -p "$WORKSPACE_STATE"
chmod 700 "$STATE_ROOT" "$WORKSPACE_STATE"
git -C "$LEGACY" status --short
echo "legacy_head=$(git -C "$LEGACY" rev-parse HEAD)"
echo "legacy_date=$(git -C "$LEGACY" show -s --format=%cI HEAD)"

# Keep the 2025 controller/queues/scouts/scalper/decision/evolution logic.
# Overlay only the already-proven authenticated execution plumbing so the
# historical brain does not fall back to simulated trades or synthetic closes.
rsync -a --delete "$SOURCE/src/leantrader/" "$LEGACY/src/leantrader/"
cp "$SOURCE/EXECUTION_ORCHESTRATOR.py" "$LEGACY/EXECUTION_ORCHESTRATOR.py"

# Apply compatibility overlays only; the October-2025 signal/decision strategy stays intact.
python3 - "$LEGACY" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])

# 1. The 2025 base initializer created RealProfitBot with its default live mode.
# Propagate the orchestrator-selected mode instead. It remains an available
# historical component but is NOT an independent execution owner.
p = root / "COMPLETE_UNIFIED_ORCHESTRATOR.py"
s = p.read_text()
s = s.replace(
    "self.trading_engines['real_profit'] = RealProfitBot()",
    "self.trading_engines['real_profit'] = RealProfitBot(mode=self.mode)",
)
if "self.trading_engines['real_profit'] = RealProfitBot(mode=self.mode)" not in s:
    raise SystemExit("failed to mode-wire historical RealProfitBot")
p.write_text(s)

# 2. Remove only the standalone RPB task from CompleteUltimateOrchestrator.
# Smart Scalper -> DataHub -> UnifiedDecisionEngine -> ExecutionOrchestrator
# remains the order-producing path.
p = root / "COMPLETE_ULTIMATE_ORCHESTRATOR.py"
s = p.read_text()
start_marker = "        # START REAL PROFIT BOT - 35 Pairs Trading!"
end_marker = "        # START DYNAMIC MARKET SCANNER - Auto-discover trending pairs!"
start = s.find(start_marker)
end = s.find(end_marker, start) if start >= 0 else -1
if start >= 0 and end > start:
    replacement = (
        "        # REAL_PROFIT_BOT remains available as a historical component,\n"
        "        # but unified 2025 orchestration owns execution.\n"
        "        if hasattr(self, 'real_profit_bot') and self.real_profit_bot:\n"
        "            logger.info(\"✅ 💰 REAL PROFIT BOT PRESENT - unified controller owns execution\")\n\n"
    )
    s = s[:start] + replacement + s[end:]

if "asyncio.to_thread(self.real_profit_bot.run)" in s:
    raise SystemExit("standalone RealProfitBot execution loop still present")

# Modern authenticated ExecutionOrchestrator reports realized_net_profit.
s = s.replace(
    "exec_stats['total_profit']",
    "exec_stats.get('realized_net_profit', exec_stats.get('total_profit', 0.0))",
)
s = s.replace(
    "exec_stats.get('total_profit', 0)",
    "exec_stats.get('realized_net_profit', exec_stats.get('total_profit', 0.0))",
)

# The two historical intelligence managers return dictionaries; preview them
# as dictionaries instead of slicing them like lists. Logging only.
old = """                                for sig in goldmine_signals[:2]:  # Log first 2
                                    logger.info(f"💎 GOLDMINE: {symbol} - {sig.get('feature', 'Unknown')}: {sig.get('signal', 'N/A')}")"""
new = """                                if isinstance(goldmine_signals, dict):
                                    preview = list(goldmine_signals.items())[:2]
                                    for feature_name, sig in preview:
                                        logger.info(f"💎 GOLDMINE: {symbol} - {feature_name}: {sig}")
                                else:
                                    for sig in list(goldmine_signals)[:2]:
                                        logger.info(f"💎 GOLDMINE: {symbol} - {sig}")"""
s = s.replace(old, new)

old = """                            for sig in divine_signals[:3]:  # Log first 3
                                logger.info(f"🔮 DIVINE: {sig.get('feature', 'Unknown')} - {sig.get('insight', 'N/A')}")"""
new = """                            if isinstance(divine_signals, dict):
                                for feature_name, sig in list(divine_signals.items())[:3]:
                                    logger.info(f"🔮 DIVINE: {feature_name} - {sig}")
                            else:
                                for sig in list(divine_signals)[:3]:
                                    logger.info(f"🔮 DIVINE: {sig}")"""
s = s.replace(old, new)
p.write_text(s)

# 3. Match the actual 2025 PrivateTxClient constructor. With no DEX sender or
# private key configured it correctly remains unavailable/monitoring-only.
p = root / "DEX_ORCHESTRATOR.py"
if p.exists():
    s = p.read_text()
    old = """                self.private_client = PrivateTxClient(
                    endpoint="https://rpc.flashbots.net",
                    api_key=""  # Set from env
                )"""
    if old in s:
        s = s.replace(old, "                self.private_client = PrivateTxClient(sender=None)")
    p.write_text(s)

print("LEGACY_2025_RUNTIME_COMPAT_OVERLAYS_OK")
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

echo
echo "=== MIRROR CURRENT TESTNET SECRET AUTHORITY ==="
SECRET_MOUNT_ARGS=()

while IFS='|' read -r mtype source name dest; do
  [ -n "$dest" ] || continue
  case "$dest" in
    /run/secrets/*)
      if [ "$mtype" = "bind" ] && [ -n "$source" ] && [ -e "$source" ]; then
        SECRET_MOUNT_ARGS+=(--mount "type=bind,src=$source,dst=$dest,readonly")
      elif [ "$mtype" = "volume" ] && [ -n "$name" ]; then
        SECRET_MOUNT_ARGS+=(--mount "type=volume,src=$name,dst=$dest,readonly")
      fi
      ;;
  esac
done < <(
  docker inspect "$CURRENT_RPB" \
    --format '{{range .Mounts}}{{printf "%s|%s|%s|%s\n" .Type .Source .Name .Destination}}{{end}}'
)

if [ "${#SECRET_MOUNT_ARGS[@]}" -eq 0 ]; then
  echo "No reusable /run/secrets mount found on current authenticated RPB."
  echo "Refusing cutover; current RPB remains untouched."
  exit 1
fi

echo "Mirrored current RPB secret mounts without exposing secret values."

for key in ANTHROPIC_API_KEY OPENAI_API_KEY HUGGINGFACE_TOKEN QISKIT_IBM_TOKEN; do
  if grep -q "^\${key}=." "$ENV_FILE"; then
    echo "$key=SET"
  else
    echo "$key=UNSET"
  fi
done

BASE_IMAGE="$(docker inspect "$CURRENT_RPB" --format '{{.Config.Image}}')"
echo "base_runtime_image=$BASE_IMAGE"

# Historical RUN_BOT.py loads /app/.env itself.  Replace only this detached
# 2025 worktree's tracked .env with the currently authenticated Testnet
# environment so stale 2025 secrets/mode values cannot override Docker env.
cp "$ENV_FILE" "$LEGACY/.env"
chmod 600 "$LEGACY/.env"

# Package markers that were part of the later import-smoke repairs.  They do
# not change trading logic; they make restored packages importable when the
# corresponding directories exist.
for pkgdir in "$LEGACY/src/leantrader/agents" "$LEGACY/src/leantrader/production"; do
  if [ -d "$pkgdir" ]; then
    touch "$pkgdir/__init__.py"
  fi
done

echo
echo "=== REQUIRE PRE-VERIFIED 2025 COMPATIBILITY IMAGE ==="
if ! docker image inspect "$LEGACY_IMAGE" >/dev/null 2>&1; then
  echo "Missing $LEGACY_IMAGE. Run ops/bootstrap_2025_runtime_dependencies.sh first."
  exit 1
fi
docker run --rm "$LEGACY_IMAGE" pip check
echo "LEGACY_2025_IMAGE_READY"

echo
echo "=== COMPLETE DEPENDENCY IMPORT MATRIX ==="
docker run --rm -i "$LEGACY_IMAGE" python - <<'PY'
import importlib
import sys

modules = [
    # previously repaired/core validation
    "pytest", "numpy", "pandas", "scipy", "sklearn", "numba", "tiktoken", "multipart", "ccxt",
    "yaml", "aiohttp", "psutil", "dotenv", "redis", "web3",
    # 2025 runtime imports
    "bs4", "lxml", "feedparser", "tensorflow", "keras", "torch",
    "transformers", "xgboost", "lightgbm", "catboost", "joblib",
    "yfinance", "websocket", "websockets", "requests", "httpx",
    "eth_account", "eth_utils", "matplotlib", "seaborn", "plotly",
    "nltk", "textblob", "vaderSentiment", "langchain",
    "langchain_community", "anthropic", "openai", "telegram", "aiogram",
    "fastapi", "uvicorn", "sqlalchemy", "stripe", "qrcode", "pytz",
    "dateutil", "networkx", "cryptography", "bcrypt", "schedule",
    "loguru", "toml", "optuna", "statsmodels", "prometheus_client",
    "tweepy", "praw", "discord", "celery", "qiskit",
    "qiskit_aer", "qiskit_ibm_runtime",
]
failed = []
for name in modules:
    try:
        importlib.import_module(name)
        print(f"IMPORT_OK {name}")
    except Exception as exc:
        failed.append((name, type(exc).__name__, str(exc)[:240]))
        print(f"IMPORT_FAIL {name} {type(exc).__name__}: {str(exc)[:240]}")

# TA-Lib is historically used by specialist/older engines. Require it when the
# wheel installed successfully; report separately if the platform cannot load
# it, before any trading cutover.
for name in ("talib", "ta"):
    try:
        importlib.import_module(name)
        print(f"IMPORT_OK {name}")
    except Exception as exc:
        failed.append((name, type(exc).__name__, str(exc)[:240]))
        print(f"IMPORT_FAIL {name} {type(exc).__name__}: {str(exc)[:240]}")

if failed:
    print("DEPENDENCY_MATRIX_FAILED", failed)
    sys.exit(1)
print("LEGACY_2025_DEPENDENCIES_OK")
PY

echo
echo "=== APPLY NON-STRATEGY 2025 SOURCE REPAIRS ==="
# These are parser/import repairs only. They do not alter trading thresholds,
# signals, sizing, execution mode, or strategy behavior.
python3 - "$LEGACY" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])

# Historical test_api_connections.py was already listed in the 2025 repair
# scripts as a syntax-error file. Repair only object naming + typing imports.
p = root / "test_api_connections.py"
if p.exists():
    s = p.read_text()
    if "from typing import Dict, Any" not in s:
        s = s.replace("import sys\n", "import sys\nfrom typing import Dict, Any\n", 1)
    s = s.replace("self.ExchangeManager() = ExchangeManager()", "self.exchange_manager = ExchangeManager()")
    s = s.replace("self.ExchangeManager()", "self.exchange_manager")
    p.write_text(s)

# Historical tools/market_data_ultra.py contains a multiline f-string that is
# invalid Python. Preserve the same URL/values and only repair the parser form.
p = root / "tools" / "market_data_ultra.py"
if p.exists():
    s = p.read_text()
    old = '''                f"https://cryptopanic.com/api/v1/posts/?auth_token={
                    self.api_keys.get(
                        'cryptopanic', '')}&currencies={symbol}",'''
    new = '''                f"https://cryptopanic.com/api/v1/posts/?auth_token={self.api_keys.get('cryptopanic', '')}&currencies={symbol}",'''
    if old in s:
        s = s.replace(old, new)
    p.write_text(s)

# The October-2025 auto-fix pass accidentally inserted a typing import
# inside two function bodies. Restore the syntax without changing behavior.
p = root / "run_live_meme.py"
if p.exists():
    s = p.read_text()
    s = s.replace(
        "    from utils import load_config\nfrom typing import Callable\n\n    cfg =",
        "    from utils import load_config\n\n    cfg =",
    )
    p.write_text(s)

p = root / "run_unified.py"
if p.exists():
    s = p.read_text()
    s = s.replace(
        "    try:\n        import os\nfrom typing import Callable\n\n        run_daemons =",
        "    try:\n        import os\n\n        run_daemons =",
    )
    # The 2025 static/ruff reports show trader_core as an expected import for
    # run_unified.py; restore that import if the broken auto-fix removed it.
    if "from trader_core import TraderCore" not in s:
        s = s.replace(
            "import argparse\n",
            "import argparse\n\nfrom trader_core import TraderCore\n",
            1,
        )
    p.write_text(s)

# Package markers restored during the later module-repair work.
for pkgdir in (root / "src" / "leantrader" / "agents", root / "src" / "leantrader" / "production"):
    if pkgdir.is_dir():
        (pkgdir / "__init__.py").touch()

print("LEGACY_2025_SOURCE_REPAIRS_APPLIED")
PY

echo
echo "=== SOURCE SYNTAX CHECK — NO PYC WRITES ==="
docker run --rm -i \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  python - <<'PY'
from pathlib import Path
import sys

root = Path("/legacy")
bad = []
checked = 0
skip_parts = {".git", "__pycache__", ".venv", "venv", "runtime", "node_modules"}

for p in sorted(root.rglob("*.py")):
    if any(part in skip_parts for part in p.parts):
        continue
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
        compile(src, str(p.relative_to(root)), "exec", dont_inherit=True)
        checked += 1
    except SyntaxError as exc:
        bad.append((str(p.relative_to(root)), exc.lineno, exc.msg))
    except Exception as exc:
        bad.append((str(p.relative_to(root)), None, f"{type(exc).__name__}: {exc}"))

print("SYNTAX_CHECKED", checked)
if bad:
    print("SYNTAX_ERRORS", len(bad))
    for row in bad:
        print(row)
    sys.exit(1)
print("LEGACY_2025_SOURCE_SYNTAX_OK")
PY

echo
echo "=== IMPORT SMOKE TEST — NO TRADING ==="
docker run --rm \
  --name leantrader-2025-import-smoke \
  --env-file "$ENV_FILE" \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  sh -lc 'cp -a /legacy /tmp/leantrader-2025 && cd /tmp/leantrader-2025 && python -c '"'"'from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator; print("LEGACY_2025_IMPORT_OK")'"'"''

echo
echo "=== FULL 2025 INITIALIZE + WIRE SMOKE — NO LOOPS / NO ORDERS ==="
docker run --rm -i \
  --name leantrader-2025-wire-smoke \
  --env-file "$ENV_FILE" \
  "${SECRET_MOUNT_ARGS[@]}" \
  -v "$WORKSPACE_STATE:/workspace" \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  sh -lc 'cp -a /legacy /tmp/leantrader-2025 && cd /tmp/leantrader-2025 && python -' <<'PY'
import asyncio

from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator

async def check():
    bot = CompleteUltimateOrchestrator(mode="testnet")
    await bot.initialize_all_systems()
    await bot.wire_all_systems()

    base = set(getattr(bot, "orchestrators", {}) or {})
    advanced = set(getattr(bot, "advanced_orchestrators", {}) or {})

    required_base = {"learning", "scouting", "decision"}
    required_advanced = {"execution", "smart_scalping"}

    missing_base = sorted(required_base - base)
    missing_advanced = sorted(required_advanced - advanced)

    print("WIRE_BASE", sorted(base))
    print("WIRE_ADVANCED", sorted(advanced))
    print("SMART_SCALPING_PRESENT", bool(getattr(bot, "smart_scalping", None)))
    print("SENTIENT_BRAIN_PRESENT", bool(getattr(bot, "sentient_brain", None)))
    print("REAL_PROFIT_BOT_PRESENT", bool(getattr(bot, "real_profit_bot", None)))

    if missing_base or missing_advanced:
        raise SystemExit(
            f"WIRE_SMOKE_FAILED base={missing_base} advanced={missing_advanced}"
        )

    print("LEGACY_2025_WIRE_OK")

asyncio.run(check())
PY

echo
echo "=== AUTHENTICATED BYBIT TESTNET PREFLIGHT — READ ONLY ==="
docker run --rm -i \
  --env-file "$ENV_FILE" \
  "${SECRET_MOUNT_ARGS[@]}" \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  sh -lc 'cp -a /legacy /tmp/leantrader-2025 && cd /tmp/leantrader-2025 && python -' <<'PY'
from src.leantrader.execution.router import execution_status, route_balance

status = execution_status(mode="testnet", exchange_id="bybit")
safe = {
    "execution_mode": status.get("execution_mode"),
    "authority": status.get("authority"),
    "backend": status.get("backend"),
    "exchange": status.get("exchange"),
    "authenticated": bool(status.get("authenticated")),
}
print("EXECUTION_STATUS", safe)

if (
    safe["execution_mode"] != "testnet"
    or safe["authority"] != "testnet"
    or safe["exchange"] != "bybit"
    or safe["authenticated"] is not True
):
    raise SystemExit("AUTHENTICATED_TESTNET_PREFLIGHT_FAILED")

balance = route_balance(mode="testnet", exchange_id="bybit") or {}
free = ((balance.get("free") or {}).get("USDT"))
if free is None:
    free = ((balance.get("USDT") or {}).get("free"))
if free is None:
    raise SystemExit("AUTHENTICATED_TESTNET_BALANCE_UNAVAILABLE")

print("AUTHENTICATED_TESTNET_FREE_USDT", round(float(free), 8))
print("AUTHENTICATED_TESTNET_PREFLIGHT_OK")
PY

echo
echo "=== CUTOVER TO 2025 CONTROLLER ==="
docker rm -f "$LEGACY_CONTAINER" >/dev/null 2>&1 || true
docker stop "$CURRENT_RPB" >/dev/null 2>&1 || true

docker run -d \
  --name "$LEGACY_CONTAINER" \
  --restart unless-stopped \
  --env-file "$ENV_FILE" \
  "${SECRET_MOUNT_ARGS[@]}" \
  -v "$WORKSPACE_STATE:/workspace" \
  -v "$LEGACY:/app" \
  -w /app \
  "$LEGACY_IMAGE" \
  python RUN_BOT.py --testnet >/dev/null

echo "Waiting for 2025 controller engine loops to come online..."
READY=0
for _ in $(seq 1 18); do
  sleep 10

  if ! docker ps --format '{{.Names}}' | grep -qx "$LEGACY_CONTAINER"; then
    break
  fi

  LOGS="$(docker logs --since 5m "$LEGACY_CONTAINER" 2>&1 || true)"

  if printf '%s\n' "$LOGS" | grep -q 'configured credential file does not exist'; then
    echo "Credential mount failure detected during 2025 startup."
    break
  fi

  DECISION_OK=0
  EXECUTION_OK=0
  SCALPER_OK=0

  printf '%s\n' "$LOGS" | grep -Eq 'Decision loop started|Decision:' && DECISION_OK=1 || true
  printf '%s\n' "$LOGS" | grep -Eq 'EXECUTION LOOP STARTED|EXECUTING:' && EXECUTION_OK=1 || true
  printf '%s\n' "$LOGS" | grep -Eq 'SMART SCALPING LOOP STARTED|Scalper generated' && SCALPER_OK=1 || true

  if [ "$DECISION_OK" -eq 1 ] && [ "$EXECUTION_OK" -eq 1 ] && [ "$SCALPER_OK" -eq 1 ]; then
    READY=1
    break
  fi
done

if [ "$READY" -ne 1 ]; then
  echo "2025 controller did not reach the required engine-ready state."
  echo "Restoring previous RPB runtime."
  docker logs --tail 320 "$LEGACY_CONTAINER" 2>&1 || true
  docker rm -f "$LEGACY_CONTAINER" >/dev/null 2>&1 || true
  docker start "$CURRENT_RPB" >/dev/null 2>&1 || true
  exit 1
fi

# The restored 2025 controller has proven that its decision, execution and
# smart-scalping loops are online. Only now retire the old intelligence-only
# sidecar to free memory/CPU. The previous RPB remains stopped but available
# for rollback.
docker stop "$CURRENT_INTEL" >/dev/null 2>&1 || true

echo
echo "=== 2025 RUNTIME STATUS ==="
docker ps --filter "name=$LEGACY_CONTAINER"   --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'

echo
echo "=== ENGINE START EVIDENCE ==="
docker logs --since 3m "$LEGACY_CONTAINER" 2>&1   | grep -E 'AUTHENTICATED_TESTNET|ALL 50\+ ORCHESTRATORS RUNNING|Decision loop started|EXECUTION LOOP STARTED|SMART SCALPING LOOP STARTED|Scalper generated|Published .* signals|Decision:|EXECUTING:|SUBMITTING|ORDER ACKNOWLEDGED|Trade executed|Evolution|Sentient|Swarm|Learning loop started|Scouting loop started|ERROR|Traceback'   | tail -n 240 || true

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
