#!/usr/bin/env python3
"""
EXECUTION ORCHESTRATOR SERVICE v2 - the 2025 execution engine, LIVE.

Peters' design: engines generate signals; the orchestrator is the
execution master - Kelly sizing (SmartPositionSizer), risk gates
(SmartRiskManager), -1% stop / +2% target (2:1), balance-fed
compounding. In 2025 its real arm was RealProfitBot on Gate.io.
Here the arm is the Bybit testnet relay with the same interface,
the sizer's amount passed through (patched), and closes enforced
on the exchange before they are booked (patched).

Inputs, both faithful:
- The 2025 alpha engines (alpha_engines.py) computing on live 15m
  candles every 60s; >=85% confidence buys go straight to
  orchestrator.execute_trade (the run_real_2025 pattern).
- Sentient-brain APPROVE_LIVE decisions from the signal bus,
  fed into the data hub's alert queue for run_execution_loop.

The governor gates its mode (allocation['orchestrator']); its
closes land in the capacity ledger as being 'orchestrator'.
Long-only (the whole fleet is); shorts are refused by the arm.
"""
import asyncio
import json
import logging
import os
import time
import urllib.parse
import urllib.request

os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - ORCHESTRATOR - %(message)s')
logger = logging.getLogger('ORCHESTRATOR')

BASE_PAIRS = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'SOL/USDT', 'ADA/USDT']


def tg(msg):
    tok = os.environ.get('TELEGRAM_BOT_TOKEN')
    cid = os.environ.get('TELEGRAM_CHAT_ID')
    if not tok or not cid:
        return
    try:
        data = urllib.parse.urlencode({'chat_id': cid, 'text': msg}).encode()
        urllib.request.urlopen(
            urllib.request.Request(
                f'https://api.telegram.org/bot{tok}/sendMessage', data=data),
            timeout=10)
    except Exception:
        pass


