import os, time, logging, requests, ccxt, json
import pandas as pd
from critical_features_addon import CompoundEngine, TrailingStopManager, PartialTPManager, EmergencyStop
from EXECUTION_ORCHESTRATOR import SmartPositionSizer
from BALANCE_TIER_COORDINATOR import BalanceTierCoordinator
from strategy_zoo import get_strategy
from session_intelligence import SessionPerformanceTracker, MarketSession
from scalping_coordinator import ScalpingCoordinator
from auto_adaptive_apex import AutoAdaptiveApex
from balance_aware_intelligence import BalanceAwareIntelligence
from central_nervous_system import get_central_nervous_system
from central_coordination_hub import CentralCoordinationHub
from central_control_intelligence import CentralControlIntelligence
from hybrid_intelligence_coordinator import HybridIntelligenceCoordinator
from exchange_spawn_manager import ExchangeSpawnManager
from collective_swarm_intelligence import CollectiveSwarmIntelligence
from ultrasonic_rare_strategies import UltrasonicStrategiesManager
from router import ExchangeRouter
from universe import Universe
from ultra_core import UltraCore
from risk_engine import RiskEngine
from ultra_scalping_engine import UltraScalpingEngine
from ultra_arbitrage_engine import UltraArbitrageEngine
from ultra_ml_pipeline import UltraMLPipeline
from ultra_moon_spotter import UltraMoonSystem

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
scalp_coord = ScalpingCoordinator(max_concurrent=5)
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
apex = AutoAdaptiveApex(ex)
bai = BalanceAwareIntelligence()
cns = get_central_nervous_system()
# Register engines with CNS
cns.register_engine("strategy_zoo", strategies)
cns.register_engine("risk", emergency)
hub = CentralCoordinationHub()
hub.register_exchange("bybit", True)
# Update with available pairs from exchange
try:
    tickers = ex.fetch_tickers()
    pairs = [s for s in tickers.keys() if "/USDT" in s][:50]
    hub.update_available_pairs("bybit", pairs)
except: pass
# Hub is single source of truth for pairs/strategies
# Supreme hierarchy: CCI coordinates all
data_hub = {}
hybrid_coord = HybridIntelligenceCoordinator(data_hub)
swarm = CollectiveSwarmIntelligence(data_hub)
cci = CentralControlIntelligence(data_hub)
spawn_mgr = ExchangeSpawnManager(data_hub, cci)
cci.register_subsystems(hybrid_coord, spawn_mgr, swarm)
ultra = UltrasonicStrategiesManager()
# Micro scalping stack (BAI recommended)
try:
    _router = ExchangeRouter()
    _universe = Universe(router=_router)
    _core = UltraCore(_router, _universe)
    _risk = RiskEngine()
    scalp_engine = UltraScalpingEngine(_core, _risk)
    arb_engine = UltraArbitrageEngine(_core, _risk)
    ml_pipeline = UltraMLPipeline()
    logger.info('🧠 ML Pipeline initialized')
    moon_system = UltraMoonSystem()
    logger.info('🌙 Moon System initialized')
    logger.info('🔀 Arbitrage Engine initialized')
    logger.info('⚡ Micro Scalping Engine initialized')
except Exception as e:
    scalp_engine = None
    logger.warning(f'Micro scalping init failed: {e}')
# 8 quant systems: VPIN, Almgren-Chriss, Pairs, HMM, Bandit, TD-Lambda, Copula, Impact
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
            apex_tier, apex_cfg = apex.get_current_tier(cash)
            # Apex provides tier-based risk: use its target_profit/stop_loss
            tier_size = tier_coord.get_recommended_position_size()
            kelly_size = kelly.calculate_position_size(confidence=0.7, volatility=0.02, stop_loss_pct=0.02)
            # Apex aggressive sizing (2025)
            apex_tier, apex_cfg = apex.get_current_tier(cash)
            size_usd = min(cash * apex_cfg["risk_pct"], cash * 0.95)
            size_usd = compounder.calculate_position_size(base_size=size_usd)
            qty = size_usd / price
            positions[sym] = {'qty': qty, 'entry': price}
            trailer.update(sym, price, price, price*0.98)
            partial.add_position(sym, price, qty)
            emergency.add_trade()
            scalp_coord.add_scalp({"symbol": sym, "entry": price})
            partial.add_position(sym, price, size_usd)
            logger.info(f"📈 BUY {sym} [{sig}] @ {price:.4f} ${size_usd:.2f}")
            tg(f"📈 BUY {sym}\nStrategy: {sig}\nEntry: ${price:.4f}\nSize: ${size_usd:.2f}")
            save_state()
            if not scalp_coord.can_take_scalp() or len(positions) >= 5: break
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
                    scalp_coord.close_scalp(sym, pct)
                    del positions[sym]; save_state()
            except: pass
        w=sum(1 for x in trades if x>0)
        logger.info(f"💵 ${cash:.2f} | Open:{len(positions)} | Trades:{len(trades)} W:{w}")
        time.sleep(120)
    except Exception as e:
        logger.error(f"E: {e}"); time.sleep(30)
