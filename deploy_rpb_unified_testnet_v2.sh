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
OLD_EXEC_WAS_RUNNING=false

say() { printf '\n=== %s ===\n' "$*"; }
fail() { echo "ERROR: $*" >&2; exit 1; }

is_running() {
  docker inspect "$1" --format '{{.State.Running}}' 2>/dev/null | grep -qx true
}

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

rollback_old_executor() {
  say "ROLLBACK"
  docker rm -f "$RPB_CONTAINER" >/dev/null 2>&1 || true
  docker rm -f "$INTEL_CONTAINER" >/dev/null 2>&1 || true
  if [[ "$OLD_EXEC_WAS_RUNNING" == true ]]; then
    docker update --restart=unless-stopped "$OLD_EXEC_CONTAINER" >/dev/null 2>&1 || true
    docker start "$OLD_EXEC_CONTAINER" >/dev/null 2>&1 || true
    echo "RESTORED=$OLD_EXEC_CONTAINER"
  fi
}

trap 'rc=$?; if (( rc != 0 )); then echo "HANDOFF_FAILED_RC=$rc" >&2; fi' EXIT

say "PRECHECK"
[[ -d "$SOURCE_REPO/.git" || -f "$SOURCE_REPO/.git" ]] || fail "Lean-Trader source repo not found: $SOURCE_REPO"
docker image inspect "$IMAGE" >/dev/null 2>&1 || fail "Docker image unavailable: $IMAGE"
[[ -d "$RUNTIME" ]] || fail "runtime directory missing: $RUNTIME"
[[ -d "$SECRETS" ]] || fail "secrets directory missing: $SECRETS"
[[ -f "$RUNTIME/vps_testnet_execution.json" ]] || fail "current Testnet execution state missing: $RUNTIME/vps_testnet_execution.json"
[[ -f "$RUNTIME/vps_evolution_fabric.json" ]] || fail "evolution fabric missing: $RUNTIME/vps_evolution_fabric.json"
mkdir -p "$RPB_DATA/runtime" "$RPB_DATA/reports" "$PRESERVE_ROOT" "$LOGS"

if is_running "$OLD_EXEC_CONTAINER"; then OLD_EXEC_WAS_RUNNING=true; fi

say "SYNC CANONICAL LEAN-TRADER BRANCH"
cd "$SOURCE_REPO"
git fetch --no-tags origin "$BRANCH:refs/remotes/origin/$BRANCH"
if [[ -e "$WORKTREE/.git" ]]; then
  git -C "$WORKTREE" fetch --no-tags origin "$BRANCH:refs/remotes/origin/$BRANCH"
  git -C "$WORKTREE" reset --hard "origin/$BRANCH"
else
  rm -rf "$WORKTREE"
  git worktree add --detach "$WORKTREE" "origin/$BRANCH"
fi
printf 'WORKTREE=%s\nHEAD=%s\n' "$WORKTREE" "$(git -C "$WORKTREE" rev-parse HEAD)"

say "SNAPSHOT CURRENT STATE"
mkdir -p "$SNAPSHOT"
for c in "$OLD_EXEC_CONTAINER" "$FASTLANE_CONTAINER" "$LEGACY_RPB_CONTAINER"; do
  docker inspect "$c" > "$SNAPSHOT/${c}.inspect.json" 2>/dev/null || true
  docker logs --tail 500 "$c" > "$SNAPSHOT/${c}.logs.txt" 2>&1 || true
done
for f in vps_testnet_execution.json vps_evolution_fabric.json vps_heartbeat.json learn_state.json; do
  [[ -f "$RUNTIME/$f" ]] && cp -a "$RUNTIME/$f" "$SNAPSHOT/$f"
done
[[ -d "$RUNTIME/evolution" ]] && tar -C "$RUNTIME" -czf "$SNAPSHOT/evolution.tar.gz" evolution || true
[[ -f /opt/leantrader/app/reports/alpha_memory.json ]] && cp -a /opt/leantrader/app/reports/alpha_memory.json "$SNAPSHOT/alpha_memory.json" || true

say "PRESERVE ACCUMULATED LEARNING"
if [[ ! -f "$RPB_DATA/runtime/learn_state.json" && -f "$RUNTIME/learn_state.json" ]]; then
  cp -a "$RUNTIME/learn_state.json" "$RPB_DATA/runtime/learn_state.json"
  echo "LEARN_STATE_MIGRATED=YES"
else
  echo "LEARN_STATE_MIGRATED=NO_ALREADY_PRESENT_OR_SOURCE_MISSING"
fi
if [[ ! -f "$RPB_DATA/reports/alpha_memory.json" && -f /opt/leantrader/app/reports/alpha_memory.json ]]; then
  cp -a /opt/leantrader/app/reports/alpha_memory.json "$RPB_DATA/reports/alpha_memory.json"
  echo "ALPHA_MEMORY_MIGRATED=YES"