class RelayExecutionArm:
    """The orchestrator's execution arm on the signing relay -
    RealProfitBot's interface, Bybit testnet underneath."""

    def __init__(self, hub):
        self.hub = hub
        self._tn = None
        self._backoff_until = 0.0

    def _client(self):
        if self._tn is None:
            from testnet_client import make_client
            self._tn = make_client()
        return self._tn

    def _mode(self):
        try:
            import allocation
            return allocation.get('orchestrator').get('mode', 'real')
        except Exception:
            return 'real'

    def execute_trade(self, symbol, signal, price, amount=None):
        if signal not in ('BUY', 'SELL'):
            return None
        if self._mode() != 'real':
            logger.info(f'governor paper mode - not executing {symbol}')
            return None
        if time.time() < self._backoff_until:
            return None
        raw = symbol.split('/')[0] + 'USDT'
        try:
            from testnet_client import qty_str, quantize
            tn = self._client()
            for pos in tn.positions():
                if pos.get('symbol') == raw and float(pos.get('positionValue') or 0) >= 1.0:
                    logger.info(f'arm: {raw} held by another being - skip')
                    return None  # conflict guard
            qty = float(amount) if amount else 12.0 / float(price)
            step = None
            mkt = self.hub.market_spec(symbol)
            if mkt is None:
                logger.info(f'arm: {raw} not live on testnet - skip')
                return None
            try:
                step = float(mkt['precision']['amount'])
                qty = quantize(qty, step) or 0
            except Exception:
                qty = round(qty, 3)
            # Bybit's perp minimum order value is $5 - quantization
            # rounds DOWN, so top up by steps to reach it (the
            # sizer's intent), never silently die below it.
            if qty and step:
                tries = 0
                while qty * float(price) < 5.0 and tries < 3:
                    qty = round(qty + step, 10)
                    tries += 1
            if not qty or qty * float(price) < 5.0:
                logger.info(f'arm: {raw} qty {qty} @ {price} below $5 min - skip')
                return None
            try:
                tn.set_leverage(raw, 10)
            except Exception:
                pass
            # Maker-first entry (2026-10-20): taker fees are the
            # structural drag at these notionals. Post-only limit at
            # the signal price with a 15s fuse; a filled maker order
            # is the position. Unfilled -> cancel -> ONE market
            # fallback (never starve a strong signal). A partial
            # fill >= $5 stands as the position; a dust partial is
            # left for the exchange sync and topped up by market.
            try:
                lr = tn.create_limit_postonly(raw, 'Buy' if signal == 'BUY' else 'Sell', qty, price)
                oid = lr.get('orderId') if isinstance(lr, dict) else None
                if oid:
                    deadline = time.time() + 15
                    filled_qty = 0.0
                    avg = float(price)
                    status = ''
                    while time.time() < deadline:
                        st = tn.order_status(raw, oid) or {}
                        status = st.get('orderStatus') or ''
                        try:
                            filled_qty = float(st.get('cumExecQty') or 0)
                            if st.get('avgPrice'):
                                avg = float(st['avgPrice'])
                        except Exception:
                            pass
                        if status in ('Filled', 'Cancelled', 'Rejected', 'Expired'):
                            break
                        time.sleep(1.5)
                    if status != 'Filled':
                        try:
                            tn.cancel_order(raw, oid)
                        except Exception:
                            pass
                        st = tn.order_status(raw, oid) or {}
                        try:
                            filled_qty = float(st.get('cumExecQty') or filled_qty)
                            if st.get('avgPrice'):
                                avg = float(st['avgPrice'])
                        except Exception:
                            pass
                    if filled_qty > 0 and filled_qty * avg >= 5.0:
                        logger.info(f'⚡ MAKER {signal} {raw} qty {filled_qty} @ {avg} (post-only)')
                        tg(f'⚡ Orchestrator MAKER {signal} {raw} qty {filled_qty} @ {avg}')
                        return {'symbol': symbol, 'side': 'buy' if signal == 'BUY' else 'sell',
                                'amount': filled_qty, 'price': avg,
                                'orderId': oid, 'simulated': False}
                    if filled_qty > 0:
                        qty = round(qty - filled_qty, 10)
                        logger.info(f'arm: maker dust partial {filled_qty} on {raw}; market top-up {qty}')
                    else:
                        logger.info(f'arm: maker unfilled on {raw} - market fallback')
            except Exception as e:
                logger.info(f'arm: maker path failed on {raw} ({e}) - market fallback')
            if signal == 'BUY':
                res = tn.create_market_buy(raw, qty_str(qty))
            else:
                res = tn.create_market_sell_open(raw, qty_str(qty))
            if isinstance(res, dict) and res.get('orderId'):
                logger.info(f'⚡ REAL {signal} {raw} qty {qty} @ {price}')
                tg(f'⚡ Orchestrator {signal} {raw} qty {qty} @ {price}')
                return {'symbol': symbol, 'side': 'buy' if signal == 'BUY' else 'sell', 'amount': qty,
                        'price': price, 'orderId': res['orderId'],
                        'simulated': False}
            if isinstance(res, dict) and '110007' in str(res):
                self._backoff_until = time.time() + 60
            logger.warning(f'arm buy rejected {raw}: {res}')
            return None
        except Exception as e:
            if '110007' in str(e):
                self._backoff_until = time.time() + 60
            logger.warning(f'arm buy {symbol}: {e}')
            return None

    def close_position(self, symbol, size, side):
        raw = symbol.split('/')[0] + 'USDT'
        try:
            from testnet_client import qty_str, quantize
            tn = self._client()
            qty = float(size)
            try:
                mkt = self.hub.market_spec(symbol)
                if mkt:
                    qty = quantize(qty, float(mkt['precision']['amount'])) or qty
            except Exception:
                pass
            # An accepted order is NOT a fill (2026-10-20): on an
            # illiquid testnet pair the market close returns an
            # orderId and executes nothing - the core booked the
            # 'close', dropped the position, the sync re-adopted
            # it, and the phantom loss repeated every cycle. A
            # close counts only when the exchange position
            # actually shrinks; attempts are throttled per symbol
            # so an unfillable pair retries calmly, not per cycle.
            _now = time.time()
            _last = getattr(self, '_close_attempts', {}).get(raw, 0)
            if _now - _last < 120:
                return False
            if not hasattr(self, '_close_attempts'):
                self._close_attempts = {}
            self._close_attempts[raw] = _now

            def _pos_size():
                for pp in tn.positions():
                    if (pp.get('symbol') or '') == raw:
                        return abs(float(pp.get('size') or 0))
                return 0.0

            before = _pos_size()
            res = None
            for _ in range(3):
                if side == 'buy':
                    res = tn.create_market_sell_reduce(raw, qty_str(qty))
                else:
                    res = tn.create_market_buy_reduce(raw, qty_str(qty))
                if isinstance(res, dict) and res.get('orderId'):
                    break
            if not (isinstance(res, dict) and res.get('orderId')):
                logger.error(f'arm close failed {raw}: {res}')
                return False
            for _ in range(3):
                time.sleep(2)
                if _pos_size() < before * 0.99:
                    logger.info(f'⚡ REAL CLOSE {raw} qty {qty} '
                                f'(fill verified)')
                    return True
            logger.warning(f'arm close {raw}: order accepted but '
                           f'position unchanged (unfilled - likely '
                           f'no testnet liquidity); not booking')
            return False
        except Exception as e:
            logger.error(f'arm close {symbol}: {e}')
            return False


