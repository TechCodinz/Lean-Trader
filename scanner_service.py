#!/usr/bin/env python3
"""
LeanTrader Dynamic Market Scanner Service (2025 microservice).

Continuously scans exchanges for trending pairs, high-volume opportunities.
Publishes signals for the adaptive pair selector.

2025 original: DYNAMIC_MARKET_SCANNER.py (2025-10-16)
"""

import asyncio
import logging
import sys

sys.path.insert(0, '/app')

from DYNAMIC_MARKET_SCANNER import DynamicMarketScanner
from REAL_PROFIT_BOT import REAL_PROFIT_BOT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SCANNER_SERVICE')


async def main():
    logger.info("🔍 Starting Dynamic Market Scanner Service (2025 microservice)")
    
    # REPAIRED 2026-10-20: the old build scanned through the profit
    # bot's dead Gate/testnet client - every scan errored (invalid
    # keys) and the fleet was fed an empty universe: 0 active, 0
    # trending. Tickers are PUBLIC: no keys needed. And the class
    # loop never called publish - it scanned and told no one.
    import ccxt.async_support as ccxt_async
    pub = ccxt_async.bybit({'enableRateLimit': True})
    exchanges = {'bybit': pub}
    from data_hub import MarketDataHub
    hub = MarketDataHub()
    scanner = DynamicMarketScanner(exchanges=exchanges, data_hub=hub)
    logger.info('Scanner initialized: public Bybit feed + data hub')

    import json as _json
    while True:
        try:
            await scanner.scan_all_exchanges()
            scanner.scan_count += 1
            from datetime import datetime as _dt
            scanner.last_scan = _dt.now()
            logger.info(f'Scan #{scanner.scan_count} complete - '
                        f'active {len(scanner.active_pairs)}, '
                        f'trending {len(scanner.trending_pairs)}')
            try:
                await scanner.publish_trending_signals()
            except Exception as e:
                logger.warning(f'trending publish: {e}')
            try:
                tops = scanner.get_trending_opportunities(limit=20)
                with open('/tmp/trending_pairs.json', 'w') as f:
                    _json.dump({'pairs': [t['symbol'] for t in tops],
                                'changes': {t['symbol']:
                                            t['price_change_pct']
                                            for t in tops}}, f)
            except Exception as e:
                logger.warning(f'trending file: {e}')
            await asyncio.sleep(scanner.rescan_interval)
        except Exception as e:
            logger.error(f'Dynamic scanner error: {e}')
            await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(main())
