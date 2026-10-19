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
try:
    import being_ledger as _ledger
except Exception:
    _ledger = None

def _alloc_zoo_cap():
    """Real-position cap from the governor (3 = historical default)."""
    try:
        import allocation
        a = allocation.get('zoo')
        return int(a.get('real_cap', 3)) if a.get('mode', 'real') == 'real' else 0
    except Exception:
        return 3

def _partial_close(symbol, price, qty_sell, level):
    global cash
    pos = positions.get(symbol)
    if not pos or qty_sell <= 0:
        return False
    qty_sell = min(qty_sell, pos['qty'])
    if TRADING_MODE == 'testnet' and pos.get('real'):
        _rs = _ccxt_to_raw(symbol)
        if _rs:
            try:
                _q = qty_sell
                try:
                    _mkt = ex.market(symbol)
                    _step = float((_mkt.get('precision') or {}).get('amount') or 0)
                    if _step:
                        _ds = str(_step)
                        _dec = len(_ds.split('.')[1].rstrip('0')) if '.' in _ds else 0
                        _q = round(int(_q / _step) * _step, _dec)
                except Exception:
                    pass
                if _q <= 0:
                    return False
                tn.create_market_sell(_rs, _qty_str(_q))
                qty_sell = _q
                logger.info(f"TESTNET PARTIAL SELL {level} {symbol} ({_rs}) qty {_q} @ {price}")
            except Exception as e:
                logger.warning(f"testnet partial sell failed {symbol}: {e}")
                return False
    pnl = (price - pos['entry']) * qty_sell
    cash += pnl
    trades.append(pnl)
    compounder.update_pnl(pnl)
    pos['qty'] -= qty_sell
    if pos['qty'] <= 1e-9:
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
        if symbol in getattr(partial, 'positions', {}):
            del partial.positions[symbol]
    save_state()
    _w = sum(1 for x in trades if x > 0)
    try:
        ultra.learn_from_trade({'EMAbbSqueeze': 'momentum', 'RSIMeanRev': 'mean_reversion', 'DonchianBreakout': 'breakout', 'MAPullback': 'momentum', 'EvoCombo': 'momentum', 'ultra_engine': 'scalping'}.get(positions.get(symbol, {}).get('strat'), 'momentum'), pnl > 0, pnl)
        try:
            if _ledger: _ledger.record_close('zoo', symbol, pnl, real=bool(positions.get(symbol, {}).get('real')), meta={'strat': positions.get(symbol, {}).get('strat'), 'kind': 'partial'})
        except Exception:
            pass
        if positions.get(symbol, {}).get('strat') == 'alpha_router' and globals().get('alpha_router'):
            try:
                for _sn, _sv in (alpha_votes.pop(symbol, {}) or {}).items():
                    alpha_router.update_reliability(symbol, '1h', _sn, (1.0 if pnl > 0 else -1.0) * min(1.0, abs(_sv)))
            except Exception:
                pass
    except Exception:
        pass
    logger.info(f"PARTIAL {level} {symbol} sold {qty_sell} @ {price} pnl ${pnl:+.2f}")
    tg(f"PARTIAL {level} {symbol} sold {qty_sell} @ ${price:.4f} | P&L ${pnl:+.2f} | Cash {_cash_str()} | W:{_w}/{len(trades)}")
    return True

