#!/usr/bin/env python3
"""
LeanTrader Risk Engine Service (2025 microservice).

The risk manager — protects the trading being from excessive risk.
Monitors positions, enforces limits, manages exposure.

2025 original: risk_engine.py (2025-08-29)
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from risk_engine import RiskEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RISK_ENGINE')


def main():
    logger.info("🛡️ Starting Risk Engine Service (2025 microservice)")
    logger.info("   Protecting the trading being from excessive risk")
    
    engine = RiskEngine()
    logger.info("✅ Risk Engine initialized")
    logger.info("   Monitoring positions and enforcing limits")
    
    # Keep alive — the risk engine monitors continuously
    try:
        while True:
            time.sleep(60)
            logger.info("🛡️ Risk Engine heartbeat — monitoring active")
    except KeyboardInterrupt:
        logger.info("🛑 Risk Engine stopped")


if __name__ == "__main__":
    main()
