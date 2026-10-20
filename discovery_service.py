#!/usr/bin/env python3
"""
LeanTrader Discovery Pipeline Service.

2025 components:
- EXPANDED_MARKET_UNIVERSE.py: 65+ pair base universe
- market_router.py: select_markets() - trend-score selection
  (z-scored returns through tanh; strat/risk args unused upstream)

Wiring history: the 2026 wrapper shipped with the router commented
out ("using universe as-is for now") and dumped the static universe
hourly - a shell. v2 (2026-10-19) wires select_markets for real with
a public ccxt client behind the safe_fetch_ohlcv adapter the router
expects, and writes the SELECTED top pairs (perp format) to
/tmp/discovered_pairs.json for the traders to consume.
"""
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, '/app')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DISCOVERY')

OUTPUT_FILE = Path('/tmp/discovered_pairs.json')
TOP_K = 30


class _Ex:
    """Adapter giving ccxt the router's safe_fetch_ohlcv contract."""

    def __init__(self):
        import ccxt
        self._ex = ccxt.bybit({'enableRateLimit': True,
                               'options': {'defaultType': 'future'}})

    def safe_fetch_ohlcv(self, sym, timeframe='1h', limit=400):
        try:
            # since-bounded: an unbounded fetch returns the OLDEST
            # candle page on this API (discovery scored 2021 data
            # until 2026-10-19). 1h candles assumed (router's use).
            import time as _t
            since = int((_t.time() - (limit + 5) * 3600) * 1000)
            return self._ex.fetch_ohlcv(sym, timeframe, since, limit)
        except Exception:
            return None


def discover_pairs():
    """Run the 2025 discovery pipeline: universe -> trend selection."""
    try:
        from market_router import select_markets
        # Princewill's rule: the universe is EVERY pair the exchange
        # offers, read live - not a frozen list (the static file held
        # 65 pairs while the venue lists hundreds).
        perps = []
        try:
            _mkts = _Ex()._ex.load_markets()
            perps = [s for s, m in _mkts.items()
                     if m.get('swap') and m.get('quote') == 'USDT'
                     and m.get('active', True)]
        except Exception as e:
            logger.warning(f'live universe failed ({e}); static fallback')
        if not perps:
            from EXPANDED_MARKET_UNIVERSE import FULL_MARKET_UNIVERSE
            perps = [f'{s}:USDT' if s.endswith('/USDT') else s
                     for s in FULL_MARKET_UNIVERSE]
        logger.info(f'📡 Base universe: {len(perps)} pairs - scoring trends...')
        selected = select_markets(_Ex(), perps, '1h', None, {}, top_k=TOP_K)
        pairs = [r['symbol'] for r in selected]
        scores = {r['symbol']: round(float(r['score']), 4) for r in selected}
        with open(OUTPUT_FILE, 'w') as f:
            json.dump({'pairs': pairs, 'scores': scores,
                       'count': len(pairs), 'timestamp': time.time(),
                       'source': '2025_discovery_pipeline_v2'}, f)
        logger.info(f'✅ Discovered {len(pairs)} pairs → {OUTPUT_FILE}: '
                    + ', '.join(f'{p}({scores[p]:+.2f})' for p in pairs[:5]))
        return pairs
    except Exception as e:
        logger.error(f'Discovery failed: {e}')
        return []


def main():
    logger.info('🔍 Starting Discovery Pipeline Service (router wired)')
    discover_pairs()
    try:
        while True:
            time.sleep(3600)
            discover_pairs()
            logger.info('🔍 Discovery heartbeat — universe refreshed')
    except KeyboardInterrupt:
        logger.info('🛑 Discovery stopped')


if __name__ == '__main__':
    main()
