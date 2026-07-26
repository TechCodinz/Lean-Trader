"""
Wave Flow Engine

Main engine for quantitative wave state detection and scoring.
Classifies market flow as IMPULSE / CORRECTIVE / CHAOS with hysteresis.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime
import logging

from .wave_flow_models import WaveState, WaveFlowOutput
from .wave_flow_features import WaveFlowFeatures

logger = logging.getLogger(__name__)


class WaveFlowEngine:
    """
    Core Wave Flow Engine
    
    Calculates wave_flow_score and chaos_score from OHLCV features.
    Classifies state as IMPULSE/CORRECTIVE/CHAOS with hysteresis to prevent rapid flipping.
    """
    
    def __init__(self, 
                 feature_window: int = 20,
                 state_history_size: int = 3,
                 wave_flow_weights: Optional[Dict[str, float]] = None,
                 chaos_weights: Optional[Dict[str, float]] = None):
        """
        Initialize Wave Flow Engine
        
        Args:
            feature_window: Window for feature calculation
            state_history_size: Number of states to track for hysteresis
            wave_flow_weights: Custom weights for wave flow score
            chaos_weights: Custom weights for chaos score
        """
        self.feature_extractor = WaveFlowFeatures(window=feature_window)
        self.state_history: List[WaveState] = []
        self.state_history_size = state_history_size
        
        # Default wave flow weights (higher = impulse)
        self.wave_flow_weights = wave_flow_weights or {
            'acceleration': 1.5,
            'range_expansion': 1.3,
            'trend_structure': 1.2,
            'velocity': 1.0,
            'candle_overlap': -1.0,  # Negative (low overlap = good)
            'wick_pressure': -0.8,   # Negative (low wicks = good)
        }
        
        # Default chaos weights (higher = chaos)
        self.chaos_weights = chaos_weights or {
            'wick_pressure': 2.0,
            'candle_overlap': 1.5,
            'mean_reversion_pull': 1.3,
            'velocity': 1.0,  # High velocity can also be choppy
        }
        
        logger.info("[OK] Wave Flow Engine initialized")
        logger.info(f"   Feature window: {feature_window}")
        logger.info(f"   Hysteresis size: {state_history_size}")
    
    def calculate_wave_flow(self, ohlcv: pd.DataFrame, 
                           bar_id: Optional[int] = None,
                           venue_features: Optional[Dict[str, float]] = None) -> WaveFlowOutput:
        """
        Calculate wave flow state from OHLCV
        
        Args:
            ohlcv: DataFrame with OHLCV data
            bar_id: Optional bar ID for backtest determinism
            venue_features: Optional venue-specific features (spread, funding, etc.)
        
        Returns:
            WaveFlowOutput with scores, state, and confidence
        """
        try:
            # Extract core features
            features = self.feature_extractor.extract_all_features(ohlcv)
            
            # Add venue features if provided
            if venue_features:
                features.update(venue_features)
            
            # Calculate wave flow score
            wave_flow_score = self._calc_wave_flow_score(features)
            
            # Calculate chaos score
            chaos_score = self._calc_chaos_score(features)
            
            # Classify state (with hysteresis)
            state = self._classify_state(wave_flow_score, chaos_score)
            
            # Calculate confidence
            confidence = self._calc_confidence(features, wave_flow_score, chaos_score)
            
            # Store state history for hysteresis
            self.state_history.append(state)
            if len(self.state_history) > self.state_history_size:
                self.state_history.pop(0)
            
            return WaveFlowOutput(
                wave_flow_score=wave_flow_score,
                chaos_score=chaos_score,
                state=state,
                components=features,
                confidence=confidence,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"Wave flow calculation error: {e}")
            return self._get_fallback_output(bar_id)
    
    def _calc_wave_flow_score(self, features: Dict[str, float]) -> float:
        """
        Calculate wave flow score [0,1]
        
        High score = clean impulse with:
        - High acceleration
        - Range expansion
        - Good trend structure
        - Low overlap
        - Low wick pressure
        """
        score = 0.0
        total_weight = 0.0
        
        for feature_name, weight in self.wave_flow_weights.items():
            if feature_name in features:
                feature_val = features[feature_name]
                
                # Handle negative weights (invert feature value)
                if weight < 0:
                    contribution = abs(weight) * (1.0 - feature_val)
                else:
                    contribution = weight * feature_val
                
                score += contribution
                total_weight += abs(weight)
        
        # Normalize
        normalized_score = score / total_weight if total_weight > 0 else 0.5
        
        return float(np.clip(normalized_score, 0.0, 1.0))
    
    def _calc_chaos_score(self, features: Dict[str, float]) -> float:
        """
        Calculate chaos score [0,1]
        
        High score = chaotic market:
        - High wick pressure (rejection)
        - High candle overlap (chop)
        - Mean reversion pull
        - Volatility spikes
        """
        score = 0.0
        total_weight = 0.0
        
        for feature_name, weight in self.chaos_weights.items():
            if feature_name in features:
                feature_val = features[feature_name]
                contribution = weight * feature_val
                
                score += contribution
                total_weight += weight
        
        # Normalize
        normalized_score = score / total_weight if total_weight > 0 else 0.5
        
        return float(np.clip(normalized_score, 0.0, 1.0))
    
    def _classify_state(self, wave_flow_score: float, chaos_score: float) -> WaveState:
        """
        Classify wave state with hysteresis
        
        Rules:
        - CHAOS: chaos_score > 0.7
        - IMPULSE: wave_flow_score > 0.6 AND chaos_score < 0.5
        - CORRECTIVE: Everything else
        
        Hysteresis: Require 2 consecutive classifications to change state
        """
       # Determine raw state
        if chaos_score > 0.7:
            raw_state = WaveState.CHAOS
        elif wave_flow_score > 0.6 and chaos_score < 0.5:
            raw_state = WaveState.IMPULSE
        else:
            raw_state = WaveState.CORRECTIVE
        
        # Apply hysteresis
        if len(self.state_history) == 0:
            return raw_state
        
        # Check if state is different from current
        current_state = self.state_history[-1]
        if raw_state != current_state:
            # Count recent occurrences of raw_state
            recent_count = sum(1 for s in self.state_history[-2:] if s == raw_state)
            
            # Require at least 1 previous occurrence to switch
            if recent_count >= 1:
                return raw_state
            else:
                # Stick with current state (hysteresis)
                return current_state
        
        return raw_state
    
    def _calc_confidence(self, features: Dict[str, float], 
                        wave_flow_score: float, chaos_score: float) -> float:
        """
        Calculate confidence in wave state classification
        
        High confidence when:
        - Scores are extreme (close to 0 or 1)
        - Features are consistent
        """
        # Confidence based on score extremity
        wave_extremity = abs(wave_flow_score - 0.5) * 2  # 0 at center, 1 at edges
        chaos_extremity = abs(chaos_score - 0.5) * 2
        
        score_confidence = (wave_extremity + chaos_extremity) / 2
        
        # Confidence based on feature consistency
        feature_std = np.std(list(features.values())) if features else 0.5
        feature_confidence = 1.0 - min(feature_std, 0.5) * 2  # Normalize
        
        # Combined confidence
        confidence = (score_confidence * 0.7 + feature_confidence * 0.3)
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _get_fallback_output(self, bar_id: Optional[int] = None) -> WaveFlowOutput:
        """Return safe fallback output when calculation fails"""
        return WaveFlowOutput(
            wave_flow_score=0.5,
            chaos_score=0.5,
            state=WaveState.CORRECTIVE,  # Safe default
            components={},
            confidence=0.0,  # Low confidence
            timestamp=datetime.now(),
            bar_id=bar_id
        )
    
    def get_state_history(self) -> List[str]:
        """Get recent state history for debugging"""
        return [s.value for s in self.state_history]
