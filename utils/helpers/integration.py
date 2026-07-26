"""
Integration with existing LeanTraderBot execution/risk systems

This is the main interface for the bot to use Pitch-Bent System
"""

import logging
from typing import Dict, List, Optional, Any
from .models import MarketState, VenueType, PitchOutput, BentParams
from .core.pitch_engine import PitchEngine
from .core.pitch_curve import PitchCurve

logger = logging.getLogger(__name__)


class PitchBentSystem:
    """
    Main interface for Pitch-Bent adaptive control
    
    Usage:
        pitch_system = PitchBentSystem(enable=True)
        
        # In your trading loop:
        market_state = MarketState(...)
        bent_params = pitch_system.get_bent_params(market_state, base_params, ...)
        
        # Use bent_params to scale: position size, SL/TP, entry delays
    """
    
    def __init__(self, 
                 enable: bool = True,
                 seed: Optional[int] = None,
                 config: Optional[Dict] = None):
        """
        Initialize Pitch-Bent System
        
        Args:
            enable: Master toggle (when False, returns baseline params)
            seed: Random seed for deterministic backtests
            config: Optional configuration overrides
        """
        self.enable = enable
        self.pitch_engine = PitchEngine(seed=seed) if enable else None
        self.pitch_curve = PitchCurve() if enable else None
        
        # Cache last pitch values per symbol
        self.pitch_cache: Dict[str, PitchOutput] = {}
        
        logger.info(f"{'[OK] ENABLED' if enable else '[X] DISABLED'} Pitch-Bent System")
    
    def get_bent_params(self,
                       market_state: MarketState,
                       base_params: Dict[str, Any],
                       venue_type: Optional[VenueType] = None,
                       symbol_class: str = "default",
                       feature_weights: Optional[Dict[str, float]] = None) -> BentParams:
        """
        Get bent parameters for current market conditions
        
        Args:
            market_state: Current market data
            base_params: Baseline parameters (lot_size, sl_pct, tp_pct, ...)
            venue_type: Override venue detection
            symbol_class: Symbol classification for curve tuning
            feature_weights: Override feature weights
            
        Returns:
            BentParams with multipliers to apply to base parameters
            
        If system disabled, returns neutral multipliers (1.0x everything)
        """
        if not self.enable:
            # Fallback mode: no bending
            return BentParams(
                lot_multiplier=1.0,
                sl_multiplier=1.0,
                tp_multiplier=1.0,
                entry_delay_multiplier=1.0,
                confirmation_multiplier=1,
                pitch_value=0.0
            )
        
        try:
            # Calculate pitch
            pitch_output = self.pitch_engine.calculate_pitch(
                market_state,
                feature_weights=feature_weights
            )
            
            # Cache for telemetry
            self.pitch_cache[market_state.symbol] = pitch_output
            
            # Map to bent params
            venue = venue_type or market_state.venue_type
            bent_params = self.pitch_curve.map_pitch_to_params(
                pitch_output,
                base_params,
                venue,
                symbol_class
            )
            
            return bent_params
            
        except Exception as e:
            logger.error(f"Pitch calculation failed: {e}, using baseline")
            # Safe fallback
            return BentParams(
                lot_multiplier=1.0,
                sl_multiplier=1.0,
                tp_multiplier=1.0,
                entry_delay_multiplier=1.0,
                confirmation_multiplier=1,
                pitch_value=0.0
            )
    
    def get_current_pitch(self, symbol: str) -> Optional[PitchOutput]:
        """Get last calculated pitch for a symbol"""
        return self.pitch_cache.get(symbol)
    
    def get_all_pitches(self) -> Dict[str, PitchOutput]:
        """Get all cached pitch values (for telemetry)"""
        return self.pitch_cache.copy()


# Global instance (singleton pattern)
_pitch_system: Optional[PitchBentSystem] = None


def initialize_pitch_system(enable: bool = True, **kwargs) -> PitchBentSystem:
    """Initialize global pitch system"""
    global _pitch_system
    _pitch_system = PitchBentSystem(enable=enable, **kwargs)
    return _pitch_system


def get_pitch_system() -> Optional[PitchBentSystem]:
    """Get global pitch system instance"""
    return _pitch_system
