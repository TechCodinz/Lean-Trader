"""
Strategy Blender

Flow + Intent aware strategy mixing.
Blends trend/mean-reversion/breakout strategies based on:
- Wave state (IMPULSE/CORRECTIVE/CHAOS)
- Pitch regime
- Intent strength and bias
- Liquidity conditions

Weights sum to 1.0, smooth transitions (no jumps).
"""

import numpy as np
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StrategyBlender:
    """
    Adaptive strategy mixing based on market state
    
    Dynamically blends strategies for optimal edge
    """
    
    def __init__(self,
                 smoothing_alpha: float = 0.3,  # EMA smoothing
                 min_strategy_weight: float = 0.05):  # Min 5% per strategy
        """
        Initialize Strategy Blender
        
        Args:
            smoothing_alpha: EMA alpha for smooth weight transitions
            min_strategy_weight: Minimum weight for any strategy
        """
        self.smoothing_alpha = smoothing_alpha
        self.min_strategy_weight = min_strategy_weight
        
        # Previous weights for smoothing
        self.prev_weights: Dict[str, float] = {
            'trend': 0.33,
            'mean_reversion': 0.33,
            'breakout': 0.33
        }
        
        logger.info("[OK] StrategyBlender initialized")
        logger.info(f"   Smoothing alpha: {smoothing_alpha}")
    
    def blend_strategies(self,
                        wave_state: Optional[str],
                        wave_flow_score: float,
                        chaos_score: float,
                        pitch_regime: Optional[str],
                        intent_bias: float,
                        intent_strength: float,
                        trap_risk: float,
                        liquidity_gravity: float,
                        sweep_risk: float) -> Dict[str, float]:
        """
        Calculate strategy weights based on market conditions
        
        Args:
            wave_state: "IMPULSE", "CORRECTIVE", "CHAOS"
            wave_flow_score: Wave flow score [0,1]
            chaos_score: Chaos score [0,1]
            pitch_regime: "calm", "normal", "hot", "chaotic"
            intent_bias: Intent bias [-1,+1]
            intent_strength: Intent strength [0,1]
            trap_risk: Trap risk [0,1]
            liquidity_gravity: Gravity vector [-1,+1]
            sweep_risk: Sweep risk [0,1]
        
        Returns:
            Dict of strategy -> weight (sum to 1.0)
        """
        try:
            # Calculate raw weights
            trend_weight = self._calc_trend_weight(
                wave_state, wave_flow_score, intent_bias, intent_strength
            )
            
            mr_weight = self._calc_mean_reversion_weight(
                wave_state, chaos_score, sweep_risk, liquidity_gravity
            )
            
            breakout_weight = self._calc_breakout_weight(
                wave_state, pitch_regime, intent_strength, trap_risk
            )
            
            # Normalize to sum to 1.0
            total = trend_weight + mr_weight + breakout_weight
            if total == 0:
                # Fallback to equal weights
                weights = {
                    'trend': 0.33,
                    'mean_reversion': 0.33,
                    'breakout': 0.34
                }
            else:
                weights = {
                    'trend': trend_weight / total,
                    'mean_reversion': mr_weight / total,
                    'breakout': breakout_weight / total
                }
            
            # Apply minimum weights
            weights = self._apply_min_weights(weights)
            
            # Smooth with previous weights
            weights = self._smooth_weights(weights)
            
            # Final normalization
            weights = self._normalize_weights(weights)
            
            # Update previous
            self.prev_weights = weights.copy()
            
            logger.debug(f"Strategy weights: Trend={weights['trend']:.2f}, MR={weights['mean_reversion']:.2f}, BO={weights['breakout']:.2f}")
            
            return weights
            
        except Exception as e:
            logger.error(f"Strategy blending error: {e}")
            return self.prev_weights.copy()
    
    def _calc_trend_weight(self,
                          wave_state: Optional[str],
                          wave_flow_score: float,
                          intent_bias: float,
                          intent_strength: float) -> float:
        """
        Calculate trend strategy weight
        
        Favored when:
        - IMPULSE wave state
        - High wave flow
        - Strong intent with clear bias
        """
        weight = 0.33  # Base
        
        # Wave state boost
        if wave_state == "IMPULSE":
            weight += 0.3 * wave_flow_score
        elif wave_state == "CORRECTIVE":
            weight += 0.1
        else:  # CHAOS
            weight -= 0.2
        
        # Intent alignment
        if abs(intent_bias) > 0.5:  # Clear directional bias
            weight += 0.2 * intent_strength
        
        return max(weight, 0.0)
    
    def _calc_mean_reversion_weight(self,
                                   wave_state: Optional[str],
                                   chaos_score: float,
                                   sweep_risk: float,
                                   liquidity_gravity: float) -> float:
        """
        Calculate mean reversion strategy weight
        
        Favored when:
        - CORRECTIVE wave state
        - High sweep risk (price at extremes)
        - Strong liquidity magnets nearby
        """
        weight = 0.33  # Base
        
        # Wave state boost
        if wave_state == "CORRECTIVE":
            weight += 0.3
        elif wave_state == "IMPULSE":
            weight -= 0.2
        
        # Sweep risk boost (overextended = revert)
        if sweep_risk > 0.6:
            weight += 0.2 * sweep_risk
        
        # Liquidity gravity boost
        if abs(liquidity_gravity) > 0.5:
            weight += 0.15 * abs(liquidity_gravity)
        
        # Chaos penalty
        weight -= chaos_score * 0.2
        
        return max(weight, 0.0)
    
    def _calc_breakout_weight(self,
                             wave_state: Optional[str],
                             pitch_regime: Optional[str],
                             intent_strength: float,
                             trap_risk: float) -> float:
        """
        Calculate breakout strategy weight
        
        Favored when:
        - Transitioning from CORRECTIVE to IMPULSE
        - High intent strength
        - Low trap risk
        - Hot pitch regime
        """
        weight = 0.33  # Base
        
        # Wave state considerations
        if wave_state == "IMPULSE":
            weight += 0.2  # Early impulse = breakout
        elif wave_state == "CHAOS":
            weight -= 0.3  # Too chaotic for breakouts
        
        # Pitch regime boost
        if pitch_regime == "hot":
            weight += 0.25
        elif pitch_regime == "chaotic":
            weight -= 0.2
        
        # Intent strength boost
        if intent_strength > 0.6:
            weight += 0.15 * intent_strength
        
        # Trap risk penalty (major!)
        weight -= trap_risk * 0.4
        
        return max(weight, 0.0)
    
    def _apply_min_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Ensure no strategy drops below minimum weight
        
        Prevents complete strategy abandonment
        """
        adjusted = weights.copy()
        
        for strategy in adjusted:
            if adjusted[strategy] < self.min_strategy_weight:
                adjusted[strategy] = self.min_strategy_weight
        
        return adjusted
    
    def _smooth_weights(self, new_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Smooth weights with EMA to prevent jumps
        
        smoothed = alpha * new + (1-alpha) * prev
        """
        smoothed = {}
        
        for strategy in new_weights:
            prev = self.prev_weights.get(strategy, 0.33)
            smoothed[strategy] = (
                self.smoothing_alpha * new_weights[strategy] +
                (1.0 - self.smoothing_alpha) * prev
            )
        
        return smoothed
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize weights to sum to exactly 1.0
        """
        total = sum(weights.values())
        
        if total == 0:
            # Equal weights fallback
            n = len(weights)
            return {k: 1.0/n for k in weights}
        
        return {k: v/total for k, v in weights.items()}
    
    def get_strategy_signal(self,
                           weights: Dict[str, float],
                           trend_signal: float,
                           mr_signal: float,
                           breakout_signal: float) -> float:
        """
        Blend individual strategy signals using weights
        
        Args:
            weights: Strategy weights from blend_strategies
            trend_signal: Trend strategy signal [-1,+1]
            mr_signal: Mean reversion signal [-1,+1]
            breakout_signal: Breakout signal [-1,+1]
        
        Returns:
            Blended signal [-1,+1]
        """
        blended = (
            weights['trend'] * trend_signal +
            weights['mean_reversion'] * mr_signal +
            weights['breakout'] * breakout_signal
        )
        
        return float(np.clip(blended, -1.0, 1.0))
