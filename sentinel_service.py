#!/usr/bin/env python3
"""
SENTINEL SERVICE - the fluid-mechanics sentinel as its own being.

SentinelBrillianceSystem (ultra_fluid_mechanics.py) is a monitoring /
market-physics system (flow, turbulence, pressure fields). Its own file's
main() uses a stale UltraCore(mode='paper', ...) constructor, so this
service builds the core the live way (router/universe) and hands it to
the system's own integrate helper. Monitor-only: it places no orders.
"""
import asyncio
import logging
import os
import urllib.request
import json as _json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger('SENTINEL')

from router import ExchangeRouter
from universe import Universe
from ultra_core import UltraCore
from risk_engine import RiskEngine


def tg(msg):
    tok = os.environ.get('TELEGRAM_BOT_TOKEN')
    cid = os.environ.get('TELEGRAM_CHAT_ID')
    if not tok or not cid:
        return
    try:
        data = _json.dumps({'chat_id': cid, 'text': msg}).encode()
        req = urllib.request.Request(
            f'https://api.telegram.org/bot{tok}/sendMessage',
            data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        pass


async def main():
    router = ExchangeRouter()
    universe = Universe(router)
    core = UltraCore(router, universe)
    risk = RiskEngine()

    from ultra_fluid_mechanics import integrate_fluid_mechanics
    system = integrate_fluid_mechanics(core, risk)
    logger.info('SENTINEL SERVICE: fluid-mechanics sentinel live (monitor-only)')
    tg('SENTINEL LIVE - fluid mechanics brilliance monitoring the being')
    await system.start_sentinel_brilliance()


if __name__ == '__main__':
    asyncio.run(main())
