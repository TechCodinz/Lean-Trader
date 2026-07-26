"""
Market Intent Inference Engine

Detects institutional intent through quantitative analysis:
- Absorption: Effort (volume/range) vs Result (price movement)
- Failed Impulses: Break attempts that snapback (traps)
- Followthrough: Post-break momentum quality
- Divergence: Price vs momentum misalignment

Works with OHLCV only, enhances with orderbook/volume when available.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
from datetime import datetime
import logging

from ..models import IntentOutput

logger = logging.getLogger(__name__)


class IntentEngine:
    """
    Quantitative market intent detection
    
    Identifies absorption, traps, and intent shifts
    """
    
    def __init__(self,
                 window: int = 20,
                 absorption_threshold: float = 0.6,
                 trap_threshold: float = 0.7):
        """
        Initialize Intent Engine
        
        Args:
            window: Lookback window for calculations
            absorption_threshold: Threshold for absorption detection
            trap_threshold: Threshold for trap detection
        """
        self.window = window
        self.absorption_threshold = absorption_threshold
        self.trap_threshold = trap_threshold
        
        logger.info("[OK] IntentEngine initialized")
        logger.info(f"   Window: {window}")
        logger.info(f"   Absorption threshold: {absorption_threshold}")
    
    def calculate_intent(self,
                        ohlcv: pd.DataFrame,
                        bar_id: Optional[int] = None,
                        orderbook: Optional[Dict] = None) -> IntentOutput:
        """
        Calculate market intent from OHLCV
        
        Args:
            ohlcv: DataFrame with OHLCV data
            bar_id: Optional bar ID for determinism
            orderbook: Optional orderbook data for enhancement
        
        Returns:
            IntentOutput with intent bias, strength, trap risk
        """
        try:
            if len(ohlcv) < self.window:
                return self._get_neutral_output(bar_id)
            
            # Calculate core components
            absorption_score = self._calc_absorption_score(ohlcv)
            failed_impulse_score = self._calc_failed_impulse_score(ohlcv)
            followthrough_score = self._calc_followthrough_score(ohlcv)
            divergence_score = self._calc_divergence_score(ohlcv)
            
            # Enhance with orderbook if available
            if orderbook:
                absorption_score = self._enhance_with_orderbook(
                    absorption_score, orderbook
                )
            
            # Derive intent bias and strength
            intent_bias = self._calc_intent_bias(
                absorption_score,
                failed_impulse_score,
                followthrough_score,
                divergence_score
            )
            
            intent_strength = self._calc_intent_strength(
                absorption_score,
                followthrough_score,
                divergence_score
            )
            
            # Calculate trap risk
            trap_risk = self._calc_trap_risk(
                failed_impulse_score,
                divergence_score,
                followthrough_score
            )
            
            # Confidence based on data quality
            confidence = self._calc_confidence(ohlcv)
            
            components = {
                'absorption': absorption_score,
                'failed_impulse': failed_impulse_score,
                'followthrough': followthrough_score,
                'divergence': divergence_score
            }
            
            return IntentOutput(
                intent_bias=intent_bias,
                intent_strength=intent_strength,
                trap_risk=trap_risk,
                absorption_score=absorption_score,
                failed_impulse_score=failed_impulse_score,
                followthrough_score=followthrough_score,
                divergence_score=divergence_score,
                components=components,
                confidence=confidence,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"Intent calculation error: {e}")
            return self._get_neutral_output(bar_id)
    
    def _calc_absorption_score(self, ohlcv: pd.DataFrame) -> float:
        """
        Absorption = Effort vs Result mismatch
        
        High effort (large range/volume) with small result (small close change)
        = absorption (institutional accumulation/distribution)
        
        Returns [0,1]: 0 = no absorption, 1 = strong absorption
        """
        close = ohlcv['close'].values
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        
        # Effort: Range expansion
        ranges = high - low
        recent_ranges = ranges[-self.window:]
        current_range = ranges[-1]
        median_range = np.median(recent_ranges)
        
        if median_range == 0:
            return 0.0
        
        effort = current_range / median_range  # High = large candle
        
        # Result: Price movement
        if len(close) < 2:
            return 0.0
        
        price_change = abs(close[-1] - close[-2])
        result = price_change / current_range if current_range > 0 else 1.0
        
        # Absorption: High effort, low result
        # If effort is 2x median but result is only 0.3 of range → absorption
        absorption = effort * (1.0 - result)
        
        # Normalize to [0,1]
        absorption_normalized = min(absorption / 2.0, 1.0)
        
        return float(absorption_normalized)
    
    def _calc_failed_impulse_score(self, ohlcv: pd.DataFrame) -> float:
        """
        Failed Impulse = Break attempt followed by rejection
        
        Detects: Price breaks recent high/low, then snaps back quickly
        Classic bull/bear trap pattern
        
        Returns [0,1]: 0 = no failed impulse, 1 = strong trap
        """
        close = ohlcv['close'].values
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        
        if len(close) < 5:
            return 0.0
        
        # Find recent swing high/low
        recent_high = np.max(high[-self.window:-3])  # Exclude last 3 bars
        recent_low = np.min(low[-self.window:-3])
        
        # Check if we broke out
        broke_high = high[-3] > recent_high
        broke_low = low[-3] < recent_low
        
        if not (broke_high or broke_low):
            return 0.0  # No breakout attempt
        
        # Check for snapback (rejection)
        if broke_high:
            # Did we snap back below breakout level?
            snapped_back = close[-1] < recent_high
            snapback_strength = (high[-3] - close[-1]) / (high[-3] - recent_high) if high[-3] > recent_high else 0
        elif broke_low:
            # Did we snap back above breakdown level?
            snapped_back = close[-1] > recent_low
            snapback_strength = (close[-1] - low[-3]) / (recent_low - low[-3]) if low[-3] < recent_low else 0
        else:
            return 0.0
        
        if snapped_back:
            return float(min(snapback_strength, 1.0))
        
        return 0.0
    
    def _calc_followthrough_score(self, ohlcv: pd.DataFrame) -> float:
        """
        Followthrough = Post-break continuation quality
        
        After a breakout, does price continue or stall?
        High followthrough = strong intent
        
        Returns [0,1]: 0 = no followthrough, 1 = strong continuation
        """
        close = ohlcv['close'].values
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        
        if len(close) < 10:
            return 0.5  # Neutral
        
        # Detect recent direction
        recent_move = close[-1] - close[-5]
        direction = 1 if recent_move > 0 else -1
        
        # Count bars moving in trend direction
        continuation_count = 0
        for i in range(-5, 0):
            bar_move = close[i] - close[i-1]
            if (bar_move > 0 and direction > 0) or (bar_move < 0 and direction < 0):
                continuation_count += 1
        
        followthrough = continuation_count / 5.0
        
        return float(min(followthrough, 1.0))
    
    def _calc_divergence_score(self, ohlcv: pd.DataFrame) -> float:
        """
        Divergence = Momentum vs Price misalignment
        
        Price makes higher high, but momentum weakens (bearish divergence)
        Price makes lower low, but momentum strengthens (bullish divergence)
        
        Returns [0,1]: 0 = no divergence, 1 = strong divergence
        """
        close = ohlcv['close'].values
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        
        if len(close) < self.window:
            return 0.0
        
        # Simple momentum proxy: rate of change
        window_half = self.window // 2
        
        # Price peaks/troughs
        recent_high_price = np.max(high[-window_half:])
        prev_high_price = np.max(high[-self.window:-window_half])
        
        recent_low_price = np.min(low[-window_half:])
        prev_low_price = np.min(low[-self.window:-window_half])
        
        # Momentum (ROC)
        recent_momentum = (close[-1] - close[-window_half]) / close[-window_half] if close[-window_half] != 0 else 0
        prev_momentum = (close[-window_half] - close[-self.window]) / close[-self.window] if close[-self.window] != 0 else 0
        
        # Bearish divergence: higher price, lower momentum
        if recent_high_price > prev_high_price and recent_momentum < prev_momentum:
            divergence = abs(recent_momentum - prev_momentum)
            return float(min(divergence * 10, 1.0))  # Scale up
        
        # Bullish divergence: lower price, higher momentum
        if recent_low_price < prev_low_price and recent_momentum > prev_momentum:
            divergence = abs(recent_momentum - prev_momentum)
            return float(min(divergence * 10, 1.0))
        
        return 0.0
    
    def _calc_intent_bias(self,
                         absorption: float,
                         failed_impulse: float,
                         followthrough: float,
                         divergence: float) -> float:
        """
        Calculate intent bias [-1, +1]
        
        Negative = sell pressure
        Positive = buy pressure
        """
        # High followthrough in recent positive move → bullish
        # High failed impulse after upside break → bearish (trap)
        # Divergence can suggest reversal
        
        # Simplified: Use followthrough direction and trap signal
        # (More sophisticated version would track direction of each component)
        
        # For now: neutral baseline, adjusted by signals
        bias = 0.0
        
        # Failed impulse suggests reversal (opposite bias)
        if failed_impulse > 0.5:
            bias -= 0.3 * failed_impulse
        
        # Divergence suggests reversal
        if divergence > 0.5:
            bias -= 0.2 * divergence
        
        # Strong followthrough suggests continuation (current direction)
        if followthrough > 0.6:
            bias += 0.4 * followthrough
        
        return float(np.clip(bias, -1.0, 1.0))
    
    def _calc_intent_strength(self,
                             absorption: float,
                             followthrough: float,
                             divergence: float) -> float:
        """
        Calculate intent strength [0, 1]
        
        High = strong conviction
        Low = weak hands
        """
        # Strong absorption + followthrough = high strength
        strength = (absorption * 0.4 + followthrough * 0.6)
        
        # Divergence weakens conviction
        strength *= (1.0 - divergence * 0.3)
        
        return float(np.clip(strength, 0.0, 1.0))
    
    def _calc_trap_risk(self,
                        failed_impulse: float,
                        divergence: float,
                        followthrough: float) -> float:
        """
        Calculate trap risk [0, 1]
        
        Bull trap: Failed breakout up
        Bear trap: Failed breakdown down
        """
        # High failed impulse = high trap risk
        trap_risk = failed_impulse * 0.6
        
        # Divergence adds trap risk
        trap_risk += divergence * 0.3
        
        # Low followthrough increases trap risk
        trap_risk += (1.0 - followthrough) * 0.1
        
        return float(np.clip(trap_risk, 0.0, 1.0))
    
    def _enhance_with_orderbook(self,
                                absorption_score: float,
                                orderbook: Dict) -> float:
        """
        Enhance absorption score with orderbook depth
        
        Large bids absorbing sells → bullish absorption
        Large asks absorbing buys → bearish absorption
        """
        # TODO: Implement orderbook enhancement (CEX only)
        # For now, return unchanged
        return absorption_score
    
    def _calc_confidence(self, ohlcv: pd.DataFrame) -> float:
        """Calculate confidence based on data quality"""
        # More data = higher confidence
        data_ratio = min(len(ohlcv) / (self.window * 2), 1.0)
        
        # Check for gaps/missing data
        close = ohlcv['close'].values
        has_zeros = np.any(close == 0)
        
        confidence = data_ratio * (0.5 if has_zeros else 1.0)
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _get_neutral_output(self, bar_id: Optional[int] = None) -> IntentOutput:
        """Return neutral output when calculation fails"""
        return IntentOutput(
            intent_bias=0.0,
            intent_strength=0.5,
            trap_risk=0.5,
            absorption_score=0.5,
            failed_impulse_score=0.0,
            followthrough_score=0.5,
            divergence_score=0.0,
            components={},
            confidence=0.0,
            timestamp=datetime.now(),
            bar_id=bar_id
        )
