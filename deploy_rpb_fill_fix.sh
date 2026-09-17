#!/usr/bin/env bash
set -Eeuo pipefail

BRANCH="${RPB_BRANCH:-restore/rpb-unified-20260917}"
CANONICAL_REPO="${LEANTRADER_CANONICAL_REPO:-/opt/leantrader/canonical-lean-trader}"
WORKTREE="${RPB_WORKTREE:-/opt/leantrader/rpb-unified-20260917}"
RUNTIME="${LEANTRADER_RUNTIME:-/opt/leantrader/app/runtime}"
RPB_DATA="${RPB_DATA:-/opt/leantrader/rpb-runtime}"
RPB_CONTAINER="${RPB_CONTAINER:-leantrader-rpb-testnet}"
BACKUP_CONTAINER="${RPB_CONTAINER}-pre-fill-fix"
EPOCH_FILE="$RPB_DATA/runtime/rpb_epoch_start_ms"
# First successful unified-RPB cutover from the preserved deployment evidence.
BOOTSTRAP_EPOCH_MS="${RPB_BOOTSTRAP_EPOCH_MS:-1789648101000}"
ENV_FILE="/tmp/${RPB_CONTAINER}.env.$$"

cleanup() { rm -f "$ENV_FILE"; }
trap cleanup EXIT

[[ -e "$CANONICAL_REPO/.git" ]] || { echo "ERROR: canonical Lean-Trader clone missing" >&2; exit 2; }

git -C "$CANONICAL_REPO" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH"

git -C "$WORKTREE" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH"
git -C "$WORKTREE" reset --hard "origin/$BRANCH"

echo "RPB_HEAD=$(git -C "$WORKTREE" rev-parse HEAD)"

mkdir -p "$RPB_DATA/runtime"
if [[ ! -s "$EPOCH_FILE" ]]; then
  printf '%s\n' "$BOOTSTRAP_EPOCH_MS" > "$EPOCH_FILE"
fi
chmod 0644 "$EPOCH_FILE"
echo "RPB_EPOCH_START_MS=$(cat "$EPOCH_FILE")"

# The old RPB has already been stopped by the operator. Preserve its exact
# configuration as a rollback artifact, but never start it again: it contains
# the delayed-fill ownership race this patch repairs.
docker rm -f "$BACKUP_CONTAINER" >/dev/null 2>&1 || true
if docker inspect "$RPB_CONTAINER" >/dev/null 2>&1; then
  docker stop "$RPB_CONTAINER" >/dev/null 2>&1 || true
  docker rename "$RPB_CONTAINER" "$BACKUP_CONTAINER"
else
  echo "ERROR: existing RPB container not found" >&2
  exit 3
fi

IMAGE="$(docker inspect "$BACKUP_CONTAINER" --format '{{.Config.Image}}')"
docker inspect "$BACKUP_CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' > "$ENV_FILE"

# Verify the exact delayed-fill and epoch-recovery contracts in the runtime
# image before restoring execution authority.
docker run --rm \
  --env-file "$ENV_FILE" \
  -v "$WORKTREE:/workspace:ro" \
  -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -e PYTHONPYCACHEPREFIX=/tmp/rpb-pycache \
  "$IMAGE" python - <<'PY'
from rpb_fill_reconciliation import aggregate_order_trades, reconstruct_epoch_positions

fill = aggregate_order_trades(
    "o1",
    "DOT/USDT",
    [{"order":"o1","symbol":"DOT/USDT","side":"buy","amount":1.5,"price":1.02,"cost":1.53,"timestamp":10}],
)
assert fill["filled"] == 1.5 and abs(fill["average"] - 1.02) < 1e-12