else
  echo "ALPHA_MEMORY_MIGRATED=NO_ALREADY_PRESENT_OR_SOURCE_MISSING"
fi

# Resolve existing credential references without displaying any secret value.
BYBIT_KEY_FILE="$(resolve_env BYBIT_TESTNET_API_KEY_FILE || true)"
BYBIT_SECRET_FILE="$(resolve_env BYBIT_TESTNET_API_SECRET_FILE || true)"
BYBIT_KEY="$(resolve_env BYBIT_TESTNET_API_KEY || true)"
BYBIT_SECRET="$(resolve_env BYBIT_TESTNET_API_SECRET || true)"
TELEGRAM_TOKEN="$(resolve_env TELEGRAM_BOT_TOKEN || true)"
TELEGRAM_ADMIN="$(resolve_env TELEGRAM_ADMIN_CHAT_ID || true)"
TELEGRAM_VIP="$(resolve_env TELEGRAM_VIP_CHAT_ID || true)"
TELEGRAM_FREE="$(resolve_env TELEGRAM_FREE_CHAT_ID || true)"

if [[ -z "$BYBIT_KEY_FILE" || -z "$BYBIT_SECRET_FILE" ]]; then
  [[ -n "$BYBIT_KEY" && -n "$BYBIT_SECRET" ]] || fail "Bybit Testnet credentials could not be resolved from the existing runtime"
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
  -v "$RPB_DATA/reports:/workspace/reports"
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

say "VERIFY ASSEMBLY IN THE ACTUAL RUNTIME IMAGE"
docker run "${COMMON_ARGS[@]}" "${SECRET_ARGS[@]}" "$IMAGE" sh -lc '
  set -e
  python verify_rpb_unified.py
  python -m py_compile \
    REAL_PROFIT_BOT.py \
    rpb_position_lifecycle.py \
    rpb_intelligence.py \
    rpb_scalping.py \
    rpb_alpha_risk.py \
    rpb_production_bridge.py \
    rpb_adopt_positions.py \
    rpb_telegram.py \
    verify_rpb_unified.py
  if python - <<"PY"
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("pytest") else 1)
PY
  then
    python -m pytest -q \
      test_rpb_production_bridge.py \
      test_rpb_adopt_positions.py \
      test_rpb_unified_runtime.py \
      test_rpb_scalping_real_indicators.py
  else
    echo "PYTEST=SKIPPED_NOT_INSTALLED_IN_RUNTIME_IMAGE"
  fi
  python - <<"PY"
from REAL_PROFIT_BOT import REAL_PROFIT_BOT
bot = REAL_PROFIT_BOT(mode="testnet")
assert bot.mode == "testnet"
assert bot.lifecycle_enabled
assert bot.production_bridge is not None
print("RPB_IMPORT_SMOKE=PASS")
print("SCALPING_HEALTH=", bot.scalping.health() if bot.scalping else {})
print("EVOLUTION_HEALTH=", bot.production_bridge.health())
PY
'

say "DRY-RUN POSITION OWNERSHIP HANDOFF WHILE OLD OWNER IS STILL ACTIVE"
docker run "${COMMON_ARGS[@]}" "${SECRET_ARGS[@]}" "$IMAGE" \
  python rpb_adopt_positions.py \
    --state /intelligence/runtime/vps_testnet_execution.json \
    --report /rpb-data/runtime/adoption-dry-run.json

say "REMOVE FAILED FASTLANE AUTHORITY"
docker stop "$FASTLANE_CONTAINER" >/dev/null 2>&1 || true
docker update --restart=no "$FASTLANE_CONTAINER" >/dev/null 2>&1 || true

echo "FASTLANE_RUNNING=$(is_running "$FASTLANE_CONTAINER" && echo yes || echo no)"

say "FREEZE CURRENT PRODUCTION EXECUTOR FOR CONSISTENT POSITION TRANSFER"
docker update --restart=no "$OLD_EXEC_CONTAINER" >/dev/null 2>&1 || true
docker stop -t 20 "$OLD_EXEC_CONTAINER" >/dev/null 2>&1 || true
sleep 2
is_running "$OLD_EXEC_CONTAINER" && { rollback_old_executor; fail "$OLD_EXEC_CONTAINER did not stop"; }
cp -a "$RUNTIME/vps_testnet_execution.json" "$SNAPSHOT/vps_testnet_execution.final.json"

say "APPLY IDEMPOTENT POSITION HANDOFF FROM FINAL FROZEN STATE"
if ! docker run "${COMMON_ARGS[@]}" "${SECRET_ARGS[@]}" "$IMAGE" \
  python rpb_adopt_positions.py \
    --state /intelligence/runtime/vps_testnet_execution.json \
    --apply \
    --report /rpb-data/runtime/adoption-applied.json; then
  rollback_old_executor
  fail "position adoption failed; old executor restored"
fi

