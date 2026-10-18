#!/usr/bin/env python3
"""
LeanTrader Swarm Consciousness Service.

Runs the 2025 SwarmConsciousness (100 specialized agents: scalping, arbitrage,
trend, black swan, general) as its own process, in parallel with the zoo
trader and the continuous orchestrator. High-confidence swarm signals
(conf > 0.8, the swarm's own gate) become REAL testnet orders through the
host signing relay; sell signals close the swarm's own positions, and a
risk sweep enforces +2% / -1.5% / 10-minute exits.

The 2025 wrapper (patch/swarm_service.py) initialized the swarm but never
ran its consciousness loop - this service runs it.
"""
import asyncio
import hashlib
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
from ultra_swarm_consciousness import SwarmConsciousness

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s')
logger = logging.getLogger('SWARM')

SLICE_CAP = 15.0       # max notional per swarm position (USD)
MAX_CONCURRENT = 2     # swarm positions at once (zoo + orchestrator trade too)


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


class SwarmExecutor:
    """Turns swarm signals into real testnet positions via the relay."""

    def __init__(self, tn, pub_ex):
        self.tn = tn
        self.ex = pub_ex
        self.positions = {}          # raw -> {'qty', 'entry', 'ts', 'symbol'}
        self.cooldown_until = 0.0

    def _market_step_min(self, perp):
        mkt = self.ex.market(perp)
        step = float((mkt.get('precision') or {}).get('amount') or 0)
        minq = float(((mkt.get('limits') or {}).get('amount') or {}).get('min') or 0)
        return step, minq

    async def open_swarm(self, signal):
        if time.time() < self.cooldown_until:
            return None
        sym = signal.symbol                       # 'APT/USDT' style
        perp = sym + ':USDT'
        raw = ccxt_to_raw(perp)
        if not raw or raw in self.positions:
            return None
        if len(self.positions) >= MAX_CONCURRENT:
            if time.time() - getattr(self, '_cap_log_ts', 0) > 60:
                self._cap_log_ts = time.time()
                logger.info(f'swarm: at capacity ({MAX_CONCURRENT}) - holding {list(self.positions)}')
            return None
        try:
            t = await asyncio.to_thread(self.ex.fetch_ticker, perp)
            price = float(t.get('last') or 0)
        except Exception:
            return None
        if price <= 0:
            return None
        # Account-level conflict guard: never stack on an existing position
        try:
            poss = await asyncio.to_thread(self.tn.positions)
            if any(p.get('symbol') == raw and float(p.get('size') or 0) > 0
                   and float(p.get('positionValue') or 0) >= 1.0 for p in poss):
                if time.time() - getattr(self, '_held_log_ts', 0) > 60:
                    self._held_log_ts = time.time()
                    logger.info(f'swarm: {sym} already held by another being - skipping')
                return None
        except Exception:
            pass
        try:
            free = await asyncio.to_thread(self.tn.wallet_free_usdt)
            step, minq = await asyncio.to_thread(self._market_step_min, perp)
        except Exception as e:
            logger.warning(f'swarm open prep {sym}: {e}')
            return None
        notional = min(free * 2, SLICE_CAP)
        qty = quantize(notional / price, step)
        if minq and qty < minq:
            if minq * price <= notional:
                qty = minq
            else:
                if time.time() - getattr(self, '_minq_log_ts', 0) > 60:
                    self._minq_log_ts = time.time()
                    logger.info(f'swarm: {sym} min order ${minq * price:.2f} exceeds slice ${notional:.2f} - skipping')
                return None
        if qty <= 0:
            return None
        try:
            try:
                await asyncio.to_thread(self.tn.set_leverage, raw, 10)
            except Exception:
                pass
            await asyncio.to_thread(self.tn.create_market_buy, raw, qty_str(qty))
        except Exception as e:
            if '110007' in str(e):
                self.cooldown_until = time.time() + 60
                logger.info('swarm: margin busy (shared wallet) - backing off 60s')
            else:
                logger.warning(f'swarm BUY failed {sym}: {e}')
            return None
        self.positions[raw] = {'qty': qty, 'entry': price, 'ts': time.time(), 'symbol': sym}
        logger.info(f'SWARM REAL BUY {sym} qty {qty} @ {price:.4f} conf {signal.confidence:.2f}')
        tg(f'SWARM BUY {sym} qty {qty} @ ${price:.4f} (conf {signal.confidence:.2f})')
        return {'id': hashlib.md5(f"{signal.agent_id}_{signal.timestamp}".encode()).hexdigest()[:8],
                'symbol': sym, 'side': 'buy', 'price': price, 'qty': qty,
                'confidence': signal.confidence, 'timestamp': signal.timestamp,
                'agent_id': signal.agent_id, 'testnet': True, 'real': True}

    async def _close_raw(self, raw, reason):
        pos = self.positions.get(raw)
        if not pos:
            return False
        perp = pos['symbol'] + ':USDT'
        qty = pos['qty']
        try:
            step, _m = await asyncio.to_thread(self._market_step_min, perp)
            qty = quantize(qty, step) or qty
        except Exception:
            pass
        try:
            await asyncio.to_thread(self.tn.create_market_sell_reduce, raw, qty_str(qty))
        except Exception as e:
            logger.warning(f'swarm SELL failed {pos["symbol"]}: {e}')
            return False
        del self.positions[raw]
        try:
            t = await asyncio.to_thread(self.ex.fetch_ticker, perp)
            xp = float(t.get('last') or pos['entry'])
        except Exception:
            xp = pos['entry']
        pnl = (xp - pos['entry']) * pos['qty']
        logger.info(f'SWARM REAL SELL {pos["symbol"]} qty {qty} @ {xp} pnl ${pnl:+.4f} ({reason})')
        tg(f'SWARM SELL {pos["symbol"]} @ ${xp:.4f} pnl ${pnl:+.2f} ({reason})')
        return True

    async def close_swarm(self, symbol):
        raw = ccxt_to_raw(symbol + ':USDT')
        if raw and raw in self.positions:
            return await self._close_raw(raw, 'sell signal')
        return False

    async def sweep(self):
        """Risk exits for swarm positions: +2% / -1.5% / 10 minutes."""
        while True:
            try:
                for raw, pos in list(self.positions.items()):
                    perp = pos['symbol'] + ':USDT'
                    try:
                        t = await asyncio.to_thread(self.ex.fetch_ticker, perp)
                        cur = float(t.get('last') or 0)
                    except Exception:
                        cur = 0
                    if cur:
                        pct = (cur - pos['entry']) / pos['entry']
                        if pct >= 0.02:
                            await self._close_raw(raw, 'take profit +2%')
                            continue
                        if pct <= -0.015:
                            await self._close_raw(raw, 'stop -1.5%')
                            continue
                    if time.time() - pos['ts'] > 600:
                        await self._close_raw(raw, 'timeout 10m')
            except Exception as e:
                logger.warning(f'swarm sweep: {e}')
            await asyncio.sleep(20)


