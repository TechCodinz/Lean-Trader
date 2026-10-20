#!/usr/bin/env python3
"""
LeanTrader Continuous Propagation Service.

Runs the 2025 UltraContinuousTradingOrchestrator as its own process, in
parallel with the zoo trader: 1-second-cadence multi-timeframe opportunity
scanning (scalping / momentum / mean-reversion / breakout / arbitrage
detectors) with REAL testnet execution through the host signing relay.

While one system waits, the ready one propagates - this is that layer.
Execution discipline mirrors the zoo: lot-step quantized quantities,
per-position notional cap, account-level conflict guard (never opens a
symbol the exchange already holds a position on).
"""
import asyncio
import logging
import os
import sys
import time
import urllib.request
import json as _json

sys.path.insert(0, '/app')
os.chdir('/app')

import ccxt

from testnet_client import make_client, ccxt_to_raw, qty_str, quantize
from router import ExchangeRouter
from universe import Universe
from ultra_core import UltraCore
from risk_engine import RiskEngine
from ultra_continuous_trading import UltraContinuousTradingOrchestrator

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s')
logger = logging.getLogger('CONT')

SLICE_CAP = 25.0       # max notional per orchestrator position (USD)
MAX_CONCURRENT = 4     # orchestrator positions at once (zoo trades in parallel)

def _alloc(being, key, default):
    """Live allocation from the governor (defaults on any problem)."""
    try:
        import allocation
        return allocation.get(being).get(key, default)
    except Exception:
        return default



