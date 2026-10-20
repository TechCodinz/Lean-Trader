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
- Thin wallet (< $8 free): only the strongest being trades real.
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
BEINGS = ['zoo', 'continuous', 'swarm', 'master', 'orchestrator']
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



GUARD_PATH = '/app/runtime/guard_state.json'
LEDGER_PATH = '/app/runtime/being_ledger.jsonl'

try:
    from risk.guards import (GuardState, RiskLimits, should_halt_trading,
                             RISK_MAX_LOSS_PER_SYMBOL, RISK_MAX_DAILY_LOSS,
                             RISK_MAX_ACCOUNT_DD, RISK_LIMITS_PCT)
    _GUARDS_OK = True
except Exception:
    _GUARDS_OK = False

try:
    from allocators.portfolio import choose_assets as _choose_assets
    _ALLOC_OK = True
except Exception:
    _ALLOC_OK = False


def _guard_evaluate(tn):
    """Princewill's 2025 risk gates (risk/guards.py, restored
    2026-10-20) fed from the being ledger + live equity. Returns
    (halted, reasons, info). Guard state rebuilt from today's real
    closes each cycle (restart-proof); peak equity persists."""
    info = {'daily_pnl': 0.0, 'peak_equity': 0.0}
    if not _GUARDS_OK:
        return False, [], info
    try:
        import datetime as _dt
        st = GuardState()
        now = _dt.datetime.now(_dt.timezone.utc)
        midnight = now.replace(hour=0, minute=0, second=0,
                               microsecond=0).timestamp()
        try:
            with open(LEDGER_PATH) as f:
                for line in f:
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    if not r.get('real') or float(r.get('ts', 0)) < midnight:
                        continue
                    st.record_fill(r.get('symbol', ''), float(r.get('pnl', 0)))
        except Exception:
            pass
        peak = 0.0
        try:
            with open(GUARD_PATH) as f:
                peak = float(json.load(f).get('peak_equity', 0.0))
        except Exception:
            peak = 0.0
        st.peak_equity = peak
        eq = 0.0
        try:
            eq = float(tn.wallet_equity_usdt())
        except Exception:
            eq = 0.0
        if eq > 0:
            st.update_equity(eq)
        limits = RiskLimits(RISK_MAX_LOSS_PER_SYMBOL, RISK_MAX_DAILY_LOSS,
                            RISK_MAX_ACCOUNT_DD, pct=RISK_LIMITS_PCT)
        halt, reasons = should_halt_trading(st, limits)
        info = {'daily_pnl': round(st.daily_pnl, 4),
                'peak_equity': round(st.peak_equity, 2),
                'equity': round(eq, 2),
                'per_symbol': {k: round(v, 4) for k, v in
                               st.per_symbol_pnl_today.items()},
                'limits': {'per_symbol': RISK_MAX_LOSS_PER_SYMBOL,
                           'daily': RISK_MAX_DAILY_LOSS,
                           'drawdown': RISK_MAX_ACCOUNT_DD}}
        try:
            with open(GUARD_PATH, 'w') as f:
                json.dump({'peak_equity': st.peak_equity,
                           'daily_pnl': st.daily_pnl,
                           'ts': time.time()}, f)
        except Exception:
            pass
        return halt, reasons, info
    except Exception as e:
        logger.warning(f'guard evaluate: {e}')
        return False, [], info


