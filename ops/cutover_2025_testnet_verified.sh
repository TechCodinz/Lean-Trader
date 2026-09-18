#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE="/opt/leantrader/rpb-unified-20260917"
BRANCH="restore/rpb-unified-20260917"
CURRENT_RPB="leantrader-rpb-testnet"
LEGACY_CONTAINER="leantrader-2025-testnet"

cd "$SOURCE"

echo "=== VERIFIED OCTOBER-2025 TESTNET CUTOVER ==="
echo "branch=$BRANCH"
echo "head=$(git rev-parse HEAD)"

chmod +x ops/activate_2025_runtime_testnet.sh
bash ops/activate_2025_runtime_testnet.sh

rollback_postcheck() {
  echo "POST-CUTOVER VERIFICATION FAILED - restoring previous RPB runtime."
  docker rm -f "$LEGACY_CONTAINER" >/dev/null 2>&1 || true
  docker start "$CURRENT_RPB" >/dev/null 2>&1 || true
  exit 1
}

docker ps --format '{{.Names}}' | grep -qx "$LEGACY_CONTAINER" || rollback_postcheck

LOGS="$(docker logs --since 10m "$LEGACY_CONTAINER" 2>&1 || true)"

for marker in   'Learning Orchestrator wired'   'Scouting Orchestrator wired'   'Decision Engine wired'   'EXECUTION ORCHESTRATOR WIRED'   'SMART SCALPING ENGINE WIRED'   'LEGACY_2025_REAL_INTELLIGENCE_BRIDGE_INSTALLED'   'REAL_MARKET_SCAN'   'Evolution database initialized'
do
  printf '%s\n' "$LOGS" | grep -q "$marker" || {
    echo "missing_runtime_marker=$marker"
    rollback_postcheck
  }
done

echo
echo "=== AUTHENTICATED BYBIT TESTNET RUNTIME PROBE ==="
docker exec -i "$LEGACY_CONTAINER" python - <<'PY' || rollback_postcheck
from src.leantrader.execution.router import execution_status, route_balance

status = execution_status(mode="testnet", exchange_id="bybit")
balance = route_balance(mode="testnet", exchange_id="bybit") or {}
free = ((balance.get("free") or {}).get("USDT"))
if free is None:
    free = ((balance.get("USDT") or {}).get("free"))

safe = {
    "execution_mode": status.get("execution_mode"),
    "authority": status.get("authority"),
    "exchange": status.get("exchange"),
    "authenticated": bool(status.get("authenticated")),
    "free_USDT": None if free is None else round(float(free), 8),
}
print("RUNTIME_PROOF AUTHENTICATED_BYBIT_ACCOUNT", safe)

assert safe["execution_mode"] == "testnet"
assert safe["authority"] == "testnet"
assert safe["exchange"] == "bybit"
assert safe["authenticated"] is True
assert safe["free_USDT"] is not None
PY

echo
echo "=== ENGINE + MARKET PROOF ==="
printf '%s\n' "$LOGS"   | grep -E 'Learning Orchestrator wired|Scouting Orchestrator wired|Decision Engine wired|EXECUTION ORCHESTRATOR WIRED|SMART SCALPING ENGINE WIRED|REAL_MARKET_SCAN|Scalper generated|Published .* signals|Decision:|EXECUTING:|Evolution database initialized|Evidence Evolution cycle'   | tail -n 220 || true

echo
echo "=== AUTHENTICATED LIFECYCLE PROOF WINDOW ==="
ROUND_TRIP_OK=0
NEXT_CYCLE_OK=0

for _ in $(seq 1 30); do
  PROOF="$(docker logs --since 15m "$LEGACY_CONTAINER" 2>&1 || true)"

  if printf '%s\n' "$PROOF" | grep -q 'RUNTIME_PROOF TESTNET_ACK'      && printf '%s\n' "$PROOF" | grep -q 'RUNTIME_PROOF AUTHENTICATED_FILL'      && printf '%s\n' "$PROOF" | grep -q 'RUNTIME_PROOF POSITION_OWNER'      && printf '%s\n' "$PROOF" | grep -q 'RUNTIME_PROOF AUTHENTICATED_CLOSE_FILL'      && printf '%s\n' "$PROOF" | grep -q 'RUNTIME_PROOF REALIZED_NET_AFTER_COSTS'      && printf '%s\n' "$PROOF" | grep -q 'RUNTIME_PROOF CAPITAL_RECYCLED'; then
    ROUND_TRIP_OK=1
  fi

  if printf '%s\n' "$PROOF" | grep -q 'RUNTIME_PROOF NEXT_TRADE_CYCLE'; then
    NEXT_CYCLE_OK=1
  fi

  if [ "$ROUND_TRIP_OK" -eq 1 ] && [ "$NEXT_CYCLE_OK" -eq 1 ]; then
    break
  fi

  sleep 10
done

docker logs --since 15m "$LEGACY_CONTAINER" 2>&1   | grep -E 'RUNTIME_PROOF (TESTNET_ACK|AUTHENTICATED_FILL|POSITION_OWNER|AUTHENTICATED_CLOSE_FILL|REALIZED_NET_AFTER_COSTS|CAPITAL_RECYCLED|NEXT_TRADE_CYCLE)'   | tail -n 120 || true

if [ "$ROUND_TRIP_OK" -eq 1 ]; then
  echo "AUTHENTICATED_ROUND_TRIP_PROVED"
else
  echo "AUTHENTICATED_ROUND_TRIP_NOT_OBSERVED_IN_PROOF_WINDOW"
fi

if [ "$NEXT_CYCLE_OK" -eq 1 ]; then
  echo "NEXT_TRADE_CYCLE_PROVED"
else
  echo "NEXT_TRADE_CYCLE_NOT_OBSERVED_IN_PROOF_WINDOW"
fi

echo
echo "=== FINAL MODE ==="
docker exec -i "$LEGACY_CONTAINER" python - <<'PY'
import os
print({
    "TRADING_MODE": os.getenv("TRADING_MODE"),
    "EXECUTION_MODE": os.getenv("EXECUTION_MODE"),
    "USE_TESTNET": os.getenv("USE_TESTNET"),
    "ENABLE_LIVE": os.getenv("ENABLE_LIVE"),
})
PY

echo
echo "VERIFIED_2025_TESTNET_RUNTIME_ACTIVE"
