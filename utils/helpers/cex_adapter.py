"""
CEX (Centralized Exchange) Feature Adapter

Extracts market stress features from crypto exchanges
"""

import logging
import numpy as np
from typing import Dict, Optional
from ..models import MarketState

logger = logging.getLogger(__name__)


class CEXAdapter:
    """
    Extract features from CEX market data
    
    Common features across all venues:
    - volatility_level (ATR or TR-based)
    - volatility_slope
    - momentum_acceleration  
    - range_expansion
    - microstructure_noise
    
    CEX-specific:
    - spread_pressure
    - orderbook_imbalance
    - depth_to_spread_ratio
    - funding_pressure (for perps)
    """
    
    def __init__(self):
        self.name = "CEXAdapter"
        logger.info(f"[OK] {self.name} initialized")
    
    def extract_features(self, market_state: MarketState) -> Dict[str, float]:
        """
        Extract all available features from CEX market data
        
        Returns:
            Dict of feature_name -> raw_value
            Missing features return NaN (handled gracefully downstream)
        """
        features = {}
        
        try:
            prices = np.array(market_state.price_series)
            
            # === COMMON FEATURES ===
            features['volatility_level'] = self._calc_volatility_level(prices)
            features['volatility_slope'] = self._calc_volatility_slope(prices)
            features['momentum_acceleration'] = self._calc_momentum_acceleration(prices)
            features['range_expansion'] = self._calc_range_expansion(prices)
            features['microstructure_noise'] = self._calc_microstructure_noise(prices)
            
            # === CEX-SPECIFIC FEATURES ===
            if market_state.spread is not None:
                features['spread_pressure'] = self._calc_spread_pressure(
                    market_state.spread, prices[-1]
                )
            else:
                features['spread_pressure'] = np.nan
            
            if market_state.orderbook is not None:
                features['orderbook_imbalance'] = self._calc_orderbook_imbalance(
                    market_state.orderbook
                )
                features['depth_to_spread_ratio'] = self._calc_depth_to_spread(
                    market_state.orderbook, market_state.spread
                )
            else:
                features['orderbook_imbalance'] = np.nan
                features['depth_to_spread_ratio'] = np.nan
            
            if market_state.funding_rate is not None:
                features['funding_pressure'] = self._calc_funding_pressure(
                    market_state.funding_rate
                )
            else:
                features['funding_pressure'] = np.nan
            
            logger.debug(f"CEX features extracted: {len([v for v in features.values() if not np.isnan(v)])}/{len(features)}")
            
        except Exception as e:
            logger.error(f"CEX feature extraction error: {e}")
            # Return NaN features on error
            return {k: np.nan for k in [
                'volatility_level', 'volatility_slope', 'momentum_acceleration',
                'range_expansion', 'microstructure_noise', 'spread_pressure',
                'orderbook_imbalance', 'depth_to_spread_ratio', 'funding_pressure'
            ]}
        
        return features
    
    def _calc_volatility_level(self, prices: np.ndarray) -> float:
        """ATR-like: average true range as % of price"""
        if len(prices) < 2:
            return np.nan
        
        tr = np.abs(np.diff(prices)) / prices[:-1]
        atr_pct = np.mean(tr[-14:]) if len(tr) >= 14 else np.mean(tr)
        return atr_pct
    
    def _calc_volatility_slope(self, prices: np.ndarray) -> float:
        """Rate of change in volatility"""
        if len(prices) < 20:
            return 0.0
        
        tr = np.abs(np.diff(prices)) / prices[:-1]
        if len(tr) < 20:
            return 0.0
        
        recent_vol = np.std(tr[-10:])
        past_vol = np.std(tr[-20:-10])
        
        if past_vol == 0:
            return 0.0
        
        return (recent_vol - past_vol) / past_vol
    
    def _calc_momentum_acceleration(self, prices: np.ndarray) -> float:
        """Second derivative of price (jerk)"""
        if len(prices) < 3:
            return 0.0
        
        returns = np.diff(prices) / prices[:-1]
        if len(returns) < 2:
            return 0.0
        
        momentum = np.diff(returns)
        return np.mean(momentum[-5:]) if len(momentum) >= 5 else np.mean(momentum)
    
    def _calc_range_expansion(self, prices: np.ndarray) -> float:
        """Bollinger Band width slope (range expansion/contraction)"""
        if len(prices) < 20:
            return 0.0
        
        window = 20
        recent_std = np.std(prices[-window:])
        if len(prices) >= window * 2:
            past_std = np.std(prices[-window*2:-window])
            if past_std == 0:
                return 0.0
            return (recent_std - past_std) / past_std
        
        return 0.0
    
    def _calc_microstructure_noise(self, prices: np.ndarray) -> float:
        """Choppiness / wick ratio proxy"""
        if len(prices) < 5:
            return 0.0
        
        # High-freq reversals as proxy for noise
        returns = np.diff(prices) / prices[:-1]
        if len(returns) < 2:
            return 0.0
        
        sign_changes = np.sum(np.diff(np.sign(returns)) != 0)
        max_changes = len(returns) - 1
        
        if max_changes == 0:
            return 0.0
        
        return sign_changes / max_changes
    
    def _calc_spread_pressure(self, spread: float, price: float) -> float:
        """Bid-ask spread as % of price"""
        if price == 0:
            return np.nan
        return spread / price
    
    def _calc_orderbook_imbalance(self, orderbook: Dict) -> float:
        """Bid/ask volume imbalance"""
        try:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if not bids or not asks:
                return 0.0
            
            bid_vol = sum(b[1] for b in bids[:10])  # Top 10 levels
            ask_vol = sum(a[1] for a in asks[:10])
            
            total = bid_vol + ask_vol
            if total == 0:
                return 0.0
            
            return (bid_vol - ask_vol) / total
        except:
            return np.nan
    
    def _calc_depth_to_spread(self, orderbook: Dict, spread: Optional[float]) -> float:
        """Orderbook depth relative to spread (liquidity indicator)"""
        if spread is None or spread == 0:
            return np.nan
        
        try:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if not bids or not asks:
                return np.nan
            
            bid_depth = sum(b[1] for b in bids[:5])
            ask_depth = sum(a[1] for a in asks[:5])
            avg_depth = (bid_depth + ask_depth) / 2
            
            return avg_depth / spread
        except:
            return np.nan
    
    def _calc_funding_pressure(self, funding_rate: float) -> float:
        """Funding rate stress (for perps)"""
        # Normalize: typical funding is -0.01% to +0.01%
        # High magnitude = stress
        return abs(funding_rate) * 100  # Convert to basis points stress
