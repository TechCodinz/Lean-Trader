"""
Wave Flow Features

Quantitative feature extraction from OHLCV for wave state detection.
All features normalized to [0,1] using rolling robust normalization.
Works for CEX, FOREX, DEX (venue-agnostic core features).
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class WaveFlowFeatures:
    """
    Extract quantitative wave flow features from OHLCV
    
    Features:
    1. Velocity - Price movement speed relative to volatility
    2. Acceleration - Change in velocity (momentum building/fading)
    3. Range Expansion - Candle size growth vs historical
    4. Candle Overlap - Choppiness/consolidation measure
    5. Wick Pressure - Rejection/indecision indicator
    6. Trend Structure - Directional consistency
    7. Mean Reversion Pull - Snapback strength
    """
    
    def __init__(self, window: int = 20, normalization_window: int = 100):
        self.window = window
        self.norm_window = normalization_window
    
    def extract_all_features(self, ohlcv: pd.DataFrame) -> Dict[str, float]:
        """
        Extract all wave flow features from OHLCV
        
        Args:
            ohlcv: DataFrame with columns: open, high, low, close, volume
                   Sorted ascending by timestamp
        
        Returns:
            Dictionary of feature_name -> normalized_value [0,1]
        """
        if len(ohlcv) < self.window:
            logger.warning(f"Insufficient data: {len(ohlcv)} < {self.window}")
            return self._get_neutral_features()
        
        try:
            features = {}
            
            # Calculate raw features
            features['velocity'] = self._calc_velocity(ohlcv)
            features['acceleration'] = self._calc_acceleration(ohlcv)
            features['range_expansion'] = self._calc_range_expansion(ohlcv)
            features['candle_overlap'] = self._calc_candle_overlap(ohlcv)
            features['wick_pressure'] = self._calc_wick_pressure(ohlcv)
            features['trend_structure'] = self._calc_trend_structure(ohlcv)
            features['mean_reversion_pull'] = self._calc_mean_reversion_pull(ohlcv)
            
            # Normalize all features to [0,1]
            normalized = {}
            for name, value in features.items():
                normalized[name] = self._normalize_feature(name, value, ohlcv)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return self._get_neutral_features()
    
    def _calc_velocity(self, ohlcv: pd.DataFrame) -> float:
        """
        Velocity = abs(price change) / ATR
        High velocity = fast price movement relative to normal volatility
        """
        close = ohlcv['close'].values
        
        # Calculate ATR
        atr = self._calc_atr(ohlcv, self.window)
        
        if atr == 0:
            return 0.0
        
        # Current velocity
        price_change = abs(close[-1] - close[-2]) if len(close) > 1 else 0
        velocity = price_change / atr
        
        return velocity
    
    def _calc_acceleration(self, ohlcv: pd.DataFrame) -> float:
        """
        Acceleration = change in velocity
        Positive = momentum building, Negative = momentum fading
        """
        close = ohlcv['close'].values
        
        if len(close) < 3:
            return 0.0
        
        # Calculate velocity for last 2 bars
        atr = self._calc_atr(ohlcv, self.window)
        if atr == 0:
            return 0.0
        
        v1 = abs(close[-2] - close[-3]) / atr  # Previous velocity
        v2 = abs(close[-1] - close[-2]) / atr  # Current velocity
        
        acceleration = v2 - v1
        
        return acceleration
    
    def _calc_range_expansion(self, ohlcv: pd.DataFrame) -> float:
        """
        Range Expansion = (current range) / (median range over window)
        High = expanding ranges (breakout/impulse)
        Low = contracting ranges (consolidation)
        """
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        
        ranges = high - low
        
        if len(ranges) < self.window:
            return 1.0  # Neutral
        
        current_range = ranges[-1]
        median_range = np.median(ranges[-self.window:])
        
        if median_range == 0:
            return 1.0
        
        expansion = current_range / median_range
        
        return expansion
    
    def _calc_candle_overlap(self, ohlcv: pd.DataFrame) -> float:
        """
        Candle Overlap = overlap of consecutive candle bodies/ranges
        High overlap = choppy, low overlap = trending
        Returns: 0 = no overlap (trending), 1 = full overlap (choppy)
        """
        if len(ohlcv) < 2:
            return 0.5  # Neutral
        
        open_vals = ohlcv['open'].values
        close_vals = ohlcv['close'].values
        
        overlaps = []
        for i in range(1, min(len(ohlcv), self.window)):
            # Define body ranges
            body1_min = min(open_vals[-i-1], close_vals[-i-1])
            body1_max = max(open_vals[-i-1], close_vals[-i-1])
            body2_min = min(open_vals[-i], close_vals[-i])
            body2_max = max(open_vals[-i], close_vals[-i])
            
            # Calculate overlap
            overlap_min = max(body1_min, body2_min)
            overlap_max = min(body1_max, body2_max)
            overlap_range = max(0, overlap_max - overlap_min)
            
            # Normalize by average body size
            body1_size = body1_max - body1_min
            body2_size = body2_max - body2_min
            avg_size = (body1_size + body2_size) / 2
            
            if avg_size > 0:
                overlap_ratio = overlap_range / avg_size
                overlaps.append(min(overlap_ratio, 1.0))
        
        return np.mean(overlaps) if overlaps else 0.5
    
    def _calc_wick_pressure(self, ohlcv: pd.DataFrame) -> float:
        """
        Wick Pressure = (upper_wick + lower_wick) / candle_range
        High = rejection/indecision, Low = clean close
        """
        if len(ohlcv) < 1:
            return 0.5
        
        open_val = ohlcv['open'].values[-1]
        high_val = ohlcv['high'].values[-1]
        low_val = ohlcv['low'].values[-1]
        close_val = ohlcv['close'].values[-1]
        
        # Calculate wicks
        body_high = max(open_val, close_val)
        body_low = min(open_val, close_val)
        
        upper_wick = high_val - body_high
        lower_wick = body_low - low_val
        total_wick = upper_wick + lower_wick
        
        candle_range = high_val - low_val
        
        if candle_range == 0:
            return 1.0  # Max pressure (doji)
        
        wick_ratio = total_wick / candle_range
        
        return min(wick_ratio, 1.0)
    
    def _calc_trend_structure(self, ohlcv: pd.DataFrame) -> float:
        """
        Trend Structure = higher-high / higher-low consistency
        High = clean trend, Low = choppy/ranging
        """
        if len(ohlcv) < self.window:
            return 0.5
        
        high = ohlcv['high'].values[-self.window:]
        low = ohlcv['low'].values[-self.window:]
        
        # Count higher highs and higher lows (uptrend)
        hh_count = sum(1 for i in range(1, len(high)) if high[i] > high[i-1])
        hl_count = sum(1 for i in range(1, len(low)) if low[i] > low[i-1])
        
        # Count lower highs and lower lows (downtrend)
        lh_count = sum(1 for i in range(1, len(high)) if high[i] < high[i-1])
        ll_count = sum(1 for i in range(1, len(low)) if low[i] < low[i-1])
        
        # Structure score = max consistency direction
        uptrend_score = (hh_count + hl_count) / (2 * (len(high) - 1))
        downtrend_score = (lh_count + ll_count) / (2 * (len(high) - 1))
        
        structure_score = max(uptrend_score, downtrend_score)
        
        return structure_score
    
    def _calc_mean_reversion_pull(self, ohlcv: pd.DataFrame) -> float:
        """
        Mean Reversion Pull = zscore + snapback tendency
        High = strong pull to mean, Low = trending away
        """
        if len(ohlcv) < self.window:
            return 0.5
        
        close = ohlcv['close'].values[-self.window:]
        
        # Calculate zscore
        mean = np.mean(close)
        std = np.std(close)
        
        if std == 0:
            return 0.5
        
        current_zscore = abs((close[-1] - mean) / std)
        
        # Normalize zscore to [0,1] (2.0 = extreme)
        zscore_normalized = min(current_zscore / 2.0, 1.0)
        
        return zscore_normalized
    
    def _calc_atr(self, ohlcv: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        close = ohlcv['close'].values
        
        if len(close) < 2:
            return (high[-1] - low[-1]) if len(high) > 0 else 0.0
        
        tr_list = []
        for i in range(1, min(len(close), period + 1)):
            tr = max(
                high[-i] - low[-i],
                abs(high[-i] - close[-i-1]),
                abs(low[-i] - close[-i-1])
            )
            tr_list.append(tr)
        
        return np.mean(tr_list) if tr_list else 0.0
    
    def _normalize_feature(self, feature_name: str, value: float, ohlcv: pd.DataFrame) -> float:
        """
        Robust normalization to [0,1] using rolling percentile
        """
        # Feature-specific normalization ranges
        ranges = {
            'velocity': (0, 3.0),  # 0-3x ATR movement
            'acceleration': (-2.0, 2.0),  # Centered at 0
            'range_expansion': (0.5, 2.0),  # 0.5x to 2x median
            'candle_overlap': (0, 1.0),  # Already 0-1
            'wick_pressure': (0, 1.0),  # Already 0-1
            'trend_structure': (0, 1.0),  # Already 0-1
            'mean_reversion_pull': (0, 1.0)  # Already 0-1
        }
        
        min_val, max_val = ranges.get(feature_name, (0, 1))
        
        # Clip and normalize
        clipped = np.clip(value, min_val, max_val)
        normalized = (clipped - min_val) / (max_val - min_val) if max_val > min_val else 0.5
        
        return float(np.clip(normalized, 0.0, 1.0))
    
    def _get_neutral_features(self) -> Dict[str, float]:
        """Return neutral feature values (0.5) when data insufficient"""
        return {
            'velocity': 0.5,
            'acceleration': 0.5,
            'range_expansion': 0.5,
            'candle_overlap': 0.5,
            'wick_pressure': 0.5,
            'trend_structure': 0.5,
            'mean_reversion_pull': 0.5
        }
