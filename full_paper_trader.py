import os, time, logging, requests, ccxt, json, asyncio
from critical_features_addon import CompoundEngine, TrailingStopManager, PartialTPManager, EmergencyStop, VolumeProfileAnalyzer
from EXECUTION_ORCHESTRATOR import SmartPositionSizer
from BALANCE_TIER_COORDINATOR import BalanceTierCoordinator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('PAPER')

def tg(msg):
    try:
        tok=os.getenv("TELEGRAM_BOT_TOKEN",""); cid=os.getenv("TELEGRAM_CHAT_ID","")
        if tok and cid: requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", json={"chat_id":cid,"text":msg}, timeout=5)
    except: pass

STATE_FILE='/tmp/paper_state.json'
compounder = CompoundEngine(initial_capital=100.0, compound_rate=0.5)
trailer = TrailingStopManager(trail_percent=0.02)
partial = PartialTPManager()
emergency = EmergencyStop(max_loss=0.10, max_trades_per_min=10)
kelly = SmartPositionSizer(initial_balance=100.0)
tier_coord = BalanceTierCoordinator(initial_balance=100.0)

cash=100.0; positions={}; trades=[]

def load_state():
    global cash, positions, trades
    try:
        d=json.load(open(STATE_FILE))
        cash=d['cash']; positions=d['positions']; trades=d['trades']
        compounder.current_capital=cash
        logger.info(f"Loaded state: ${cash:.2f}")
    except: pass

def save_state():
    json.dump({'cash':cash,'positions':positions,'trades':trades}, open(STATE_FILE,'w'))

load_state()
ex = ccxt.bybit({'enableRateLimit': True}); ex.set_sandbox_mode(True)
logger.info("💰 Full Intelligence Paper Trader started"); tg("💰 Full Intelligence LIVE")

while True:
    try:
        # EMERGENCY CHECK
        if emergency.emergency_active or emergency.check_conditions(cash, 100.0):
            logger.error("🚨 EMERGENCY STOP"); tg("🚨 EMERGENCY STOP"); time.sleep(300); continue

        tickers = ex.fetch_tickers()
        trending = []
        for sym, t in tickers.items():
            if '/USDT' in sym and t.get('quoteVolume',0) > 1000000:
                chg = t.get('percentage',0)
                if chg and chg < -3 and chg > -10:
                    trending.append((sym, t['last'], chg))
        trending.sort(key=lambda x: x[2])

        for sym, price, chg in trending[:3]:
            if sym in positions or not price: continue
            # KELLY SIZING + COMPOUNDING
            tier_coord.update_balance(cash)
            tier_size = tier_coord.get_recommended_position_size()
            kelly_size = kelly.calculate_position_size(confidence=0.7, volatility=0.02, stop_loss_pct=0.02)
            # Blend: use tier aggression (50% at small tier) capped by Kelly
            kelly_size = min(tier_size, max(kelly_size, cash * 0.10))
            size_usd = compounder.calculate_position_size(base_size=max(1.0, kelly_size))
            qty = size_usd / price
            positions[sym] = {'qty': qty, 'entry': price}
            # REGISTER WITH ALL SYSTEMS
            trailer.update(sym, price, price, price*0.98)
            partial.add_position(sym, price, qty)
            emergency.add_trade()
            logger.info(f"📈 BUY {sym} @ {price:.4f} size=${size_usd:.2f}")
            tg(f"📈 BUY {sym}\nEntry: ${price:.4f}\nSize: ${size_usd:.2f}\nKelly+Compound")
            save_state()

        for sym, pos in list(positions.items()):
            try:
                cur = ex.fetch_ticker(sym)['last']
                # TRAILING STOP UPDATE
                new_stop = trailer.update(sym, cur, pos['entry'], pos['entry']*0.98)
                trail_stop = trailer.get_stop(sym)
                pct = (cur - pos['entry']) / pos['entry'] * 100
                # EXIT LOGIC: trailing stop OR 3% TP
                should_sell = False
                if trail_stop and cur <= trail_stop:
                    should_sell = True; reason = "trailing"
                elif pct >= 3.0:
                    should_sell = True; reason = "TP"
                if should_sell:
                    pnl = (cur - pos['entry']) * pos['qty']
                    cash += pnl; trades.append(pnl)
                    compounder.update_pnl(pnl)
                    trailer.clear(sym)
                    w = sum(1 for x in trades if x > 0)
                    logger.info(f"📉 SELL {sym} ({reason}) P&L:${pnl:+.2f} ({pct:+.1f}%)")
                    tg(f"📉 SELL {sym} ({reason})\nP&L: ${pnl:+.2f} ({pct:+.1f}%)\nCash: ${cash:.2f}\nW:{w}/{len(trades)}")
                    del positions[sym]; save_state()
            except: pass

        w = sum(1 for x in trades if x > 0)
        logger.info(f"💵 ${cash:.2f} | Open:{len(positions)} | Trades:{len(trades)} W:{w}")
        time.sleep(60)
    except Exception as e:
        logger.error(f"E: {e}"); time.sleep(30)
