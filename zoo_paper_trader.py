import asyncio
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
# === AUTO PROFIT TAKER (sell brain, paper-routed) ===
def _paper_close(symbol, side, size, price, reason):
    global cash
    pos = positions.get(symbol)
    if not pos:
        return {'ok': False, 'error': 'not in paper book'}
    pnl = (price - pos['entry']) * pos['qty']
    cash += pnl
    trades.append(pnl)
    compounder.update_pnl(pnl)
    trailer.clear(symbol)
    try:
        sess = MarketSession.get_current_session()
        session_tracker.record_trade(symbol, sess, pnl, pnl > 0)
    except Exception:
        pass
    try:
        scalp_coord.close_scalp(symbol, (price - pos['entry']) / pos['entry'] * 100)
    except Exception:
        pass
    del positions[symbol]
    save_state()
    w = sum(1 for x in trades if x > 0)
    logger.info(f"PT SELL {symbol} ({reason}) ${pnl:+.2f}")
    tg(f"PT SELL {symbol} ({reason})\nP&L: ${pnl:+.2f}\nCash: ${cash:.2f}\nW:{w}/{len(trades)}")
    return {'ok': True, 'pnl': pnl}

try:
    from AUTO_PROFIT_TAKER import AutoProfitTaker as _APT
    profit_taker = _APT(ex, {}, close_handler=_paper_close)
    logger.info('Auto Profit Taker initialized (paper-routed)')
except Exception as e:
    profit_taker = None
    logger.warning(f'Profit taker init failed: {e}')

# === CROSS-EXCHANGE ARBITRAGE SCAN (public prices, fresh clients per cycle) ===
async def _xarb_scan():
    import ccxt.async_support as _cca
    from CROSS_EXCHANGE_ARBITRAGE import CrossExchangeArbitrage as _XARB
    _exs = {}
    for _nm, _cid in [('bybit', 'bybit'), ('gate', 'gateio'), ('gate', 'gate'), ('kucoin', 'kucoin'), ('okx', 'okx')]:
        if _nm in _exs:
            continue
        _f = getattr(_cca, _cid, None)
        if _f:
            try:
                _exs[_nm] = _f({'enableRateLimit': True})
            except Exception:
                pass
    _xa = _XARB(_exs, {})
    _out = []
    try:
        for _xs in ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'AVAX/USDT', 'LINK/USDT', 'NEAR/USDT', 'SUI/USDT', 'ARB/USDT', 'OP/USDT']:
            _prices = await _xa.fetch_all_prices(_xs)
            if _prices and len(_prices) >= 2:
                for _opp in _xa.find_arbitrage_opportunities(_xs, _prices):
                    if _opp['profit_pct'] >= _xa.min_profit_pct:
                        _out.append(_opp)
    finally:
        for _e in _exs.values():
            try:
                await _e.close()
            except Exception:
                pass
    return _out

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
        # === ULTRA ENGINE SIGNALS (harvested once per cycle) ===
        engine_hot = {}
        if globals().get('scalp_engine'):
            try:
                for sg in asyncio.run(scalp_engine._scan_scalp_opportunities('5m')):
                    if sg.confidence >= 0.6:
                        engine_hot[sg.symbol] = True
                        logger.info(f"SCALP {sg.symbol} {sg.strategy} {sg.confidence:.2f}")
            except Exception as e:
                logger.warning(f"scalp scan: {e}")
        if globals().get('moon_system'):
            try:
                for g in asyncio.run(moon_system.spotter.scan_for_new_gems()):
                    gs = g.get('symbol') if isinstance(g, dict) else None
                    if gs:
                        engine_hot[gs] = True
                        logger.info(f"MOON GEM {gs}")
            except Exception as e:
                logger.warning(f"moon scan: {e}")
        if globals().get('arb_engine'):
            try:
                asyncio.run(arb_engine._scan_arbitrage_opportunities([x for x, _ in cands], 'high'))
                for opp in list(arb_engine.active_arbitrages.values()):
                    osym = getattr(opp, 'symbol', None)
                    if osym:
                        engine_hot[osym] = True
                        logger.info(f"ARB {osym}")
            except Exception as e:
                logger.warning(f"arb scan: {e}")
        try:
            for opp in asyncio.run(_xarb_scan()):
                engine_hot[opp['symbol']] = True
                logger.info(f"XARB {opp['symbol']} buy {opp['buy_exchange']} sell {opp['sell_exchange']} +{opp['profit_pct']:.2f}%")
        except Exception as e:
            logger.warning(f"xarb scan: {e}")
        _cand_syms = {x for x, _ in cands}
        _norm = {k.split(':')[0]: k for k in tickers}
        for hs in list(engine_hot):
            tk = hs if hs in tickers else _norm.get(hs)
            if tk and tk not in _cand_syms and tickers[tk].get('last'):
                cands.append((tk, tickers[tk]['last']))
                engine_hot[tk] = True
                _cand_syms.add(tk)
        for sym, price in cands:
            if sym in positions: continue
            sig = get_signal(sym)
            ml_act = None
            if globals().get('ml_pipeline') and (sig or sym in engine_hot):
                try:
                    _ml = asyncio.run(ml_pipeline.ultra_analysis(sym))
                    ml_act = _ml.get('action')
                    logger.info(f"ML {sym}: {ml_act} conf {_ml.get('confidence')}")
                except Exception as e:
                    logger.warning(f"ml {sym}: {e}")
            if sig and ml_act in ('SELL', 'SHORT'):
                logger.info(f"ML veto {sym}")
                continue
            if not sig:
                if sym in engine_hot and ml_act not in ('SELL', 'SHORT'):
                    sig = 'ultra_engine'
                else:
                    continue
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
            if globals().get('profit_taker'):
                try:
                    profit_taker.register_position(sym, 'buy', price, qty, 'micro_scalp' if sig == 'ultra_engine' else 'normal')
                except Exception:
                    pass
            partial.add_position(sym, price, size_usd)
            logger.info(f"📈 BUY {sym} [{sig}] @ {price:.4f} ${size_usd:.2f}")
            tg(f"📈 BUY {sym}\nStrategy: {sig}\nEntry: ${price:.4f}\nSize: ${size_usd:.2f}")
            save_state()
            if not scalp_coord.can_take_scalp() or len(positions) >= 5: break
        if globals().get('profit_taker'):
            try:
                for _sym, _pos in list(positions.items()):
                    if _sym not in profit_taker.open_positions:
                        profit_taker.register_position(_sym, 'buy', _pos['entry'], _pos['qty'], 'normal')
                asyncio.run(profit_taker.check_and_close_positions())
            except Exception as e:
                logger.warning(f"profit taker: {e}")
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
