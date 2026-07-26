"""
Anti-Fragility Engine (AFE)

Adaptive defense system that learns from stress events.
Detects: volatility spikes, slippage bursts, stop hunts, MEV attacks (DEX).
Records fingerprints and automatically adjusts defensive parameters.

Bounded adjustments within config limits - never silently changes risk profile.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

from ..models import StressFingerprint, AFEOutput

logger = logging.getLogger(__name__)


class AntiFragilityEngine:
    """
    Stress-adaptive defense system
    
    Learns from market stress and automatically adapts defenses
    """
    
    def __init__(self,
                 fingerprint_memory_hours: float = 168.0,  # 1 week
                 vol_spike_threshold: float = 2.0,  # 2x normal vol
                 max_size_reduction: float = 0.5,  # Max 50% size cut
                 max_entry_delay: float = 3.0):  # Max 3x delay
        """
        Initialize Anti-Fragility Engine
        
        Args:
            fingerprint_memory_hours: How long to remember stress events
            vol_spike_threshold: Vol multiplier to trigger stress detection
            max_size_reduction: Maximum size reduction factor
            max_entry_delay: Maximum entry delay multiplier
        """
        self.fingerprint_memory_hours = fingerprint_memory_hours
        self.vol_spike_threshold = vol_spike_threshold
        self.max_size_reduction = max_size_reduction
        self.max_entry_delay = max_entry_delay
        
        # Stress event memory
        self.stress_fingerprints: List[StressFingerprint] = []
        
        logger.info("[OK] AntiFragilityEngine initialized")
        logger.info(f"   Fingerprint memory: {fingerprint_memory_hours}h")
        logger.info(f"   Vol spike threshold: {vol_spike_threshold}x")
   
    def evaluate_fragility(self,
                          ohlcv: pd.DataFrame,
                          venue_type: str,
                          symbol_class: str,
                          current_volatility: float,
                          baseline_volatility: float,
                          wave_state: Optional[str],
                          pitch_regime: Optional[str],
                          spread_pct: Optional[float] = None,
                          gas_price: Optional[float] = None,
                          bar_id: Optional[int] = None) -> AFEOutput:
        """
        Evaluate anti-fragility and adapt defenses
        
        Args:
            ohlcv: OHLCV data
            venue_type: "CEX", "FOREX", "DEX"
            symbol_class: Symbol classification
            current_volatility: Current volatility measure
            baseline_volatility: Normal volatility baseline
            wave_state: Current wave state
            pitch_regime: Current pitch regime
            spread_pct: Bid-ask spread (CEX/FOREX)
            gas_price: Gas price in gwei (DEX)
            bar_id: Optional bar ID
        
        Returns:
            AFEOutput with guard level and active safeties
        """
        try:
            # Clean old fingerprints
            self._clean_old_fingerprints()
            
            # Detect stress events
            stress_events = self._detect_stress_events(
                ohlcv, current_volatility, baseline_volatility,
                spread_pct, gas_price, venue_type
            )
            
            # Record new fingerprints
            if stress_events:
                fingerprint = self._create_fingerprint(
                    venue_type, symbol_class, wave_state, pitch_regime,
                    stress_events, ohlcv
                )
                self.stress_fingerprints.append(fingerprint)
            
            # Find matching fingerprints
            fingerprint_matches = self._find_matching_fingerprints(
                venue_type, symbol_class, wave_state, pitch_regime
            )
            
            # Calculate guard level
            af_guard_level = self._calc_guard_level(
                stress_events, fingerprint_matches, current_volatility, baseline_volatility
            )
            
            # Determine active safeties
            active_safeties = self._determine_safeties(
                af_guard_level, stress_events, venue_type
            )
            
            # Calculate parameter adjustments (bounded)
            size_cap, entry_delay, confirmations = self._calc_adjustments(
                af_guard_level, stress_events
            )
            
            components = {
                'current_vol_ratio': current_volatility / baseline_volatility if baseline_volatility > 0 else 1.0,
                'stress_event_count': len(stress_events),
                'fingerprint_match_count': len(fingerprint_matches),
                'total_fingerprints': len(self.stress_fingerprints)
            }
            
            return AFEOutput(
                af_guard_level=af_guard_level,
                active_safeties=active_safeties,
                stress_events_detected=stress_events,
                fingerprint_matches=fingerprint_matches,
                size_cap_multiplier=size_cap,
                entry_delay_multiplier=entry_delay,
                confirmation_requirement=confirmations,
                components=components,
                confidence=self._calc_confidence(len(fingerprint_matches)),
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"AFE evaluation error: {e}")
            return self._get_neutral_output(bar_id)
    
    def _detect_stress_events(self,
                             ohlcv: pd.DataFrame,
                             current_vol: float,
                             baseline_vol: float,
                             spread_pct: Optional[float],
                             gas_price: Optional[float],
                             venue_type: str) -> List[str]:
        """
        Detect stress events in market
        
        Returns list of stress event types
        """
        stress_events = []
        
        # Volatility spike
        if baseline_vol > 0 and current_vol / baseline_vol > self.vol_spike_threshold:
            stress_events.append("volatility_spike")
        
        # Stop hunt detection (large wicks)
        if len(ohlcv) > 0:
            recent_wicks = self._detect_stop_hunts(ohlcv)
            if recent_wicks:
                stress_events.append("stop_hunt")
        
        # Spread explosion (CEX/FOREX)
        if spread_pct is not None and spread_pct > 0.003:  # >0.3%
            stress_events.append("slippage_burst")
        
        # Gas spike (DEX)
        if gas_price is not None and venue_type == "DEX":
            if gas_price > 150:  # >150 gwei
                stress_events.append("gas_spike")
        
        # Flash crash pattern
        if len(ohlcv) >= 3:
            if self._detect_flash_crash(ohlcv):
                stress_events.append("flash_crash")
        
        return stress_events
    
    def _detect_stop_hunts(self, ohlcv: pd.DataFrame) -> bool:
        """
        Detect stop hunt patterns (large wicks with reversal)
        """
        if len(ohlcv) < 2:
            return False
        
        open_vals = ohlcv['open'].values
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        close = ohlcv['close'].values
        
        # Check last 2 bars for extreme wicks
        for i in range(-1, -3, -1):
            if abs(i) > len(ohlcv):
                continue
            
            candle_range = high[i] - low[i]
            if candle_range == 0:
                continue
            
            body_high = max(open_vals[i], close[i])
            body_low = min(open_vals[i], close[i])
            
            upper_wick = high[i] - body_high
            lower_wick = body_low - low[i]
            
            # Large wick (>60% of range)
            if upper_wick / candle_range > 0.6 or lower_wick / candle_range > 0.6:
                return True
        
        return False
    
    def _detect_flash_crash(self, ohlcv: pd.DataFrame) -> bool:
        """
        Detect flash crash pattern (rapid drop and recovery)
        """
        close = ohlcv['close'].values
        
        if len(close) < 3:
            return False
        
        # Check for V-shaped recovery
        drop = (close[-2] - close[-3]) / close[-3] if close[-3] != 0 else 0
        recovery = (close[-1] - close[-2]) / close[-2] if close[-2] != 0 else 0
        
        # Large drop followed by large recovery
        if drop < -0.05 and recovery > 0.04:  # >5% drop, >4% recovery
            return True
        
        return False
    
    def _create_fingerprint(self,
                          venue_type: str,
                          symbol_class: str,
                          wave_state: Optional[str],
                          pitch_regime: Optional[str],
                          stress_events: List[str],
                          ohlcv: pd.DataFrame) -> StressFingerprint:
        """
        Create stress fingerprint for learning
        """
        # Extract key features at stress time
        close = ohlcv['close'].values
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        
        features = {}
        if len(close) >= 5:
            features['recent_range_avg'] = float(np.mean(high[-5:] - low[-5:]))
            features['price_momentum'] = float((close[-1] - close[-5]) / close[-5]) if close[-5] != 0 else 0.0
        
        return StressFingerprint(
            venue_type=venue_type,
            symbol_class=symbol_class,
            wave_state=wave_state,
            pitch_regime=pitch_regime,
            stress_type=",".join(stress_events),
            feature_signature=features,
            timestamp=datetime.now()
        )
    
    def _find_matching_fingerprints(self,
                                   venue_type: str,
                                   symbol_class: str,
                                   wave_state: Optional[str],
                                   pitch_regime: Optional[str]) -> List[StressFingerprint]:
        """
        Find historical fingerprints matching current conditions
        """
        matches = []
        
        for fp in self.stress_fingerprints:
            # Check venue and symbol class match
            if fp.venue_type != venue_type:
                continue
            if fp.symbol_class != symbol_class:
                continue
            
            # Wave/pitch match (optional)
            if wave_state and fp.wave_state == wave_state:
                matches.append(fp)
            elif pitch_regime and fp.pitch_regime == pitch_regime:
                matches.append(fp)
        
        return matches
    
    def _calc_guard_level(self,
                         stress_events: List[str],
                         fingerprint_matches: List[StressFingerprint],
                         current_vol: float,
                         baseline_vol: float) -> float:
        """
        Calculate anti-fragility guard level [0,1]
        
        0 = no defense needed
        1 = maximum defense
        """
        guard = 0.0
        
        # Active stress events
        guard += len(stress_events) * 0.15
        
        # Historical pattern matches
        guard += len(fingerprint_matches) * 0.1
        
        # Volatility ratio
        if baseline_vol > 0:
            vol_ratio = current_vol / baseline_vol
            guard += min((vol_ratio - 1.0) * 0.3, 0.3)
        
        return float(np.clip(guard, 0.0, 1.0))
    
    def _determine_safeties(self,
                          guard_level: float,
                          stress_events: List[str],
                          venue_type: str) -> List[str]:
        """
        Determine which safety mechanisms to activate
        """
        safeties = []
        
        if guard_level > 0.3:
            safeties.append("size_reduction")
        
        if guard_level > 0.5:
            safeties.append("entry_delay")
        
        if guard_level > 0.7:
            safeties.append("extra_confirmation")
        
        # Event-specific safeties
        if "stop_hunt" in stress_events:
            safeties.append("wider_stops")
        
        if "slippage_burst" in stress_events:
            safeties.append("limit_orders_only")
        
        if "gas_spike" in stress_events and venue_type == "DEX":
            safeties.append("dex_pause")
        
        return safeties
    
    def _calc_adjustments(self,
                         guard_level: float,
                         stress_events: List[str]) -> Tuple[float, float, int]:
        """
        Calculate bounded parameter adjustments
        
        Returns: (size_cap_multiplier, entry_delay_multiplier, confirmation_requirement)
        """
        # Size cap (reduces with guard level)
        size_cap = 1.0 - (guard_level * self.max_size_reduction)
        size_cap = max(1.0 - self.max_size_reduction, size_cap)  # Never below limit
        
        # Entry delay (increases with guard level)
        entry_delay = 1.0 + (guard_level * (self.max_entry_delay - 1.0))
        entry_delay = min(self.max_entry_delay, entry_delay)  # Never above limit
        
        # Confirmations (step function)
        if guard_level > 0.7:
            confirmations = 3
        elif guard_level > 0.5:
            confirmations = 2
        else:
            confirmations = 1
        
        return float(size_cap), float(entry_delay), int(confirmations)
    
    def _clean_old_fingerprints(self):
        """Remove fingerprints older than memory window"""
        cutoff = datetime.now() - timedelta(hours=self.fingerprint_memory_hours)
        self.stress_fingerprints = [
            fp for fp in self.stress_fingerprints
            if fp.timestamp > cutoff
        ]
    
    def _calc_confidence(self, match_count: int) -> float:
        """Calculate confidence based on historical data"""
        # More matches = higher confidence in defense
        confidence = min(match_count / 5.0, 1.0)
        return float(confidence)
    
    def _get_neutral_output(self, bar_id: Optional[int] = None) -> AFEOutput:
        """Return neutral output when calculation fails"""
        return AFEOutput(
            af_guard_level=0.5,
            active_safeties=[],
            stress_events_detected=[],
            fingerprint_matches=[],
            size_cap_multiplier=0.8,
            entry_delay_multiplier=1.2,
            confirmation_requirement=1,
            components={},
            confidence=0.0,
            timestamp=datetime.now(),
            bar_id=bar_id
        )
