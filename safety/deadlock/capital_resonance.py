"""
Capital Resonance Matching (CRM)

Ensures trading capital "resonates" with market conditions.
Evaluates liquidity fit, execution quality, volatility alignment.
Sets exposure caps and frequency limits per venue/symbol class.

Prevents over-leverage in low-liquidity markets.
"""

import numpy as np
from typing import Dict, Optional
from datetime import datetime
import logging

from ..models import CRMOutput

logger = logging.getLogger(__name__)


class CapitalResonanceEngine:
    """
    Capital-to-market fitness evaluation
    
    Matches capital deployment to market capacity
    """
    
    def __init__(self,
                 base_exposure_cap: float = 0.25,  # 25% max per position
                 base_frequency_cap: float = 1.0,  # 1.0x normal frequency
                 liquidity_threshold: float = 0.3):
        """
        Initialize Capital Resonance Engine
        
        Args:
            base_exposure_cap: Base exposure cap multiplier
            base_frequency_cap: Base frequency cap multiplier
            liquidity_threshold: Min liquidity score to allow trading
        """
        self.base_exposure_cap = base_exposure_cap
        self.base_frequency_cap = base_frequency_cap
        self.liquidity_threshold = liquidity_threshold
        
        logger.info("✅ CapitalResonanceEngine initialized")
        logger.info(f"   Base exposure cap: {base_exposure_cap:.1%}")
        logger.info(f"   Liquidity threshold: {liquidity_threshold}")
    
    def evaluate_resonance(self,
                          venue_type: str,
                          symbol_class: str,
                          portfolio_size: float,
                          market_liquidity: Optional[float],  # Daily volume or TVL
                          current_volatility: float,
                          chaos_score: float,
                          spread_pct: Optional[float] = None,
                          bar_id: Optional[int] = None) -> CRMOutput:
        """
        Evaluate capital resonance with market
        
        Args:
            venue_type: "CEX", "FOREX", "DEX"
            symbol_class: Symbol classification
            portfolio_size: Total portfolio size in $
            market_liquidity: Market liquidity (volume/TVL)
            current_volatility: Current volatility
            chaos_score: Market chaos level
            spread_pct: Bid-ask spread
            bar_id: Optional bar ID
        
        Returns:
            CRMOutput with caps and fit scores
        """
        try:
            # Calculate liquidity fit
            liquidity_fit = self._calc_liquidity_fit(
                portfolio_size, market_liquidity, venue_type
            )
            
            # Calculate execution quality
            execution_quality = self._calc_execution_quality(
                spread_pct, current_volatility, liquidity_fit
            )
            
            # Calculate volatility resonance
            volatility_resonance = self._calc_volatility_resonance(
                current_volatility, chaos_score, symbol_class
            )
            
            # Calculate chaos penalty
            chaos_penalty = self._calc_chaos_penalty(chaos_score)
            
            # Calculate exposure cap multiplier
            exposure_cap = self._calc_exposure_cap(
                liquidity_fit, execution_quality, volatility_resonance, chaos_penalty
            )
            
            # Calculate frequency cap multiplier
            frequency_cap = self._calc_frequency_cap(
                liquidity_fit, execution_quality, chaos_score
            )
            
            # Venue-specific limits
            venue_limits = self._calc_venue_limits(
                venue_type, symbol_class, liquidity_fit
            )
            
            # Confidence
            confidence = self._calc_confidence(
                market_liquidity, liquidity_fit
            )
            
            components = {
                'liquidity_fit': liquidity_fit,
                'execution_quality': execution_quality,
                'volatility_resonance': volatility_resonance,
                'chaos_penalty': chaos_penalty
            }
            
            return CRMOutput(
                exposure_cap_multiplier=exposure_cap,
                frequency_cap_multiplier=frequency_cap,
                liquidity_fit_score=liquidity_fit,
                execution_quality_score=execution_quality,
                volatility_resonance=volatility_resonance,
                chaos_penalty=chaos_penalty,
                venue_limits=venue_limits,
                components=components,
                confidence=confidence,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"CRM evaluation error: {e}")
            return self._get_neutral_output(bar_id)
    
    def _calc_liquidity_fit(self,
                           portfolio_size: float,
                           market_liquidity: Optional[float],
                           venue_type: str) -> float:
        """
        Calculate how well capital fits market liquidity [0,1]
        
        Ideal: Portfolio is small relative to market
        Poor: Portfolio is large relative to market (slippage risk)
        """
        if market_liquidity is None or market_liquidity == 0:
            # Use venue-specific defaults
            if venue_type == "FOREX":
                return 0.9  # FOREX is deep
            elif venue_type == "CEX":
                return 0.7  # CEX varies
            else:  # DEX
                return 0.5  # DEX can be shallow
        
        # Portfolio as % of market liquidity
        capital_ratio = portfolio_size / market_liquidity
        
        # Good fit if portfolio < 1% of market
        if capital_ratio < 0.01:
            fit = 1.0
        elif capital_ratio < 0.05:
            fit = 0.8
        elif capital_ratio < 0.1:
            fit = 0.6
        else:
            fit = 0.3  # Too large
        
        return float(fit)
    
    def _calc_execution_quality(self,
                                spread_pct: Optional[float],
                                volatility: float,
                                liquidity_fit: float) -> float:
        """
        Calculate expected execution quality [0,1]
        
        High spread or high vol = poor execution
        """
        quality = liquidity_fit * 0.5  # Base from liquidity
        
        # Spread penalty
        if spread_pct is not None:
            spread_penalty = min(spread_pct / 0.002, 1.0)  # 0.2% = high
            quality += (1.0 - spread_penalty) * 0.3
        else:
            quality += 0.15  # Neutral if unknown
        
        # Volatility penalty
        vol_penalty = min(volatility / 0.04, 1.0)  # 4% = high vol
        quality += (1.0 - vol_penalty) * 0.2
        
        return float(np.clip(quality, 0.0, 1.0))
    
    def _calc_volatility_resonance(self,
                                   current_vol: float,
                                   chaos_score: float,
                                   symbol_class: str) -> float:
        """
        Calculate volatility resonance [0,1]
        
        Matches position size to volatility:
        - Low vol = can use more size
        - High vol = use less size
        """
        # Normalize volatility (typical ranges)
        vol_normalized = min(current_vol / 0.03, 1.0)  # 3% = high
        
        # Resonance: inverse of volatility
        resonance = 1.0 - vol_normalized
        
        # Chaos penalty
        resonance *= (1.0 - chaos_score * 0.3)
        
        # Symbol class adjustment
        if symbol_class in ["CRYPTO_ALT", "DEX_POOL"]:
            resonance *= 0.8  # More conservative for alts/DEX
        
        return float(np.clip(resonance, 0.0, 1.0))
    
    def _calc_chaos_penalty(self, chaos_score: float) -> float:
        """
        Calculate chaos penalty [0,1]
        
        High chaos = high penalty
        """
        return float(chaos_score)
    
    def _calc_exposure_cap(self,
                          liquidity_fit: float,
                          execution_quality: float,
                          volatility_resonance: float,
                          chaos_penalty: float) -> float:
        """
        Calculate exposure cap multiplier
        
        Good conditions = higher cap
        Poor conditions = lower cap
        """
        # Base cap
        cap = self.base_exposure_cap
        
        # Adjust based on conditions
        condition_score = (
            liquidity_fit * 0.4 +
            execution_quality * 0.3 +
            volatility_resonance * 0.3
        ) - chaos_penalty * 0.3
        
        # Scale cap
        cap *= condition_score / 0.5  # Normalize to ~1.0 at neutral
        
        # Bounds: 0.05 (5%) to 0.50 (50%)
        cap = np.clip(cap, 0.05, 0.50)
        
        return float(cap)
    
    def _calc_frequency_cap(self,
                           liquidity_fit: float,
                           execution_quality: float,
                           chaos_score: float) -> float:
        """
        Calculate trade frequency cap multiplier
        
        Good liquidity = can trade more frequently
        Poor liquidity = slow down
        """
        # Base frequency
        freq = self.base_frequency_cap
        
        # Liquidity boost
        freq *= liquidity_fit
        
        # Execution quality boost
        freq *= execution_quality
        
        # Chaos penalty
        freq *= (1.0 - chaos_score * 0.5)
        
        # Bounds: 0.2x to 2.0x
        freq = np.clip(freq, 0.2, 2.0)
        
        return float(freq)
    
    def _calc_venue_limits(self,
                          venue_type: str,
                          symbol_class: str,
                          liquidity_fit: float) -> Dict[str, float]:
        """
        Calculate per-venue exposure limits
        
        Returns dict of limit_type -> value
        """
        limits = {}
        
        # Base limits by venue
        if venue_type == "FOREX":
            limits['max_position_pct'] = 0.40  # 40%
            limits['max_total_exposure_pct'] = 2.0  # 200% (leverage)
        elif venue_type == "CEX":
            limits['max_position_pct'] = 0.30  # 30%
            limits['max_total_exposure_pct'] = 1.5  # 150%
        else:  # DEX
            limits['max_position_pct'] = 0.15  # 15%
            limits['max_total_exposure_pct'] = 0.5  # 50%
        
        # Adjust for liquidity fit
        if liquidity_fit < 0.5:
            limits['max_position_pct'] *= 0.6
            limits['max_total_exposure_pct'] *= 0.7
        
        # Symbol class adjustments
        if symbol_class in ["CRYPTO_ALT", "DEX_POOL"]:
            limits['max_position_pct'] *= 0.5  # Very conservative
            limits['max_total_exposure_pct'] *= 0.6
        
        return limits
    
    def _calc_confidence(self,
                        market_liquidity: Optional[float],
                        liquidity_fit: float) -> float:
        """Calculate confidence in CRM output"""
        confidence = 0.5
        
        # If we have liquidity data, higher confidence
        if market_liquidity is not None:
            confidence += 0.3
        
        # High liquidity fit = higher confidence
        confidence += liquidity_fit * 0.2
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _get_neutral_output(self, bar_id: Optional[int] = None) -> CRMOutput:
        """Return neutral output when calculation fails"""
        return CRMOutput(
            exposure_cap_multiplier=0.15,  # Conservative default
            frequency_cap_multiplier=0.5,
            liquidity_fit_score=0.5,
            execution_quality_score=0.5,
            volatility_resonance=0.5,
            chaos_penalty=0.5,
            venue_limits={},
            components={},
            confidence=0.0,
            timestamp=datetime.now(),
            bar_id=bar_id
        )