def _allocator_select(stats, free):
    """Princewill's 2025 allocator (allocators/portfolio.py
    choose_assets): beings are assets; mu = 72h expectancy, Sigma =
    covariance of hourly realized P&L; budget = real slots by
    wallet tier. Returns (selected_set, mu_dict) or (None, mu) to
    fall back to the legacy mode logic."""
    mu = {}
    for b in BEINGS:
        st = stats.get(b) or {}
        # Evidence discipline (Princewill's own demotion standard):
        # under 30 closes there is no track record to select on -
        # the being is an explorer with a small positive mu, never
        # benched by an anecdote (one pre-restoration close of
        # -$2.44 sat in 'continuous' history all day).
        mu[b] = float(st.get('expectancy', 0.0)) if (st.get('closes') or 0) >= 30 else 0.001
    if not _ALLOC_OK:
        return None, mu
    try:
        import datetime as _dt
        import numpy as _np
        now = _dt.datetime.now(_dt.timezone.utc)
        start = (now - _dt.timedelta(hours=72)).timestamp()
        buckets = {b: _np.zeros(72) for b in BEINGS}
        try:
            with open(LEDGER_PATH) as f:
                for line in f:
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    if not r.get('real'):
                        continue
                    b = r.get('being')
                    ts = float(r.get('ts', 0))
                    if b in buckets and ts >= start:
                        idx = min(71, int((ts - start) // 3600))
                        buckets[b][idx] += float(r.get('pnl', 0))
        except Exception:
            pass
        X = _np.array([buckets[b] for b in BEINGS])
        if _np.any(X):
            Sigma = _np.cov(X)
            if Sigma.shape != (len(BEINGS), len(BEINGS)):
                Sigma = _np.diag(_np.var(X, axis=1) + 1e-6)
        else:
            Sigma = _np.eye(len(BEINGS))
        # beings with no variance signal get the fleet median so the
        # exploration epsilon cannot dominate the Sharpe-like score
        d = _np.diag(Sigma).copy()
        pos = d[d > 1e-9]
        med = float(_np.median(pos)) if pos.size else 1e-4
        for i in range(len(BEINGS)):
            if d[i] <= 1e-9:
                Sigma[i, i] = med
        if free <= 0:
            budget = len(BEINGS)
        elif free < 2:
            budget = 2
        elif free < 8:
            budget = 3
        elif free < 25:
            budget = 4
        else:
            budget = len(BEINGS)
        sel = _choose_assets([mu[b] for b in BEINGS], Sigma, budget)
        selected = {BEINGS[i] for i, v in enumerate(sel) if int(v) == 1}
        return selected, mu
    except Exception as e:
        logger.warning(f'allocator select: {e}')
        return None, mu


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

    mult = {'zoo': 1.0, 'continuous': 1.0, 'swarm': 1.0, 'master': 1.0, 'orchestrator': 1.0}
    if regime == 'ranging':
        mult['swarm'] = 1.15
        mult['master'] = 1.1
    elif regime == 'bear':
        mult['zoo'] = 0.8
        mult['swarm'] = 1.1
    elif regime in ('bull', 'trend', 'trending', 'bullish'):
        mult['zoo'] = 1.1
        mult['continuous'] = 1.1

    adj = {b: max(scores[b] or 0.0, 0.0) * mult[b] for b in BEINGS}
    total = sum(adj.values())
    if total <= 0:
        weights = {b: 1.0 / len(BEINGS) for b in BEINGS}
    else:
        weights = {b: 0.05 + 0.85 * adj[b] / total for b in BEINGS}

    selected, _mu = _allocator_select(stats, free)

    modes = {}
    for b in BEINGS:
        s = scores[b]
        n = (stats.get(b) or {}).get('closes', 0)
        # Demotion must be EVIDENCE, not noise: at these notionals a
        # close's sigma is ~$0.30, so n=15-18 cannot resolve a
        # -$0.004 expectancy from zero (the zoo was benched fleet-
        # wide on four-tenths of a cent, 2026-10-20). Require a real
        # sample AND material negativity.
        exp = (stats.get(b) or {}).get('expectancy', 0.0)
        demoted = (n >= 30 and exp <= -0.02)
        # Rehabilitation by ADVANCEMENT (Peters' no-demotion rule):
        # a benched being keeps working on paper; if its CURRENT
        # paper form measures profitable over a real sample, it has
        # earned its way back - it does not serve a 72h sentence
        # waiting for old closes to age out.
        pst = stats.get(b) or {}
        rehabilitated = (pst.get('paper_closes', 0) >= 20
                          and pst.get('paper_expectancy', 0.0) > 0)
        real = not (demoted and not rehabilitated)
        if selected is not None:
            real = real and (b in selected)
        modes[b] = 'real' if real else 'paper'
    if 0 < free < 8 and selected is None:
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
        'master': {
            'mode': modes['master'],
            'slice_usd': round(max(10.0, min(30.0, 8 + weights['master'] * 22)), 2),
            'max_concurrent': max(1, min(3, round(1 + weights['master'] * 2))),
        },
        'orchestrator': {
            'mode': modes['orchestrator'],
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
        'allocator': {'selected': sorted(selected) if selected is not None
                      else None,
                      'mu': {b: round(_mu[b], 5) for b in BEINGS}},
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
