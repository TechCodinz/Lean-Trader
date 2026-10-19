"""Shared allocation reader - the governor's output, the beings' input.

The allocation governor (governor_service.py) writes
/app/runtime/allocation.json every few minutes: per-being mode
(real/paper), slice size and concurrency, derived from each being's
measured capacity (being_ledger) + wallet + regime.

Beings call get(being) and fall back to the historical defaults on any
problem - a missing/stale file must never stop a being from trading.
"""
import json
import os
import time

PATH = os.environ.get('ALLOCATION_PATH', '/app/runtime/allocation.json')
DEFAULTS = {
    'zoo': {'mode': 'real', 'real_cap': 3},
    'continuous': {'mode': 'real', 'slice_usd': 25.0, 'max_concurrent': 4},
    'swarm': {'mode': 'real', 'slice_usd': 15.0, 'max_concurrent': 2},
    'master': {'mode': 'real', 'slice_usd': 12.0, 'max_concurrent': 2},
    'orchestrator': {'mode': 'real'},
}
_cache = {'ts': 0.0, 'data': None}


def get(being):
    now = time.time()
    if _cache['data'] is None or now - _cache['ts'] > 20:
        try:
            with open(PATH) as f:
                _cache['data'] = json.load(f)
        except Exception:
            _cache['data'] = {}
        _cache['ts'] = now
    out = dict(DEFAULTS.get(being, {}))
    live = (_cache['data'].get('beings') or {}).get(being) or {}
    out.update(live)
    return out
