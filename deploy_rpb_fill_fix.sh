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

mkdir -p "$RPB_DATA/runtime" "$RPB_DATA/runtime/learn" "$RPB_DATA/reports"
if [[ ! -s "$EPOCH_FILE" ]]; then
  printf '%s\n' "$BOOTSTRAP_EPOCH_MS" > "$EPOCH_FILE"
fi
chmod 0644 "$EPOCH_FILE"
echo "RPB_EPOCH_START_MS=$(cat "$EPOCH_FILE")"

# Preserve the currently stopped RPB as rollback evidence while replacing only
# its runtime wiring. The backup is restart-disabled and never becomes an
# execution owner.
docker rm -f "$BACKUP_CONTAINER" >/dev/null 2>&1 || true
if docker inspect "$RPB_CONTAINER" >/dev/null 2>&1; then
  docker stop "$RPB_CONTAINER" >/dev/null 2>&1 || true
  docker rename "$RPB_CONTAINER" "$BACKUP_CONTAINER"
  docker update --restart=no "$BACKUP_CONTAINER" >/dev/null 2>&1 || true
else
  echo "ERROR: existing RPB container not found" >&2
  exit 3
fi

IMAGE="$(docker inspect "$BACKUP_CONTAINER" --format '{{.Config.Image}}')"
docker inspect "$BACKUP_CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' > "$ENV_FILE"

IMAGE_UID="$(docker run --rm --entrypoint sh "$IMAGE" -lc 'id -u' | tail -n 1)"
IMAGE_GID="$(docker run --rm --entrypoint sh "$IMAGE" -lc 'id -g' | tail -n 1)"
if [[ "$IMAGE_UID" =~ ^[0-9]+$ && "$IMAGE_GID" =~ ^[0-9]+$ ]]; then
  chown -R "$IMAGE_UID:$IMAGE_GID" "$RPB_DATA/runtime" "$RPB_DATA/reports"
fi

# Verify fill reconstruction plus the hardening predicates before restoring
# authenticated execution authority.
docker run --rm -i \
  --env-file "$ENV_FILE" \
  -v "$WORKTREE:/workspace:ro" \
  -w /workspace \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -e PYTHONPYCACHEPREFIX=/tmp/rpb-pycache \
  "$IMAGE" python - <<'PY'
from pathlib import Path
from rpb_fill_reconciliation import aggregate_order_trades, reconstruct_epoch_positions
from rpb_runtime_hardening import (
    PendingExecutionStore,
    PairQuarantineStore,
    definitive_exchange_reject_reason,
    is_dust_block,
)

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

assert is_dust_block({
    "blocker":"CAPITAL_BELOW_EXECUTABLE_MINIMUM",
    "detail":"ETH/USDT requested 0.00001 is worth 0.02 USDT, below the venue floor 1.0",
})
assert definitive_exchange_reject_reason('retCode":170209 only available to the China region') == "region_restricted_market"
assert definitive_exchange_reject_reason('retCode":170381 maximum allowed per order') == "venue_max_order_constraint"

pending_path = Path("/tmp/rpb-pending-contract.json")
pending = PendingExecutionStore(pending_path)
pending.set({"symbol":"DOT/USDT","side":"buy","order_id":"123"})
assert pending.get()["order_id"] == "123"
pending.clear()
assert pending.get() == {}

q_path = Path("/tmp/rpb-quarantine-contract.json")
q = PairQuarantineStore(q_path)
q.add("HNT/USDT", kind="exchange_reject", reason="region_restricted_market", ttl_seconds=60)
assert "HNT/USDT" in q.symbols()
print("RPB_RUNTIME_HARDENING_CONTRACT=PASS")
PY

