#!/usr/bin/env bash
set -Eeuo pipefail

BRANCH="${RPB_BRANCH:-restore/rpb-unified-20260917}"
SOURCE_REPO="${LEANTRADER_SOURCE_REPO:-/opt/leantrader/native-integrity-pass4-20260911T022930Z}"
WORKTREE="${RPB_WORKTREE:-/opt/leantrader/rpb-unified-20260917}"
RUNTIME="${LEANTRADER_RUNTIME:-/opt/leantrader/app/runtime}"
LOGS="${LEANTRADER_LOGS:-/opt/leantrader/app/logs}"
SECRETS="${LEANTRADER_SECRETS:-/opt/leantrader/app/secrets}"
RPB_DATA="${RPB_DATA:-/opt/leantrader/rpb-runtime}"
PRESERVE_ROOT="${LEANTRADER_PRESERVE_ROOT:-/opt/leantrader/preserved}"
OLD_EXEC_CONTAINER="${OLD_EXEC_CONTAINER:-app-leantrader-1}"
FASTLANE_CONTAINER="${FASTLANE_CONTAINER:-leantrader-fast-lane-testnet}"
LEGACY_RPB_CONTAINER="${LEGACY_RPB_CONTAINER:-leantrader-old-bybit-profit}"
RPB_CONTAINER="${RPB_CONTAINER:-leantrader-rpb-testnet}"
INTEL_CONTAINER="${INTEL_CONTAINER:-leantrader-intelligence-only}"
IMAGE="${RPB_IMAGE:-leantrader-paper:local}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
SNAPSHOT="$PRESERVE_ROOT/rpb-handoff-$TS"