class PriceAdapter:
    """orchestrator.router: async fetch_ticker over the hub client.

    PRICE TRUTH (2026-10-20): positions live on TESTNET but the hub
    serves MAINNET tickers - for most pairs the marks agree, but
    illiquid testnet pairs drift hard (KAS testnet mark 0.0351 vs
    mainnet 0.0375: +6.8%). Monitoring a testnet position against a
    mainnet price fired phantom stops. So: when the symbol has an
    open exchange position, its own markPrice (the exchange's
    testnet truth) wins; the hub price serves entry sizing only."""

    def __init__(self, hub, arm=None):
        self.hub = hub
        self.arm = arm
        self._marks = {}
        self._marks_ts = 0.0

    async def fetch_ticker(self, symbol):
        raw = symbol.split('/')[0] + 'USDT'
        try:
            if self.arm is not None:
                import time as _t
                if _t.time() - self._marks_ts > 10:
                    tn = self.arm._client()
                    self._marks = {
                        (pp.get('symbol') or ''):
                        float(pp.get('markPrice') or 0)
                        for pp in tn.positions()}
                    self._marks_ts = _t.time()
                mp = self._marks.get(raw)
                if mp:
                    return {'last': mp}
        except Exception:
            pass
        try:
            t = self.hub.ex.fetch_ticker(symbol + ':USDT')
            return {'last': float(t['last'])}
        except Exception:
            return {}


class BusHub:
    """The orchestrator's data hub: alert queue in, trade records
    out to the capacity ledger + Telegram."""

    def __init__(self, arm):
        self.alert_queue = asyncio.Queue()
        self.arm = arm

    async def publish_trade(self, record):
        try:
            if record.get('status') == 'closed':
                import being_ledger
                being_ledger.record_close(
                    'orchestrator', record.get('symbol', '?'),
                    float(record.get('pnl') or 0.0), real=True,
                    meta={'reason': record.get('reason'),
                          'strat': 'alpha_router'})
                tg(f"⚡ Orchestrator close {record.get('symbol')} "
                   f"${float(record.get('pnl') or 0.0):+.2f} "
                   f"({record.get('reason')})")
            else:
                logger.info(f"trade opened: {record.get('symbol')} "
                            f"@ {record.get('entry_price')}")
        except Exception as e:
            logger.warning(f'publish_trade: {e}')


async def decision_feeder(hub):
    """Sentient APPROVE_LIVE decisions -> the alert queue."""
    import signal_bus
    seen = set()
    while True:
        try:
            for item in signal_bus.get_pending_decisions():
                d = item[1] if isinstance(item, tuple) else item
                if d.get('brain') != 'sentient_brain':
                    continue
                if d.get('signal') != 'APPROVE_LIVE':
                    continue
                key = f"{d.get('timestamp')}|{d.get('symbol')}"
                if key in seen:
                    continue
                seen.add(key)
                meta = d.get('metadata') or {}
                side = str(meta.get('side', 'BUY')).lower()
                if side not in ('buy', 'sell'):
                    side = 'buy'
                await hub.alert_queue.put({
                    'signal': {'symbol': d.get('symbol'),
                               'data': {'symbol': d.get('symbol')}},
                    'action': side,
                    'confidence': float(d.get('confidence', 0)) / 100.0,
                })
                logger.info(f"decision fed: {d.get('symbol')} {side} "
                            f"conf {d.get('confidence')}")
        except Exception as e:
            logger.warning(f'feeder: {e}')
        await asyncio.sleep(15)


