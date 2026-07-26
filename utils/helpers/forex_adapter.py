"""
FOREX/CFD Feature Adapter

Extracts market stress features from forex broker data
"""

import logging
import numpy as np
from typing import Dict
from ..models import MarketState

logger = logging.getLogger(__name__)


class ForexAdapter:
    """
    Extract features from FOREX/CFD market data
    
    Common features:
    - volatility_level
    - volatility_slope
    - momentum_acceleration
    - range_expansion
    - microstructure_noise
    
    Forex-specific:
    - spread_pressure
    - session_energy (ASIA/LONDON/NY)
    - spike_guard_score (TR outlier detection)
    """
    
    def __init__(self):
        self.name = "ForexAdapter"
        self.session_mult = {
            'ASIA': 0.7,   # Lower volatility
            'LONDON': 1.2,  # Higher volatility
            'NY': 1.0,      # Normal
            'LONDON_NY_OVERLAP': 1.5  # Highest
        }
        logger.info(f"[OK] {self.name} initialized")
    
    def extract_features(self, market_state: MarketState) -> Dict[str, float]:
        """Extract all available features from forex data"""
        features = {}
        
        try:
            prices = np.array(market_state.price_series)
            
            # === COMMON FEATURES ===
            features['volatility_level'] = self._calc_volatility_level(prices)
            features['volatility_slope'] = self._calc_volatility_slope(prices)
            features['momentum_acceleration'] = self._calc_momentum_acceleration(prices)
            features['range_expansion'] = self._calc_range_expansion(prices)
            features['microstructure_noise'] = self._calc_microstructure_noise(prices)
            
            # === FOREX-SPECIFIC ===
            if market_state.spread is not None:
                features['spread_pressure'] = self._calc_spread_pressure(
                    market_state.spread, prices[-1]
                )
            else:
                features['spread_pressure'] = np.nan
            
            features['session_energy'] = self._calc_session_energy(market_state.session)
            features['spike_guard_score'] = self._calc_spike_guard(prices)
            
            logger.debug(f"Forex features: {len([v for v in features.values() if not np.isnan(v)])}/{len(features)}")
            
        except Exception as e:
            logger.error(f"Forex feature extraction error: {e}")
            return {k: np.nan for k in [
                'volatility_level', 'volatility_slope', 'momentum_acceleration',
                'range_expansion', 'microstructure_noise', 'spread_pressure',
                'session_energy', 'spike_guard_score'
            ]}
        
        return features
    
    def _calc_volatility_level(self, prices: np.ndarray) -> float:
        """ATR as % of price"""
        if len(prices) < 2:
            return np.nan
        tr = np.abs(np.diff(prices)) / prices[:-1]
        return np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
    
    def _calc_volatility_slope(self, prices: np.ndarray) -> float:
        """Vol acceleration"""
        if len(prices) < 20:
            return 0.0
        tr = np.abs(np.diff(prices)) / prices[:-1]
        if len(tr) < 20:
            return 0.0
        recent = np.std(tr[-10:])
        past = np.std(tr[-20:-10])
        return (recent - past) / past if past != 0 else 0.0
    
    def _calc_momentum_acceleration(self, prices: np.ndarray) -> float:
        """Price jerk"""
        if len(prices) < 3:
            return 0.0
        returns = np.diff(prices) / prices[:-1]
        if len(returns) < 2:
            return 0.0
        momentum = np.diff(returns)
        return np.mean(momentum[-5:]) if len(momentum) >= 5 else np.mean(momentum)
    
    def _calc_range_expansion(self, prices: np.ndarray) -> float:
        """BB width slope"""
        if len(prices) < 20:
            return 0.0
        window = 20
        recent_std = np.std(prices[-window:])
        if len(prices) >= window * 2:
            past_std = np.std(prices[-window*2:-window])
            return (recent_std - past_std) / past_std if past_std != 0 else 0.0
        return 0.0
    
    def _calc_microstructure_noise(self, prices: np.ndarray) -> float:
        """Choppiness"""
        if len(prices) < 5:
            return 0.0
        returns = np.diff(prices) / prices[:-1]
        if len(returns) < 2:
            return 0.0
        sign_changes = np.sum(np.diff(np.sign(returns)) != 0)
        max_changes = len(returns) - 1
        return sign_changes / max_changes if max_changes > 0 else 0.0
    
    def _calc_spread_pressure(self, spread: float, price: float) -> float:
        """Spread as % of price"""
        return spread / price if price != 0 else np.nan
    
    def _calc_session_energy(self, session: str) -> float:
        """
        Energy multiplier based on forex session
        Higher = more volatility expected
        """
        if session is None:
            return 1.0  # Unknown session, assume normal
        return self.session_mult.get(session.upper(), 1.0)
    
    def _calc_spike_guard(self, prices: np.ndarray) -> float:
        """
        Detect abnormal price spikes (TR outliers)
        Returns: zscore of recent TR vs historical
        """
        if len(prices) < 20:
            return 0.0
        
        tr = np.abs(np.diff(prices)) / prices[:-1]
        if len(tr) < 20:
            return 0.0
        
        recent_tr = tr[-1]
        historical_mean = np.mean(tr[-20:-1])
        historical_std = np.std(tr[-20:-1])
        
        if historical_std == 0:
            return 0.0
        
        zscore = (recent_tr - historical_mean) / historical_std
        return max(0, zscore)  # Only positive (expansion)
