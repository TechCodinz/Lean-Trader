#!/usr/bin/env python3
"""
MASTER APEX SERVICE v2 - the 2025 MasterOrchestrator, actually running.

The 2026 wrapper constructed the Master and heartbeated - it never
called initialize or started anything. v2:
- initialize_all() brings up the 27 subsystems (21+ alive after the
  2026-10-19 signature repairs; the rest fail honestly, logged).
- Starts the engines' OWN loops, as the 2025 design intended:
  the UltraScalpingEngine (start_scalping) - now with a real relay
  execution core grafted into its trade points, governed by
  allocation['master'] and recorded in the capacity ledger.
- Oversight loop: performance summaries + real position counts.

Not started, deliberately:
- Arbitrage engine loop: real cross-exchange arbitrage needs a
  second funded exchange; its signals already feed the zoo harvest.
- Moon system run_forever: its AutoSniper is a DEX/web3 actor (no
  wallet configured); its spotter already feeds the zoo harvest.
- The Master's own main_loop: its per-cycle engine calls target an
  API the engines never had (more 2026 drift) - oversight lives
  here instead until that loop is repaired.
"""
import asyncio
import logging
import os
import time
import urllib.parse
import urllib.request

os.environ.setdefault('TESTNET_RELAY', 'http://172.17.0.1:18099')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - MASTER_APEX - %(message)s')
logger = logging.getLogger('MASTER_APEX')


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


async def main():
    from MASTER_ORCHESTRATOR import MasterOrchestrator
    master = MasterOrchestrator(mode='testnet')
    await master.initialize_all()
    _attrs = [k for k in vars(master) if k not in ('mode', 'is_running')]
    alive = [k for k in _attrs if getattr(master, k) is not None]
    logger.info(f'Master initialized: {len(alive)}/{len(_attrs)} subsystems alive: {alive}')
    tg(f'👑 Master Orchestrator online: {len(alive)}/{len(_attrs)} systems alive. '
       f'Scalping engine live on testnet (allocation-governed).')

    tasks = []
    eng = master.scalping_engine
    if eng is not None:
        tasks.append(asyncio.create_task(eng.start_scalping()))
        logger.info('UltraScalpingEngine loop started (real execution grafted)')
    else:
        logger.error('Scalping engine dead - Master has no live engine')

    # Oversight: report the scalping engine's own performance summary
    while True:
        await asyncio.sleep(300)
        try:
            if eng is not None:
                summ = eng.get_performance_summary()
                real_open = sum(1 for sg in eng.active_positions.values()
                                if getattr(sg, 'real_qty', None))
                logger.info(f'oversight: {summ} | real open: {real_open}')
        except Exception as e:
            logger.warning(f'oversight: {e}')


if __name__ == '__main__':
    asyncio.run(main())
