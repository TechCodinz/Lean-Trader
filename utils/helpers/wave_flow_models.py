"""
Wave Flow Engine Models

Data models for quantitative wave state detection (no subjective Elliott wave counting)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
from datetime import datetime


class WaveState(Enum):
    """
    Quantitative market wave states
    
    IMPULSE: Clean directional flow with momentum
    CORRECTIVE: Choppy consolidation or pullback  
    CHAOS: High volatility, wicks, poor structure (distribution/stop-hunt zone)
    """
    IMPULSE = "impulse"
    CORRECTIVE = "corrective"
    CHAOS = "chaos"


@dataclass
class WaveFlowOutput:
    """
    Output from Wave Flow Engine
    
    Attributes:
        wave_flow_score: Energy/cleanliness of flow [0,1] (0=dead, 1=clean impulse)
        chaos_score: Market chaos level [0,1] (0=stable, 1=stop-hunt/spiky)
        state: Classified wave state (IMPULSE/CORRECTIVE/CHAOS)
        components: Individual feature scores
        confidence: Confidence in classification [0,1]
        timestamp: When calculated
        bar_id: Bar ID for backtest determinism
    """
    wave_flow_score: float  # [0, 1]
    chaos_score: float  # [0, 1]  
    state: WaveState
    components: Dict[str, float]
    confidence: float  # [0, 1]
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None
    
    def __post_init__(self):
        """Validate scores"""
        if not 0 <= self.wave_flow_score <= 1:
            raise ValueError(f"wave_flow_score must be in [0,1], got {self.wave_flow_score}")
        if not 0 <= self.chaos_score <= 1:
            raise ValueError(f"chaos_score must be in [0,1], got {self.chaos_score}")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be in [0,1], got {self.confidence}")