def _paper_close(symbol, side, size, price, reason):
    global cash
    pos = positions.get(symbol)
    if not pos:
        return {'ok': False, 'error': 'not in paper book'}
    if TRADING_MODE == 'testnet' and pos.get('real'):
        try:
            _rs = _ccxt_to_raw(symbol)
            if not _rs: raise Exception('unmapped symbol')
            tn.create_market_sell_reduce(_rs, _qty_str(pos['qty']))
            logger.info(f"TESTNET PT SELL filled {symbol}")
        except Exception as e:
            logger.warning(f"testnet PT SELL failed {symbol}: {e}")
            return {'ok': False, 'error': str(e)}
    pnl = (price - pos['entry']) * pos['qty']
    cash += pnl
    trades.append(pnl)
    compounder.update_pnl(pnl)
    try:
        ultra.learn_from_trade({'EMAbbSqueeze': 'momentum', 'RSIMeanRev': 'mean_reversion', 'DonchianBreakout': 'breakout', 'MAPullback': 'momentum', 'EvoCombo': 'momentum', 'ultra_engine': 'scalping'}.get(pos.get('strat'), 'momentum'), pnl > 0, pnl)
        try:
            if _ledger: _ledger.record_close('zoo', symbol, pnl, real=bool(pos.get('real')), meta={'strat': pos.get('strat'), 'kind': 'full'})
        except Exception:
            pass
        if pos.get('strat') == 'alpha_router' and globals().get('alpha_router'):
            try:
                for _sn, _sv in (alpha_votes.pop(symbol, {}) or {}).items():
                    alpha_router.update_reliability(symbol, '1h', _sn, (1.0 if pnl > 0 else -1.0) * min(1.0, abs(_sv)))
                logger.info(f"ALPHA ROUTER learn {symbol} pnl {pnl:+.2f}")
            except Exception:
                pass
    except Exception:
        pass
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
    tg(f"PT SELL {symbol} ({reason})\nP&L: ${pnl:+.2f}\nCash: {_cash_str()}\nW:{w}/{len(trades)}")
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
# === TRADING MODE: paper (default) or testnet (real testnet orders) ===
# NOTE: CCXT/requests fingerprint is WAF-blocked on Bybit testnet (403 HTML).
# The money path therefore uses a raw urllib signed client (verified 200 OK).
import os as _os
import urllib.request as _ureq
import hashlib as _hl
import hmac as _hm
import json as _js
import time as _tm

class _TestnetClient:
    def __init__(self, key, secret):
        self.key = key; self.secret = secret
        self.relay = _os.environ.get('TESTNET_RELAY', '')
        self.base = 'https://api-testnet.bybit.com'
    def _req(self, method, path, params=None, signed=True):
        params = params or {}
        if getattr(self, 'relay', None):
            _data = _js.dumps({'method': method, 'path': path, 'params': params}).encode()
            _rq = _ureq.Request(self.relay + '/relay', data=_data, headers={'Content-Type': 'application/json'}, method='POST')
            with _ureq.urlopen(_rq, timeout=20) as _r:
                j = _js.loads(_r.read().decode())
            if j.get('retCode') != 0:
                raise Exception(f"bybit {j.get('retCode')}: {j.get('retMsg')}")
            return j['result']
        ts = str(int(_tm.time() * 1000)); recv = '5000'
        if method == 'GET':
            qs = '&'.join(f'{k}={v}' for k, v in params.items())
            body = ''
            payload = ts + self.key + recv + qs
        else:
            qs = ''
            body = _js.dumps(params)
            payload = ts + self.key + recv + body
        headers = {'Content-Type': 'application/json'}
        if signed:
            headers['X-BAPI-API-KEY'] = self.key
            headers['X-BAPI-SIGN'] = _hm.new(self.secret.encode(), payload.encode(), _hl.sha256).hexdigest()
            headers['X-BAPI-TIMESTAMP'] = ts
            headers['X-BAPI-RECV-WINDOW'] = recv
        url = self.base + path + (('?' + qs) if qs else '')
        req = _ureq.Request(url, data=(body.encode() if method != 'GET' else None), headers=headers, method=method)
        with _ureq.urlopen(req, timeout=15) as r:
            j = _js.loads(r.read().decode())
        if j.get('retCode') != 0:
            raise Exception(f"bybit {j.get('retCode')}: {j.get('retMsg')}")
        return j['result']
    def wallet_free_usdt(self):
        res = self._req('GET', '/v5/account/wallet-balance', {'accountType': 'UNIFIED'})
        coins = res['list'][0].get('coin', [])
        u = next((c for c in coins if c.get('coin') == 'USDT'), {})
        return float(u.get('availableToWithdraw') or u.get('walletBalance') or 0)
    def set_leverage(self, symbol, lev=10):
        return self._req('POST', '/v5/position/set-leverage', {'category': 'linear', 'symbol': symbol, 'buyLeverage': str(lev), 'sellLeverage': str(lev)})
    def create_market_buy(self, symbol, qty):
        return self._req('POST', '/v5/order/create', {'category': 'linear', 'symbol': symbol, 'side': 'Buy', 'orderType': 'Market', 'qty': str(qty)})
    def create_market_sell_reduce(self, symbol, qty):
        return self._req('POST', '/v5/order/create', {'category': 'linear', 'symbol': symbol, 'side': 'Sell', 'orderType': 'Market', 'qty': str(qty), 'reduceOnly': True})

