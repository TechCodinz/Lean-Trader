"""
DEX (Decentralized Exchange) Feature Adapter

Extracts market stress features from DEX/AMM data
"""

import logging
import numpy as np
from typing import Dict
from ..models import MarketState

logger = logging.getLogger(__name__)


class DEXAdapter:
    """
    Extract features from DEX/AMM market data
    
    Common features:
    - volatility_level
    - volatility_slope
    - momentum_acceleration
    - range_expansion
    - microstructure_noise
    
    DEX-specific:
    - pool_liquidity_score
    - price_impact_estimate
    - gas_stress_score
    - mev_risk_proxy
    """
    
    def __init__(self):
        self.name = "DEXAdapter"
        # Typical gas ranges for stress detection (gwei)
        self.gas_normal = 30
        self.gas_high = 100
        logger.info(f"[OK] {self.name} initialized")
    
    def extract_features(self, market_state: MarketState) -> Dict[str, float]:
        """Extract all available features from DEX data"""
        features = {}
        
        try:
            prices = np.array(market_state.price_series)
            
            # === COMMON FEATURES ===
            features['volatility_level'] = self._calc_volatility_level(prices)
            features['volatility_slope'] = self._calc_volatility_slope(prices)
            features['momentum_acceleration'] = self._calc_momentum_acceleration(prices)
            features['range_expansion'] = self._calc_range_expansion(prices)
            features['microstructure_noise'] = self._calc_microstructure_noise(prices)
            
            # === DEX-SPECIFIC ===
            if market_state.pool_liquidity is not None:
                features['pool_liquidity_score'] = self._calc_pool_liquidity_score(
                    market_state.pool_liquidity
                )
                features['price_impact_estimate'] = self._calc_price_impact(
                    market_state.pool_liquidity, prices[-1]
                )
            else:
                features['pool_liquidity_score'] = np.nan
                features['price_impact_estimate'] = np.nan
            
            if market_state.gas_price is not None:
                features['gas_stress_score'] = self._calc_gas_stress(market_state.gas_price)
            else:
                features['gas_stress_score'] = np.nan
            
            # MEV risk combines liquidity, volatility, and gas
            features['mev_risk_proxy'] = self._calc_mev_risk(
                market_state.pool_liquidity,
                features['volatility_level'],
                market_state.gas_price
            )
            
            logger.debug(f"DEX features: {len([v for v in features.values() if not np.isnan(v)])}/{len(features)}")
            
        except Exception as e:
            logger.error(f"DEX feature extraction error: {e}")
            return {k: np.nan for k in [
                'volatility_level', 'volatility_slope', 'momentum_acceleration',
                'range_expansion', 'microstructure_noise', 'pool_liquidity_score',
                'price_impact_estimate', 'gas_stress_score', 'mev_risk_proxy'
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
    
    def _calc_pool_liquidity_score(self, liquidity: float) -> float:
        """
        Pool liquidity stress (inverse)
        Lower liquidity = higher stress
        
        Returns: stress score (0 = high liq, 1 = low liq)
        """
        # Normalize: typical pool ranges from $10k to $10M
        # Log scale
        if liquidity <= 0:
            return 1.0  # No liquidity = max stress
        
        log_liq = np.log10(liquidity)
        # Map: $10k (4) -> 1.0, $10M (7) -> 0.0
        stress = max(0, min(1, (7 - log_liq) / 3))
        return stress
    
    def _calc_price_impact(self, liquidity: float, price: float) -> float:
        """
        Estimated price impact for typical trade size
        Assumes $1000 trade
        """
        if liquidity is None or liquidity <= 0 or price <= 0:
            return np.nan
        
        trade_size = 1000  # USD
        # Constant product: impact ≈ trade_size / liquidity
        impact = trade_size / liquidity
        return min(impact, 1.0)  # Cap at 100%
    
    def _calc_gas_stress(self, gas_price: float) -> float:
        """
        Gas price stress
        Normal = 30 gwei, High = 100+ gwei
        """
        if gas_price <= self.gas_normal:
            return 0.0
        if gas_price >= self.gas_high:
            return 1.0
        # Linear interpolation
        return (gas_price - self.gas_normal) / (self.gas_high - self.gas_normal)
    
    def _calc_mev_risk(self, liquidity: float, volatility: float, gas: float) -> float:
        """
        MEV risk proxy
        High MEV risk when: low liquidity + high volatility + high gas
        """
        components = []
        
        if liquidity is not None:
            liq_risk = self._calc_pool_liquidity_score(liquidity)
            components.append(liq_risk)
        
        if not np.isnan(volatility):
            # Normalize volatility: assume 0-10% is 0-1
            vol_risk = min(volatility / 0.10, 1.0)
            components.append(vol_risk)
        
        if gas is not None:
            gas_risk = self._calc_gas_stress(gas)
            components.append(gas_risk)
        
        if not components:
            return np.nan
        
        # Geometric mean (all must be high for high MEV risk)
        return np.prod(components) ** (1 / len(components))
