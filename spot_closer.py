import sys; sys.path.insert(0, '/app')
import asyncio, logging, ccxt
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SPOT_CLOSER')

# Your 2025 exit params
TAKE_PROFIT_PCT = 0.015  # 1.5%
STOP_LOSS_PCT = 0.02     # 2%

async def manage_spot():
    with open('/run/secrets/bybit_testnet_api_key') as f: k = f.read().strip()
    with open('/run/secrets/bybit_testnet_api_secret') as f: s = f.read().strip()
    ex = ccxt.bybit({'apiKey': k, 'secret': s, 'enableRateLimit': True})
    ex.set_sandbox_mode(True)
    
    # Track entry prices (from your trade history - XRP ~1.40)
    entries = {'XRP': 1.40, 'CHIP': 0.0465}  # CHIP: 6.97/149.9
    
    while True:
        try:
            bal = ex.fetch_balance()
            for coin in ['XRP', 'CHIP']:
                amt = bal['total'].get(coin, 0)
                if amt and amt > 0:
                    t = ex.fetch_ticker(f'{coin}/USDT')
                    px = t['last']
                    entry = entries.get(coin, px)
                    pnl_pct = (px - entry) / entry
                    val = amt * px
                    if pnl_pct >= TAKE_PROFIT_PCT:
                        ex.create_market_sell_order(f'{coin}/USDT', amt)
                        logger.info(f"✅ CLOSED {coin}: +{pnl_pct*100:.1f}% (${val:.2f})")
                    elif pnl_pct <= -STOP_LOSS_PCT:
                        ex.create_market_sell_order(f'{coin}/USDT', amt)
                        logger.info(f"🛑 STOPPED {coin}: {pnl_pct*100:.1f}% (${val:.2f})")
                    else:
                        logger.info(f"⏳ HOLD {coin}: {pnl_pct*100:+.1f}% (${val:.2f})")
        except Exception as e:
            logger.error(f"Closer error: {e}")
        await asyncio.sleep(60)

asyncio.run(manage_spot())
