#!/usr/bin/env python3
"""
LeanTrader Paper Broker Service (2025 microservice).

Paper trading — trades pairs not available on testnet.
The being learns from paper trades to refine memory.

2025 original: paper_broker.py (2025-08-29)
User design: paper-trade pairs unavailable on testnet for learning.
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from paper_broker import PaperBroker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PAPER_BROKER')


def main():
    logger.info("📝 Starting Paper Broker Service (2025 microservice)")
    logger.info("   Paper-trading pairs not on testnet for learning")
    
    broker = PaperBroker()
    logger.info("✅ Paper Broker initialized")
    
    # Keep alive — paper trades execute on demand
    try:
        while True:
            time.sleep(300)
            logger.info("📝 Paper Broker heartbeat — ready for paper trades")
    except KeyboardInterrupt:
        logger.info("🛑 Paper Broker stopped")


if __name__ == "__main__":
    main()