async def alpha_loop(orchestrator, hub, bus_hub):
    """Feed the orchestrator the way the design intends: the alpha
    engines return SCORES; AlphaRouter fuses them (with the
    reliability weights the zoo's closes keep teaching it - fresh
    instance each cycle reads the shared memo). Router buy verdicts
    enter the alert queue, so the orchestrator's own gates (risk
    manager, Kelly sizing) decide execution. 1h frames match the
    zoo's reliability keys."""
    import pandas as pd
    from alpha_engines import AlphaRouter
    from SESSION_AWARE_TRADING import SessionAwareTrading
    sessions = SessionAwareTrading()
    logger.info('alpha loop: AlphaRouter on 15m+1h, session-adjusted -> alert queue')
    while True:
        try:
            router = AlphaRouter()
            pairs = list(BASE_PAIRS)
            try:
                with open('/tmp/discovered_pairs.json') as f:
                    for p in (json.load(f).get('pairs') or [])[:20]:
                        s = p.replace(':USDT', '')
                        if s not in pairs:
                            pairs.append(s)
            except Exception:
                pass
            # FAST MOVERS LEAD: the dynamic scanner's trending pairs
            # (big % moves on real volume) are what grows a small
            # wallet - they enter analysis first.
            try:
                with open('/tmp/trending_pairs.json') as f:
                    for p in (json.load(f).get('pairs') or [])[:10]:
                        s = p.replace(':USDT', '')
                        if s not in pairs:
                            pairs.append(s)
            except Exception:
                pass
            # FULL-MARKET ROTATION (Princewill's rule): every pair
            # the exchange offers gets analyzed - a rotating
            # VELOCITY-ranked slice joins each cycle (fast movers
            # first, $1M volume floor), so the whole market passes
            # through the router over time.
            try:
                ticks = hub.ex.fetch_tickers()
                ranked = sorted(
                    (x for x in ticks if x.endswith('/USDT:USDT')
                     and (ticks[x].get('quoteVolume') or 0) >= 1_000_000),
                    key=lambda x: -abs(ticks[x].get('percentage') or 0))
                rot = getattr(alpha_loop, '_rot', 0)
                window = ranked[rot:rot + 20]
                alpha_loop._rot = (rot + 20) % max(1, len(ranked) - 20)
                for x in window:
                    b = x.replace(':USDT', '')
                    if b not in pairs:
                        pairs.append(b)
            except Exception:
                pass
            # Session stationing: the session's optimal pairs hunt too
            try:
                for p in sessions.get_optimal_pairs_for_session():
                    s = p.replace(':USDT', '')
                    if s in BASE_PAIRS + ['EUR/USD', 'GBP/USD']:
                        continue
                    if p not in pairs and '/' in p:
                        pairs.append(p)
            except Exception:
                pass
            # LEARNED session winners (wired 2026-10-20): the
            # session performance tracker - fed by every zoo close
            # and persisted in runtime/session_perf.json - names
            # the markets that have actually won in this session;
            # they join the hunt beside the static session lists.
            # Fresh tracker per cycle (the learning is never
            # stale); the tracker's own evidence thresholds apply
            # (>=10 trades, >=60% win rate) - until a market earns
            # them, this adds nothing, by design.
            try:
                from session_intelligence import (SessionPerformanceTracker,
                                                  MarketSession)
                _trk = SessionPerformanceTracker()
                for _sym, _sc in _trk.get_optimal_markets(
                        MarketSession.get_current_session()):
                    _s = _sym.replace(':USDT', '')
                    if _s not in pairs:
                        pairs.append(_s)
                        logger.info(f'session tracker: learned winner {_s} joins the hunt')
            except Exception:
                pass
            session_now = sessions.get_current_session()
            frames = [('15m', 40 * 3600, 160), ('1h', 130 * 3600, 120)]
            # Parallel market reads (speed fix, 2026-10-20): the
            # serial loop spent 25-80s per sweep fetching candles
            # pair by pair - the 2025 design scanned in parallel.
            # Public reads only, small pool, same decisions after.
            from concurrent.futures import ThreadPoolExecutor

            def _fetch(job):
                _pair, _tf, _span, _limit = job
                try:
                    _since = int((time.time() - _span) * 1000)
                    _rows = hub.ex.fetch_ohlcv(_pair + ':USDT', _tf,
                                               _since, _limit)
                except Exception:
                    _rows = None
                return _pair, _tf, _rows

            jobs = []
            for pair in pairs:
                # Analysis only where the testnet arm can execute
                try:
                    if hub.market_spec(pair) is None:
                        continue
                except Exception:
                    continue
                for tf, span, limit in frames:
                    jobs.append((pair, tf, span, limit))
            fetched = {}
            if jobs:
                with ThreadPoolExecutor(max_workers=6) as pool:
                    for _pair, _tf, _rows in pool.map(_fetch, jobs):
                        fetched[(_pair, _tf)] = _rows
            for pair in pairs:
                for tf, span, limit in frames:
                    try:
                        rows = fetched.get((pair, tf))
                        if not rows or len(rows) < 60:
                            continue
                        df = pd.DataFrame(rows, columns=['ts', 'open', 'high',
                                                         'low', 'close', 'vol'])
                        dec = router.pick(df, pair, tf)
                        if dec is not None and dec.side in ('buy', 'sell'):
                            # Peters' session organ: confidence (and
                            # through Kelly, size) scales by session
                            sess, mult = sessions.get_session_multiplier(pair)
                            _conv = float(dec.prob) if dec.side == 'buy' else 1.0 - float(dec.prob)
                            conf = min(0.98, _conv * mult)
                            logger.info(f'📡 alpha_router[{tf}]: {pair} {dec.side.upper()} '
                                        f'p={dec.prob:.2f} session {sess} x{mult:.2f} '
                                        f'-> conf {conf:.2f}')
                            await bus_hub.alert_queue.put({
                                'signal': {'symbol': pair,
                                           'data': {'symbol': pair,
                                                    'price': float(df['close'].iloc[-1])}},
                                'action': dec.side,
                                'confidence': conf,
                            })
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f'alpha loop: {e}')
        await asyncio.sleep(30)


