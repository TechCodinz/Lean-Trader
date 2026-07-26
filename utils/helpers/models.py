"""
Core data models for Pitch-Bent System
Unified representation across CEX, FOREX, and DEX venues
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime


class VenueType(Enum):
    """Trading venue types"""
    CEX = "cex"  # Centralized exchange (crypto)
    FOREX = "forex"  # Forex/CFD via broker APIs
    DEX = "dex"  # Decentralized exchange (AMMs)


@dataclass
class MarketState:
    """
    Unified market state across all venue types
    
    Fields are optional to handle missing data gracefully
    """
    symbol: str
    venue_type: VenueType
    timeframe: str  # e.g., "1m", "5m", "1h"
    
    # Core price data (required)
    price_series: List[float]  # Recent prices (OHLC close or equiv)
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Microstructure (optional, venue-specific)
    spread: Optional[float] = None  # Bid-ask spread
    orderbook: Optional[Dict[str, Any]] = None  # Top N levels
    volume_series: Optional[List[float]] = None
    
    # CEX-specific
    funding_rate: Optional[float] = None  # For perps
    open_interest: Optional[float] = None  # For futures/perps
    
    # DEX-specific
    pool_liquidity: Optional[float] = None  # TVL in pool
    gas_price: Optional[float] = None  # Current gas (gwei)
    
    # Forex-specific
    session: Optional[str] = None  # "ASIA", "LONDON", "NY"
    
    def __post_init__(self):
        """Validate required fields"""
        if not self.price_series or len(self.price_series) < 2:
            raise ValueError(f"price_series must have at least 2 values, got {len(self.price_series)}")


@dataclass
class PitchOutput:
    """
    Output from pitch engine
    
    pitch_value: Continuous stress scalar in [0, 1]
        0 = calm/low stress (normal trading)
        1 = chaotic/high stress (defensive mode)
    """
    pitch_value: float  # [0, 1]
    components: Dict[str, float]  # Individual feature contributions
    confidence: float  # [0, 1] based on data availability
    regime: str  # "calm", "normal", "hot", "chaotic"
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None  # For backtest determinism
    
    # Wave Flow fields (NEW - from Wave Flow Engine)
    wave_state: Optional[str] = None  # "impulse", "corrective", "chaos"
    wave_flow_score: Optional[float] = None  # [0,1] Wave energy/cleanliness
    chaos_score: Optional[float] = None  # [0,1] Market chaos level
    
    def __post_init__(self):
        """Validate pitch value"""
        if not 0 <= self.pitch_value <= 1:
            raise ValueError(f"pitch_value must be in [0, 1], got {self.pitch_value}")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")


@dataclass
class BentParams:
    """
    Trading parameters after pitch bending
    
    These are the outputs that feed into risk sizing and execution
    """
    # Position sizing
    lot_multiplier: float  # Scale factor for base position size
    
    # Stop/Target adjustments
    sl_multiplier: float  # Scale factor for stop loss distance
    tp_multiplier: float  # Scale factor for take profit distance
    rr_adjust: float = 1.0  # Risk/reward ratio adjustment
    
    # Entry gating
    entry_delay_multiplier: float = 1.0  # Cooldown scale (higher = slower)
    confirmation_multiplier: int = 1  # Additional confirmations needed
    
    # Optional portfolio adjustments
    max_positions_adjust: Optional[int] = None  # Override max positions
    
    # Metadata
    pitch_value: float = 0.0  # Reference to pitch that generated this
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StrategyWeight:
    """
    Weight for strategy blending
    
    Used when multiple strategies exist (trend vs mean-reversion)
    """
    strategy_name: str
    weight: float  # [0, 1], weights sum to 1 across all strategies
    pitch_sensitivity: float = 1.0  # How much pitch affects this strategy


# Config data classes
@dataclass
class PitchConfig:
    """Configuration for pitch engine"""
    # Normalization
    normalize_method: str = "robust_zscore"  # "robust_zscore" or "rolling_minmax"
    zscore_clip: float = 3.0
    rolling_window: int = 100
    
    # Smoothing
    ema_alpha: float = 0.3  # Lower = smoother
    hysteresis_threshold: float = 0.05  # Min change to update regime
    
    # Regime thresholds
    regime_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "calm": 0.25,
        "normal": 0.5,
        "hot": 0.75
    })
    
    # Feature weights (venue-specific, set at runtime)
    feature_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class VenueConfig:
    """Configuration for a specific venue"""
    venue_type: VenueType
    symbol_class: str  # e.g., "BTC_majors", "forex_pairs", "dex_lowliq"
    
    # Feature weights for this venue/class
    feature_weights: Dict[str, float] = field(default_factory=dict)
    
    # Control law parameters
    pitch_curve_params: Dict[str, Any] = field(default_factory=dict)
    
    # Strategy blend (if multiple strategies)
    strategy_blend: List[StrategyWeight] = field(default_factory=list)
