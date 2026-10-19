#!/usr/bin/env python3
"""
PROFIT TAKER SHADOW TRIAL - the fleet exit manager, measured safely.

Peters' design: try the beings separately to learn which is profitable.
The fleet profit_taker_service is an exit manager that adopts exchange
positions and closes them at its own targets - but running it live
would race the zoo's internal exits on the same positions (double
closer). So it runs here in SHADOW mode:

- Same RelayExchange, same AutoProfitTaker, same sync + check loop.
- Order methods are replaced with recorders that capture the would-be
  exit price at the decision instant; per-position hypothetical P&L is
  computed exactly ((exit-entry) x size for longs) and written to the
  capacity ledger as being='profit_taker_shadow'.
- NO real orders are ever placed by this process.

Compare against the internal managers' actual realized exits on the
same positions in being_ledger to learn whose exits extract more.
"""
import asyncio
import logging
import os

os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - PT_SHADOW - %(message)s')
logger = logging.getLogger('PT_SHADOW')

from profit_taker_service import RelayExchange
from AUTO_PROFIT_TAKER import AutoProfitTaker
import being_ledger


class ShadowExchange(RelayExchange):
    """RelayExchange with order placement replaced by recording."""

    def __init__(self):
        super().__init__()
        self.shadow_exits = {}   # symbol -> {'price': float, 'qty': float}

    def create_market_sell_order(self, symbol, size):
        price = float(self.fetch_ticker(symbol)['last'])
        self.shadow_exits[symbol] = {'price': price, 'qty': float(size)}
        logger.info(f'SHADOW CLOSE (sell) {symbol} qty {size} @ {price}')
        return {'shadow': True, 'symbol': symbol, 'size': size}

    def create_market_buy_order(self, symbol, cost):
        price = float(self.fetch_ticker(symbol)['last'])
        qty = float(cost) / price if price else 0
        self.shadow_exits[symbol] = {'price': price, 'qty': qty}
        logger.info(f'SHADOW CLOSE (buy) {symbol} qty {qty:.4f} @ {price}')
        return {'shadow': True, 'symbol': symbol, 'cost': cost}


async def main():
    ex = ShadowExchange()
    apt = AutoProfitTaker(ex, None)
    n = await apt.sync_from_exchange()
    logger.info(f'shadow sync: adopted {n} position(s)')
    tracked = dict(apt.open_positions)
    cycle = 0
    while True:
        try:
            cycle += 1
            if cycle >= 10:
                cycle = 0
                await apt.sync_from_exchange()
                for k, v in apt.open_positions.items():
                    tracked.setdefault(k, v)
            before = {k: dict(v) for k, v in apt.open_positions.items()}
            await apt.check_and_close_positions()
            for sym in before.keys() - set(apt.open_positions.keys()):
                pos = before[sym]
                exinfo = ex.shadow_exits.pop(sym, None)
                if exinfo is None:
                    continue
                entry = float(pos['entry_price'])
                size = float(pos['size'])
                xp = exinfo['price']
                if (pos.get('side') or 'buy').lower() == 'buy':
                    pnl = (xp - entry) * size
                else:
                    pnl = (entry - xp) * size
                being_ledger.record_close(
                    'profit_taker_shadow', sym, pnl, real=False,
                    meta={'shadow': True, 'entry': entry, 'exit': xp})
                logger.info(f'SHADOW RESULT {sym}: pnl ${pnl:+.4f} '
                            f'(entry {entry} -> {xp})')
                tracked.pop(sym, None)
            tracked.update(apt.open_positions)
        except Exception as e:
            logger.error(f'shadow loop: {e}')
        await asyncio.sleep(30)


if __name__ == '__main__':
    asyncio.run(main())
