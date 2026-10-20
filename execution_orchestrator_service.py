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
        if signal != 'BUY':
            return None  # long-only
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
            res = tn.create_market_buy(raw, qty_str(qty))
            if isinstance(res, dict) and res.get('orderId'):
                logger.info(f'⚡ REAL BUY {raw} qty {qty} @ {price}')
                tg(f'⚡ Orchestrator BUY {raw} qty {qty} @ {price}')
                # Claim ownership: the zoo's reconcile must not adopt
                # (and exit) the compounding engine's positions -
                # on 2026-10-20 it exited all five of them under zoo
                # rules and left this book clogged with ghosts.
                try:
                    import json as _jj
                    _own = {}
                    try:
                        _own = _jj.load(open('/app/runtime/orchestrator_positions.json'))
                    except Exception:
                        pass
                    _own[raw] = {'qty': qty, 'entry': float(price),
                                 'ts': time.time()}
                    with open('/app/runtime/orchestrator_positions.json', 'w') as _f:
                        _jj.dump(_own, _f)
                except Exception:
                    pass
                return {'symbol': symbol, 'side': 'buy', 'amount': qty,
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
        if side != 'buy':
            return True  # nothing real was opened for shorts
        _raw_cp = symbol.split('/')[0] + 'USDT'
        try:
            import json as _jj
            _own = _jj.load(open('/app/runtime/orchestrator_positions.json'))
            if _raw_cp in _own:
                _own.pop(_raw_cp, None)
                with open('/app/runtime/orchestrator_positions.json', 'w') as _f:
                    _jj.dump(_own, _f)
        except Exception:
            pass
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
            for _ in range(3):
                res = tn.create_market_sell_reduce(raw, qty_str(qty))
                if isinstance(res, dict) and res.get('orderId'):
                    logger.info(f'⚡ REAL CLOSE {raw} qty {qty}')
                    return True
            logger.error(f'arm close failed {raw}: {res}')
            return False
        except Exception as e:
            logger.error(f'arm close {symbol}: {e}')
            return False


class PriceAdapter:
    """orchestrator.router: async fetch_ticker over the hub client."""

    def __init__(self, hub):
        self.hub = hub

    async def fetch_ticker(self, symbol):
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
                    for p in (json.load(f).get('pairs') or [])[:6]:
                        s = p.replace(':USDT', '')
                        if s not in pairs:
                            pairs.append(s)
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
            session_now = sessions.get_current_session()
            frames = [('15m', 40 * 3600, 160), ('1h', 130 * 3600, 120)]
            for pair in pairs:
                for tf, span, limit in frames:
                    try:
                        since = int((time.time() - span) * 1000)
                        rows = hub.ex.fetch_ohlcv(pair + ':USDT', tf, since, limit)
                        if not rows or len(rows) < 60:
                            continue
                        df = pd.DataFrame(rows, columns=['ts', 'open', 'high',
                                                         'low', 'close', 'vol'])
                        dec = router.pick(df, pair, tf)
                        if dec is not None and dec.side == 'buy':
                            # Peters' session organ: confidence (and
                            # through Kelly, size) scales by session
                            sess, mult = sessions.get_session_multiplier(pair)
                            conf = min(0.98, float(dec.prob) * mult)
                            logger.info(f'📡 alpha_router[{tf}]: {pair} BUY '
                                        f'p={dec.prob:.2f} session {sess} x{mult:.2f} '
                                        f'-> conf {conf:.2f}')
                            await bus_hub.alert_queue.put({
                                'signal': {'symbol': pair,
                                           'data': {'symbol': pair,
                                                    'price': float(df['close'].iloc[-1])}},
                                'action': 'buy',
                                'confidence': conf,
                            })
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f'alpha loop: {e}')
        await asyncio.sleep(60)


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
    orchestrator.router = PriceAdapter(hub)
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
    )


if __name__ == '__main__':
    asyncio.run(main())
