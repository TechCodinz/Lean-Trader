#!/usr/bin/env python3
"""
LeanTrader HiveMind Service (2025 microservice).

The collective intelligence — aggregates decisions from multiple
strategies and timeframes into a unified hive decision.

Uses the Strategy Brain (7 alpha strategies) for signals.

2025 original: hivemind.py (2025-08-29)
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from hivemind import HiveCoordinator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HIVEMIND')


def main():
    logger.info("🐝 Starting HiveMind Service (2025 microservice)")
    logger.info("   Collective intelligence — aggregating hive decisions")
    
    coordinator = HiveCoordinator(timeframes=['1m', '5m', '15m', '1h'])
    logger.info("✅ Hive Coordinator initialized")
    logger.info("   Ready to aggregate signals from the nervous system")
    
    # Keep alive — the coordinator aggregates on demand
    try:
        while True:
            time.sleep(300)
            logger.info("🐝 HiveMind heartbeat — collective ready")
    except KeyboardInterrupt:
        logger.info("🛑 HiveMind stopped")


if __name__ == "__main__":
    main()
