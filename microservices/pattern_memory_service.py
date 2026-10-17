#!/usr/bin/env python3
"""
LeanTrader Pattern Memory Service (2025 microservice).

Stores and recalls trading patterns for the learning systems.
The memory bank of the trading being.

2025 original: pattern_memory.py (2025-08-29)
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from pattern_memory import PatternMemory

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PATTERN_MEMORY')


def main():
    logger.info("🧠 Starting Pattern Memory Service (2025 microservice)")
    logger.info("   Storing patterns for the learning systems")
    
    memory = PatternMemory()
    logger.info("✅ Pattern Memory initialized")
    
    # Keep alive — stores patterns continuously
    try:
        while True:
            time.sleep(300)
            logger.info("🧠 Pattern Memory heartbeat — storing patterns")
    except KeyboardInterrupt:
        logger.info("🛑 Pattern Memory stopped")


if __name__ == "__main__":
    main()
