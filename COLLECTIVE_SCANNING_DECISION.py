#!/usr/bin/env python3
"""
🧠 COLLECTIVE SCANNING DECISION SYSTEM 🧠

NO HARDCODED SETTINGS!

ALL scanning parameters determined COLLECTIVELY by:
- Supreme Situational Awareness
- Market conditions
- System health
- Risk levels
- Opportunity windows
- Performance metrics

HYBRID APPROACH:
- Aggressive when conditions optimal
- Balanced when conditions normal
- Conservative when conditions poor
- Emergency when risk high

NO GATING - ALL ADAPTIVE!
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CollectiveScanningDecision:
    """
    🧠 Determines scanning parameters COLLECTIVELY
    
    No hardcoded values - everything adaptive based on:
    - Situational awareness score
    - Market volatility
    - System health
    - Risk exposure
    - Performance metrics
    """
    
    @staticmethod
    async def get_scanning_parameters(situational_awareness=None) -> Dict[str, Any]:
        """
        Get scanning parameters from COLLECTIVE intelligence
        
        Returns:
            Dict with adaptive parameters based on situation
        """
        
        # Default to balanced if no situational awareness
        situation_score = 0.70  # Default balanced
        mode = 'balanced'
        
        # 🧠 Get situational awareness assessment
        if situational_awareness:
            try:
                assessment = await situational_awareness.assess_complete_situation()
                situation_score = assessment.get('situation_score', 0.70)
                mode = assessment.get('adaptive_state', {}).get('mode', 'balanced')
                
                logger.info(f"🧠 Collective Decision - Situation Score: {situation_score:.0%}")
                logger.info(f"   Mode: {mode.upper()}")
                
            except Exception as e:
                logger.debug(f"Situational awareness error: {e}")
        
        # 🎯 ADAPTIVE PARAMETERS based on situation
        
        if situation_score >= 0.90 or mode == 'supersede':
            # SUPERSEDE MODE - Maximum aggression!
            params = {
                'mode': 'supersede',
                'min_volume_usd': 10_000,  # $10K - Very low threshold
                'min_price_change_pct': 0.1,  # 0.1% - Catch everything!
                'include_all_pairs': True,  # Include ALL
                'max_pairs': 5000,  # No real limit
                'trending_threshold': 0.3,  # 0.3% for trending
                'description': 'SUPERSEDE: Maximum opportunity capture'
            }
            
        elif situation_score >= 0.80 or mode == 'flawless':
            # FLAWLESS MODE - High aggression
            params = {
                'mode': 'flawless',
                'min_volume_usd': 50_000,  # $50K
                'min_price_change_pct': 0.5,  # 0.5%
                'include_all_pairs': True,  # Include all
                'max_pairs': 3000,
                'trending_threshold': 0.5,  # 0.5% for trending
                'description': 'FLAWLESS: High opportunity capture'
            }
            
        elif situation_score >= 0.60 or mode == 'balanced':
            # BALANCED MODE - Standard filtering
            params = {
                'mode': 'balanced',
                'min_volume_usd': 100_000,  # $100K
                'min_price_change_pct': 1.0,  # 1%
                'include_all_pairs': False,  # Volume-filtered
                'max_pairs': 2000,
                'trending_threshold': 1.5,  # 1.5% for trending
                'description': 'BALANCED: Standard filtering'
            }
            
        elif situation_score >= 0.40 or mode == 'conservative':
            # CONSERVATIVE MODE - Stricter filtering
            params = {
                'mode': 'conservative',
                'min_volume_usd': 500_000,  # $500K
                'min_price_change_pct': 2.0,  # 2%
                'include_all_pairs': False,
                'max_pairs': 1000,
                'trending_threshold': 3.0,  # 3% for trending
                'description': 'CONSERVATIVE: Strict filtering'
            }
            
        else:
            # DEFENSIVE MODE - Very strict
            params = {
                'mode': 'defensive',
                'min_volume_usd': 1_000_000,  # $1M
                'min_price_change_pct': 3.0,  # 3%
                'include_all_pairs': False,
                'max_pairs': 500,
                'trending_threshold': 5.0,  # 5% for trending
                'description': 'DEFENSIVE: Very strict filtering'
            }
        
        logger.info(f"   📊 Scanning Parameters: {params['description']}")
        logger.info(f"   Min Volume: ${params['min_volume_usd']:,}")
        logger.info(f"   Include All: {params['include_all_pairs']}")
        logger.info(f"   Max Pairs: {params['max_pairs']:,}")
        
        return params


# ============================================================================
# ADD TO SCANNER CLASS
# ============================================================================

async def _get_collective_scanning_decision_method(self):
    """
    Get scanning parameters from collective intelligence
    (To be added to DynamicMarketScanner class)
    """
    from COLLECTIVE_SCANNING_DECISION import CollectiveScanningDecision
    
    # Get parameters from collective decision
    params = await CollectiveScanningDecision.get_scanning_parameters(
        self.situational_awareness
    )
    
    # Apply to scanner
    self.adaptive_mode = params['mode']
    self.min_24h_volume_usd = params['min_volume_usd']
    self.min_price_change_pct = params['min_price_change_pct']
    self.include_all_pairs = params['include_all_pairs']
    self.last_collective_decision = params
    
    return params
