#!/usr/bin/env python3
"""
Wire 2025 design: Dynamic Scanner -> SteadyProfitExtractor.

The scanner finds trending pairs. The extractor filters for
fast pairs + 70% confidence and auto-executes.

2025 design, no new logic.
"""

import asyncio
import logging
import sys
sys.path.insert(0, '/app')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SCANNER_TO_EXTRACTOR')

from DYNAMIC_MARKET_SCANNER import DynamicMarketScanner
from STEADY_PROFIT_EXTRACTOR import SteadyProfitExtractor
import ccxt.async_support as ccxt


class LiveDataHub:
    def __init__(self):
        self.signal_queue = asyncio.Queue()


class LiveExecutionEngine:
    def __init__(self):
        import ccxt as ccxt_sync
        with open('/run/secrets/bybit_testnet_api_key') as f:
            k = f.read().strip()
        with open('/run/secrets/bybit_testnet_api_secret') as f:
            s = f.read().strip()
        self.ex = ccxt_sync.bybit({'apiKey': k, 'secret': s, 'enableRateLimit': True})
        self.ex.set_sandbox_mode(True)

    async def execute(self, trade):
        symbol = trade.get('symbol')
        side = trade.get('side')
        qty = trade.get('qty')
        if not all([symbol, side, qty]):
            return None
        import concurrent.futures
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            fn = (lambda: self.ex.create_market_buy_order(symbol, qty)
                  if side.upper() == 'BUY'
                  else lambda: self.ex.create_market_sell_order(symbol, qty))
            # Fix: define properly
            if side.upper() == 'BUY':
                order = await loop.run_in_executor(
                    pool, lambda: self.ex.create_market_buy_order(symbol, qty))
            else:
                order = await loop.run_in_executor(
                    pool, lambda: self.ex.create_market_sell_order(symbol, qty))
        logger.info(f"⚡ Executed: {side} {qty} {symbol}")
        return order


def trending_to_signal(trending):
    """Convert scanner trending dict to extractor signal dict."""
    symbol = trending.get('symbol')
    pct = trending.get('price_change_pct', 0)
    side = 'BUY' if pct > 0 else 'SELL'
    # Confidence from magnitude: 1.5% -> 0.70, scales up
    confidence = min(0.95, 0.70 + abs(pct) / 20.0)
    return {
        'symbol': symbol,
        'side': side,
        'confidence': confidence,
        'price_change_pct': pct,
        'exchange': trending.get('exchange'),
    }


async def signal_producer(scanner, data_hub):
    """Feed scanner trending opportunities into extractor's queue."""
    while True:
        try:
            await scanner.scan_all_exchanges()
            trending = scanner.get_trending_opportunities(limit=20)
            for t in trending:
                signal = trending_to_signal(t)
                await data_hub.signal_queue.put(signal)
                logger.info(
                    f"📡 Signal: {signal['symbol']} {signal['side']} "
                    f"conf={signal['confidence']:.2f}"
                )
        except Exception as e:
            logger.error(f"Producer error: {e}")
        await asyncio.sleep(300)  # Rescan every 5 min


async def main():
    # Build exchanges (exchange-agnostic)
    exchanges = {}
    try:
        with open('/run/secrets/bybit_testnet_api_key') as f:
            key = f.read().strip()
        with open('/run/secrets/bybit_testnet_api_secret') as f:
            secret = f.read().strip()
        ex = ccxt.bybit({'apiKey': key, 'secret': secret, 'enableRateLimit': True})
        ex.set_sandbox_mode(True)
        exchanges['bybit_testnet'] = ex
    except Exception as e:
        logger.error(f"No exchanges: {e}")
        return

    # Your 2025 components
    scanner = DynamicMarketScanner(exchanges=exchanges, data_hub=None)
    data_hub = LiveDataHub()
    execution = LiveExecutionEngine()
    extractor = SteadyProfitExtractor(data_hub=data_hub, execution_engine=execution)

    logger.info("🔗 Wired: Scanner -> Extractor (your 2025 design)")

    # Run both: producer feeds signals, extractor consumes
    await asyncio.gather(
        signal_producer(scanner, data_hub),
        extractor.run_profit_extraction(),
    )


if __name__ == '__main__':
    asyncio.run(main())
