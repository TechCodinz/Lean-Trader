"""Being capacity ledger - per-being realized performance truth.

Every being records its REAL closes here (testnet fills only; paper closes
are recorded separately as learning data and never count as capacity).
The allocation governor reads summaries of this file to size each being
by measured capacity; Peters reads it to see who is actually profitable.

Storage: /app/runtime/being_ledger.jsonl (append-only, one JSON per close)
Summary: capacity_summary() -> {being: {closes, wins, win_rate,
         realized_pnl, expectancy, paper_closes}}
"""
import json
import os
import time

LEDGER_PATH = os.environ.get('BEING_LEDGER', '/app/runtime/being_ledger.jsonl')


def record_close(being, symbol, pnl, real=True, meta=None):
    """Append one close. Never raises - measurement must not break trading."""
    try:
        os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
        row = {
            'ts': time.time(),
            'being': str(being),
            'symbol': str(symbol),
            'pnl': float(pnl),
            'real': bool(real),
            'meta': meta or {},
        }
        with open(LEDGER_PATH, 'a') as f:
            f.write(json.dumps(row) + '\n')
        return True
    except Exception:
        return False


def load_closes(since_ts=0):
    rows = []
    try:
        with open(LEDGER_PATH) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get('ts', 0) >= since_ts:
                    rows.append(r)
    except FileNotFoundError:
        pass
    return rows


def capacity_summary(window_hours=72):
    """Per-being realized stats over the trailing window."""
    since = time.time() - window_hours * 3600
    out = {}
    _rows = load_closes(since)
    # TRUTH OVERLAY (2026-10-21): when the truth service has
    # written exchange records (source='exchange') into the
    # window, real capacity is computed from THEM alone - the
    # beings' own real records are signal-price estimates that
    # the forensic read showed disagreeing with the venue by
    # ~$11 over 48h. Paper stats are unaffected.
    _has_truth = any(r.get('real')
                     and r.get('source') == 'exchange'
                     for r in _rows)
    for r in _rows:
        if (_has_truth and r.get('real')
                and r.get('source') != 'exchange'):
            continue
        b = out.setdefault(r['being'], {
            'closes': 0, 'wins': 0, 'realized_pnl': 0.0, 'paper_closes': 0,
            'paper_pnl': 0.0})
        if r.get('real'):
            b['closes'] += 1
            b['realized_pnl'] += r['pnl']
            if r['pnl'] > 0:
                b['wins'] += 1
        else:
            b['paper_closes'] += 1
            b['paper_pnl'] += r['pnl']
    for b in out.values():
        n = b['closes']
        b['win_rate'] = (b['wins'] / n) if n else 0.0
        b['expectancy'] = (b['realized_pnl'] / n) if n else 0.0
        pn = b['paper_closes']
        b['paper_expectancy'] = (b['paper_pnl'] / pn) if pn else 0.0
    return out


if __name__ == '__main__':
    import pprint
    pprint.pprint(capacity_summary())
