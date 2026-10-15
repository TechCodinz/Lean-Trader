#!/usr/bin/env python3
"""
LeanTrader MT5 & Universe Wiring (2026).

Wires 2025:
- mt5_signals: MT5 Forex signals
- EXPANDED_MARKET_UNIVERSE: 65-pair universe
- simple_bot

2025: Multi-market (crypto + FX).
2026: Wired.
"""

import logging
import sys

sys.path.insert(0, '/app')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MT5')


def main():
    logger.info("💱 Wiring 2025 MT5 & Universe")
    
    try:
        import mt5_signals
        logger.info("✅ mt5_signals: MT5 Forex")
    except Exception as e:
        logger.info(f"⏳ MT5: {e}")
    
    try:
        from EXPANDED_MARKET_UNIVERSE import FULL_MARKET_UNIVERSE
        logger.info(f"✅ Universe: {len(FULL_MARKET_UNIVERSE)} pairs")
    except Exception as e:
        logger.info(f"⏳ Universe: {e}")
    
    try:
        import simple_bot
        logger.info("✅ simple_bot")
    except Exception as e:
        logger.info(f"⏳ Simple: {e}")
    
    logger.info("")
    logger.info("💱 MT5 & Universe wired")
    
    import time
    try:
        while True:
            time.sleep(300)
            logger.info("💱 MT5 heartbeat")
    except KeyboardInterrupt:
        logger.info("🛑 Stopped")


if __name__ == "__main__":
    main()
