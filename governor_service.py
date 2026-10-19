#!/usr/bin/env python3
"""
ALLOCATION GOVERNOR - LeanTrader's resource brain.

Peters' design (2026-10-18): the beings are not run in isolation and
not left on fixed caps - the being allocates work and capital to each
being based on its MEASURED CAPACITY and the CURRENT NEED.

Inputs (every 5 minutes):
- being_ledger capacity summary (72h): per-being realized expectancy,
  win rate, close count on real testnet closes.
- Wallet free USDT via the signing relay.
- Market regime from the zoo's latest ultrasonic read.

Outputs /app/runtime/allocation.json: per-being mode (real/paper),
slice size, max concurrent real positions. Beings read it through
allocation.py with safe defaults - the governor can die without
stopping any being.

Rules:
- Capacity score = expectancy x sample confidence (closes/20, cap 1).
- Weights keep a floor: nobody starves; a being with no data yet gets
  exploration weight.
- A being with negative expectancy on >= 15 closes is demoted to
  paper-learning (never stopped - it keeps learning until its numbers
  recover). This is the zoo's own flow rule generalised.
- Thin wallet (< $15 free): only the strongest being trades real.
- Regime tilts are mild: ranging favours the swarm, bear trims the
  zoo and favours the swarm, bull/trend favours zoo + continuous.
- November (inside continuous_service) remains the growth brain -
  targets and phases. The governor only splits resources beneath it.
"""
import json
import logging
import os
import re
import time
import urllib.parse
import urllib.request

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - GOVERNOR - %(message)s')
logger = logging.getLogger('GOVERNOR')

ALLOC_PATH = '/app/runtime/allocation.json'
BEINGS = ['zoo', 'continuous', 'swarm']
CYCLE = 300


def tg(msg):
    tok = os.environ.get('TELEGRAM_BOT_TOKEN')
    cid = os.environ.get('TELEGRAM_CHAT_ID')
    if not tok or not cid:
        return
    try:
        data = urllib.parse.urlencode({'chat_id': cid, 'text': msg}).encode()
        urllib.request.urlopen(
            urllib.request.Request(
                f'https://api.telegram.org/bot{tok}/sendMessage', data=data),
            timeout=10)
    except Exception:
        pass


def wallet_free(tn):
    try:
        return float(tn.wallet_free_usdt())
    except Exception:
        return 0.0


def current_regime():
    try:
        path = '/tmp/zoo_paper.log'
        size = os.path.getsize(path)
        with open(path, 'rb') as f:
            f.seek(max(0, size - 300000))
            tail = f.read().decode(errors='ignore')
        hits = re.findall(r'ULTRASONIC regime=(\w+)', tail)
        return hits[-1] if hits else 'unknown'
    except Exception:
        return 'unknown'


def compute(tn):
    import being_ledger
    stats = being_ledger.capacity_summary(72)
    free = wallet_free(tn)
    regime = current_regime()

    scores = {}
    for b in BEINGS:
        st = stats.get(b) or {'closes': 0, 'expectancy': 0.0}
        n = st['closes']
        scores[b] = (st['expectancy'] * min(1.0, n / 20.0)) if n else None

    mult = {'zoo': 1.0, 'continuous': 1.0, 'swarm': 1.0}
    if regime == 'ranging':
        mult['swarm'] = 1.15
    elif regime == 'bear':
        mult['zoo'] = 0.8
        mult['swarm'] = 1.1
    elif regime in ('bull', 'trend', 'trending', 'bullish'):
        mult['zoo'] = 1.1
        mult['continuous'] = 1.1

    adj = {b: max(scores[b] or 0.0, 0.0) * mult[b] for b in BEINGS}
    total = sum(adj.values())
    if total <= 0:
        weights = {b: 1.0 / 3 for b in BEINGS}
    else:
        weights = {b: 0.05 + 0.85 * adj[b] / total for b in BEINGS}

    modes = {}
    for b in BEINGS:
        s = scores[b]
        n = (stats.get(b) or {}).get('closes', 0)
        modes[b] = 'paper' if (s is not None and s < 0 and n >= 15) else 'real'
    if 0 < free < 15:
        top = max(weights, key=weights.get)
        for b in BEINGS:
            if b != top:
                modes[b] = 'paper'

    beings = {
        'zoo': {
            'mode': modes['zoo'],
            'real_cap': 0 if modes['zoo'] != 'real'
            else max(1, min(4, round(1 + weights['zoo'] * 3))),
        },
        'continuous': {
            'mode': modes['continuous'],
            'slice_usd': round(max(12.0, min(60.0, 10 + weights['continuous'] * 45)), 2),
            'max_concurrent': max(2, min(6, round(2 + weights['continuous'] * 4))),
        },
        'swarm': {
            'mode': modes['swarm'],
            'slice_usd': round(max(11.0, min(40.0, 8 + weights['swarm'] * 30)), 2),
            'max_concurrent': max(1, min(4, round(1 + weights['swarm'] * 3))),
        },
    }
    return {
        'ts': time.time(),
        'wallet_free': free,
        'regime': regime,
        'scores': {b: (round(scores[b], 4) if scores[b] is not None else None)
                   for b in BEINGS},
        'weights': {b: round(weights[b], 3) for b in BEINGS},
        'stats': {b: stats.get(b) for b in BEINGS},
        'beings': beings,
    }


def main():
    os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')
    from testnet_client import make_client
    tn = make_client()
    logger.info('Allocation governor live - capacity-based allocation every 5m')
    tg('🧠 Allocation governor live: beings will be sized by measured capacity.')
    prev_modes = {}
    while True:
        try:
            alloc = compute(tn)
            os.makedirs(os.path.dirname(ALLOC_PATH), exist_ok=True)
            tmp = ALLOC_PATH + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(alloc, f, indent=1)
            os.replace(tmp, ALLOC_PATH)
            b = alloc['beings']
            logger.info(
                f"alloc zoo[{b['zoo']['mode']} cap {b['zoo']['real_cap']}] "
                f"cont[{b['continuous']['mode']} ${b['continuous']['slice_usd']} x{b['continuous']['max_concurrent']}] "
                f"swarm[{b['swarm']['mode']} ${b['swarm']['slice_usd']} x{b['swarm']['max_concurrent']}] "
                f"| free ${alloc['wallet_free']:.2f} regime {alloc['regime']} "
                f"weights {alloc['weights']}")
            modes = {k: v['mode'] for k, v in b.items()}
            if prev_modes and modes != prev_modes:
                tg(f"🧠 Allocation change: {modes} (free ${alloc['wallet_free']:.2f}, regime {alloc['regime']})")
            prev_modes = modes
        except Exception as e:
            logger.warning(f'governor cycle: {e}')
        time.sleep(CYCLE)


if __name__ == '__main__':
    main()
