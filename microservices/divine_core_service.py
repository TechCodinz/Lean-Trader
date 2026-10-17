#!/usr/bin/env python3
"""
LeanTrader Divine Intelligence Core Service (2025 microservice).

Advanced AI that continuously learns and evolves trading strategies.
Uses RandomForest, GradientBoosting, MLP — traditional ML complement
to the Evolution Engine's deep learning.

2025 original: divine_intelligence_core.py (2025-09-29)
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from divine_intelligence_core import DivineIntelligenceCore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DIVINE_CORE')


def main():
    logger.info("✨ Starting Divine Intelligence Core Service (2025 microservice)")
    logger.info("   Advanced AI — continuous learning with RandomForest/GBM/MLP")
    
    core = DivineIntelligenceCore()
    logger.info("✅ Divine Core initialized")
    
    # Keep alive — the core learns continuously
    try:
        while True:
            time.sleep(300)
            logger.info("✨ Divine Core heartbeat — learning active")
    except KeyboardInterrupt:
        logger.info("🛑 Divine Core stopped")


if __name__ == "__main__":
    main()
