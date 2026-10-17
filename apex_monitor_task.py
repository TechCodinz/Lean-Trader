#!/usr/bin/env python3
"""
Apex Balance Monitor Task - runs in the async runner.

Monitors balance and auto-adjusts tiers.
"""
import asyncio
import logging
import sys
sys.path.insert(0, '/app')

from auto_adaptive_apex import AutoAdaptiveApex
import ccxt

logger = logging.getLogger('APEX_MONITOR')

async def apex_monitor_task():
    """Run the Apex balance monitor loop."""
    logger.info("Starting Apex Balance Monitor")
    ex = ccxt.bybit({'enableRateLimit': True})
    ex.set_sandbox_mode(True)
    
    apex = AutoAdaptiveApex(ex)
    
    # Run the monitor (this is the async loop from Apex)
    await apex.run_auto_balance_monitor()

if __name__ == '__main__':
    asyncio.run(apex_monitor_task())
