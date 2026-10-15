#!/usr/bin/env python3
"""
LeanTrader Small Systems Wiring (2026).

Wires 2025 small but significant systems:
- sizer: position sizing
- auto_loop: auto loop
- router_safe: safe routing
- dashboard_reporter: reporting

2025: Small systems matter too.
2026: Wired.
"""

import logging
import sys

sys.path.insert(0, '/app')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SMALL')


def main():
    logger.info("🔧 Wiring 2025 Small Systems")
    
    for mod in ['sizer', 'auto_loop', 'router_safe', 'dashboard_reporter', 'mt5_single_shot']:
        try:
            __import__(mod)
            logger.info(f"✅ {mod}")
        except Exception as e:
            logger.info(f"⏳ {mod}: {str(e)[:40]}")
    
    logger.info("")
    logger.info("🔧 Small systems wired")
    
    import time
    try:
        while True:
            time.sleep(300)
            logger.info("🔧 Small heartbeat")
    except KeyboardInterrupt:
        logger.info("🛑 Stopped")


if __name__ == "__main__":
    main()