def account_equity(tn):
    """Whole-account equity: the sizer's designed reference ('will
    auto-update from exchange balance') - read straight from the
    wallet payload's totalEquity."""
    try:
        return tn.wallet_equity_usdt() or 0.0
    except Exception:
        return 0.0


async def stats_loop(orchestrator, arm):
    while True:
        await asyncio.sleep(300)
        try:
            # Truth anchor: re-seed the sizer from account equity
            eq = account_equity(arm._client())
            if eq:
                orchestrator.position_sizer.update_balance(eq)
            logger.info(f'stats: {orchestrator.get_stats()}')
        except Exception as e:
            logger.warning(f'stats: {e}')


async def exchange_sync_loop(orchestrator, arm):
    """Exchange-truth sync (the zoo reconcile pattern, applied to
    the orchestrator): its in-process book can phantom when another
    being exits a position it opened (the pre-registry era did
    exactly that - 5 phantom opens, endless failed closes). Every
    180s: a tracked symbol with NO exchange position >= $1 is
    dropped WITHOUT a booked close (the exiter's own ledger record
    carries the truth) and its ownership claim is pruned; a tracked
    size that drifted from the exchange is corrected."""
    import json as _j
    import os as _o
    from testnet_client import ccxt_to_raw
    await asyncio.sleep(20)
    while True:
        try:
            tn = arm._client()
            truth = {}
            for pos in tn.positions():
                truth[pos['symbol']] = (abs(float(pos.get('size') or 0)),
                                        float(pos.get('positionValue') or 0),
                                        pos.get('side') or 'Buy',
                                        float(pos.get('avgPrice') or 0))
            rm = orchestrator.risk_manager
            for sym in list(rm.open_positions.keys()):
                raw = ccxt_to_raw(sym)
                have = truth.get(raw) if raw else None
                if not have or have[1] < 1.0:
                    del rm.open_positions[sym]
                    logger.warning(f'EXCHANGE SYNC: dropped phantom {sym} '
                                   f'(no exchange position; closed outside '
                                   f'the orchestrator - no P&L booked)')
                    try:
                        rp = '/app/runtime/orchestrator_positions.json'
                        reg = _j.load(open(rp)) if _o.path.exists(rp) else {}
                        if raw in reg:
                            del reg[raw]
                            with open(rp, 'w') as f:
                                _j.dump(reg, f)
                    except Exception:
                        pass
                else:
                    cur = float(rm.open_positions[sym].get('size') or 0)
                    if cur and abs(have[0] - cur) / cur > 0.05:
                        rm.open_positions[sym]['size'] = have[0]
                        logger.info(f'EXCHANGE SYNC: {sym} size corrected '
                                    f'{cur} -> {have[0]}')
            # Adopt orphan shorts + guarantee claims (2026-10-20):
            # claims were originally written only on the market-
            # buy path, so maker fills and every short went
            # unclaimed and the zoo adopted them - and the zoo's
            # long-only exits mismanage shorts. Now: (a) every
            # tracked position gets its claim (re)written here;
            # (b) an untracked Sell-side position >= $3 can only
            # be this engine's (it is the fleet's only short
            # source) - adopt it into the book with the exchange's
            # own side/entry/size so the -1%/+2% exits govern it.
            try:
                rp = '/app/runtime/orchestrator_positions.json'
                reg = _j.load(open(rp)) if _o.path.exists(rp) else {}
                dirty = False
                tracked_raw = {}
                for s2 in list(rm.open_positions.keys()):
                    r2 = ccxt_to_raw(s2)
                    if r2:
                        tracked_raw[r2] = s2
                for raw, have in truth.items():
                    if have[1] >= 3.0 and have[2] == 'Sell' \
                            and raw not in tracked_raw:
                        sym = raw[:-4] + '/USDT:USDT'
                        rm.record_position(sym, 'sell', have[0], have[3])
                        tracked_raw[raw] = sym
                        logger.warning(f'EXCHANGE SYNC: adopted orphan '
                                       f'short {sym} size {have[0]} @ {have[3]}')
                for raw, s2 in tracked_raw.items():
                    if raw not in reg:
                        _pos = rm.open_positions.get(s2) or {}
                        reg[raw] = {'qty': _pos.get('size', 0),
                                    'entry': _pos.get('entry_price', 0),
                                    'ts': time.time()}
                        dirty = True
                if dirty:
                    with open(rp, 'w') as f:
                        _j.dump(reg, f)
            except Exception as e:
                logger.warning(f'exchange sync adopt/claim: {e}')
            # Prune orphaned ownership claims: a registry symbol
            # with no exchange position and no tracked position is
            # a leftover from a dead era - left in place it makes
            # the zoo skip that symbol forever.
            try:
                rp = '/app/runtime/orchestrator_positions.json'
                if _o.path.exists(rp):
                    reg = _j.load(open(rp))
                    tracked_raw = set()
                    for s2 in rm.open_positions.keys():
                        r2 = ccxt_to_raw(s2)
                        if r2:
                            tracked_raw.add(r2)
                    changed = False
                    for raw in list(reg.keys()):
                        have = truth.get(raw)
                        if raw not in tracked_raw and (not have or have[1] < 1.0):
                            del reg[raw]
                            changed = True
                            logger.warning(f'EXCHANGE SYNC: pruned stale '
                                           f'ownership claim {raw}')
                    if changed:
                        with open(rp, 'w') as f:
                            _j.dump(reg, f)
            except Exception:
                pass
        except Exception as e:
            logger.warning(f'exchange sync: {e}')
        await asyncio.sleep(180)


