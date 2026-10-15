#!/usr/bin/env python3
"""
LeanTrader Evolution Engine Service (2025 microservice architecture).

The learning system — trains on trade outcomes, evolves strategies,
spawns new models. Runs standalone (not in the broken orchestrator).

Usage: python3 evolution_service.py
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from EVOLUTION_ENGINE import ULTIMATE_EVOLUTION_ENGINE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EVOLUTION_SERVICE')


def main():
    logger.info("🧬 Starting Evolution Engine Service (2025 microservice)")
    
    engine = ULTIMATE_EVOLUTION_ENGINE(data_hub=None)
    logger.info("✅ Evolution Engine initialized")
    
    engine.start_evolution_cycle()
    logger.info("✅ Evolution cycle started - learning active")
    
    # Keep alive (threads are daemons, main must not exit)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("🛑 Evolution service stopped")


if __name__ == "__main__":
    main()
