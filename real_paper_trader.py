import os, time, logging, requests, ccxt, json
from critical_features_addon import CompoundEngine, TrailingStopManager, PartialTPManager, EmergencyStop, VolumeProfileAnalyzer
from EXECUTION_ORCHESTRATOR import SmartPositionSizer
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('PAPER')
def tg(msg):
    try:
        tok=os.getenv("TELEGRAM_BOT_TOKEN",""); cid=os.getenv("TELEGRAM_CHAT_ID","")
        if tok and cid: requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", json={"chat_id":cid,"text":msg}, timeout=5)
    except: pass
compounder = CompoundEngine(initial_capital=100.0, compound_rate=0.5)
trailer = TrailingStopManager(trail_percent=0.02)
partial = PartialTPManager()
emergency = EmergencyStop(max_loss=0.10, max_trades_per_min=10)
kelly = SmartPositionSizer(initial_balance=100.0)
vol_analyzer = VolumeProfileAnalyzer(bins=50)
STATE_FILE='/tmp/paper_state.json'
def load_state():
    global cash, positions, trades, compounder
    try:
        d=json.load(open(STATE_FILE))
        cash=d['cash']; positions=d['positions']; trades=d['trades']
        for _ in range(len([t for t in trades if t>0])): pass
        compounder.current_capital=cash
        print(f"Loaded: ${cash:.2f}, {len(positions)} positions")
    except: pass
def save_state():
    json.dump({'cash':cash,'positions':positions,'trades':trades}, open(STATE_FILE,'w'))
cash = 100.0; positions = {}; trades = []
load_state()
ex = ccxt.bybit({'enableRateLimit': True}); ex.set_sandbox_mode(True)
logger.info("💰 Real Paper Trader started with $100"); tg("💰 Paper Trader LIVE - $100")
while True:
    try:
        tickers = ex.fetch_tickers()
        trending = []
        for sym, t in tickers.items():
            if '/USDT' in sym and t.get('quoteVolume',0) > 1000000:
                chg = t.get('percentage',0)
                if chg and abs(chg) > 2: trending.append((sym, t['last'], chg))
        trending.sort(key=lambda x: abs(x[2]), reverse=True)
        for sym, price, chg in trending[:3]:
            if sym in positions or not price: continue
            size_usd = compounder.calculate_position_size(base_size=1.0)
            qty = size_usd / price
            positions[sym] = {'qty': qty, 'entry': price}
            logger.info(f"📈 PAPER BUY {sym} @ {price:.4f} ({chg:+.1f}%)")
            tg(f"📈 PREMIUM BUY\n{sym}\nEntry: ${price:.4f}\nMomentum: {chg:+.1f}%\nSize: ${size_usd:.2f}\nCash: ${cash:.2f}")
        for sym, pos in list(positions.items()):
            try:
                cur = ex.fetch_ticker(sym)['last']
                pct = (cur - pos['entry']) / pos['entry'] * 100
                if pct >= 2.0 or pct <= -1.0:
                    pnl = (cur - pos['entry']) * pos['qty']
                    cash += pnl; trades.append(pnl); compounder.update_pnl(pnl)
                    logger.info(f"📉 SELL {sym} P&L: ${pnl:+.4f} ({pct:+.2f}%)")
                    tg(f"📉 PREMIUM SELL\n{sym}\nP&L: ${pnl:+.2f} ({pct:+.1f}%)\nCash: ${cash:.2f}\nWin Rate: {w}/{len(trades)}")
                    del positions[sym]; save_state()
            except: pass
        w = sum(1 for x in trades if x > 0)
        logger.info(f"💵 ${cash:.2f} | Open:{len(positions)} | Trades:{len(trades)} W:{w}")
        time.sleep(60)
    except Exception as e: logger.error(f"E: {e}"); time.sleep(30)
