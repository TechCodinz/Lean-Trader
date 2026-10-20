"""Triangular arbitrage organ - STAGED with self-activation.

Built 2026-10-20 on Princewill's instruction: 'wire it - when the
api that has what it needs, it activates and starts working.'

The GOLDMINE file's finder was cross-exchange latency arbitrage
with invented 50ms latencies and a two-venue balance requirement -
not wireable honestly. This organ is REAL triangular arbitrage on
ONE venue (Bybit spot): USDT -> A -> B -> USDT cycles priced from
live bid/ask, fees charged per leg. One venue = the pending
mainnet key set is the only API it needs.

STAGED BEHAVIOUR (the funding-arb pattern):
- NOW: scans real public spot prices every cycle, logs the best
  cycle net of fees, and ledger-records paper detections. It is
  learning what the real opportunity rate is.
- ACTIVATES ITSELF when ALL of these are true (checked every
  cycle): /app/runtime/mainnet_enabled exists (the mainnet
  kill-switch file), the mainnet relay answers healthy, and the
  unified USDT balance is >= $6. Then live cycles execute through
  the mainnet spot arm under the shared mainnet rails: starting
  leg <= $7.50, one cycle at a time, the shared $2 daily-loss
  halt (runtime/mainnet_day.json).
- If the gate closes (kill-switch removed, relay down), it
  disarms back to paper on the next cycle.
"""
import json
import os
import time
from datetime import datetime, timezone

import requests

from being_ledger import record_close
from tg_utils import send_text as tg_send

LOG_PREFIX = 'TRIANGLE'
CYCLE_SEC = 120
FEE_PER_LEG = 0.001          # Bybit spot taker 0.1% per leg
MIN_NET_BPS = 15             # paper-record / live threshold
START_NOTIONAL = 7.50        # shared mainnet order cap
MIN_BALANCE = 6.0
DAY_FILE = '/app/runtime/mainnet_day.json'
ARM_FILE = '/app/runtime/mainnet_enabled'
BASES = ['BTC', 'ETH', 'SOL', 'XRP', 'BNB', 'DOGE', 'ADA', 'NEAR',
         'LINK', 'AVAX', 'DOT', 'LTC']


def log(msg):
    print(f"{datetime.now(timezone.utc).isoformat()} {LOG_PREFIX} {msg}",
          flush=True)


def edge(prices, frm, to):
    """Units of `to` received per 1 unit of `frm`, executable side.
    Pair 'TO/FRM' (to priced in frm): buy at ask -> 1/ask.
    Pair 'FRM/TO' (frm priced in to): sell at bid -> bid."""
    p = prices.get(f'{to}/{frm}')
    if p and p.get('ask'):
        return 1.0 / p['ask']
    p = prices.get(f'{frm}/{to}')
    if p and p.get('bid'):
        return float(p['bid'])
    return None


def pair_for(prices, frm, to):
    if f'{to}/{frm}' in prices:
        return (f'{to}/{frm}', 'buy')
    if f'{frm}/{to}' in prices:
        return (f'{frm}/{to}', 'sell')
    return (None, None)


def best_cycle(prices):
    """Return (net_fraction, path, legs) for the best USDT 3-cycle."""
    best = None
    assets = [a for a in BASES if f'{a}/USDT' in prices]
    for a in assets:
        for b in assets:
            if a == b:
                continue
            e1 = edge(prices, 'USDT', a)
            e2 = edge(prices, a, b)
            e3 = edge(prices, b, 'USDT')
            if not (e1 and e2 and e3):
                continue
            gross = e1 * e2 * e3
            net = gross * (1 - FEE_PER_LEG) ** 3 - 1.0
            if best is None or net > best[0]:
                legs = [pair_for(prices, 'USDT', a),
                        pair_for(prices, a, b),
                        pair_for(prices, b, 'USDT')]
                best = (net, f'USDT->{a}->{b}->USDT', legs)
    return best


def load_prices(ex):
    valid = set(ex.symbols or [])
    syms = [f'{a}/USDT' for a in BASES]
    for a in BASES:
        for b in BASES:
            if a != b:
                syms.append(f'{a}/{b}')
    syms = [s for s in syms if s in valid]
    tickers = ex.fetch_tickers(syms)
    prices = {}
    for s, t in tickers.items():
        if t and t.get('bid') and t.get('ask'):
            prices[s] = {'bid': float(t['bid']), 'ask': float(t['ask'])}
    return prices


