"""
Liquidity Gravity Fields Engine

Identifies price magnets (support/resistance clusters) and sweep risks.
Maps the "gravity field" of liquidity zones that attract price action.

Methodology:
- Swing clustering: Recent pivot highs/lows create magnetic zones
- Wick concentration: Rejection wicks cluster at liquidity levels
- Time-at-price: Approximate volume-at-price via candle body distribution
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..models import LiquidityMagnet, LiquidityFieldOutput

logger = logging.getLogger(__name__)


class LiquidityGravityEngine:
    """
    Quantitative liquidity magnet detection
    
    Identifies price levels with high liquidity (stop clusters)
    """
    
    def __init__(self,
                 swing_window: int = 50,
                 wick_threshold: float = 0.5,
                 magnet_strength_threshold: float = 0.3):
        """
        Initialize Liquidity Gravity Engine
        
        Args:
            swing_window: Window for swing high/low detection
            wick_threshold: Min wick size (% of range) to count
            magnet_strength_threshold: Min strength to report magnet
        """
        self.swing_window = swing_window
        self.wick_threshold = wick_threshold
        self.magnet_strength_threshold = magnet_strength_threshold
        
        logger.info("[OK] LiquidityGr avityEngine initialized")
        logger.info(f"   Swing window: {swing_window}")
        logger.info(f"   Wick threshold: {wick_threshold}")
    
    def calculate_liquidity_field(self,
                                  ohlcv: pd.DataFrame,
                                  current_price: float,
                                  bar_id: Optional[int] = None) -> LiquidityFieldOutput:
        """
        Calculate liquidity gravity field
        
        Args:
            ohlcv: DataFrame with OHLCV data
            current_price: Current market price
            bar_id: Optional bar ID for determinism
        
        Returns:
            LiquidityFieldOutput with magnets and sweep risks
        """
        try:
            if len(ohlcv) < self.swing_window:
                return self._get_neutral_output(current_price, bar_id)
            
            # Detect magnets from different sources
            swing_magnets = self._detect_swing_magnets(ohlcv, current_price)
            wick_magnets = self._detect_wick_magnets(ohlcv, current_price)
            time_magnets = self._detect_time_magnets(ohlcv, current_price)
            
            # Combine and deduplicate
            all_magnets = swing_magnets + wick_magnets + time_magnets
            merged_magnets = self._merge_nearby_magnets(all_magnets, current_price)
            
            # Sort by distance
            merged_magnets.sort(key=lambda m: m.distance)
            
            # Keep top magnets
            nearest_magnets = merged_magnets[:10]
            
            # Calculate gravity vector
            gravity_vector = self._calc_gravity_vector(nearest_magnets, current_price)
            
            # Calculate sweep risk
            sweep_risk = self._calc_sweep_risk(nearest_magnets, ohlcv, current_price)
            
            # Find nearest support/resistance
            support_strength, resistance_strength = self._calc_support_resistance(
                nearest_magnets, current_price
            )
            
            # Confidence
            confidence = self._calc_confidence(len(nearest_magnets), ohlcv)
            
            components = {
                'swing_magnet_count': len(swing_magnets),
                'wick_magnet_count': len(wick_magnets),
                'time_magnet_count': len(time_magnets),
                'total_magnets': len(nearest_magnets)
            }
            
            return LiquidityFieldOutput(
                nearest_magnets=nearest_magnets,
                gravity_vector=gravity_vector,
                sweep_risk=sweep_risk,
                support_strength=support_strength,
                resistance_strength=resistance_strength,
                components=components,
                confidence=confidence,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"Liquidity field calculation error: {e}")
            return self._get_neutral_output(current_price, bar_id)
    
    def _detect_swing_magnets(self,
                             ohlcv: pd.DataFrame,
                             current_price: float) -> List[LiquidityMagnet]:
        """
        Detect swing high/low magnets
        
        Pivot points are natural liquidity zones (stop clusters)
        """
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        
        magnets = []
        window = min(5, len(high) // 10)  # Pivot detection window
        
        # Find swing highs
        for i in range(window, len(high) - window):
            is_swing_high = True
            for j in range(i - window, i + window + 1):
                if j != i and high[j] >= high[i]:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                # Count how many times this level was tested
                tests = sum(1 for h in high[i+1:] if abs(h - high[i]) / high[i] < 0.005)
                strength = min(0.3 + tests * 0.15, 1.0)
                
                distance = abs(high[i] - current_price) / current_price
                
                magnets.append(LiquidityMagnet(
                    price_level=high[i],
                    strength=strength,
                    distance=distance,
                    magnet_type="swing_high"
                ))
        
        # Find swing lows
        for i in range(window, len(low) - window):
            is_swing_low = True
            for j in range(i - window, i + window + 1):
                if j != i and low[j] <= low[i]:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                tests = sum(1 for l in low[i+1:] if abs(l - low[i]) / low[i] < 0.005)
                strength = min(0.3 + tests * 0.15, 1.0)
                
                distance = abs(low[i] - current_price) / current_price
                
                magnets.append(LiquidityMagnet(
                    price_level=low[i],
                    strength=strength,
                    distance=distance,
                    magnet_type="swing_low"
                ))
        
        return magnets
    
    def _detect_wick_magnets(self,
                            ohlcv: pd.DataFrame,
                            current_price: float) -> List[LiquidityMagnet]:
        """
        Detect wick concentration zones
        
        Large wicks indicate rejection → liquidity zones
        """
        open_vals = ohlcv['open'].values
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        close = ohlcv['close'].values
        
        wick_levels = []
        
        for i in range(len(ohlcv)):
            candle_range = high[i] - low[i]
            if candle_range == 0:
                continue
            
            body_high = max(open_vals[i], close[i])
            body_low = min(open_vals[i], close[i])
            
            upper_wick = high[i] - body_high
            lower_wick = body_low - low[i]
            
            # Significant upper wick
            if upper_wick / candle_range > self.wick_threshold:
                wick_levels.append(high[i])
            
            # Significant lower wick
            if lower_wick / candle_range > self.wick_threshold:
                wick_levels.append(low[i])
        
        # Cluster wick levels
        if not wick_levels:
            return []
        
        wick_levels = np.array(wick_levels)
        clusters = self._cluster_levels(wick_levels, current_price)
        
        magnets = []
        for level, count in clusters:
            strength = min(0.2 + count * 0.1, 1.0)
            distance = abs(level - current_price) / current_price
            
            magnets.append(LiquidityMagnet(
                price_level=level,
                strength=strength,
                distance=distance,
                magnet_type="wick_cluster"
            ))
        
        return magnets
    
    def _detect_time_magnets(self,
                            ohlcv: pd.DataFrame,
                            current_price: float) -> List[LiquidityMagnet]:
        """
        Detect time-at-price magnets (volume profile approximation)
        
        Use candle body distribution as proxy for time spent at levels
        """
        open_vals = ohlcv['open'].values
        close = ohlcv['close'].values
        
        # Create price bins
        all_prices = np.concatenate([open_vals, close])
        min_price = np.min(all_prices)
        max_price = np.max(all_prices)
        
        if max_price == min_price:
            return []
        
        bins = 20
        hist, edges = np.histogram(all_prices, bins=bins, range=(min_price, max_price))
        
        # Find high-volume bins
        threshold = np.percentile(hist, 70)
        
        magnets = []
        for i, count in enumerate(hist):
            if count >= threshold:
                level = (edges[i] + edges[i+1]) / 2
                strength = min(count / np.max(hist), 1.0) * 0.6
                distance = abs(level - current_price) / current_price
                
                magnets.append(LiquidityMagnet(
                    price_level=level,
                    strength=strength,
                    distance=distance,
                    magnet_type="time_cluster"
                ))
        
        return magnets
    
    def _cluster_levels(self,
                       levels: np.ndarray,
                       current_price: float) -> List[tuple]:
        """
        Cluster nearby price levels
        
        Returns [(level, count)]
        """
        if len(levels) == 0:
            return []
        
        # Sort levels
        sorted_levels = np.sort(levels)
        
        clusters = []
        current_cluster = [sorted_levels[0]]
        
        cluster_tolerance = current_price * 0.005  # 0.5% clustering
        
        for level in sorted_levels[1:]:
            if level - current_cluster[-1] < cluster_tolerance:
                current_cluster.append(level)
            else:
                # Finish current cluster
                clusters.append((np.mean(current_cluster), len(current_cluster)))
                current_cluster = [level]
        
        # Add last cluster
        if current_cluster:
            clusters.append((np.mean(current_cluster), len(current_cluster)))
        
        return clusters
    
    def _merge_nearby_magnets(self,
                             magnets: List[LiquidityMagnet],
                             current_price: float) -> List[LiquidityMagnet]:
        """
        Merge magnets that are very close together
        """
        if not magnets:
            return []
        
        # Sort by price
        sorted_magnets = sorted(magnets, key=lambda m: m.price_level)
        
        merged = []
        current_group = [sorted_magnets[0]]
        
        merge_tolerance = current_price * 0.003  # 0.3% merge distance
        
        for magnet in sorted_magnets[1:]:
            if magnet.price_level - current_group[-1].price_level < merge_tolerance:
                current_group.append(magnet)
            else:
                # Merge current group
                merged.append(self._merge_group(current_group))
                current_group = [magnet]
        
        # Merge last group
        if current_group:
            merged.append(self._merge_group(current_group))
        
        return merged
    
    def _merge_group(self, group: List[LiquidityMagnet]) -> LiquidityMagnet:
        """Merge a group of magnets into one"""
        avg_price = np.mean([m.price_level for m in group])
        total_strength = sum(m.strength for m in group) / len(group)  # Average strength
        avg_distance = np.mean([m.distance for m in group])
        
        # Type priority: swing > wick > time
        types = [m.magnet_type for m in group]
        if "swing_high" in types or "swing_low" in types:
            magnet_type = types[0]
        elif "wick_cluster" in types:
            magnet_type = "wick_cluster"
        else:
            magnet_type = "time_cluster"
        
        return LiquidityMagnet(
            price_level=avg_price,
            strength=min(total_strength, 1.0),
            distance=avg_distance,
            magnet_type=magnet_type
        )
    
    def _calc_gravity_vector(self,
                            magnets: List[LiquidityMagnet],
                            current_price: float) -> float:
        """
        Calculate gravity vector [-1, +1]
        
        Negative = pulled down
        Positive = pulled up
        """
        if not magnets:
            return 0.0
        
        weighted_pull = 0.0
        total_weight = 0.0
        
        for magnet in magnets:
            # Strength inversely proportional to distance
            weight = magnet.strength / (1.0 + magnet.distance * 10)
            
            # Direction
            direction = 1.0 if magnet.price_level > current_price else -1.0
            
            weighted_pull += direction * weight
            total_weight += weight
        
        gravity = weighted_pull / total_weight if total_weight > 0 else 0.0
        
        return float(np.clip(gravity, -1.0, 1.0))
    
    def _calc_sweep_risk(self,
                        magnets: List[LiquidityMagnet],
                        ohlcv: pd.DataFrame,
                        current_price: float) -> float:
        """
        Calculate stop sweep risk [0, 1]
        
        High if we're approaching strong magnet with weak momentum
        """
        if not magnets:
            return 0.0
        
        # Find nearest strong magnet
        strong_magnets = [m for m in magnets if m.strength > 0.5]
        if not strong_magnets:
            return 0.0
        
        nearest = strong_magnets[0]
        
        # Risk increases as we approach magnet
        proximity_risk = 1.0 - min(nearest.distance / 0.02, 1.0)  # Max at 2% distance
        
        # Check momentum (are we moving toward it?)
        close = ohlcv['close'].values
        if len(close) < 3:
            momentum_aligned = 0.5
        else:
            recent_direction = 1.0 if close[-1] > close[-3] else -1.0
            magnet_direction = 1.0 if nearest.price_level > current_price else -1.0
            momentum_aligned = 1.0 if recent_direction == magnet_direction else 0.0
        
        sweep_risk = proximity_risk * 0.6 + momentum_aligned * 0.4
        
        return float(np.clip(sweep_risk * nearest.strength, 0.0, 1.0))
    
    def _calc_support_resistance(self,
                                magnets: List[LiquidityMagnet],
                                current_price: float) -> tuple:
        """
        Calculate nearest support and resistance strength
        
        Returns: (support_strength, resistance_strength)
        """
        if not magnets:
            return 0.5, 0.5
        
        support_magnets = [m for m in magnets if m.price_level < current_price]
        resistance_magnets = [m for m in magnets if m.price_level > current_price]
        
        support_strength = max([m.strength for m in support_magnets], default=0.0)
        resistance_strength = max([m.strength for m in resistance_magnets], default=0.0)
        
        return float(support_strength), float(resistance_strength)
    
    def _calc_confidence(self, magnet_count: int, ohlcv: pd.DataFrame) -> float:
        """Calculate confidence based on magnet count and data quality"""
        # More magnets = higher confidence (up to a point)
        magnet_confidence = min(magnet_count / 5.0, 1.0)
        
        # More data = higher confidence
        data_confidence = min(len(ohlcv) / (self.swing_window * 2), 1.0)
        
        return float((magnet_confidence + data_confidence) / 2.0)
    
    def _get_neutral_output(self,
                           current_price: float,
                           bar_id: Optional[int] = None) -> LiquidityFieldOutput:
        """Return neutral output when calculation fails"""
        return LiquidityFieldOutput(
            nearest_magnets=[],
            gravity_vector=0.0,
            sweep_risk=0.5,
            support_strength=0.5,
            resistance_strength=0.5,
            components={},
            confidence=0.0,
            timestamp=datetime.now(),
            bar_id=bar_id
        )
