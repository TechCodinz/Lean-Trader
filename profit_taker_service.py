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


async def main():
    logger.info("🚀 Starting AutoProfitTaker Service (2025 microservice)")
    
    # Use RPB's Bybit testnet client
    rpb = REAL_PROFIT_BOT(mode='testnet')
    apt = AutoProfitTaker(rpb.gate, None)
    logger.info("✅ AutoProfitTaker initialized with Bybit testnet")
    
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