say() { printf '\n=== %s ===\n' "$*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

container_env() {
  local container="$1" key="$2"
  docker inspect "$container" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null \
    | sed -n "s/^${key}=//p" | tail -n 1
}

file_env() {
  local file="$1" key="$2"
  [[ -f "$file" ]] || return 0
  sed -n "s/^${key}=//p" "$file" | tail -n 1
}

resolve_env() {
  local key="$1" value=""
  for c in "$LEGACY_RPB_CONTAINER" "$OLD_EXEC_CONTAINER"; do
    value="$(container_env "$c" "$key" || true)"
    [[ -n "$value" ]] && { printf '%s' "$value"; return 0; }
  done
  value="$(file_env /opt/leantrader/app/.env.production "$key" || true)"
  [[ -n "$value" ]] && printf '%s' "$value"
}

say "PRECHECK"
[[ -d "$SOURCE_REPO/.git" || -f "$SOURCE_REPO/.git" ]] || fail "Lean-Trader source repo not found at $SOURCE_REPO"
docker image inspect "$IMAGE" >/dev/null 2>&1 || fail "Docker image $IMAGE is unavailable"
[[ -d "$RUNTIME" ]] || fail "runtime directory missing: $RUNTIME"
[[ -d "$SECRETS" ]] || fail "secrets directory missing: $SECRETS"
mkdir -p "$RPB_DATA/runtime" "$RPB_DATA/reports" "$PRESERVE_ROOT"

say "SYNC CORRECT LEAN-TRADER BRANCH"
cd "$SOURCE_REPO"
git fetch --no-tags origin "$BRANCH:refs/remotes/origin/$BRANCH"
if [[ -e "$WORKTREE/.git" ]]; then
  git -C "$WORKTREE" fetch --no-tags origin "$BRANCH:refs/remotes/origin/$BRANCH"
  git -C "$WORKTREE" reset --hard "origin/$BRANCH"
else
  rm -rf "$WORKTREE"
  git worktree add -B "$BRANCH" "$WORKTREE" "origin/$BRANCH"
fi
printf 'WORKTREE=%s\nHEAD=%s\n' "$WORKTREE" "$(git -C "$WORKTREE" rev-parse HEAD)"

say "SNAPSHOT CURRENT EXECUTION AND EVOLUTION STATE"
mkdir -p "$SNAPSHOT"
for c in "$OLD_EXEC_CONTAINER" "$FASTLANE_CONTAINER" "$LEGACY_RPB_CONTAINER"; do
  docker inspect "$c" > "$SNAPSHOT/${c}.inspect.json" 2>/dev/null || true
  docker logs --tail 500 "$c" > "$SNAPSHOT/${c}.logs.txt" 2>&1 || true
done
for f in vps_testnet_execution.json vps_evolution_fabric.json vps_heartbeat.json; do
  [[ -f "$RUNTIME/$f" ]] && cp -a "$RUNTIME/$f" "$SNAPSHOT/$f"
done
[[ -d "$RUNTIME/evolution" ]] && tar -C "$RUNTIME" -czf "$SNAPSHOT/evolution.tar.gz" evolution || true

# Resolve credentials without printing their values.
BYBIT_KEY_FILE="$(resolve_env BYBIT_TESTNET_API_KEY_FILE || true)"
BYBIT_SECRET_FILE="$(resolve_env BYBIT_TESTNET_API_SECRET_FILE || true)"
BYBIT_KEY="$(resolve_env BYBIT_TESTNET_API_KEY || true)"
BYBIT_SECRET="$(resolve_env BYBIT_TESTNET_API_SECRET || true)"
TELEGRAM_TOKEN="$(resolve_env TELEGRAM_BOT_TOKEN || true)"
TELEGRAM_ADMIN="$(resolve_env TELEGRAM_ADMIN_CHAT_ID || true)"
TELEGRAM_VIP="$(resolve_env TELEGRAM_VIP_CHAT_ID || true)"
TELEGRAM_FREE="$(resolve_env TELEGRAM_FREE_CHAT_ID || true)"

if [[ -z "$BYBIT_KEY_FILE" || -z "$BYBIT_SECRET_FILE" ]]; then
  [[ -n "$BYBIT_KEY" && -n "$BYBIT_SECRET" ]] || fail "Bybit Testnet credential references could not be resolved from existing runtime"
fi

SECRET_ARGS=()
[[ -n "$BYBIT_KEY_FILE" ]] && SECRET_ARGS+=( -e "BYBIT_TESTNET_API_KEY_FILE=$BYBIT_KEY_FILE" )
[[ -n "$BYBIT_SECRET_FILE" ]] && SECRET_ARGS+=( -e "BYBIT_TESTNET_API_SECRET_FILE=$BYBIT_SECRET_FILE" )
[[ -n "$BYBIT_KEY" ]] && SECRET_ARGS+=( -e "BYBIT_TESTNET_API_KEY=$BYBIT_KEY" )
[[ -n "$BYBIT_SECRET" ]] && SECRET_ARGS+=( -e "BYBIT_TESTNET_API_SECRET=$BYBIT_SECRET" )
[[ -n "$TELEGRAM_TOKEN" ]] && SECRET_ARGS+=( -e "TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN" )
[[ -n "$TELEGRAM_ADMIN" ]] && SECRET_ARGS+=( -e "TELEGRAM_ADMIN_CHAT_ID=$TELEGRAM_ADMIN" )
[[ -n "$TELEGRAM_VIP" ]] && SECRET_ARGS+=( -e "TELEGRAM_VIP_CHAT_ID=$TELEGRAM_VIP" )
[[ -n "$TELEGRAM_FREE" ]] && SECRET_ARGS+=( -e "TELEGRAM_FREE_CHAT_ID=$TELEGRAM_FREE" )

COMMON_ARGS=(
  --rm
  -v "$WORKTREE:/workspace"
  -v "$RUNTIME:/intelligence/runtime:ro"
  -v "$RPB_DATA:/rpb-data"
  -v "$SECRETS:/run/secrets:ro"
  -w /workspace
  -e PYTHONPATH=/workspace
  -e EXECUTION_MODE=testnet
  -e CCXT_EXCHANGE=bybit
  -e EXCHANGE_ID=bybit
  -e EXCHANGE_MODE=spot
  -e LEANTRADER_DATA_DIR=/rpb-data
  -e LEARN_STATE_PATH=/rpb-data/runtime/learn_state.json
  -e RPB_EVOLUTION_FABRIC_PATH=/intelligence/runtime/vps_evolution_fabric.json
  -e RPB_MAX_HOLD_SECONDS=30
  -e RPB_CYCLE_SLEEP_SECONDS=0.5
  -e RPB_POST_ENTRY_SLEEP_SECONDS=0.5
)

say "VERIFY UNIFIED RPB CODE IN ACTUAL RUNTIME IMAGE"
docker run "${COMMON_ARGS[@]}" "${SECRET_ARGS[@]}" "$IMAGE" sh -lc '
  python -m pytest --version >/dev/null 2>&1 || python -m pip install -q pytest
  python -m pytest -q \
    test_rpb_production_bridge.py \
    test_rpb_adopt_positions.py \
    test_rpb_unified_runtime.py
  python -m py_compile \
    REAL_PROFIT_BOT.py \
    rpb_position_lifecycle.py \
    rpb_intelligence.py \
    rpb_scalping.py \
    rpb_alpha_risk.py \
    rpb_production_bridge.py \
    rpb_adopt_positions.py \
    rpb_telegram.py
  python - <<"PY"
from REAL_PROFIT_BOT import REAL_PROFIT_BOT
bot = REAL_PROFIT_BOT(mode="testnet")
assert bot.mode == "testnet"
assert bot.lifecycle_enabled
print("RPB_IMPORT_SMOKE=PASS")
print("EVOLUTION_HEALTH=", bot.production_bridge.health() if bot.production_bridge else {})
PY
'

say "DRY-RUN POSITION OWNERSHIP HANDOFF"
docker run "${COMMON_ARGS[@]}" "${SECRET_ARGS[@]}" "$IMAGE" \
  python rpb_adopt_positions.py \
    --state /intelligence/runtime/vps_testnet_execution.json \
    --report /rpb-data/runtime/adoption-dry-run.json

say "APPLY IDEMPOTENT POSITION HANDOFF"
docker run "${COMMON_ARGS[@]}" "${SECRET_ARGS[@]}" "$IMAGE" \
  python rpb_adopt_positions.py \
    --state /intelligence/runtime/vps_testnet_execution.json \
    --apply \
    --report /rpb-data/runtime/adoption-applied.json

say "CREATE NON-EXECUTING PRODUCTION INTELLIGENCE RUNTIME"
INTEL_ENV="$RPB_DATA/intelligence-only.env"
: > "$INTEL_ENV"
chmod 600 "$INTEL_ENV"
if docker inspect "$OLD_EXEC_CONTAINER" >/dev/null 2>&1; then
  docker inspect "$OLD_EXEC_CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep -Ev '(^|_)(KEY|SECRET|TOKEN|PASSWORD|PASSPHRASE|CREDENTIAL)=' \
    | grep -Ev '^(EXECUTION_MODE|BROKER_BACKEND|BYBIT_TESTNET_ENABLED|ENABLE_LIVE|ALLOW_LIVE|LIVE_CONFIRM|LIVE_AUTHORITY)=' \
    >> "$INTEL_ENV" || true
fi
cat >> "$INTEL_ENV" <<'EOF'
EXECUTION_MODE=paper
BROKER_BACKEND=emu
BYBIT_TESTNET_ENABLED=false
ENABLE_LIVE=false
ALLOW_LIVE=false
LIVE_CONFIRM=NO
LIVE_AUTHORITY=false
EOF

say "CUT OVER TO ONE EXECUTION OWNER"
docker stop "$FASTLANE_CONTAINER" >/dev/null 2>&1 || true
docker update --restart=no "$FASTLANE_CONTAINER" >/dev/null 2>&1 || true
docker stop "$OLD_EXEC_CONTAINER" >/dev/null 2>&1 || true
docker update --restart=no "$OLD_EXEC_CONTAINER" >/dev/null 2>&1 || true
docker stop "$LEGACY_RPB_CONTAINER" >/dev/null 2>&1 || true
docker update --restart=no "$LEGACY_RPB_CONTAINER" >/dev/null 2>&1 || true

docker rm -f "$INTEL_CONTAINER" >/dev/null 2>&1 || true
docker run -d \
  --name "$INTEL_CONTAINER" \
  --restart unless-stopped \
  --env-file "$INTEL_ENV" \
  -v "$RUNTIME:/app/runtime" \
  -v "$LOGS:/app/logs" \
  "$IMAGE" \
  python -m leantrader.production.runner >/dev/null

# The intelligence runner receives no secrets mount and is forced to paper.
# Even if a legacy lane tries to initialize, it has no authenticated order authority.

say "START RPB AS SOLE BYBIT TESTNET ORDER OWNER"
docker rm -f "$RPB_CONTAINER" >/dev/null 2>&1 || true
docker run -d \
  --name "$RPB_CONTAINER" \
  --restart unless-stopped \
  -v "$WORKTREE:/workspace" \
  -v "$RUNTIME:/intelligence/runtime:ro" \
  -v "$RPB_DATA:/rpb-data" \
  -v "$SECRETS:/run/secrets:ro" \
  -w /workspace \
  -e PYTHONPATH=/workspace \
  -e EXECUTION_MODE=testnet \
  -e CCXT_EXCHANGE=bybit \
  -e EXCHANGE_ID=bybit \
  -e EXCHANGE_MODE=spot \
  -e LEANTRADER_DATA_DIR=/rpb-data \
  -e LEARN_STATE_PATH=/rpb-data/runtime/learn_state.json \
  -e RPB_EVOLUTION_FABRIC_PATH=/intelligence/runtime/vps_evolution_fabric.json \
  -e RPB_MAX_HOLD_SECONDS=30 \
  -e RPB_CYCLE_SLEEP_SECONDS=0.5 \
  -e RPB_POST_ENTRY_SLEEP_SECONDS=0.5 \
  "${SECRET_ARGS[@]}" \
  "$IMAGE" \
  python -u -c 'from REAL_PROFIT_BOT import REAL_PROFIT_BOT; REAL_PROFIT_BOT(mode="testnet").run()' >/dev/null

sleep 8
if ! docker inspect "$RPB_CONTAINER" --format '{{.State.Running}}' 2>/dev/null | grep -qx true; then
  echo "RPB failed startup; rolling execution authority back to the prior production runner." >&2
  docker logs --tail 200 "$RPB_CONTAINER" 2>&1 || true
  docker rm -f "$RPB_CONTAINER" >/dev/null 2>&1 || true
  docker rm -f "$INTEL_CONTAINER" >/dev/null 2>&1 || true
  docker update --restart=unless-stopped "$OLD_EXEC_CONTAINER" >/dev/null 2>&1 || true
  docker start "$OLD_EXEC_CONTAINER" >/dev/null 2>&1 || true
  exit 20
fi

say "VERIFY SINGLE-AUTHORITY RUNTIME"
printf '%-34s %-15s %s\n' NAME STATUS IMAGE
docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}' \
  | grep -E 'leantrader-(rpb-testnet|fast-lane-testnet|intelligence-only)|app-leantrader-1|leantrader-old-bybit-profit' \
  | awk -F'|' '{printf "%-34s %-15s %s\n", $1, $2, $3}' || true

echo
echo "--- RPB LOG TAIL ---"
docker logs --tail 160 "$RPB_CONTAINER" 2>&1

echo
echo "--- INTELLIGENCE-ONLY LOG TAIL ---"
docker logs --tail 60 "$INTEL_CONTAINER" 2>&1 || true

say "HANDOFF COMPLETE"
echo "RPB_CONTAINER=$RPB_CONTAINER"
echo "RPB_WORKTREE=$WORKTREE"
echo "RPB_HEAD=$(git -C "$WORKTREE" rev-parse HEAD)"
echo "SNAPSHOT=$SNAPSHOT"
echo "ADOPTION_REPORT=$RPB_DATA/runtime/adoption-applied.json"
echo "NOTE=Profit is authoritative only after an authenticated completed Testnet close with actual fees."
