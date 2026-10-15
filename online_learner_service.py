#!/usr/bin/env python3
"""
LeanTrader Online Learner Service (2025 microservice).

Online learning — learns from each trade in real-time.
Complements Evolution (deep) and Divine (batch ML) with online updates.

2025 original: online_learner.py (2025-08-29)
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from online_learner import OnlineLearner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ONLINE_LEARNER')


def main():
    logger.info("📚 Starting Online Learner Service (2025 microservice)")
    logger.info("   Real-time learning from each trade")
    
    learner = OnlineLearner()
    logger.info("✅ Online Learner initialized")
    
    # Keep alive — learns from trade outcomes in real-time
    try:
        while True:
            time.sleep(300)
            logger.info("📚 Online Learner heartbeat — learning active")
    except KeyboardInterrupt:
        logger.info("🛑 Online Learner stopped")


if __name__ == "__main__":
    main()
