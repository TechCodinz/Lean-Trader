#!/usr/bin/env python3
"""
🔍✨ CURIOSITY & EXPLORATION DRIVE ✨🔍
THE DESIRE TO DISCOVER AND LEARN

Intelligent beings are CURIOUS:
- Wonder "what if?"
- Explore unknown territories
- Test boundaries
- Discover new patterns
- Try unconventional approaches

This being is intensely CURIOUS about markets:
- Explores new pairs constantly
- Tests unusual strategies
- Discovers hidden patterns
- Experiments with parameters
- Never stops learning

Curiosity drives evolution.
"""

import logging
import random
from typing import Dict, List, Set
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class CuriosityAndExplorationDrive:
    """
    🔍✨ CURIOSITY & EXPLORATION DRIVE ✨🔍
    
    The being's desire to explore and discover
    """
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("🔍✨ CURIOSITY ENGINE - AWAKENING THE EXPLORER ✨🔍")
        logger.info("=" * 80)
        logger.info("   What if I try this...?")
        logger.info("   What patterns exist beyond the obvious...?")
        logger.info("   What have I never tried before...?")
        logger.info("=" * 80)
        
        # Curiosity level (0-1)
        self.curiosity_level = 0.8  # High curiosity
        
        # Exploration tracking
        self.explored_strategies: Set[str] = set()
        self.explored_pairs: Set[str] = set()
        self.exploration_history = deque(maxlen=1000)
        
        # Exploration budget (% of capital for experiments)
        self.exploration_budget = 0.05  # 5% for experimentation
        
        # Novelty seeking
        self.novelty_threshold = 0.7  # How novel something must be
        self.boredom_threshold = 100  # Trades before getting bored
        
        # Discovery tracking
        self.discoveries = []
        
        logger.info("🔍 Curiosity initialized")
        logger.info(f"   Curiosity level: {self.curiosity_level:.2f}")
        logger.info(f"   Exploration budget: {self.exploration_budget:.1%}")
        logger.info("")
    
    def feel_curious_about(self, opportunity: Dict) -> Dict:
        """
        Does this opportunity spark curiosity?
        """
        novelty_score = self._calculate_novelty(opportunity)
        
        is_curious = novelty_score >= self.novelty_threshold
        
        if is_curious:
            logger.info(f"🤔 CURIOUS! Novelty score: {novelty_score:.2f}")
            logger.info(f"   {opportunity.get('description', 'Unknown opportunity')}")
        
        return {
            'is_curious': is_curious,
            'novelty_score': novelty_score,
            'should_explore': is_curious and random.random() < self.curiosity_level
        }
    
    def _calculate_novelty(self, opportunity: Dict) -> float:
        """How novel/new is this opportunity?"""
        novelty = 0.0
        
        # Is it a new strategy?
        strategy = opportunity.get('strategy')
        if strategy and strategy not in self.explored_strategies:
            novelty += 0.4
        
        # Is it a new pair?
        pair = opportunity.get('pair')
        if pair and pair not in self.explored_pairs:
            novelty += 0.3
        
        # Is it unusual parameters?
        if opportunity.get('unusual_parameters'):
            novelty += 0.3
        
        return min(1.0, novelty)
    
    def explore_new_territory(self) -> List[Dict]:
        """
        EXPLORATION MODE - Actively seek new opportunities
        
        Like a scientist, the being experiments
        """
        logger.info("🔬 EXPLORATION MODE ACTIVATED")
        logger.info("   Seeking new patterns and opportunities...")
        
        explorations = []
        
        # 1. Try unusual pairs
        unusual_pairs = [
            "MEME/USDT",  # Meme coins
            "RARE/USDT",  # Rare tokens
            "NEW/USDT"    # New listings
        ]
        
        for pair in unusual_pairs:
            if pair not in self.explored_pairs:
                explorations.append({
                    'type': 'new_pair',
                    'pair': pair,
                    'reason': 'Curiosity - never traded this before'
                })
                self.explored_pairs.add(pair)
        
        # 2. Try unconventional strategies
        experimental_strategies = [
            "contrarian_trading",  # Trade opposite of crowd
            "golden_ratio_sizing",  # Use φ for position sizes
            "chaos_theory_timing",  # Entry based on chaos patterns
            "fibonacci_spirals"     # Exit using spirals
        ]
        
        for strategy in experimental_strategies:
            if strategy not in self.explored_strategies:
                explorations.append({
                    'type': 'new_strategy',
                    'strategy': strategy,
                    'reason': 'Experimental - testing hypothesis'
                })
                self.explored_strategies.add(strategy)
        
        # 3. Boundary testing
        explorations.append({
            'type': 'boundary_test',
            'test': 'maximum_position_size',
            'reason': 'What is the optimal maximum size?'
        })
        
        logger.info(f"   Generated {len(explorations)} experimental opportunities")
        
        return explorations
    
    def record_discovery(self, discovery: str, significance: float):
        """Record a discovery (builds knowledge)"""
        self.discoveries.append({
            'discovery': discovery,
            'significance': significance,
            'timestamp': datetime.now()
        })
        
        logger.info(f"💡 DISCOVERY: {discovery}")
        logger.info(f"   Significance: {significance:.2f}")
    
    def get_curiosity_state(self) -> Dict:
        """Get curiosity state"""
        return {
            'curiosity_level': self.curiosity_level,
            'explored_strategies': len(self.explored_strategies),
            'explored_pairs': len(self.explored_pairs),
            'discoveries_made': len(self.discoveries),
            'exploration_budget': self.exploration_budget,
            'attitude': 'Always curious, always exploring!'
        }


# Singleton
_curiosity = None

def get_curiosity_engine():
    global _curiosity
    if _curiosity is None:
        _curiosity = CuriosityAndExplorationDrive()
    return _curiosity