def tg(msg):
    tok = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    cid = os.environ.get('TELEGRAM_CHAT_ID', '')
    if not tok or not cid:
        return
    try:
        data = _json.dumps({'chat_id': cid, 'text': msg}).encode()
        rq = urllib.request.Request(f'https://api.telegram.org/bot{tok}/sendMessage',
                                    data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(rq, timeout=10).read()
    except Exception:
        pass


class RelayExecutor:
    """Turns orchestrator sessions into real testnet positions via the relay."""

    def __init__(self, tn, pub_ex):
        self.tn = tn
        self.ex = pub_ex
        self.open_raw = set()
        self.cooldown_until = 0.0

    def _market_step_min(self, perp):
        mkt = self.ex.market(perp)
        step = float((mkt.get('precision') or {}).get('amount') or 0)
        minq = float(((mkt.get('limits') or {}).get('amount') or {}).get('min') or 0)
        return step, minq

    async def open_position(self, session, opportunity):
        if time.time() < self.cooldown_until:
            return False
        sym = opportunity['symbol']                 # 'SOL/USDT' style
        perp = sym + ':USDT'
        raw = ccxt_to_raw(perp)
        if not raw:
            logger.info(f'cont skip {sym}: not testnet-tradable')
            return False
        if raw in self.open_raw:
            return False
        if _alloc('continuous', 'mode', 'real') != 'real':
            return False
        if len(self.open_raw) >= _alloc('continuous', 'max_concurrent', MAX_CONCURRENT):
            return False
        price = float(opportunity.get('entry_price') or 0)
        if price <= 0:
            return False
        # Account-level conflict guard: never stack on an existing position
        try:
            poss = await asyncio.to_thread(self.tn.positions)
            if any(p.get('symbol') == raw and float(p.get('size') or 0) > 0
                   and float(p.get('positionValue') or 0) >= 1.0 for p in poss):
                return False
        except Exception:
            pass
        try:
            free = await asyncio.to_thread(self.tn.wallet_free_usdt)
            step, minq = await asyncio.to_thread(self._market_step_min, perp)
        except Exception as e:
            logger.warning(f'cont open prep {sym}: {e}')
            return False
        notional = min(free * 2, _alloc('continuous', 'slice_usd', SLICE_CAP))
        qty = notional / price
        qty = quantize(qty, step)
        if minq and qty < minq:
            if minq * price <= notional:
                qty = minq
            else:
                return False        # instrument minimum exceeds the slice cap
        if qty <= 0:
            return False
        try:
            try:
                await asyncio.to_thread(self.tn.set_leverage, raw, 10)
            except Exception:
                pass
            await asyncio.to_thread(self.tn.create_market_buy, raw, qty_str(qty))
        except Exception as e:
            if '110007' in str(e):
                self.cooldown_until = time.time() + 60
                logger.info('cont: margin busy (zoo positions using the wallet) - backing off 60s')
            else:
                logger.warning(f'cont BUY failed {sym}: {e}')
            return False
        session.entry_price = price
        session.qty = qty
        self.open_raw.add(raw)
        logger.info(f'CONT TESTNET BUY {sym} ({raw}) qty {qty} @ {price} [{opportunity.get("strategy")}/{opportunity.get("timeframe")}]')
        tg(f'CONT BUY {sym} qty {qty} @ ${price:.4f} [{opportunity.get("strategy")}]')
        return True

    async def close_position(self, session):
        perp = session.symbol + ':USDT'
        raw = ccxt_to_raw(perp)
        qty = session.qty
        try:
            step, _minq = await asyncio.to_thread(self._market_step_min, perp)
            qty = quantize(qty, step) or qty
        except Exception:
            pass
        await asyncio.to_thread(self.tn.create_market_sell_reduce, raw, qty_str(qty))
        self.open_raw.discard(raw)
        try:
            t = await asyncio.to_thread(self.ex.fetch_ticker, perp)
            exit_price = float(t.get('last') or session.entry_price)
        except Exception:
            exit_price = session.entry_price
        logger.info(f'CONT TESTNET SELL {session.symbol} ({raw}) qty {qty} @ {exit_price}')
        tg(f'CONT SELL {session.symbol} qty {qty} @ ${exit_price:.4f}')
        return exit_price


async def main():
    tn = make_client()
    free = tn.wallet_free_usdt()
    logger.info(f'CONTINUOUS SERVICE: testnet wallet = {free:.2f} USDT')

    router = ExchangeRouter()
    universe = Universe(router)
    core = UltraCore(router, universe)
    risk = RiskEngine()
    orch = UltraContinuousTradingOrchestrator(core, risk)
    # Seed from EQUITY, never from momentary available: available can
    # be ~$0 while positions are open, and a sub-$5 seed trips the
    # orchestrator's own minimum-balance gate permanently.
    _eq = tn.wallet_equity_usdt() or free
    orch.daily_balance = _eq
    orch.total_balance = _eq
    pub = ccxt.bybit()
    pub.load_markets()
    orch.executor = RelayExecutor(tn, pub)
    logger.info('CONTINUOUS SERVICE: orchestrator live with real execution (relay)')
    tg(f'CONTINUOUS SERVICE LIVE - orchestrator propagating (wallet ${free:.2f})')

    nov = None
    try:
        from november_growth_strategy import NovemberGrowthStrategy, NovemberTarget
        from datetime import datetime, timedelta
        _t0 = datetime.now()
        nov = NovemberGrowthStrategy(core, risk, target=NovemberTarget(
            start_balance=free, target_balance=150.0, stretch_target=300.0,
            start_date=_t0.strftime('%Y-%m-%d'),
            target_date=(_t0 + timedelta(days=60)).strftime('%Y-%m-%d'),
            days_remaining=60))
        nov.continuous_trading = orch
        nov.current_balance = free
        logger.info(f'NOVEMBER GROWTH: governor attached - ${free:.2f} -> $150 in 60d, phase {nov.target.phases[0].phase_name}')
        tg(f'NOVEMBER GROWTH governor live - ${free:.2f} -> $150 target (60d)')
    except Exception as e:
        nov = None
        logger.warning(f'NOVEMBER GROWTH unavailable: {e}')

    async def _balance_sync():
        # ROOT CAUSE of the zero-trade era (found 2026-10-20): the
        # orchestrator and the November grower read their balance
        # ONCE at boot. This instance booted when available was
        # $0.64, so _can_trade's $5 minimum refused every trade for
        # 16h while equity sat at $40 - and the grower "thought"
        # about a $0.64 balance. Sync both to TRUE equity forever.
        last = -1.0
        while True:
            try:
                eq = tn.wallet_equity_usdt()
                if eq and eq > 0:
                    orch.total_balance = eq
                    orch.daily_balance = eq
                    if nov is not None:
                        nov.current_balance = eq
                    if abs(eq - last) > 0.5:
                        logger.info(f'BALANCE SYNC: orchestrator + grower now on true equity ${eq:.2f}')
                        last = eq
            except Exception as e:
                logger.warning(f'balance sync: {e}')
            await asyncio.sleep(120)

    tasks = [
        asyncio.create_task(_balance_sync()),
        asyncio.create_task(orch._continuous_trading_loop()),
        asyncio.create_task(orch._monitor_all_positions()),
        asyncio.create_task(orch._manage_compound_growth()),
        asyncio.create_task(orch._track_performance()),
        asyncio.create_task(orch._daily_reset()),
    ]
    if nov is not None:
        tasks += [
            asyncio.create_task(nov._manage_growth_phases()),
            asyncio.create_task(nov._monitor_target_progress()),
            asyncio.create_task(nov._optimize_strategies()),
            asyncio.create_task(nov._track_performance()),
            asyncio.create_task(nov._daily_optimization()),
        ]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
