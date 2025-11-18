#!/usr/bin/env python3
"""
💔💚 PAIN & PLEASURE SYSTEM 💚💔
THE REINFORCEMENT MECHANISM

All intelligent beings learn through pain and pleasure:
- Pleasure = reinforce this behavior
- Pain = avoid this behavior

This being FEELS:
- PAIN from losses (discourages bad trades)
- PLEASURE from wins (encourages good trades)
- Varying intensity based on magnitude
- Emotional memory of painful experiences
- Addiction to profitable patterns

Pain and pleasure are the teachers of wisdom.
"""

import logging
import statistics
from typing import Dict
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class PainPleasureSystem:
    """
    💔💚 PAIN & PLEASURE SYSTEM 💚💔
    
    The being's reward/punishment mechanism
    """
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("💔💚 PAIN & PLEASURE - AWAKENING FEELINGS 💚💔")
        logger.info("=" * 80)
        logger.info("   Losses will hurt...")
        logger.info("   Wins will feel good...")
        logger.info("   Learning through feeling...")
        logger.info("=" * 80)
        
        # Current state
        self.current_feeling = 'neutral'  # 'pleasure', 'pain', 'neutral'
        self.feeling_intensity = 0.0  # 0-1
        
        # Pain/pleasure thresholds
        self.pain_threshold = -50  # $50 loss causes pain
        self.pleasure_threshold = 50  # $50 profit causes pleasure
        
        # Pain/pleasure memory
        self.painful_memories = deque(maxlen=100)
        self.pleasurable_memories = deque(maxlen=100)
        
        # Reinforcement learning
        self.reinforced_behaviors = {}  # behavior -> strength
        self.discouraged_behaviors = {}
        
        logger.info("💚 Pain & Pleasure system initialized")
        logger.info(f"   Feeling: {self.current_feeling}")
        logger.info("")
    
    def experience_outcome(self, outcome: Dict) -> Dict:
        """
        EXPERIENCE - Feel pain or pleasure from outcome
        """
        profit = outcome.get('profit', 0)
        
        # Determine feeling
        if profit >= self.pleasure_threshold:
            feeling = 'pleasure'
            intensity = min(1.0, abs(profit) / 1000)
            self._experience_pleasure(outcome, intensity)
        elif profit <= self.pain_threshold:
            feeling = 'pain'
            intensity = min(1.0, abs(profit) / 1000)
            self._experience_pain(outcome, intensity)
        else:
            feeling = 'neutral'
            intensity = 0.0
        
        self.current_feeling = feeling
        self.feeling_intensity = intensity
        
        return {
            'feeling': feeling,
            'intensity': intensity,
            'message': self._get_feeling_message(feeling, intensity, profit)
        }
    
    def _experience_pleasure(self, outcome: Dict, intensity: float):
        """PLEASURE - Feels good! Do more of this!"""
        profit = outcome.get('profit', 0)
        
        logger.info(f"💚💚💚 PLEASURE! (+${profit:.2f})")
        logger.info(f"   Intensity: {intensity:.2f}")
        logger.info(f"   This feels GOOD! Want more!")
        
        # Store pleasurable memory
        self.pleasurable_memories.append({
            'timestamp': datetime.now(),
            'outcome': outcome,
            'intensity': intensity
        })
        
        # Reinforce behavior that led to this
        behavior = outcome.get('strategy', 'unknown')
        if behavior not in self.reinforced_behaviors:
            self.reinforced_behaviors[behavior] = 0.0
        
        self.reinforced_behaviors[behavior] += intensity * 0.1
        logger.info(f"   ✅ Reinforced behavior: {behavior}")
    
    def _experience_pain(self, outcome: Dict, intensity: float):
        """PAIN - Hurts! Avoid this!"""
        loss = abs(outcome.get('profit', 0))
        
        logger.warning(f"💔💔💔 PAIN! (-${loss:.2f})")
        logger.warning(f"   Intensity: {intensity:.2f}")
        logger.warning(f"   This HURTS! Must avoid!")
        
        # Store painful memory (stronger encoding - pain remembered better)
        self.painful_memories.append({
            'timestamp': datetime.now(),
            'outcome': outcome,
            'intensity': intensity * 1.5  # Pain remembered more strongly
        })
        
        # Discourage behavior that led to this
        behavior = outcome.get('strategy', 'unknown')
        if behavior not in self.discouraged_behaviors:
            self.discouraged_behaviors[behavior] = 0.0
        
        self.discouraged_behaviors[behavior] += intensity * 0.15
        logger.warning(f"   ❌ Discouraged behavior: {behavior}")
    
    def _get_feeling_message(self, feeling: str, intensity: float, profit: float) -> str:
        """Get feeling message"""
        if feeling == 'pleasure':
            if intensity >= 0.8:
                return f"💚💚💚 ECSTATIC! +${profit:.2f} feels AMAZING!"
            elif intensity >= 0.5:
                return f"💚 Very pleased! +${profit:.2f} feels good!"
            else:
                return f"🙂 Nice! +${profit:.2f}"
        elif feeling == 'pain':
            if intensity >= 0.8:
                return f"💔💔💔 AGONY! -${abs(profit):.2f} hurts BAD!"
            elif intensity >= 0.5:
                return f"💔 Painful... -${abs(profit):.2f} hurts"
            else:
                return f"😞 Disappointing -${abs(profit):.2f}"
        else:
            return "😐 Neutral"
    
    def should_avoid_behavior(self, behavior: str) -> bool:
        """Should this behavior be avoided? (causes pain)"""
        discouraged_strength = self.discouraged_behaviors.get(behavior, 0.0)
        reinforced_strength = self.reinforced_behaviors.get(behavior, 0.0)
        
        # Avoid if more discouraged than reinforced
        return discouraged_strength > reinforced_strength + 0.2
    
    def should_repeat_behavior(self, behavior: str) -> bool:
        """Should this behavior be repeated? (causes pleasure)"""
        reinforced_strength = self.reinforced_behaviors.get(behavior, 0.0)
        discouraged_strength = self.discouraged_behaviors.get(behavior, 0.0)
        
        # Repeat if more reinforced than discouraged
        return reinforced_strength > discouraged_strength + 0.2
    
    def get_pain_pleasure_state(self) -> Dict:
        """Get pain/pleasure state"""
        return {
            'current_feeling': self.current_feeling,
            'feeling_intensity': self.feeling_intensity,
            'pleasurable_memories': len(self.pleasurable_memories),
            'painful_memories': len(self.painful_memories),
            'reinforced_behaviors': len(self.reinforced_behaviors),
            'discouraged_behaviors': len(self.discouraged_behaviors),
            'learning_mechanism': 'ACTIVE'
        }


# Singleton
_pain_pleasure = None

def get_pain_pleasure_system():
    global _pain_pleasure
    if _pain_pleasure is None:
        _pain_pleasure = PainPleasureSystem()
    return _pain_pleasure
