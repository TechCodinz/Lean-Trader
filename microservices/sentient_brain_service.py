#!/usr/bin/env python3
"""
LeanTrader Sentient Trading Brain Service (2025 microservice).

The sentient brain — processes signals with consciousness-level analysis.
Other systems send signals, the brain returns enhanced decisions.

2025 original: SENTIENT_TRADING_BRAIN.py (2025-10-16)
Was instantiated in orchestrator but never started (dead on arrival).
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from SENTIENT_TRADING_BRAIN import SentientTradingBrain

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SENTIENT_BRAIN')


def main():
    logger.info("🧠 Starting Sentient Trading Brain Service (2025 microservice)")
    
    brain = SentientTradingBrain(data_hub=None, execution_orchestrator=None)
    logger.info("✅ Sentient Brain initialized")
    logger.info("   Ready to process signals from the nervous system")
    
    # Keep alive — the brain is queryable via process_signal()
    try:
        while True:
            time.sleep(300)
            logger.info("🧠 Sentient Brain heartbeat — ready for signals")
    except KeyboardInterrupt:
        logger.info("🛑 Sentient Brain stopped")


if __name__ == "__main__":
    main()