def daily_halted():
    try:
        d = json.load(open(DAY_FILE))
        day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        return d.get('date') == day and float(d.get('pnl', 0)) <= -2.0
    except Exception:
        return False


def activation_state(mc):
    """(armed, reason) - the whole staging contract in one place."""
    if not os.path.exists(ARM_FILE):
        return False, 'kill-switch file absent'
    try:
        h = requests.get('http://172.17.0.1:18098/health', timeout=5)
        if not h.ok:
            return False, 'mainnet relay unhealthy'
    except Exception:
        return False, 'mainnet relay unreachable'
    try:
        bal = mc.wallet_free_usdt()
    except Exception as e:
        return False, f'balance read failed: {e}'
    if bal is None or bal < MIN_BALANCE:
        return False, f'balance {bal} < {MIN_BALANCE}'
    return True, f'armed (balance ${bal:.2f})'


def run_live_cycle(mc, prices, net, path, legs):
    """Execute one cycle through the spot arm. Leg sizing uses the
    scan's live prices (estimates); the RETURNED number is the
    wallet equity delta - the only honest realized figure. None
    if a leg failed (residuals logged loudly)."""
    before = mc.wallet_equity_usdt()
    amt = START_NOTIONAL
    cur = 'USDT'
    try:
        for (sym, side), nxt in zip(legs, path.split('->')[1:]):
            raw = sym.replace('/', '')
            t = prices[sym]
            if side == 'buy':
                qty = amt / t['ask']
                mc.spot_market_buy(raw, qty)
                amt = qty
            else:
                mc.spot_market_sell(raw, amt)
                amt = amt * t['bid']
            cur = nxt
        time.sleep(2)
        after = mc.wallet_equity_usdt()
        return (after - before) if (before is not None and after is not None) else None
    except Exception as e:
        log(f'LIVE CYCLE LEG FAILURE on {path} at {cur}: {e} - '
            f'RESIDUAL ASSET MAY BE HELD IN {cur}; check the account')
        tg_send(f'🔺 TRIANGLE leg failure on {path} at {cur}: {e}. '
                f'A residual asset may be held - check the account.')
        return None


def main():
    import ccxt
    ex = ccxt.bybit({'enableRateLimit': True,
                     'options': {'defaultType': 'spot'}})
    ex.load_markets()
    mc = None

    def get_client():
        # Lazy + retried: pre-activation there are no keys and
        # make_client() returns None; the cycle the API appears,
        # this starts succeeding on its own.
        nonlocal mc
        if mc is None:
            try:
                from mainnet_client import make_client
                mc = make_client()
            except Exception:
                mc = None
        return mc
    armed = False
    log('triangular organ live - PAPER scanning (staged)')
    while True:
        try:
            # Self-activation watch: evaluated every cycle, so the
            # moment the needed API exists the organ arms itself
            # and announces it - no restart, no human step.
            client = get_client()
            if client is not None:
                now_armed, why = activation_state(client)
                if now_armed and not armed:
                    log(f'ACTIVATED: {why}')
                    tg_send('🔺 TRIANGULAR ARB ACTIVATED - the '
                            'mainnet API it needed is present; '
                            'live cycles will execute on detection.')
                elif armed and not now_armed:
                    log(f'DISARMED ({why}) - back to paper scanning')
                armed = now_armed
            prices = load_prices(ex)
            found = best_cycle(prices)
            if found:
                net, path, legs = found
                log(f'scan: pairs {len(prices)} best {path} '
                    f'net {net * 10000:+.1f} bps')
                if net * 10000 >= MIN_NET_BPS:
                    if armed and not daily_halted():
                        realized = run_live_cycle(client, prices, net, path, legs)
                        if realized is not None:
                            record_close('triangular', path, realized,
                                         real=True,
                                         meta={'kind': 'triangular_live',
                                               'net_bps_est': net * 10000})
                            log(f'LIVE cycle {path} realized {realized:+.4f}')
                    else:
                        gate = why if client is not None else 'no mainnet client yet'
                        record_close('triangular', path,
                                     net * START_NOTIONAL, real=False,
                                     meta={'kind': 'triangular_paper',
                                           'net_bps': net * 10000,
                                           'gate': gate})
                        log(f'paper detection {path} net {net * 10000:+.1f} bps '
                            f'(gate: {gate})')
            else:
                log(f'scan: pairs {len(prices)} no complete cycle')
        except Exception as e:
            log(f'cycle error: {e}')
        time.sleep(CYCLE_SEC)


if __name__ == '__main__':
    main()
