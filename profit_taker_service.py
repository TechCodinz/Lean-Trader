#!/usr/bin/env python3
"""
LeanTrader AutoProfitTaker Service (2025 microservice architecture).

Runs as a standalone service (not in the orchestrator).
Watches Bybit testnet, adopts positions, closes at profit targets.

Targets: 0.5% micro / 0.3% quick / 1% normal / 3% swing
Stop: 1.5% | Time stop: 1 hour

Usage: python3 profit_taker_service.py
"""

import asyncio
import logging
import os
import sys

sys.path.insert(0, '/app')

from AUTO_PROFIT_TAKER import AutoProfitTaker
from REAL_PROFIT_BOT import REAL_PROFIT_BOT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PROFIT_TAKER_SERVICE')


class RelayExchange:
    """ccxt-shaped adapter over the host signing relay."""

    def __init__(self):
        import ccxt
        os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')
        from testnet_client import make_client, ccxt_to_raw
        self.tn = make_client()
        self._to_raw = ccxt_to_raw
        self.pub = ccxt.bybit({'enableRateLimit': True})
        self.pub.load_markets()

    @staticmethod
    def _ccxt_sym(raw):
        base = raw[:-4] if raw.endswith('USDT') else raw
        return f"{base}/USDT:USDT"

    def fetch_ticker(self, symbol):
        # TESTNET frame only: prices come from the relay's testnet tickers.
        # The original adapter read PUBLIC MAINNET tickers here, so every
        # PnL comparison mixed frames (phantom +/-20-40% swings) - the
        # 2026-10-21 frame lesson, applied to the exit manager.
        raw = self._to_raw(symbol)
        r = self.tn._req('GET', '/v5/market/tickers',
                         {'category': 'linear', 'symbol': raw})
        lst = (r or {}).get('list') or []
        last = float(lst[0]['lastPrice']) if lst else 0.0
        return {'last': last, 'symbol': symbol}

    def fetch_positions(self):
        out = []
        for p in self.tn.positions():
            qty = float(p.get('size') or 0)
            if qty == 0:
                continue
            if (p.get('side') or '').lower() == 'sell':
                qty = -qty
            out.append({
                'symbol': self._ccxt_sym(p['symbol']),
                'contracts': qty,
                'entryPrice': float(p.get('avgPrice') or 0),
            })
        return out

    def create_market_sell_order(self, symbol, size):
        raw = self._to_raw(symbol)
        # Touch close first (2026-10-22): a reduce-only limit
        # resting at the touch catches the depth flickers this
        # service's market closes have missed for a day on the
        # stale book - the funding rent. Same smart_close route
        # the sniper and orchestrator arms use; market fallback.
        try:
            from testnet_client import smart_close
            if smart_close(self.tn, raw, True, float(size), wait_s=30):
                return {'id': 'touch', 'orderId': 'touch',
                        'symbol': raw, 'filled': float(size)}
        except Exception:
            pass
        return self.tn.create_market_sell_reduce(raw, float(size))

    def create_market_buy_order(self, symbol, cost):
        # AutoProfitTaker passes quote cost for short closes.
        raw = self._to_raw(symbol)
        price = float(self.fetch_ticker(symbol)['last'])
        qty = float(cost) / price if price else 0
        try:
            from testnet_client import smart_close
            if qty > 0 and smart_close(self.tn, raw, False, qty,
                                       wait_s=30):
                return {'id': 'touch', 'orderId': 'touch',
                        'symbol': raw, 'filled': qty}
        except Exception:
            pass
        return self.tn.create_market_buy(raw, qty)


async def main():
    logger.info("🚀 Starting AutoProfitTaker Service (2025 microservice)")
    
    # Relay-backed exchange (ccxt testnet is WAF-blocked in-container)
    apt = AutoProfitTaker(RelayExchange(), None)
    logger.info("✅ AutoProfitTaker initialized via signing relay")
    
    # Initial sync
    n = await apt.sync_from_exchange()
    logger.info(f"📥 Initial sync: adopted {n} position(s)")
    
    cycle = 0
    while True:
        try:
            cycle += 1
            # Re-sync every 10 cycles (~5 min)
            if cycle >= 10:
                cycle = 0
                n = await apt.sync_from_exchange()
                if n > 0:
                    logger.info(f"📥 Re-sync: adopted {n} new position(s)")
            
            # Check and close
            closed = await apt.check_and_close_positions()
            if closed:
                logger.info(f"💰 Closed {len(closed)} position(s): {closed}")
            
        except Exception as e:
            logger.error(f"Loop error: {e}")
        
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
