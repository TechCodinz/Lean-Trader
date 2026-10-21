"""TRUTH SERVICE - the being's single source of real-money truth.

Princewill's directive (2026-10-21): what Telegram shows must match
what is on the testnet, and the way they trade must be resolved and
routed properly. The forensic read proved the beings book closes
from SIGNAL prices (their ledgers summed ~-$3 over 48h) while the
exchange booked FILL prices (-$14.36 over the same window) - an
~$11 disagreement of spread + fees that no internal log showed.

This service closes that gap at the source:
- Polls the exchange's closed-PnL (the venue's realized record)
  every 60s, nets out the actual fill fees from the execution
  list, attributes each close to its owning being (nearest
  ledger close on the same symbol within +-600s; else 'fleet'),
  and appends it to being_ledger.jsonl with source='exchange'.
  Consumers (governor capacity, bus-bridge learning, pair study)
  treat source='exchange' records as the ONLY real record; the
  beings' own optimistic records remain for paper and audit.
- Writes /app/runtime/wallet_truth.json every cycle (real wallet
  balance, IM rate, available, USDT) - one truth for every
  consumer that used to read the phantom equity.
- Is the single Telegram voice for REAL closes (the zoo
  suppresses its own real-close messages while the heartbeat
  /app/runtime/truth_active is fresh): every real close is
  announced with the EXCHANGE figure, never an internal estimate.

It places no orders and changes no positions. Read + report only.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, '/app')
from testnet_client import make_client

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - TRUTH - %(message)s')
logger = logging.getLogger('truth')

LEDGER = '/app/runtime/being_ledger.jsonl'
STATE = '/app/runtime/truth_state.json'
WALLET_TRUTH = '/app/runtime/wallet_truth.json'
HEARTBEAT = '/app/runtime/truth_active'
WINDOW_MS = 72 * 3600 * 1000


def tg(msg):
    tok = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat = os.environ.get('TELEGRAM_CHAT_ID')
    if not tok or not chat:
        return
    try:
        data = json.dumps({'chat_id': chat, 'text': msg}).encode()
        req = urllib.request.Request(
            f'https://api.telegram.org/bot{tok}/sendMessage',
            data=data,
            headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        logger.warning(f'tg failed: {e}')


def norm(sym):
    return (sym or '').replace(':USDT', '').replace('/', '').upper()


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {'seen': [], 'last_poll_ms': 0}


def save_state(st):
    try:
        with open(STATE, 'w') as f:
            json.dump(st, f)
    except Exception as e:
        logger.warning(f'state save failed: {e}')


def ledger_real_closes():
    """(ts, norm_symbol, being) for the beings' own real closes -
    the attribution index for exchange records."""
    out = []
    try:
        with open(LEDGER) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get('real') and d.get('source') != 'exchange':
                    out.append((float(d.get('ts') or 0),
                                norm(d.get('symbol')),
                                d.get('being') or 'fleet'))
    except Exception:
        pass
    return out


def attribute(ts_s, nsym, index):
    best, best_dt = 'fleet', 601
    for lts, lsym, being in index:
        if lsym != nsym:
            continue
        dt = abs(lts - ts_s)
        if dt < best_dt:
            best, best_dt = being, dt
    return best


def fetch_fees(tn, order_id):
    """Actual fill fees for one order from the execution list.
    Returns None when the venue read is unavailable - the record
    then carries gross closed-PnL, labelled as such."""
    try:
        r = tn._req('GET', '/v5/execution/list',
                    {'category': 'linear', 'orderId': order_id,
                     'limit': 50})
        rows = r.get('list') or []
        if not rows:
            return None
        return sum(float(x.get('execFee') or 0) for x in rows)
    except Exception:
        return None


def wallet_truth(tn):
    try:
        r = tn._req('GET', '/v5/account/wallet-balance',
                    {'accountType': 'UNIFIED'})
        a = (r.get('list') or [{}])[0]
        usdt = 0.0
        for c in a.get('coin') or []:
            if c.get('coin') == 'USDT':
                usdt = float(c.get('walletBalance') or 0)
        wt = {
            'ts': time.time(),
            'wallet_balance': float(a.get('totalWalletBalance')
                                    or 0),
            'im_rate': float(a.get('accountIMRate') or 0),
            'available': float(a.get('totalAvailableBalance') or 0),
            'equity_display': float(a.get('totalEquity') or 0),
            'usdt': usdt,
        }
        with open(WALLET_TRUTH, 'w') as f:
            json.dump(wt, f)
        return wt
    except Exception as e:
        logger.warning(f'wallet truth failed: {e}')
        return None


def _req_retry(tn, method, path, params, tries=3):
    """Venue reads from this shared IP collide with the fleet's
    own bursts and draw WAF 403s that clear in seconds (a quiet
    probe passes immediately). Retry on a short jittered ladder
    instead of failing the whole cycle."""
    import random
    last = None
    for k in range(tries):
        try:
            return tn._req(method, path, params)
        except Exception as e:
            last = e
            if '403' not in str(e):
                raise
            time.sleep(4 + 5 * k + random.uniform(0, 3))
    raise last


def _append_records(tn, rows, st, live):
    seen = set(st.get('seen') or [])
    index = ledger_real_closes()
    appended = []
    for x in rows:
        oid = x.get('orderId')
        if not oid or oid in seen:
            continue
        seen.add(oid)
        ts_s = float(x.get('updatedTime') or 0) / 1000.0
        being = attribute(ts_s, norm(x.get('symbol')), index)
        gross = float(x.get('closedPnl') or 0)
        fees = fetch_fees(tn, oid) if live else None
        pnl = gross - fees if fees is not None else gross
        rec = {
            'ts': ts_s,
            'being': being,
            'symbol': (x.get('symbol') or '')[:-4] + '/USDT'
            if (x.get('symbol') or '').endswith('USDT')
            else x.get('symbol'),
            'pnl': round(pnl, 4),
            'real': True,
            'source': 'exchange',
            'meta': {'exchange_order': oid,
                     'gross': gross, 'fees': fees},
        }
        with open(LEDGER, 'a') as f:
            f.write(json.dumps(rec) + '\n')
        appended.append(rec)
    st['seen'] = list(seen)[-2000:]
    return appended


def _fetch_window(tn, start_ms, end_ms):
    """One window of closed-PnL, paged politely. Returns
    (rows, complete)."""
    rows, cursor = [], None
    for _page in range(4):
        params = {'category': 'linear', 'startTime': start_ms,
                  'endTime': end_ms, 'limit': 100}
        if cursor:
            params['cursor'] = cursor
        try:
            r = _req_retry(tn, 'GET', '/v5/position/closed-pnl',
                           params)
        except Exception as e:
            logger.warning(f'closed-pnl fetch failed: {e}')
            return rows, False
        rows += r.get('list') or []
        cursor = r.get('nextPageCursor')
        if not cursor:
            return rows, True
        time.sleep(2)
    return rows, True


def poll_closes(tn, st, live):
    """Live tail first (last hour - flows even while history is
    still filling), then ONE 6h backfill slice per cycle. The
    old design retried the full 72h window every cycle - the
    biggest burst on the box, starving itself."""
    now_ms = int(time.time() * 1000)
    appended = []
    tail_start = max(st.get('last_poll_ms', 0) - 300000,
                     now_ms - 3600000)
    rows, complete = _fetch_window(tn, tail_start, now_ms)
    appended += _append_records(tn, rows, st, live)
    if complete:
        st['last_poll_ms'] = now_ms
    bf_from = st.get('backfill_from_ms')
    if bf_from is None:
        bf_from = now_ms - WINDOW_MS
    if bf_from < tail_start:
        bf_to = min(bf_from + 6 * 3600 * 1000, tail_start)
        rows, ok = _fetch_window(tn, bf_from, bf_to)
        appended += _append_records(tn, rows, st, live=False)
        if ok:
            st['backfill_from_ms'] = bf_to
    return appended


def main():
    tn = make_client()
    st = load_state()
    wt = wallet_truth(tn)
    # boot backfill (silent): history becomes truth records
    try:
        back = poll_closes(tn, st, live=False)
    except Exception as e:
        logger.warning(f'boot backfill deferred: {e}')
        back = []
    save_state(st)
    logger.info(f'truth service live - backfilled {len(back)} '
                f'exchange closes; wallet {wt}')
    tg('⚖️ Truth service live: real closes now book from the '
       'exchange record (fills + fees), not internal estimates.')
    while True:
        try:
            with open(HEARTBEAT, 'w') as f:
                f.write(str(time.time()))
            wt = wallet_truth(tn)
            new = poll_closes(tn, st, live=True)
            save_state(st)
            for rec in new[:5]:
                tg(f"💰 REAL {rec['being']} {rec['symbol']} close "
                   f"${rec['pnl']:+.2f} (exchange)"
                   + (f" | Wallet ${wt['wallet_balance']:.2f} | "
                      f"IM {wt['im_rate'] * 100:.0f}%"
                      if wt else ''))
            if len(new) > 5:
                tot = sum(r['pnl'] for r in new)
                tg(f'💰 REAL +{len(new) - 5} more closes, '
                   f'net ${tot:+.2f} (exchange)')
            if new:
                logger.info(f'truth: +{len(new)} exchange closes')
        except Exception as e:
            logger.warning(f'cycle failed: {e}')
        import random
        time.sleep(75 + random.uniform(0, 20))


if __name__ == '__main__':
    main()
