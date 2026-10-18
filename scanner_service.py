#!/usr/bin/env python3
"""
SCANNER SERVICE - the multi-platform scanner as its own being.

UltraMultiPlatformScanner (ultra_multi_platform_scanner.py) sweeps CEX,
DEX and DeFi venues for PlatformOpportunities. Its own file's main() uses
a stale UltraCore(mode='paper', ...) constructor, so this service builds
the core the live way (router/universe) and hands it to the scanner's own
integrate helper. Discovery-only for now: it places no orders; its
opportunities are logged for the other beings (and a later engine_hot
bridge) to act on.
"""
import asyncio
import logging
import os
import urllib.request
import json as _json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger('SCANNER')

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

    from ultra_multi_platform_scanner import integrate_multi_platform_scanner
    scanner = integrate_multi_platform_scanner(core, risk)
    logger.info('SCANNER SERVICE: multi-platform scanner live (discovery-only)')
    tg('SCANNER LIVE - sweeping CEX/DEX/DeFi for opportunities')
    await scanner.start_multi_platform_scanning()


if __name__ == '__main__':
    asyncio.run(main())
