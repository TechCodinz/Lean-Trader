#!/usr/bin/env python3
"""being_status.py - one view of the whole being.

Run inside the container: python3 /app/being_status.py
Processes, wallet, positions, capacity ledger, current allocation.
Read-only; safe to run any time.
"""
import json
import os
import collections

print('=== PROCESSES ===')
seen = []
for pid in os.listdir('/proc'):
    if pid.isdigit():
        try:
            cl = open(f'/proc/{pid}/cmdline', 'rb').read().decode(errors='ignore').replace(chr(0), ' ')
            if 'python3' in cl and '.py' in cl:
                n = [t for t in cl.split(' ') if t.endswith('.py')]
                if n:
                    seen.append(n[0].split('/')[-1])
        except Exception:
            pass
for k, v in sorted(collections.Counter(seen).items()):
    print(f'  {k}: {v}')

print('=== WALLET (testnet, via relay) ===')
os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')
try:
    from testnet_client import make_client
    tn = make_client()
    print(f'  free USDT: ${tn.wallet_free_usdt():.2f}')
    print('=== EXCHANGE POSITIONS ===')
    for p in tn.positions():
        print(f"  {p.get('symbol')} size {p.get('size')} avg {p.get('avgPrice')} "
              f"value ${float(p.get('positionValue') or 0):.2f} uPnL {p.get('unrealisedPnl')}")
except Exception as e:
    print(f'  wallet read failed: {e}')

print('=== CAPACITY LEDGER (72h) ===')
try:
    import being_ledger
    for being, st in sorted(being_ledger.capacity_summary(72).items()):
        print(f"  {being}: real closes {st['closes']} W {st['wins']} "
              f"winrate {st['win_rate']:.0%} expectancy ${st['expectancy']:+.4f} "
              f"realized ${st['realized_pnl']:+.2f} (paper closes {st['paper_closes']})")
except Exception as e:
    print(f'  ledger read failed: {e}')

print('=== ALLOCATION ===')
try:
    a = json.load(open('/app/runtime/allocation.json'))
    print(f"  as of ts {int(a['ts'])} | free ${a['wallet_free']:.2f} | regime {a['regime']}")
    for k, v in a['beings'].items():
        print(f'  {k}: {v}')
except Exception as e:
    print(f'  allocation read failed: {e}')

print('=== ZOO BOOK ===')
try:
    st = json.load(open('/tmp/paper_state.json'))
    print(f"  paper cash ${st.get('cash', 0):.2f} | trades {len(st.get('trades', []))} "
          f"| open {len(st.get('positions', {}))}")
except Exception as e:
    print(f'  zoo state read failed: {e}')
