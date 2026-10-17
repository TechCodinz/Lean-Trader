#!/usr/bin/env python3
"""
LeanTrader Smart Scalping Engine Service (2025 microservice).

Multi-timeframe confluence + session awareness.
Only trades when ALL timeframes align (75% must agree) in optimal sessions.

2025 original: SMART_SCALPING_ENGINE.py (2025-10-13)
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from SMART_SCALPING_ENGINE import MultiTimeframeAnalyzer, MarketSession

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SCALP_SERVICE')


def main():
    logger.info("⚡ Starting Smart Scalping Engine Service (2025 microservice)")
    logger.info("   Multi-timeframe confluence + session awareness")
    
    analyzer = MultiTimeframeAnalyzer()
    logger.info("✅ Multi-timeframe analyzer initialized")
    
    # Get current session
    session = MarketSession.get_current_session()
    logger.info(f"📊 Current session: {session}")
    
    # The analyzer runs via check_confluence() calls from the trading loop
    # This service keeps the analyzer warm and logs session changes
    last_session = session
    try:
        while True:
            time.sleep(60)
            current = MarketSession.get_current_session()
            if current != last_session:
                logger.info(f"📊 Session change: {last_session} → {current}")
                last_session = current
    except KeyboardInterrupt:
        logger.info("🛑 Scalp service stopped")


if __name__ == "__main__":
    main()
