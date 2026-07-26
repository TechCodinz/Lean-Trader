"""
Pitch Curve - Maps pitch value to bent parameters

The control law that determines HOW parameters bend based on pitch
"""

import logging
import numpy as np
from typing import Dict, Any, Optional
from ..models import PitchOutput, BentParams, VenueType

logger = logging.getLogger(__name__)


class PitchCurve:
    """
    Maps pitch [0, 1] to trading parameter adjustments
    
    Core principle:
    - Higher pitch = MORE defensive
    - Lower pitch = Normal operation
    
    Bends:
    - Position size (lot_multiplier): Lower as pitch increases
    - Stop loss (sl_multiplier): Wider as pitch increases  
    - Take profit (tp_multiplier): Adjustable based on strategy
    - Entry delay: Longer as pitch increases
    - Confirmations: More as pitch increases
    """
    
    def __init__(self):
        self.name = "PitchCurve"
        logger.info(f"✅ {self.name} initialized")
    
    def map_pitch_to_params(self,
                           pitch_output: PitchOutput,
                           base_params: Dict[str, Any],
                           venue_type: VenueType,
                           symbol_class: str = "default") -> BentParams:
        """
        Map pitch to bent parameters
        
        Args:
            pitch_output: Output from pitch engine
            base_params: Baseline trading parameters (lot_size, sl_pct, tp_pct, etc.)
            venue_type: CEX, FOREX, or DEX
            symbol_class: e.g., "BTC_majors", "forex_pairs", "dex_lowliq"
            
        Returns:
            BentParams with adjusted multipliers
        """
        pitch = pitch_output.pitch_value
        wave_state = pitch_output.wave_state  # May be None if wave flow disabled
        
        # Get curve parameters for this venue/class
        curve_params = self._get_curve_params(venue_type, symbol_class, wave_state)
        
        # Calculate multipliers using smooth curves (wave-aware)
        lot_mult = self._calc_lot_multiplier(pitch, curve_params, wave_state)
        sl_mult = self._calc_sl_multiplier(pitch, curve_params, wave_state)
        tp_mult = self._calc_tp_multiplier(pitch, curve_params)
        entry_delay_mult = self._calc_entry_delay(pitch, curve_params)
        confirmation_mult = self._calc_confirmations(pitch, curve_params)
        
        bent = BentParams(
            lot_multiplier=lot_mult,
            sl_multiplier=sl_mult,
            tp_multiplier=tp_mult,
            entry_delay_multiplier=entry_delay_mult,
            confirmation_multiplier=confirmation_mult,
            pitch_value=pitch
        )
        
        logger.debug(f"Pitch {pitch:.2f} -> lot={lot_mult:.2f}x sl={sl_mult:.2f}x tp={tp_mult:.2f}x")
        
        return bent
    
    def _get_curve_params(self, venue_type: VenueType, symbol_class: str, wave_state: Optional[str] = None) -> Dict[str, Any]:
        """
        Get curve parameters for specific venue/class
        
        These control the shape of the response curves
        """
        # Default params
        defaults = {
            'lot_min': 0.3,      # Min lot size at max pitch
            'lot_curve': 2.0,    # Exponential curve (lower = gentler)
            'sl_max': 2.0,       # Max SL widening at max pitch
            'sl_curve': 1.5,
            'tp_max': 1.5,       # Max TP adjustment
            'tp_curve': 1.0,
            'entry_delay_max': 3.0,  # Max delay multiplier
            'confirmation_thresholds': [0.6, 0.8]  # Pitch levels for +1, +2 confirms
        }
        
        # Venue-specific overrides
        venue_overrides = {
            VenueType.DEX: {
                'lot_min': 0.2,  # More conservative on DEX
                'sl_max': 2.5,   # Wider stops for slippage
            },
            VenueType.FOREX: {
                'sl_curve': 1.2,  # Gentler SL widening
            },
            VenueType.CEX: {
                # Use defaults
            }
        }
        
        params = defaults.copy()
        if venue_type in venue_overrides:
            params.update(venue_overrides[venue_type])
        
        return params
    
    def _calc_lot_multiplier(self, pitch: float, params: Dict, wave_state: Optional[str] = None) -> float:
        """
        Lot size multiplier: decreases as pitch increases
        Wave-aware adjustments:
        - IMPULSE: 10% larger positions (clean flow)
        - CHAOS: 40% smaller positions (dangerous)
        """
        lot_min = params['lot_min']
        curve = params['lot_curve']
        
        # Exponential decay
        mult = 1.0 - (1.0 - lot_min) * (pitch ** curve)
        
        # Wave state adjustments
        if wave_state == 'impulse':
            mult *= 1.1  # 10% larger
        elif wave_state == 'chaos':
            mult *= 0.6  # 40% smaller
        
        return max(lot_min, mult)
    
    def _calc_sl_multiplier(self, pitch: float, params: Dict, wave_state: Optional[str] = None) -> float:
        """
        Stop loss multiplier: increases as pitch increases
        Wave-aware adjustments:
        - IMPULSE: 5% tighter stops (clean flow, less noise)
        - CHAOS: 30% wider stops (choppy, avoid noise stops)
        """
        sl_max = params['sl_max']
        curve = params['sl_curve']
        
        # Exponential growth
        mult = 1.0 + (sl_max - 1.0) * (pitch ** curve)
        
        # Wave state adjustments
        if wave_state == 'impulse':
            mult *= 0.95  # 5% tighter
        elif wave_state == 'chaos':
            mult *= 1.3   # 30% wider
        
        return min(sl_max * 1.5, mult)  # Cap at 1.5x sl_max for safety
    
    def _calc_tp_multiplier(self, pitch: float, params: Dict) -> float:
        """
        Take profit multiplier
        
        Strategy-dependent:
        - Some strategies: wider TP in stress (let winners run)
        - Others: tighter TP in stress (take profits quickly)
        
        Default: slightly wider in stress
        """
        tp_max = params['tp_max']
        curve = params['tp_curve']
        
        mult = 1.0 + (tp_max - 1.0) * (pitch ** curve)
        return mult
    
    def _calc_entry_delay(self, pitch: float, params: Dict) -> float:
        """
        Entry delay multiplier: increases with pitch
        
        Higher pitch = longer cooldown between entries
        Prevents overtrading in volatile conditions
        """
        delay_max = params['entry_delay_max']
        
        # Linear growth
        mult = 1.0 + (delay_max - 1.0) * pitch
        return mult
    
    def _calc_confirmations(self, pitch: float, params: Dict) -> int:
        """
        Additional confirmations needed at high pitch
        
        pitch < 0.6 -> 1 (normal)
        pitch >= 0.6 < 0.8 -> 2
        pitch >= 0.8 -> 3
        """
        thresholds = params['confirmation_thresholds']
        
        if pitch < thresholds[0]:
            return 1
        elif pitch < thresholds[1]:
            return 2
        else:
            return 3
