"""
Core Pitch Engine

Combines venue adapter features into a single pitch value [0, 1]
"""

import logging
import numpy as np
from collections import deque
from typing import Dict, Optional
from ..models import MarketState, PitchOutput, PitchConfig, VenueType
from ..adapters.cex_adapter import CEXAdapter
from ..adapters.forex_adapter import ForexAdapter
from ..adapters.dex_adapter import DEXAdapter

logger = logging.getLogger(__name__)

# Wave Flow Engine (optional import)
try:
    from .wave_flow_engine import WaveFlowEngine
    WAVE_FLOW_AVAILABLE = True
except ImportError:
    WAVE_FLOW_AVAILABLE = False
    logger.warning("Wave Flow Engine not available - pitch will work without wave state")


class PitchEngine:
    """
    Converts market features into continuous pitch scalar
    
    Flow:
    1. Route to appropriate adapter based on venue
    2. Extract raw features
    3. Normalize features to [0, 1]
    4. Weighted combination
    5. Smooth + hysteresis
    6. Output PitchOutput with regime label
    """
    
    def __init__(self, config: Optional[PitchConfig] = None, seed: Optional[int] = None):
        self.config = config or PitchConfig()
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)
        
        # Adapters
        self.adapters = {
            VenueType.CEX: CEXAdapter(),
            VenueType.FOREX: ForexAdapter(),
            VenueType.DEX: DEXAdapter()
        }
        
        # Rolling statistics for normalization
        self.feature_history = {}  # feature_name -> deque of values
        self.max_history = self.config.rolling_window
        
        # Smoothing state
        self.last_pitch = 0.0
        self.last_regime = "normal"
        
        logger.info(f"[OK] PitchEngine initialized (normalize={self.config.normalize_method})")
        
        # Initialize Wave Flow Engine (optional)
        self.wave_flow_engine = None
        if WAVE_FLOW_AVAILABLE:
            try:
                self.wave_flow_engine = WaveFlowEngine(feature_window=20)
                logger.info("[OK] Wave Flow Engine enabled")
            except Exception as e:
                logger.warning(f"Wave Flow Engine init failed: {e}")
    
    def calculate_pitch(self, market_state: MarketState, 
                       feature_weights: Optional[Dict[str, float]] = None) -> PitchOutput:
        """
        Calculate pitch from market state
        
        Args:
            market_state: Current market data
            feature_weights: Optional override for feature weights
            
        Returns:
            PitchOutput with pitch value and metadata
        """
        # 1. Extract raw features
        adapter = self.adapters[market_state.venue_type]
        raw_features = adapter.extract_features(market_state)
        
        # 2. Normalize features
        normalized = self._normalize_features(raw_features)
        
        # 3. Calculate weighted combination
        weights = feature_weights or self.config.feature_weights
        if not weights:
            # Fallback: equal weights
            weights = {k: 1.0 for k in normalized.keys()}
        
        pitch_raw = self._combine_features(normalized, weights)
        
        # 4. Smooth
        pitch_smooth = self._smooth_pitch(pitch_raw)
        
        # 5. Regime + hysteresis
        regime = self._determine_regime(pitch_smooth)
        
        # 6. Confidence based on feature availability
        confidence = self._calculate_confidence(raw_features)
        
        # 7. Calculate Wave Flow (if available)
        wave_output = None
        if self.wave_flow_engine and hasattr(market_state, 'ohlcv'):
            try:
                import pandas as pd
                # Convert price_series to OHLCV DataFrame if needed
                if isinstance(market_state.ohlcv, pd.DataFrame):
                    wave_output = self.wave_flow_engine.calculate_wave_flow(
                        market_state.ohlcv,
                        bar_id=getattr(market_state, 'bar_id', None)
                    )
            except Exception as e:
                logger.debug(f"Wave flow calculation skipped: {e}")
        
        # Create output with wave data
        output = PitchOutput(
            pitch_value=pitch_smooth,
            components=normalized,
            confidence=confidence,
            regime=regime,
            bar_id=getattr(market_state, 'bar_id', None),
            # Wave Flow fields (optional)
            wave_state=wave_output.state.value if wave_output else None,
            wave_flow_score=wave_output.wave_flow_score if wave_output else None,
            chaos_score=wave_output.chaos_score if wave_output else None
        )
        
        self.last_pitch = pitch_smooth
        self.last_regime = regime
        
        logger.debug(f"Pitch: {pitch_smooth:.3f} regime={regime} conf={confidence:.2f}")
        
        return output
    
    def _normalize_features(self, raw_features: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize features to [0, 1] using configured method
        """
        normalized = {}
        
        for name, value in raw_features.items():
            if np.isnan(value):
                normalized[name] = 0.0  # Missing feature = neutral
                continue
            
            # Update history
            if name not in self.feature_history:
                self.feature_history[name] = deque(maxlen=self.max_history)
            self.feature_history[name].append(value)
            
            # Normalize
            if self.config.normalize_method == "robust_zscore":
                norm_val = self._robust_zscore_normalize(name, value)
            elif self.config.normalize_method == "rolling_minmax":
                norm_val = self._rolling_minmax_normalize(name, value)
            else:
                norm_val = value  # Pass through
            
            normalized[name] = np.clip(norm_val, 0.0, 1.0)
        
        return normalized
    
    def _robust_zscore_normalize(self, feature_name: str, value: float) -> float:
        """
        Robust z-score normalization with clipping
        Maps: mean -> 0.5, +3std -> 1.0, -3std -> 0.0
        """
        history = list(self.feature_history[feature_name])
        if len(history) < 2:
            return 0.5  # Insufficient history, neutral
        
        mean = np.mean(history)
        std = np.std(history)
        
        if std == 0:
            return 0.5
        
        zscore = (value - mean) / std
        # Clip to ±3 std
        zscore = np.clip(zscore, -self.config.zscore_clip, self.config.zscore_clip)
        
        # Map [-3, +3] -> [0, 1]
        normalized = (zscore + self.config.zscore_clip) / (2 * self.config.zscore_clip)
        return normalized
    
    def _rolling_minmax_normalize(self, feature_name: str, value: float) -> float:
        """
        Rolling min-max normalization
        Maps: [min, max] of history -> [0, 1]
        """
        history = list(self.feature_history[feature_name])
        if len(history) < 2:
            return 0.5
        
        min_val = np.min(history)
        max_val = np.max(history)
        
        if max_val == min_val:
            return 0.5
        
        return (value - min_val) / (max_val - min_val)
    
    def _combine_features(self, normalized: Dict[str, float], 
                         weights: Dict[str, float]) -> float:
        """
        Weighted combination of normalized features
        """
        total_weight = 0.0
        weighted_sum = 0.0
        
        for feature_name, feature_value in normalized.items():
            weight = weights.get(feature_name, 0.0)
            if weight > 0:
                weighted_sum += feature_value * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def _smooth_pitch(self, pitch_raw: float) -> float:
        """
        EMA smoothing to avoid oscillation
        """
        alpha = self.config.ema_alpha
        return alpha * pitch_raw + (1 - alpha) * self.last_pitch
    
    def _determine_regime(self, pitch: float) -> str:
        """
        Map pitch to regime with hysteresis
        """
        thresholds = self.config.regime_thresholds
        hyst = self.config.hysteresis_threshold
        
        # Check for regime change with hysteresis
        if pitch < thresholds['calm'] - hyst:
            return "calm"
        elif pitch < thresholds['normal'] - hyst:
            return "normal" if self.last_regime != "calm" else "calm"
        elif pitch < thresholds['hot'] - hyst:
            return "normal"
        else:
            return "hot" if pitch < thresholds['hot'] + hyst else "chaotic"
    
    def _calculate_confidence(self, raw_features: Dict[str, float]) -> float:
        """
        Confidence based on feature availability and stability
        """
        total = len(raw_features)
        available = sum(1 for v in raw_features.values() if not np.isnan(v))
        
        if total == 0:
            return 0.0
        
        availability_score = available / total
        
        # Stability: if history exists, check recent variance
        stability_score = 1.0  # Default
        if self.feature_history:
            variances = []
            for name, hist in self.feature_history.items():
                if len(hist) >= 5:
                    recent_var = np.var(list(hist)[-5:])
                    variances.append(recent_var)
            if variances:
                avg_var = np.mean(variances)
                # Low variance = high stability
                stability_score = 1.0 / (1.0 + avg_var)
        
        return (availability_score + stability_score) / 2
