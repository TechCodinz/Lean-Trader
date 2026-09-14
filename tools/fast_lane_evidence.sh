#!/usr/bin/env bash
# One-shot evidence collector for the fast lane, run on the VPS.
#
# Reads only. Places no orders, writes nothing into the container, and prints
# no credential values. Run it, paste the whole output back.
#
#   bash tools/fast_lane_evidence.sh > /tmp/fastlane_evidence.txt 2>&1
#   cat /tmp/fastlane_evidence.txt

C="${CONTAINER:-leantrader-native-testnet}"
rule() { printf '\n===== %s =====\n' "$1"; }

rule "CONTAINER"
docker ps --filter "name=${C}" --format '{{.Names}}\t{{.Image}}\t{{.Status}}'

rule "VELOCITY LANE STATE  /app/data/runtime/velocity_sniper_lane.json"
# The lane's own last verdict. This is the single most decisive field: it says
# which stage the lane stopped at on its most recent cycle.
docker exec "$C" python3 - <<'PY'
import json, os
for path in ("/app/data/runtime/velocity_sniper_lane.json",
             "/app/runtime/velocity_sniper_lane.json"):
    if not os.path.exists(path):
        continue
    print("PATH:", path)
    state = json.load(open(path))
    for key in ("last_decision", "last_reason", "last_error", "started_at",
                "entries_today", "active", "pending", "positions", "day"):
        if key in state:
            print(f"  {key} = {json.dumps(state[key])[:400]}")
    print("  ALL KEYS:", sorted(state))
    break
else:
    print("NO LANE STATE FILE FOUND")
PY

rule "EXECUTION TELEMETRY  (funnel + blockers + idle reason)"
docker exec "$C" python3 - <<'PY'
import json, os, sys
sys.path.insert(0, "/app")
from src.leantrader.execution import preflight, idle
snap = preflight.telemetry_snapshot()
print("PATH:", os.getenv("EXECUTION_TELEMETRY_PATH", "runtime/execution_telemetry.json"))
for k in ("attempts", "prepared", "submitted", "acknowledged", "fills", "closes"):
    print(f"  {k:14} {snap.get(k, 0)}")
print("  blockers:")
for name, entry in sorted((snap.get("blockers") or {}).items(),
                          key=lambda kv: -int(kv[1].get("count", 0))):
    print(f"    {name:38} {entry.get('count')}  last={str(entry.get('last_detail'))[:90]}")
v = idle.classify_idle_reason()
print("  EXECUTION_IDLE_REASON =", v["reason"])
print("  detail:", v["detail"])
print("  evidence:", json.dumps(v["evidence"]))
PY

rule "EXECUTOR SNAPSHOT + AUTHENTICATED FREE QUOTE"
# Diagnostic context: these reads are booked as diagnostic_* and must not
# move the runtime funnel above.
docker exec "$C" python3 - <<'PY'
import json, sys
sys.path.insert(0, "/app")
from src.leantrader.execution import preflight
from src.leantrader.production.fast_lane_executor import CentralAuthorityExecutor
with preflight.diagnostic_context():
    ex = CentralAuthorityExecutor()
    snap = ex.safe_snapshot()
    print("  fresh            ", snap.get("fresh"))
    print("  environment      ", snap.get("environment"))
    print("  free_quote       ", snap.get("free_quote"))
    print("  positions        ", json.dumps(snap.get("positions")))
    print("  open_orders      ", snap.get("open_orders"))
    print("  kill_switch      ", snap.get("kill_switch_active"))
PY

rule "MINIMUM EXECUTABLE TICKET vs FREE QUOTE"
docker exec "$C" python3 - <<'PY'
import sys
sys.path.insert(0, "/app")
from src.leantrader.execution import preflight
with preflight.diagnostic_context():
    b = preflight.shared_broker()
    bal = preflight.fetch_balance_cached(b) or {}
    free = float((bal.get("free") or {}).get("USDT") or 0.0)
    print("  authenticated free USDT =", free)
    mk = preflight.load_markets_cached(b) or {}
    ex = b._make_exchange(b.resolve_mode(), authenticated=False)
    for sym in ("BTC/USDT", "ETH/USDT", "DOGE/USDT"):
        m = mk.get(sym)
        if not m:
            continue
        px = preflight.fetch_last_price_cached(b, sym)
        if not px:
            continue
        t = preflight.minimum_executable_ticket(
            symbol=sym, venue=b.exchange_id, price=px,
            min_notional=((m.get("limits") or {}).get("cost") or {}).get("min") or 0.0,
            min_amount=((m.get("limits") or {}).get("amount") or {}).get("min") or 0.0,
            fee_rate=float(m.get("taker") or 0.001), exchange=ex)
        gap = t.total_cost - free
        print(f"  {sym:10} min_ticket={t.total_cost:.8f}  shortfall={gap:+.8f}  {t.detail[:70]}")
PY

rule "FULL EXECUTION STATUS (inventory, valuation, recovery, funnel)"
docker exec "$C" python3 -m tools.execution_status 2>&1 | tail -120

rule "INTENT LINEAGE  (where intents actually stop)"
docker exec "$C" python3 - <<'PY'
import sys, json
sys.path.insert(0, "/app")
from src.leantrader.execution import lineage
s = lineage.journal_summary()
print("  path:", s["path"])
print("  transitions:", s["transitions"], " distinct_intents:", s["distinct_intents"])
print("  furthest_stage_reached:", s["furthest_stage_reached"])
print("  intents_last_stage:", json.dumps(s["intents_last_stage"]))
print("  terminal_outcomes:", json.dumps(s["terminal_outcomes"]))
print("  by_source_engine:", json.dumps(s["by_source_engine"]))
print("  --- last 15 transitions ---")
for row in lineage.read_transitions(limit=15):
    print(f"    {row.get('stage'):24} {row.get('symbol',''):12} ok={row.get('ok')} "
          f"{str(row.get('reason') or row.get('detail') or '')[:70]}")
PY

rule "LANE DECISION REASONS IN LOGS (which stage stops the chain)"
docker logs --since 30m "$C" 2>&1 \
  | grep -oE '"?(testnet_[a-z_]+|fast_[a-z_]+|waiting_for_[a-z_]+|velocity_[a-z_]+|no_[a-z_]+)"?' \
  | sort | uniq -c | sort -rn | head -25

rule "FAST LANE LOG LINES (last 40)"
docker logs --since 30m "$C" 2>&1 | grep -iE "FAST LANE|velocity|microstream|precision|candidate|qualified" | tail -40

rule "EXECUTION LOG LINES (last 40)"
docker logs --since 30m "$C" 2>&1 \
  | grep -iE "submitted|acknowledged|filled|BUY|SELL|close|realized|free_quote|portfolio|principal_floor|BELOW_MIN|CAPITAL_BELOW" \
  | tail -40

rule "ERRORS / TRACEBACKS (last 30)"
docker logs --since 30m "$C" 2>&1 | grep -iE "Traceback|ERROR|CRITICAL|stopped:" | tail -30