async def main():
    tn = make_client()
    free = tn.wallet_free_usdt()
    logger.info(f'SWARM SERVICE: testnet wallet = {free:.2f} USDT')

    router = ExchangeRouter()
    universe = Universe(router)
    core = UltraCore(router, universe)
    risk = RiskEngine()
    swarm = SwarmConsciousness(core, risk)

    # Deploy on the adaptive universe (2025 design), majors as fallback
    try:
        from ADAPTIVE_PAIR_SELECTOR import AdaptivePairSelector
        pairs = AdaptivePairSelector().get_active_pairs(balance=free)
        if pairs:
            swarm.symbols = pairs
    except Exception as e:
        logger.warning(f'adaptive pairs unavailable ({e}); keeping {swarm.symbols}')
    logger.info(f'SWARM SERVICE: {swarm.agent_count} agents on {len(swarm.symbols)} pairs: {swarm.symbols}')

    pub = ccxt.bybit()
    pub.load_markets()
    swarm.executor = SwarmExecutor(tn, pub)
    logger.info('SWARM SERVICE: consciousness live with real execution (relay)')
    tg(f'SWARM LIVE - {swarm.agent_count} agents on {len(swarm.symbols)} pairs (wallet ${free:.2f})')

    await asyncio.gather(
        swarm.start_swarm_consciousness(),
        swarm.executor.sweep(),
    )


if __name__ == '__main__':
    asyncio.run(main())