positions = reconstruct_epoch_positions(
    [
        {"order":"n1","symbol":"DOT/USDT","side":"buy","amount":2.0,"price":1.0,"cost":2.0,"timestamp":1000},
        {"order":"n2","symbol":"DOT/USDT","side":"buy","amount":2.0,"price":1.1,"cost":2.2,"timestamp":1001},
    ],
    {"total":{"DOT":3.9}},
    since_ms=1000,
)
assert len(positions) == 1
assert abs(positions[0]["quantity"] - 3.9) < 1e-12
assert abs(positions[0]["entry_cost"] - 4.095) < 1e-12
print("RPB_FILL_RECONCILIATION_CONTRACT=PASS")
PY

# Start exactly one authenticated RPB owner with the same secret mounts and
# environment as the preserved container, but with the corrected entrypoint.
docker run -d \
  --name "$RPB_CONTAINER" \
  --restart unless-stopped \
  --env-file "$ENV_FILE" \
  -v "$WORKTREE:/workspace:ro" \
  -v "$RUNTIME:/intelligence/runtime:ro" \
  -v "$RPB_DATA:/rpb-data" \
  -v "$RPB_DATA/reports:/workspace/reports" \
  -v "$RPB_DATA/secrets:/run/secrets:ro" \
  -w /workspace \
  --health-cmd='python -c "import os; assert os.getpid() > 0; assert os.path.isdir(\"/rpb-data/runtime\")"' \
  --health-interval=30s \
  --health-timeout=5s \
  --health-retries=3 \
  "$IMAGE" \
  python -u rpb_runtime_entry.py >/dev/null

sleep 12
if ! docker inspect "$RPB_CONTAINER" --format '{{.State.Running}}' | grep -qx true; then
  echo "ERROR: corrected RPB failed to stay running" >&2
  docker logs --tail 220 "$RPB_CONTAINER" 2>&1 || true
  exit 4
fi

# Prove execution remains Testnet and only the corrected RPB owns it.
docker exec -i "$RPB_CONTAINER" python - <<'PY'
from src.leantrader.execution.router import execution_status
s = execution_status(mode="testnet", exchange_id="bybit")
print("EXECUTION_STATUS=", {k:s.get(k) for k in ("execution_mode","authority","backend","exchange","authenticated")})
assert s.get("execution_mode") == "testnet"
assert s.get("authority") == "testnet"
assert s.get("exchange") == "bybit"
assert s.get("authenticated") is True
print("RPB_TESTNET_AUTHORITY=PASS")
PY

for c in app-leantrader-1 leantrader-fast-lane-testnet leantrader-old-bybit-profit; do
  if docker inspect "$c" >/dev/null 2>&1 && docker inspect "$c" --format '{{.State.Running}}' | grep -qx true; then
    echo "ERROR: competing execution container is running: $c" >&2
    docker stop "$RPB_CONTAINER" >/dev/null 2>&1 || true
    exit 5
  fi
done

echo
echo "=== CORRECTED RPB STATUS ==="
docker ps --filter "name=$RPB_CONTAINER" --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'

echo
echo "=== FILL OWNERSHIP / EXIT EVIDENCE ==="
docker logs --since 10m "$RPB_CONTAINER" 2>&1 \
  | grep -E 'RPB EPOCH RECOVERY|POSITION LEDGER|AUTHENTICATED FILL RECONCILED|POSITION OPENED|AUTHENTICATED ENTRY|EXIT SIGNAL|POSITION CLOSED|PRECHECK|RPB START|DYNAMIC PAIRS|TOP MOVERS|RPB cycle error|EPOCH RECOVERY FAILED' \
  | tail -n 220 || true

echo
echo "=== CURRENT RPB LEDGER ==="
cat "$RPB_DATA/runtime/rpb_positions.json" 2>/dev/null || echo "RPB_LEDGER_NOT_YET_WRITTEN"

echo
echo "RPB_FILL_FIX=ACTIVE"
echo "OLD_BROKEN_RPB_PRESERVED_AS=$BACKUP_CONTAINER"
echo "NOTE=Bybit Testnet only; no live authority granted."
