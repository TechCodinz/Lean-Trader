#!/usr/bin/env python3
"""
LeanTrader Dynamic Market Scanner Service (2025 microservice).

Continuously scans exchanges for trending pairs, high-volume opportunities.
Publishes signals for the adaptive pair selector.

2025 original: DYNAMIC_MARKET_SCANNER.py (2025-10-16)
"""

import asyncio
import logging
import sys

sys.path.insert(0, '/app')

from DYNAMIC_MARKET_SCANNER import DynamicMarketScanner
from REAL_PROFIT_BOT import REAL_PROFIT_BOT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SCANNER_SERVICE')


async def main():
    logger.info("🔍 Starting Dynamic Market Scanner Service (2025 microservice)")
    
    # Use Bybit testnet (working keys)
    rpb = REAL_PROFIT_BOT(mode='testnet')
    exchanges = {'bybit_testnet': rpb.gate}
    
    scanner = DynamicMarketScanner(exchanges=exchanges, data_hub=None)
    logger.info("✅ Scanner initialized with Bybit testnet")
    
    # Run continuous scanning
    await scanner.run_continuous_scanning()


if __name__ == "__main__":
    asyncio.run(main())