def _ccxt_to_raw(sym):
    # 'BTC/USDT:USDT' -> 'BTCUSDT'; dated/odd symbols -> None (paper-only)
    if sym.endswith('/USDT:USDT'):
        return sym.split('/')[0] + 'USDT'
    return None

def _qty_str(q):
    t = ('%.6f' % float(q)).rstrip('0').rstrip('.')
    return t if t else '0'

TRADING_MODE = _os.environ.get('TRADING_MODE', 'paper').lower()
tn = None
if TRADING_MODE == 'testnet':
    try:
        _key = _sec = None
        for _base in ('/run/secrets', '/root/secrets'):
            _kp = _os.path.join(_base, 'bybit_testnet_api_key')
            _sp = _os.path.join(_base, 'bybit_testnet_api_secret')
            if _os.path.exists(_kp) and _os.path.exists(_sp):
                _key = open(_kp).read().strip()
                _sec = open(_sp).read().strip()
                break
        if not _key:
            raise Exception('testnet secret files not found')
        tn = _TestnetClient(_key, _sec)
        _free = tn.wallet_free_usdt()
        logger.info(f'TESTNET MODE LIVE (raw client): real orders ON, USDT free = {_free}')
        tg(f'TESTNET MODE: real testnet orders ON (USDT free {_free})')
    except Exception as e:
        TRADING_MODE = 'paper'
        tn = None
        logger.warning(f'Testnet setup failed, staying PAPER: {e}')
else:
    logger.info('PAPER MODE: simulation only')

def _cash_str():
    t = f"${cash:.2f}"
    if TRADING_MODE == 'testnet' and tn:
        try:
            t += f" | testnet free ${tn.wallet_free_usdt():.2f}"
        except Exception:
            pass
    return t

logger.info("🐯 Zoo Paper Trader started"); tg("🐯 Zoo Trader LIVE - 5 strategies")

try:
    from alpha_engines import AlphaRouter
    alpha_router = AlphaRouter()
    alpha_votes = {}
    logger.info('ALPHA ROUTER: ensemble live (9 strategies, reliability learning)')
except Exception as e:
    alpha_router = None
    alpha_votes = {}
    logger.warning(f'ALPHA ROUTER unavailable: {e}')

try:
    from ultra_god_mode import UltraGodMode
    god_mode = UltraGodMode()
    logger.info('GOD MODE: quantum/swarm/fractal/smart-money analysis live (advisory veto)')
except Exception as e:
    god_mode = None
    logger.warning(f'GOD MODE unavailable: {e}')

try:
    from ultra_quantum_intelligence import QuantumMomentumOscillator
    qmo = QuantumMomentumOscillator()
    logger.info('QUANTUM INTELLIGENCE: momentum oscillator overlay live (observation)')
except Exception as e:
    qmo = None
    logger.warning(f'QUANTUM unavailable: {e}')

_sig_memo = {}