say "DISABLE LEGACY RPB EXECUTION AUTHORITY"
docker stop "$LEGACY_RPB_CONTAINER" >/dev/null 2>&1 || true
docker update --restart=no "$LEGACY_RPB_CONTAINER" >/dev/null 2>&1 || true

say "START PRODUCTION INTELLIGENCE AS NON-AUTHENTICATED PAPER-ONLY SERVICE"
INTEL_ENV="$RPB_DATA/intelligence-only.env"
: > "$INTEL_ENV"
chmod 600 "$INTEL_ENV"
if docker inspect "$OLD_EXEC_CONTAINER" >/dev/null 2>&1; then
  docker inspect "$OLD_EXEC_CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep -E '^[A-Za-z_][A-Za-z0-9_]*=' \
    | grep -Evi '(KEY|SECRET|TOKEN|PASSWORD|PASSPHRASE|CREDENTIAL)' \
    | grep -Evi '^(EXECUTION_MODE|BROKER_BACKEND|BYBIT_TESTNET_ENABLED|ENABLE_LIVE|ALLOW_LIVE|LIVE_CONFIRM|LIVE_AUTHORITY)=' \
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

docker rm -f "$INTEL_CONTAINER" >/dev/null 2>&1 || true
docker run -d \
  --name "$INTEL_CONTAINER" \
  --restart unless-stopped \
  --env-file "$INTEL_ENV" \
  -v "$RUNTIME:/app/runtime" \
  -v "$LOGS:/app/logs" \
  "$IMAGE" \
  python -m leantrader.production.runner >/dev/null

say "START RPB AS SOLE AUTHENTICATED BYBIT TESTNET ORDER OWNER"
docker rm -f "$RPB_CONTAINER" >/dev/null 2>&1 || true
docker run -d \
  --name "$RPB_CONTAINER" \
  --restart unless-stopped \
  -v "$WORKTREE:/workspace" \
  -v "$RUNTIME:/intelligence/runtime:ro" \
  -v "$RPB_DATA:/rpb-data" \
  -v "$RPB_DATA/reports:/workspace/reports" \
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
if ! is_running "$RPB_CONTAINER"; then
  echo "RPB_STARTUP_FAILED" >&2
  docker logs --tail 220 "$RPB_CONTAINER" 2>&1 || true
  rollback_old_executor
  fail "RPB failed startup; old executor restored"
fi

say "VERIFY AUTHENTICATED TESTNET AUTHORITY"
if ! docker exec "$RPB_CONTAINER" python - <<'PY'
from src.leantrader.execution.router import execution_status
s = execution_status(mode="testnet", exchange_id="bybit")
print("EXECUTION_STATUS=", {k: s.get(k) for k in ("execution_mode","authority","backend","exchange","authenticated")})
assert s.get("execution_mode") == "testnet"
assert s.get("authority") == "testnet"
assert s.get("exchange") == "bybit"
assert s.get("authenticated") is True
print("RPB_TESTNET_AUTHORITY=PASS")
PY
then
  rollback_old_executor
  fail "RPB did not prove authenticated Bybit Testnet authority"
fi

say "VERIFY SINGLE EXECUTION OWNER"
for c in "$OLD_EXEC_CONTAINER" "$FASTLANE_CONTAINER" "$LEGACY_RPB_CONTAINER"; do
  if is_running "$c"; then
    rollback_old_executor
    fail "competing execution container is still running: $c"
  fi
done
is_running "$RPB_CONTAINER" || { rollback_old_executor; fail "RPB is not running"; }
is_running "$INTEL_CONTAINER" || echo "WARNING: intelligence-only runner is not running; evolution sidecar remains independent"

printf '%-34s %-18s %s\n' NAME STATUS IMAGE
docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}' \
  | grep -E 'leantrader-(rpb-testnet|fast-lane-testnet|intelligence-only)|app-leantrader-1|leantrader-old-bybit-profit' \
  | awk -F'|' '{printf "%-34s %-18s %s\n", $1, $2, $3}' || true

echo
echo "--- RPB LOG TAIL ---"
docker logs --tail 220 "$RPB_CONTAINER" 2>&1

echo
echo "--- INTELLIGENCE-ONLY LOG TAIL ---"
docker logs --tail 80 "$INTEL_CONTAINER" 2>&1 || true

say "HANDOFF STARTED AND AUTHORITY VERIFIED"
echo "RPB_CONTAINER=$RPB_CONTAINER"
echo "RPB_WORKTREE=$WORKTREE"
echo "RPB_HEAD=$(git -C "$WORKTREE" rev-parse HEAD)"
echo "SNAPSHOT=$SNAPSHOT"
echo "ADOPTION_REPORT=$RPB_DATA/runtime/adoption-applied.json"
echo "LEARN_STATE=$RPB_DATA/runtime/learn_state.json"
echo "ALPHA_MEMORY=$RPB_DATA/reports/alpha_memory.json"
echo "NOTE=Trading is Bybit Testnet only. Profit is authoritative only after an authenticated completed close with actual costs."
