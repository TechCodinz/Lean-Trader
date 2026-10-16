import sys; sys.path.insert(0, '/app')
import asyncio, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('COLONY')

async def run():
    from paper_broker import PaperBroker
    from DYNAMIC_MARKET_SCANNER import DynamicMarketScanner
    import ccxt.async_support as ccxt
    broker = PaperBroker(start_cash=5000.0)
    logger.info("📝 Colony paper broker: $5000 virtual")
    ex = ccxt.bybit({'enableRateLimit': True})
    ex.set_sandbox_mode(True)
    scanner = DynamicMarketScanner(exchanges={'b': ex}, data_hub=None)
    n = 0
    while True:
        n += 1
        try:
            await scanner.scan_all_exchanges()
            trending = scanner.get_trending_opportunities(limit=10)
            logger.info(f"🐝 Colony cycle {n}: scanning {len(trending)} pairs")
            for t in trending[:3]:
                sym = t['symbol']
                px = t.get('price', 0)
                # Paper trade: simulate small positions on trending
                if px > 0:
                    logger.info(f"  📊 {sym} @ {px:.4f} ({t['price_change_pct']:+.1f}%)")
        except Exception as e:
            logger.error(f"Colony: {e}")
        await asyncio.sleep(60)

asyncio.run(run())
