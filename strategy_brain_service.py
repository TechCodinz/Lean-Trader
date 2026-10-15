#!/usr/bin/env python3
"""
LeanTrader Strategy Brain Service (2025 microservice).

The 7 alpha strategies as an intelligent system in the nervous system:
- OscillatorConfluence, NakedPriceAction, TrendSqueeze
- DonchianBreakout, KeltnerBreakout, VWAPBounce, VolumeSpike

Other systems query this brain for signals. It does not trade directly.

2025 original: alpha_engines.py (2025-08-29)
"""

import logging
import sys
import time

sys.path.insert(0, '/app')

from alpha_engines import (
    OscillatorConfluence,
    NakedPriceAction,
    TrendSqueeze,
    DonchianBreakout,
    KeltnerBreakout,
    VWAPBounce,
    VolumeSpike,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('STRATEGY_BRAIN')


def main():
    logger.info("🧠 Starting Strategy Brain Service (2025 microservice)")
    logger.info("   7 alpha strategies as an intelligent system")
    
    strategies = [
        OscillatorConfluence(),
        NakedPriceAction(),
        TrendSqueeze(),
        DonchianBreakout(),
        KeltnerBreakout(),
        VWAPBounce(),
        VolumeSpike(),
    ]
    
    for s in strategies:
        logger.info(f"   ✅ {s.name} loaded")
    
    logger.info(f"✅ Strategy Brain online — {len(strategies)} strategies ready")
    logger.info("   Other systems can query this brain for signals")
    
    # Keep alive — the brain is queryable, not a loop
    try:
        while True:
            time.sleep(300)
            logger.info(f"🧠 Strategy Brain heartbeat — {len(strategies)} strategies ready")
    except KeyboardInterrupt:
        logger.info("🛑 Strategy Brain stopped")


if __name__ == "__main__":
    main()
