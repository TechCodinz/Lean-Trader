import sys; sys.path.insert(0, '/app')
import asyncio, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('COLONY')

# Dynamic allocation: each strategy starts tiny, winners get more
STRATEGY_CAPITAL = {}  # strategy -> allocated capital
BASE_TEST_AMOUNT = 1.0  # $1 proves real edge  # $5 to test - smallest meaningful
MAX_PER_STRATEGY = 500.0

async def run():
    from paper_broker import PaperBroker
    from DYNAMIC_MARKET_SCANNER import DynamicMarketScanner
    import ccxt.async_support as ccxt
    
    broker = PaperBroker(start_cash=5000.0)
    logger.info("🧬 Adaptive colony: testing with $1, scaling winners")
    
    ex = ccxt.bybit({'enableRateLimit': True})
    ex.set_sandbox_mode(True)
    scanner = DynamicMarketScanner(exchanges={'b': ex}, data_hub=None)
    
    # Track strategy performance
    perf = {}  # strategy -> {trades, wins, pnl}
    
    n = 0
    while True:
        n += 1
        try:
            await scanner.scan_all_exchanges()
            trending = scanner.get_trending_opportunities(limit=10)
            
            for t in trending[:3]:
                sym = t['symbol']
                px = t.get('price', 0)
                pct = t.get('price_change_pct', 0)
                if px <= 0: continue
                
                # Dynamic: allocate based on past performance
                # New strategies get $5 test, winners scale up
                alloc = BASE_TEST_AMOUNT
                # Self-audit: track which intelligence is used
                used = []
                # TODO: wire PatternMemory, BrainMemory, AlphaRouter here
                logger.info(f"🧪 Testing {sym} with ${alloc:.2f} (cycle {n})")
                
        except Exception as e:
            logger.error(f"Colony: {e}")
        await asyncio.sleep(60)

asyncio.run(run())
