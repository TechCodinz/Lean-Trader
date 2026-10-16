import sys; sys.path.insert(0, '/app')
import asyncio, logging, ccxt
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('POSITION_MGR')

# Track open extractor positions: {symbol: {entry, qty, tp, sl, side}}
open_positions = {}
trailing = TrailingStopManager(trail_percent=0.02)
partial_tp = PartialTPManager()
def load_positions():
    try:
        import json
        return json.load(open('/tmp/open_positions.json'))
    except: return {}

def track_open(symbol, side, qty, entry, tp, sl):
    open_positions[symbol] = {
        'side': side, 'qty': qty, 'entry': entry,
        'tp': tp, 'sl': sl
    }
    logger.info(f"📝 Tracking {symbol} {side} @ {entry:.4f} (TP:{tp:.4f} SL:{sl:.4f})")

async def monitor():
    with open('/run/secrets/bybit_testnet_api_key') as f: k = f.read().strip()
    with open('/run/secrets/bybit_testnet_api_secret') as f: s = f.read().strip()
    ex = ccxt.bybit({'apiKey': k, 'secret': s, 'enableRateLimit': True})
    ex.set_sandbox_mode(True)
    while True:
        try:
            open_positions.update(load_positions())
            for symbol in list(open_positions.keys()):
                pos = open_positions[symbol]
                t = ex.fetch_ticker(symbol)
                px = t['last']
                side = pos['side']
                # Check TP/SL
                hit_tp = (side == 'BUY' and px >= pos['tp']) or (side == 'SELL' and px <= pos['tp'])
                hit_sl = (side == 'BUY' and px <= pos['sl']) or (side == 'SELL' and px >= pos['sl'])
                if hit_tp or hit_sl:
                    # Close
                    if side == 'BUY':
                        ex.create_market_sell_order(symbol, pos['qty'])
                    else:
                        ex.create_market_buy_order(symbol, pos['qty'])
                    pnl = (px - pos['entry']) / pos['entry'] * 100
                    if side == 'SELL': pnl = -pnl
                    reason = "TP" if hit_tp else "SL"
                    logger.info(f"✅ CLOSED {symbol} {reason}: {pnl:+.2f}%")
                    ledger_record("extractor", symbol, pos["side"], pos["entry"], px, pos["qty"])
                    del open_positions[symbol]
        except Exception as e:
            logger.error(f"Monitor error: {e}")
        await asyncio.sleep(10)

# Run monitor
asyncio.run(monitor())
