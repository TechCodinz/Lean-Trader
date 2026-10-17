#!/usr/bin/env python3
"""
LeanTrader Moon Spotter Service (2025 microservice).

Spots fast-moving pairs and snipes opportunities.
The dynamic fast-mover system.

2025 original: ultra_moon_spotter.py
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from ultra_moon_spotter import MicroMoonSpotter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MOON_SPOTTER')


def main():
    logger.info("🌙 Starting Moon Spotter Service (2025 microservice)")
    logger.info("   Spotting fast-moving pairs and sniping opportunities")
    
    spotter = MicroMoonSpotter()
    logger.info("✅ Moon Spotter initialized")
    
    # Keep alive — spots moons continuously
    try:
        while True:
            time.sleep(300)
            logger.info("🌙 Moon Spotter heartbeat — scanning for moons")
    except KeyboardInterrupt:
        logger.info("🛑 Moon Spotter stopped")


if __name__ == "__main__":
    main()
