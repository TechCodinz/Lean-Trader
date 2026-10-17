import os, time, logging, requests, ccxt, json
import pandas as pd
from critical_features_addon import CompoundEngine, TrailingStopManager, PartialTPManager, EmergencyStop
from EXECUTION_ORCHESTRATOR import SmartPositionSizer
from BALANCE_TIER_COORDINATOR import BalanceTierCoordinator
from strategy_zoo import get_strategy
from session_intelligence import SessionPerformanceTracker, MarketSession

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('ZOO')

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
session_tracker = SessionPerformanceTracker()
strategies = [get_strategy(n) for n in ['RSIMeanRev','DonchianBreakout','EMAbbSqueeze','MAPullback','EvoCombo']]

cash=100.0; positions={}; trades=[]
def load_state():
    global cash, positions, trades
    try:
        d=json.load(open(STATE_FILE))
        cash=d['cash']; positions=d['positions']; trades=d['trades']
        compounder.current_capital=cash
        logger.info(f"Loaded: ${cash:.2f}")
    except: pass
def save_state():
    json.dump({'cash':cash,'positions':positions,'trades':trades}, open(STATE_FILE,'w'))

load_state()
ex = ccxt.bybit({'enableRateLimit': True}); ex.set_sandbox_mode(True)
logger.info("🐯 Zoo Paper Trader started"); tg("🐯 Zoo Trader LIVE - 5 strategies")

def get_signal(sym):
    try:
        ohlcv = ex.fetch_ohlcv(sym, '1h', 100)
        if len(ohlcv) < 50: return None
        df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','vol'])
        for strat in strategies:
            try:
                out = strat.apply(df)
                if out['long_signal'].iloc[-1]:
                    return strat.name
            except: pass
    except: pass
    return None

while True:
    try:
        if emergency.emergency_active or emergency.check_conditions(cash, 100.0):
            logger.error("🚨 EMERGENCY"); tg("🚨 EMERGENCY STOP"); time.sleep(300); continue
        tickers = ex.fetch_tickers()
        cands = [(s,t['last']) for s,t in tickers.items() if '/USDT' in s and t.get('quoteVolume',0)>1000000 and t['last']]
        cands = cands[:20]
        for sym, price in cands:
            if sym in positions: continue
            sig = get_signal(sym)
            if not sig: continue
            tier_coord.update_balance(cash)
            tier_size = tier_coord.get_recommended_position_size()
            kelly_size = kelly.calculate_position_size(confidence=0.7, volatility=0.02, stop_loss_pct=0.02)
            size_usd = min(tier_size, max(kelly_size, cash*0.10))
            size_usd = compounder.calculate_position_size(base_size=size_usd)
            qty = size_usd / price
            positions[sym] = {'qty': qty, 'entry': price}
            trailer.update(sym, price, price, price*0.98)
            partial.add_position(sym, price, qty)
            emergency.add_trade()
            logger.info(f"📈 BUY {sym} [{sig}] @ {price:.4f} ${size_usd:.2f}")
            tg(f"📈 BUY {sym}\nStrategy: {sig}\nEntry: ${price:.4f}\nSize: ${size_usd:.2f}")
            save_state()
            if len(positions) >= 5: break
        for sym, pos in list(positions.items()):
            try:
                cur = ex.fetch_ticker(sym)['last']
                trailer.update(sym, cur, pos['entry'], pos['entry']*0.98)
                trail_stop = trailer.get_stop(sym)
                pct = (cur-pos['entry'])/pos['entry']*100
                sell=False; reason=""
                if trail_stop and cur <= trail_stop: sell=True; reason="trailing"
                elif pct >= 3.0: sell=True; reason="TP"
                if sell:
                    pnl=(cur-pos['entry'])*pos['qty']
                    cash+=pnl; trades.append(pnl); compounder.update_pnl(pnl); trailer.clear(sym)
                    sess = MarketSession.get_current_session()
                    session_tracker.record_trade(sym, sess, pnl, pnl>0)
                    w=sum(1 for x in trades if x>0)
                    logger.info(f"📉 SELL {sym} ({reason}) ${pnl:+.2f}")
                    tg(f"📉 SELL {sym} ({reason})\nP&L: ${pnl:+.2f} ({pct:+.1f}%)\nCash: ${cash:.2f}\nW:{w}/{len(trades)}")
                    del positions[sym]; save_state()
            except: pass
        w=sum(1 for x in trades if x>0)
        logger.info(f"💵 ${cash:.2f} | Open:{len(positions)} | Trades:{len(trades)} W:{w}")
        time.sleep(120)
    except Exception as e:
        logger.error(f"E: {e}"); time.sleep(30)
