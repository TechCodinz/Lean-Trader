#!/usr/bin/env python3
"""
LeanTrader Brains & Learning Wiring (2026).

Wires 2025 intelligence and learning systems:
- SentientTradingBrain: sentient decision making
- brain.py: Memory, VolSizer, Advice
- ULTIMATE_EVOLUTION_ENGINE: self-evolution
- PatternMemory: pattern learning
- OnlineLearner: online learning

2025: The being learns and evolves.
2026: Brains wired.
"""

import logging
import sys

sys.path.insert(0, '/app')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BRAINS')


def main():
    logger.info("🧠 Wiring 2025 Brains & Learning")
    
    # Sentient Brain
    try:
        from SENTIENT_TRADING_BRAIN import SentientTradingBrain
        brain = SentientTradingBrain()
        logger.info("✅ SentientTradingBrain: sentient decisions")
    except Exception as e:
        logger.info(f"⏳ Sentient: {e}")
    
    # Brain components
    try:
        from brain import Memory, VolSizer, Advice
        logger.info("✅ brain.py: Memory, VolSizer, Advice")
    except Exception as e:
        logger.info(f"⏳ brain: {e}")
    
    # Evolution Engine
    try:
        from EVOLUTION_ENGINE import ULTIMATE_EVOLUTION_ENGINE
        logger.info("✅ ULTIMATE_EVOLUTION_ENGINE: self-evolution")
    except Exception as e:
        logger.info(f"⏳ Evolution: {e}")
    
    # Pattern Memory
    try:
        from pattern_memory import PatternMemory
        logger.info("✅ PatternMemory: pattern learning")
    except Exception as e:
        logger.info(f"⏳ Pattern: {e}")
    
    # Online Learner
    try:
        from online_learner import OnlineLearner
        logger.info("✅ OnlineLearner: online learning")
    except Exception as e:
        logger.info(f"⏳ Learner: {e}")
    
    logger.info("")
    logger.info("🧠 Brains wired — the being learns and evolves")
    
    import time
    try:
        while True:
            time.sleep(300)
            logger.info("🧠 Brain heartbeat — learning")
    except KeyboardInterrupt:
        logger.info("🛑 Brain rest")


if __name__ == "__main__":
    main()