# Start exactly one authenticated RPB owner with writable RPB-owned learning,
# a venue-executable micro floor, persistent pending ownership, and a simple
# container-local healthcheck. Nothing here grants live authority.
docker run -d \
  --name "$RPB_CONTAINER" \
  --restart unless-stopped \
  --env-file "$ENV_FILE" \
  -e LEANTRADER_DATA_DIR=/rpb-data \
  -e LEARN_STATE_PATH=/rpb-data/runtime/learn_state.json \
  -e LEARN_LOG_DIR=/rpb-data/runtime/learn \
  -e RPB_EXECUTABLE_FLOOR_USD="${RPB_EXECUTABLE_FLOOR_USD:-5.10}" \
  -e RPB_FILL_RECONCILE_SECONDS="${RPB_FILL_RECONCILE_SECONDS:-6}" \
  -e RPB_OWNERSHIP_SWEEP_SECONDS="${RPB_OWNERSHIP_SWEEP_SECONDS:-5}" \
  -e RPB_PENDING_PATH=/rpb-data/runtime/rpb_pending_execution.json \
  -e RPB_QUARANTINE_PATH=/rpb-data/runtime/rpb_quarantined_pairs.json \
  -v "$WORKTREE:/workspace:ro" \
  -v "$RUNTIME:/intelligence/runtime:ro" \
  -v "$RPB_DATA:/rpb-data" \
  -v "$RPB_DATA/reports:/workspace/reports" \
  -v "$RPB_DATA/secrets:/run/secrets:ro" \
  -w /workspace \
  --health-cmd='test -d /rpb-data/runtime && test -r /workspace/rpb_runtime_entry.py' \
  --health-interval=10s \
  --health-timeout=5s \
  --health-retries=3 \
  --health-start-period=5s \
  "$IMAGE" \
  python -u rpb_runtime_entry.py >/dev/null

sleep 14
if ! docker inspect "$RPB_CONTAINER" --format '{{.State.Running}}' | grep -qx true; then
  echo "ERROR: hardened RPB failed to stay running" >&2
  docker logs --tail 220 "$RPB_CONTAINER" 2>&1 || true
  exit 4
fi

HEALTH="$(docker inspect "$RPB_CONTAINER" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}')"
echo "RPB_HEALTH=$HEALTH"
if [[ "$HEALTH" == "unhealthy" ]]; then
  echo "ERROR: hardened RPB healthcheck failed" >&2
  docker inspect "$RPB_CONTAINER" --format '{{range .State.Health.Log}}{{println .ExitCode .Output}}{{end}}' || true
  exit 6
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
echo "=== HARDENED RPB STATUS ==="
docker ps --filter "name=$RPB_CONTAINER" --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'

echo
echo "=== RUNTIME EVIDENCE ==="
docker logs --since 10m "$RPB_CONTAINER" 2>&1 \
  | grep -E 'RPB EPOCH RECOVERY|RPB OWNERSHIP SWEEP|PENDING|POSITION LEDGER|AUTHENTICATED FILL RECONCILED|POSITION OPENED|AUTHENTICATED ENTRY|DUST QUARANTINED|PAIR QUARANTINED|EXIT SIGNAL|POSITION CLOSED|PRECHECK|RPB START|DYNAMIC PAIRS|TOP MOVERS|learner feedback unavailable|RPB cycle error|EPOCH RECOVERY FAILED' \
  | tail -n 260 || true

echo
echo "=== CURRENT RPB LEDGER ==="
cat "$RPB_DATA/runtime/rpb_positions.json" 2>/dev/null || echo "RPB_LEDGER_NOT_YET_WRITTEN"

echo
echo "=== QUARANTINES ==="
cat "$RPB_DATA/runtime/rpb_quarantined_pairs.json" 2>/dev/null || echo "NO_QUARANTINES_YET"

echo
echo "=== PENDING EXECUTION ==="
cat "$RPB_DATA/runtime/rpb_pending_execution.json" 2>/dev/null || echo "NO_PENDING_EXECUTION"

echo
echo "RPB_RUNTIME_HARDENING=ACTIVE"
echo "EXECUTABLE_MICRO_FLOOR_USD=${RPB_EXECUTABLE_FLOOR_USD:-5.10}"
echo "OLD_RPB_PRESERVED_AS=$BACKUP_CONTAINER"
echo "NOTE=Bybit Testnet only; no live authority granted."