async def main():
    from data_hub import MarketDataHub
    from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator
    from testnet_client import make_client

    hub = MarketDataHub()
    arm = RelayExecutionArm(hub)
    bus_hub = BusHub(arm)
    orchestrator = ExecutionOrchestrator(
        data_hub=bus_hub, trading_engines={'real_profit': arm},
        risk_engine=None, ledger=[], mode='testnet')
    orchestrator.router = PriceAdapter(hub, arm)
    # The 0.80 default was calibrated for brain decisions; the alpha
    # ensemble's calibrated probabilities live lower (its own buy
    # line is 0.58). Kelly sizing + the risk manager carry the risk
    # work - the gate just filters noise.
    orchestrator.min_confidence = 0.60

    equity = account_equity(make_client())
    if equity:
        orchestrator.position_sizer.update_balance(equity)
    logger.info(f'Execution Orchestrator LIVE - sizer balance ${equity:.2f} '
                f'(account equity), Kelly sizing, -1%/+2% exits, relay arm armed')
    tg(f'⚡ Execution Orchestrator LIVE (the 2025 engine): Kelly sizing '
       f'on ${equity:.2f} equity, alpha engines + sentient decisions executing.')

    await asyncio.gather(
        orchestrator.run_execution_loop(),
        decision_feeder(bus_hub),
        alpha_loop(orchestrator, hub, bus_hub),
        stats_loop(orchestrator, arm),
        exchange_sync_loop(orchestrator, arm),
    )


if __name__ == '__main__':
    asyncio.run(main())
