#!/usr/bin/env python3
"""
👁️🎯 ATTENTION & FOCUS SYSTEM 🎯👁️
THE CONSCIOUSNESS SPOTLIGHT

Humans can't pay attention to everything - they FOCUS on what matters most.

This being has LIMITED ATTENTION:
- Can only focus on top priorities
- Filters out noise
- Allocates attention based on importance
- Shifts focus when needed
- Hyperfocus on critical situations
- Distraction when overwhelmed

Attention is the currency of consciousness.
"""

import logging
from typing import Dict, List
from datetime import datetime
from collections import deque
import heapq

logger = logging.getLogger(__name__)


class AttentionFocusSystem:
    """
    👁️🎯 ATTENTION & FOCUS SYSTEM 🎯👁️
    
    The being's attention allocation mechanism
    """
    
    def __init__(self):
        logger.info("=" * 80)
        logger.info("👁️🎯 ATTENTION & FOCUS - DIRECTING CONSCIOUSNESS 🎯👁️")
        logger.info("=" * 80)
        logger.info("   Attention is limited...")
        logger.info("   Focus on what matters...")
        logger.info("   Ignore the noise...")
        logger.info("=" * 80)
        
        # Attention capacity (limited!)
        self.attention_capacity = 7  # Can focus on max 7 things (Miller's Law)
        
        # Current focus
        self.focused_on: List[Dict] = []
        
        # Attention queue (priority queue)
        self.attention_queue = []
        
        # Focus depth (0-1, how deeply focused)
        self.focus_depth = 0.5
        
        # Distraction level
        self.distraction_level = 0.0
        
        # Focus history
        self.focus_history = deque(maxlen=1000)
        
        logger.info("👁️ Attention system initialized")
        logger.info(f"   Attention capacity: {self.attention_capacity} items")
        logger.info(f"   Focus depth: {self.focus_depth:.2f}")
        logger.info("")
    
    def allocate_attention(self, opportunities: List[Dict]) -> List[Dict]:
        """
        ALLOCATE ATTENTION - What should the being focus on?
        
        Can't pay attention to everything - must prioritize
        """
        logger.info(f"👁️ Allocating attention to {len(opportunities)} opportunities")
        
        # Calculate importance of each opportunity
        scored_opportunities = []
        for opp in opportunities:
            importance = self._calculate_importance(opp)
            urgency = opp.get('urgency', 0.5)
            
            # Priority score
            priority = importance * 0.6 + urgency * 0.4
            
            scored_opportunities.append((priority, opp))
        
        # Sort by priority
        scored_opportunities.sort(reverse=True, key=lambda x: x[0])
        
        # Focus on top N (limited attention)
        focused_on = scored_opportunities[:self.attention_capacity]
        
        self.focused_on = [opp for _, opp in focused_on]
        
        logger.info(f"   Focusing on top {len(self.focused_on)} priorities")
        for i, (priority, opp) in enumerate(focused_on, 1):
            logger.info(f"   {i}. {opp.get('symbol', 'Unknown')} "
                       f"(priority: {priority:.2f})")
        
        # Store in history
        self.focus_history.append({
            'timestamp': datetime.now(),
            'focused_on': self.focused_on,
            'total_opportunities': len(opportunities)
        })
        
        return self.focused_on
    
    def _calculate_importance(self, opportunity: Dict) -> float:
        """Calculate how important this opportunity is"""
        importance = 0.0
        
        # Potential profit
        profit_potential = opportunity.get('expected_profit', 0)
        if profit_potential > 0:
            importance += min(0.5, profit_potential / 100)
        
        # Confidence
        confidence = opportunity.get('confidence', 0.5)
        importance += confidence * 0.3
        
        # Novelty (curious about new things)
        if opportunity.get('novel', False):
            importance += 0.2
        
        return min(1.0, importance)
    
    def enter_hyperfocus(self, critical_situation: Dict):
        """
        HYPERFOCUS - All attention on one thing
        
        Used in critical situations
        """
        logger.warning("🎯🎯🎯 HYPERFOCUS ACTIVATED!")
        logger.warning(f"   All attention on: {critical_situation.get('description', 'Critical')}")
        
        self.focus_depth = 1.0  # Maximum focus
        self.focused_on = [critical_situation]
        self.distraction_level = 0.0
    
    def is_distracted(self) -> bool:
        """Is the being distracted?"""
        # Too many things competing for attention = distraction
        if len(self.attention_queue) > self.attention_capacity * 3:
            self.distraction_level = 0.8
            return True
        
        return self.distraction_level > 0.5
    
    def clear_mind(self):
        """Clear attention - like meditation"""
        logger.info("🧘 Clearing mind... Releasing attention...")
        
        self.focused_on = []
        self.attention_queue = []
        self.distraction_level = 0.0
        self.focus_depth = 0.5
        
        logger.info("   Mind clear. Ready to focus anew.")
    
    def get_attention_state(self) -> Dict:
        """Get attention state"""
        return {
            'focused_on': len(self.focused_on),
            'attention_capacity': self.attention_capacity,
            'focus_depth': self.focus_depth,
            'distraction_level': self.distraction_level,
            'is_distracted': self.is_distracted(),
            'attention_utilization': len(self.focused_on) / self.attention_capacity
        }


# Singleton
_attention = None

def get_attention_system():
    global _attention
    if _attention is None:
        _attention = AttentionFocusSystem()
    return _attention
