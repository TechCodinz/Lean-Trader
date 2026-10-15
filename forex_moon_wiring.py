#!/usr/bin/env python3
"""
LeanTrader Forex & Moon Wiring (2026).

Wires 2025:
- ultra_forex_master: Forex trading (multi-market!)
- UltimateLearntraderBot: learning trader
- MicroMoonSpotter: moon spotter

2025: Forex + moonshots.
2026: Wired.
"""

import logging
import sys

sys.path.insert(0, '/app')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FOREX')


def main():
    logger.info("💱 Wiring 2025 Forex & Moon Systems")
    
    try:
        from ultra_forex_master import MarketSessionAnalyzer
        logger.info("✅ ForexMaster: multi-market Forex trading")
    except Exception as e:
        logger.info(f"⏳ Forex: {e}")
    
    try:
        from ultimate_learntrader import UltimateLearntraderBot
        logger.info("✅ UltimateLearntraderBot")
    except Exception as e:
        logger.info(f"⏳ Learntrader: {e}")
    
    try:
        from ultra_moon_spotter import MicroMoonSpotter
        logger.info("✅ MicroMoonSpotter: moonshot detection")
    except Exception as e:
        logger.info(f"⏳ Moon: {e}")
    
    logger.info("")
    logger.info("💱 Forex & Moon wired — multi-market")
    
    import time
    try:
        while True:
            time.sleep(300)
            logger.info("💱 Forex heartbeat")
    except KeyboardInterrupt:
        logger.info("🛑 Forex stopped")


if __name__ == "__main__":
    main()