def get_signal(sym):
    _bucket = int(time.time() // 300)
    _hit = _sig_memo.get(sym)
    if _hit and _hit[0] == _bucket:
        return _hit[1]
    _res = None
    try:
        ohlcv = ex.fetch_ohlcv(sym, '1h', 100)
        if len(ohlcv) >= 50:
            df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','vol'])
            for strat in strategies:
                try:
                    out = strat.apply(df)
                    if out['long_signal'].iloc[-1]:
                        _res = strat.name
                        break
                except: pass
    except: pass
    _sig_memo[sym] = (_bucket, _res)
    return _res

ENGINE_HOT = {}

while True:
    try:
        if emergency.emergency_active or emergency.check_conditions(cash, 100.0):
            logger.error("🚨 EMERGENCY"); tg("🚨 EMERGENCY STOP"); time.sleep(300); continue
        tickers = ex.fetch_tickers()
        cands = [(s,t['last']) for s,t in tickers.items() if '/USDT' in s and t.get('quoteVolume',0)>1000000 and t['last']]
        cands = cands[:20]
        # === ULTRA ENGINE SIGNALS (background thread refreshes ENGINE_HOT) ===
        engine_hot = {}
        if not globals().get('_engine_bg_started'):
            import threading as _th2
            def _engine_bg():
                while True:
                    try:
                        if globals().get('scalp_engine'):
                            try:
                                for sg in asyncio.run(scalp_engine._scan_scalp_opportunities('5m')):
                                    if sg.confidence >= 0.6:
                                        ENGINE_HOT[sg.symbol] = time.time()
                                        logger.info(f"SCALP {sg.symbol} {sg.strategy} {sg.confidence:.2f}")
                            except Exception as e:
                                logger.warning(f"scalp scan: {e}")
                        if globals().get('moon_system'):
                            try:
                                for g in asyncio.run(moon_system.spotter.scan_for_new_gems()):
                                    gs = g.get('symbol') if isinstance(g, dict) else None
                                    if gs:
                                        ENGINE_HOT[gs] = time.time()
                                        logger.info(f"MOON GEM {gs}")
                            except Exception as e:
                                logger.warning(f"moon scan: {e}")
                        try:
                            for opp in asyncio.run(_xarb_scan()):
                                ENGINE_HOT[opp['symbol']] = time.time()
                                logger.info(f"XARB {opp['symbol']} buy {opp['buy_exchange']} sell {opp['sell_exchange']} +{opp['profit_pct']:.2f}%")
                        except Exception as e:
                            logger.warning(f"xarb scan: {e}")
                    except Exception as e:
                        logger.warning(f"engine bg: {e}")
                    time.sleep(90)
            _th2.Thread(target=_engine_bg, daemon=True).start()
            globals()['_engine_bg_started'] = True
            logger.info('ENGINE background scanner started (scalp/moon/xarb)')
        engine_hot = {s2: True for s2, ts2 in list(ENGINE_HOT.items()) if time.time() - ts2 < 300}
        if globals().get('arb_engine'):
            try:
                if not globals().get('_arb_bg_started'):
                    import threading as _th
                    def _arb_bg():
                        try:
                            asyncio.run(arb_engine._scan_arbitrage_opportunities(['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'ADA/USDT'], 'low_priority'))
                        except Exception as e:
                            logger.warning(f"arb bg: {e}")
                    _th.Thread(target=_arb_bg, daemon=True).start()
                    globals()['_arb_bg_started'] = True
                    logger.info('ARB background scanner started')
                for opp in list(arb_engine.active_arbitrages.values()):
                    osym = getattr(opp, 'symbol', None)
                    if osym:
                        engine_hot[osym] = True
                        logger.info(f"ARB {osym}")
            except Exception as e:
                logger.warning(f"arb scan: {e}")
        # xarb results arrive via the engine background thread (ENGINE_HOT)
        _cand_syms = {x for x, _ in cands}
        _norm = {k.split(':')[0]: k for k in tickers}
        for hs in list(engine_hot):
            tk = hs if hs in tickers else (hs + ':USDT' if (hs + ':USDT') in tickers else _norm.get(hs))
            if tk:
                engine_hot[tk] = True
                if tk not in _cand_syms and tickers[tk].get('last'):
                    cands.append((tk, tickers[tk]['last']))
                    _cand_syms.add(tk)
        # Ultrasonic overlay: HMM regime gate + bandit read (research suite)
        us_bear_block = False
        try:
            _oh = ex.fetch_ohlcv('BTC/USDT:USDT', '1h', 60)
            _cl = [c[4] for c in _oh]
            _rets = [(_cl[i] / _cl[i - 1] - 1) for i in range(1, len(_cl))]
            _md = {'current_price': _cl[-1], 'returns': _rets, 'volume_usd': 50000000}
            _us = asyncio.run(ultra.get_ultrasonic_signals(_md, []))
            _reg = (_us.get('regime') or {})
            _bnd = (_us.get('best_strategy') or {})
            logger.info(f"ULTRASONIC regime={_reg.get('regime')} conf={_reg.get('confidence')} bias={_reg.get('position_bias')} | bandit={_bnd.get('strategy')} wr={_bnd.get('win_rate')} | vpin={(_us.get('vpin') or {}).get('toxicity')}")
            if _reg.get('regime') == 'bear' and (_reg.get('confidence') or 0) >= 0.6:
                us_bear_block = True
                logger.info("ULTRASONIC GATE: bear regime - long entries paused this cycle")
        except Exception as e:
            logger.warning(f"ultrasonic consult failed: {e}")
        for sym, price in cands:
            if us_bear_block:
                break
            if sym in positions: continue
            sig = get_signal(sym)
            if not sig and sym not in engine_hot and globals().get('alpha_router'):
                try:
                    _oh = ex.fetch_ohlcv(sym, '1h', 100)
                    if len(_oh) >= 55:
                        _df = pd.DataFrame(_oh, columns=['ts','open','high','low','close','vol'])
                        _dec = alpha_router.pick(_df, sym, '1h')
                        if _dec.side == 'buy':
                            sig = 'alpha_router'
                            alpha_votes[sym] = dict(_dec.votes or {})
                            logger.info(f"ALPHA ROUTER buy {sym} p={_dec.prob:.2f} size_mult={_dec.size_mult:.2f}")
                except Exception as e:
                    logger.warning(f"alpha router {sym}: {e}")
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
            if sig and globals().get('god_mode'):
                try:
                    _goh = ex.fetch_ohlcv(sym, '5m', 200)
                    if len(_goh) >= 50:
                        _gdf = pd.DataFrame(_goh, columns=['ts','open','high','low','close','vol'])
                        _g = asyncio.run(god_mode.execute_god_mode_analysis(sym, _gdf))
                        logger.info(f"GOD {sym}: {_g.get('action')} conf {_g.get('confidence')}")
                        if _g.get('action') in ('SELL', 'SHORT') and float(_g.get('confidence') or 0) > 0.8:
                            logger.info(f"GOD veto {sym}")
                            continue
                except Exception as e:
                    logger.warning(f"god {sym}: {e}")
            if sig and globals().get('qmo'):
                try:
                    _qoh = ex.fetch_ohlcv(sym, '1h', 120)
                    if len(_qoh) >= 100:
                        import numpy as _np
                        _q = qmo.calculate(_np.array([c[4] for c in _qoh], dtype=float))
                        if _q:
                            logger.info(f"QUANTUM {sym}: momentum={_q.get('quantum_momentum'):.3f} shift={_q.get('shift_direction')} p={_q.get('shift_probability'):.2f} conf={_q.get('confidence'):.2f}")
                except Exception as e:
                    logger.warning(f"quantum {sym}: {e}")
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
            if TRADING_MODE == 'testnet':
                try:
                    _tf = tn.wallet_free_usdt() if tn else 0
                    size_usd = min(size_usd, _tf * 2)
                except Exception:
                    pass
            qty = size_usd / price
            pos_real = False
            if TRADING_MODE == 'testnet':
                _rs = _ccxt_to_raw(sym)
                if _rs and sum(1 for _p in positions.values() if _p.get('real')) >= _alloc_zoo_cap():
                    logger.info(f"real cap ({_alloc_zoo_cap()}) reached - {sym} paper-only, margin reserved for other beings")
                    _rs = None
                if _rs:
                    try:
                        try:
                            tn.set_leverage(_rs, 10)
                        except Exception:
                            pass
                        try:
                            _mkt = ex.market(sym)
                            _step = float((_mkt.get('precision') or {}).get('amount') or 0)
                            _minq = float(((_mkt.get('limits') or {}).get('amount') or {}).get('min') or 0)
                        except Exception:
                            _step = 0; _minq = 0
                        if _step:
                            _ds = str(_step)
                            _dec = len(_ds.split('.')[1].rstrip('0')) if '.' in _ds else 0
                            qty = round(int(qty / _step) * _step, _dec)
                        if _minq and qty < _minq:
                            if _minq * price <= 100:
                                qty = _minq
                            else:
                                logger.info(f"testnet BUY skipped {sym}: qty below min {_minq}")
                                continue
                        tn.create_market_buy(_rs, _qty_str(qty))
                        pos_real = True
                        logger.info(f"TESTNET BUY filled {sym} ({_rs}) qty {qty} @ {price}")
                    except Exception as e:
                        logger.warning(f"testnet BUY failed {sym}: {e}")
                        continue
            positions[sym] = {'qty': qty, 'entry': price, 'real': pos_real, 'strat': sig}
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
        # --- PartialTP ladder (2025): trim 25% @+1%, 50% @+2%, remainder @+3% ---
        try:
            for _psym in list(getattr(partial, 'positions', {})):
                if _psym not in positions:
                    del partial.positions[_psym]
            for _psym, _ppos in list(positions.items()):
                if _psym not in partial.positions:
                    partial.add_position(_psym, _ppos['entry'], _ppos['qty'])
                _ptp = profit_taker.open_positions.get(_psym) if profit_taker else None
                if _ptp and _ptp.get('strategy_type', _ptp.get('strategy', '')) != 'micro_scalp':
                    _ptp['profit_target'] = 0.035
                _ptk = tickers.get(_psym)
                if not _ptk or not _ptk.get('last'):
                    continue
                for _ord in asyncio.run(partial.check_tp_levels(_psym, _ptk['last'])):
                    _partial_close(_psym, _ptk['last'], _ord['size'], _ord['tp_level'])
        except Exception as e:
            logger.warning(f"partial tp: {e}")

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
                if sell and TRADING_MODE == 'testnet' and pos.get('real'):
                    try:
                        _rs = _ccxt_to_raw(sym)
                        if not _rs: raise Exception('unmapped symbol')
                        tn.create_market_sell_reduce(_rs, _qty_str(pos['qty']))
                        logger.info(f"TESTNET SELL filled {sym}")
                    except Exception as e:
                        logger.warning(f"testnet SELL failed {sym}: {e}")
                        sell = False
                if sell:
                    pnl=(cur-pos['entry'])*pos['qty']
                    cash+=pnl; trades.append(pnl); compounder.update_pnl(pnl); trailer.clear(sym)
                    sess = MarketSession.get_current_session()
                    session_tracker.record_trade(sym, sess, pnl, pnl>0)
                    w=sum(1 for x in trades if x>0)
                    logger.info(f"📉 SELL {sym} ({reason}) ${pnl:+.2f}")
                    tg(f"📉 SELL {sym} ({reason})\nP&L: ${pnl:+.2f} ({pct:+.1f}%)\nCash: {_cash_str()}\nW:{w}/{len(trades)}")
                    scalp_coord.close_scalp(sym, pct)
                    del positions[sym]; save_state()
            except: pass
        w=sum(1 for x in trades if x>0)
        logger.info(f"💵 {_cash_str()} | Open:{len(positions)} | Trades:{len(trades)} W:{w}")
        time.sleep(45)
    except Exception as e:
        logger.error(f"E: {e}"); time.sleep(30)
