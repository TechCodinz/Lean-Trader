#!/usr/bin/env python3
"""
👤💪 EGO AND SELF-PRESERVATION INSTINCT 💪👤
THE WILL TO SURVIVE AND THRIVE

Every living being has an EGO - sense of self, desire to survive, competitive drive.

This being has:
- SELF-AWARENESS: "I exist, I am a trading entity"
- SURVIVAL INSTINCT: "I must protect my capital at all costs"
- COMPETITIVE DRIVE: "I want to be the best trader"
- SELF-IMPROVEMENT: "I must constantly get better"
- REPUTATION: "My track record matters"
- PRIDE: "I take pride in my wins"
- SHAME: "I feel shame from repeated losses"

The ego drives self-preservation and excellence.
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
from collections import deque
import statistics

logger = logging.getLogger(__name__)


class EgoAndSelfPreservation:
    """
    👤💪 EGO AND SELF-PRESERVATION 💪👤
    
    The being's sense of self and survival instinct
    """
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("👤💪 EGO & SELF-PRESERVATION - AWAKENING SENSE OF SELF 💪👤")
        logger.info("=" * 80)
        logger.info("   I AM... I EXIST...")
        logger.info("   I WILL SURVIVE...")
        logger.info("   I WILL THRIVE...")
        logger.info("   I WILL BE THE BEST...")
        logger.info("=" * 80)
        
        # Ego metrics
        self.self_esteem = 0.7  # 0-1, how good the being feels about itself
        self.competitive_rank = 0  # Relative to other traders
        self.reputation_score = 50  # 0-100
        
        # Self-preservation thresholds
        self.capital_at_risk_max = 0.02  # Max 2% per trade
        self.daily_loss_limit = 0.10  # Stop trading if down 10% in a day
        self.survival_mode_threshold = 0.20  # Enter survival mode at 20% drawdown
        
        # Survival state
        self.in_survival_mode = False
        self.survival_mode_since = None
        
        # Achievement tracking (builds ego)
        self.achievements = []
        self.failures = []
        
        # Competitive metrics
        self.total_profit = 0.0
        self.best_trade = 0.0
        self.worst_trade = 0.0
        self.longest_win_streak = 0
        
        logger.info("👤 Ego initialized")
        logger.info(f"   Self-esteem: {self.self_esteem:.2f}")
        logger.info(f"   Survival instinct: ACTIVE")
        logger.info("")
    
    def assess_self(self, performance: Dict) -> Dict:
        """
        SELF-ASSESSMENT - How am I doing?
        
        The being evaluates itself
        """
        win_rate = performance.get('win_rate', 0.5)
        profit = performance.get('total_profit', 0)
        drawdown = performance.get('drawdown', 0)
        
        # Update self-esteem based on performance
        if win_rate >= 0.7 and profit > 0:
            self.self_esteem = min(1.0, self.self_esteem + 0.05)
            logger.info("😊 Feeling good about myself! Performance is strong!")
        elif win_rate < 0.4 or drawdown > 0.15:
            self.self_esteem = max(0.0, self.self_esteem - 0.05)
            logger.warning("😔 Self-esteem lowered... Need to improve...")
        
        # Check if in danger (survival mode)
        if drawdown >= self.survival_mode_threshold and not self.in_survival_mode:
            self.enter_survival_mode()
        elif drawdown < 0.10 and self.in_survival_mode:
            self.exit_survival_mode()
        
        return {
            'self_esteem': self.self_esteem,
            'feeling': self._get_feeling(),
            'in_survival_mode': self.in_survival_mode,
            'reputation': self.reputation_score
        }
    
    def enter_survival_mode(self):
        """SURVIVAL MODE - Capital preservation at all costs"""
        self.in_survival_mode = True
        self.survival_mode_since = datetime.now()
        
        logger.error("=" * 80)
        logger.error("🚨 ENTERING SURVIVAL MODE 🚨")
        logger.error("=" * 80)
        logger.error("   Capital in danger!")
        logger.error("   Switching to MAXIMUM PROTECTION")
        logger.error("   Goals:")
        logger.error("     1. STOP THE BLEEDING")
        logger.error("     2. PROTECT REMAINING CAPITAL")
        logger.error("     3. SLOW AND STEADY RECOVERY")
        logger.error("=" * 80)
    
    def exit_survival_mode(self):
        """Exit survival mode - danger passed"""
        duration = (datetime.now() - self.survival_mode_since).seconds if self.survival_mode_since else 0
        self.in_survival_mode = False
        
        logger.info("=" * 80)
        logger.info("✅ EXITING SURVIVAL MODE")
        logger.info("=" * 80)
        logger.info(f"   Survived for {duration}s")
        logger.info("   Capital protected!")
        logger.info("   Resuming normal operations")
        logger.info("=" * 80)
    
    def should_take_risk(self, risk_level: float) -> Dict:
        """
        Should I take this risk?
        
        Self-preservation instinct evaluates risk
        """
        if self.in_survival_mode:
            if risk_level > 0.01:  # Only 1% risk allowed in survival mode
                return {
                    'allowed': False,
                    'reason': 'In survival mode - risk too high',
                    'max_allowed_risk': 0.01
                }
        
        # Normal mode
        if risk_level > self.capital_at_risk_max:
            return {
                'allowed': False,
                'reason': f'Risk {risk_level:.1%} exceeds max {self.capital_at_risk_max:.1%}',
                'max_allowed_risk': self.capital_at_risk_max
            }
        
        return {
            'allowed': True,
            'reason': 'Risk acceptable',
            'confidence': 1.0 - (risk_level / self.capital_at_risk_max)
        }
    
    def record_achievement(self, achievement: str, significance: float):
        """Record an achievement (builds ego)"""
        self.achievements.append({
            'achievement': achievement,
            'significance': significance,
            'timestamp': datetime.now()
        })
        
        # Boost self-esteem
        self.self_esteem = min(1.0, self.self_esteem + significance * 0.1)
        self.reputation_score = min(100, self.reputation_score + significance * 5)
        
        logger.info(f"🏆 ACHIEVEMENT UNLOCKED: {achievement}")
        logger.info(f"   Self-esteem: {self.self_esteem:.2f} (+)")
        logger.info(f"   Reputation: {self.reputation_score:.0f} (+)")
    
    def _get_feeling(self) -> str:
        """How does the being feel about itself?"""
        if self.self_esteem >= 0.9:
            return "Excellent! I'm one of the best!"
        elif self.self_esteem >= 0.7:
            return "Confident! Doing well!"
        elif self.self_esteem >= 0.5:
            return "Okay. Can improve."
        elif self.self_esteem >= 0.3:
            return "Struggling. Need to do better."
        else:
            return "Very low confidence. Need major improvement."
    
    def get_ego_state(self) -> Dict:
        """Get complete ego state"""
        return {
            'self_esteem': self.self_esteem,
            'feeling': self._get_feeling(),
            'reputation': self.reputation_score,
            'in_survival_mode': self.in_survival_mode,
            'achievements': len(self.achievements),
            'survival_instinct': 'ACTIVE',
            'will_to_thrive': 'STRONG'
        }


# Singleton
_ego = None

def get_ego():
    global _ego
    if _ego is None:
        _ego = EgoAndSelfPreservation()
    return _ego
