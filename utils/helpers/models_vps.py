"""
Elite Stack Core Models

Comprehensive type system for elite trading decision-making.
All models designed for production use across CEX/FOREX/DEX venues.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime


class SymbolClass(Enum):
    """
    Symbol classification for tailored parameter sets
    """
    FX_MAJOR = "fx_major"          # EUR/USD, GBP/USD, USD/JPY
    FX_CROSS = "fx_cross"          # EUR/GBP, AUD/NZD, etc
    METAL = "metal"                # XAUUSD, XAGUSD
    CRYPTO_LARGE = "crypto_large"  # BTC, ETH (high liquidity)
    CRYPTO_ALT = "crypto_alt"      # Everything else
    DEX_POOL = "dex_pool"          # AMM pools


@dataclass
class IntentOutput:
    """
    Market Intent Inference output
    
    Detects institutional absorption, failed impulses, followthrough quality
    """
    intent_bias: float  # [-1, +1] sell pressure ... buy pressure
    intent_strength: float  # [0, 1] conviction level
    trap_risk: float  # [0, 1] probability of bull/bear trap
    absorption_score: float  # [0, 1] effort vs result mismatch
    failed_impulse_score: float  # [0, 1] break attempt then snapback
    followthrough_score: float  # [0, 1] post-break continuation quality
    divergence_score: float  # [0, 1] momentum vs price divergence
    components: Dict[str, float]
    confidence: float  # [0, 1]
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None


@dataclass
class LiquidityMagnet:
    """Individual liquidity magnet (support/resistance cluster)"""
    price_level: float
    strength: float  # [0, 1]
    distance: float  # Distance from current price
    magnet_type: str  # "swing_high", "swing_low", "wick_cluster", "time_cluster"


@dataclass
class LiquidityFieldOutput:
    """
    Liquidity Gravity Fields output
    
    Identifies price magnets and sweep risks
    """
    nearest_magnets: List[LiquidityMagnet]  # Sorted by distance
    gravity_vector: float  # [-1, +1] direction of dominant pull
    sweep_risk: float  # [0, 1] risk of stop hunt
    support_strength: float  # [0, 1] nearest support quality
    resistance_strength: float  # [0, 1] nearest resistance quality
    components: Dict[str, float]
    confidence: float  # [0, 1]
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None


@dataclass
class OCEOutput:
    """
    Opportunity Cost Engine output
    
    Evaluates trade opportunity score vs alternatives
    """
    oce_decision: str  # "TAKE", "SKIP", "WAIT"
    oce_score: float  # [0, 1] overall opportunity quality
    expected_edge_score: float  # [0, 1]
    risk_cost: float  # [0, 1] drawdown + volatility risk
    capital_lock_cost: float  # [0, 1] expected holding time cost
    execution_cost: float  # [0, 1] spread/slip/gas/MEV estimate
    reason_codes: List[str]  # Human-readable reasons
    components: Dict[str, float]
    confidence: float  # [0, 1]
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None


@dataclass
class ShadowScenario:
    """Single forward simulation scenario"""
    expected_return: float  # Expected % return
    expected_drawdown: float  # Max % drawdown
    probability: float  # Scenario probability
    path_id: int


@dataclass
class ShadowPathOutput:
    """
    Shadow Path Simulation output
    
    Lightweight forward scenario analysis
    """
    take_scenarios: List[ShadowScenario]
    skip_scenarios: List[ShadowScenario]
    take_expected_return: float  # Weighted avg
    take_expected_dd: float  # Weighted avg max DD
    skip_opportunity_cost: float  # Missed gains estimate
    regret_score: float  # [0, 1] potential regret
    components: Dict[str, float]
    confidence: float  # [0, 1]
    simulation_count: int  # Number of paths simulated
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None


@dataclass
class RMFOutput:
    """
    Regret Minimization Framework output
    
    Final gated decision considering all factors
    """
    final_action: str  # "TAKE", "SKIP", "WAIT"
    regret_take: float  # [0, 1] regret if we take and it fails
    regret_skip: float  # [0, 1] regret if we skip and it wins
    correlation_penalty: float  # [0, 1] portfolio correlation cost
    diversification_bonus: float  # [0, 1] uncorrelated opportunity bonus
    action_confidence: float  # [0, 1] confidence in final action
    components: Dict[str, float]
    reason_codes: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None


@dataclass
class StressFingerprint:
    """Recorded stress event fingerprint"""
    venue_type: str  # "CEX", "FOREX", "DEX"
    symbol_class: str  # SymbolClass value
    wave_state: Optional[str]  # "impulse", "corrective", "chaos"
    pitch_regime: Optional[str]  # "calm", "normal", "hot", "chaotic"
    stress_type: str  # "volatility_spike", "slippage_burst", "stop_hunt", etc
    feature_signature: Dict[str, float]  # Key features at stress time
    timestamp: datetime


@dataclass
class AFEOutput:
    """
    Anti-Fragility Engine output
    
    Adaptive defense based on stress pattern recognition
    """
    af_guard_level: float  # [0, 1] defensive intensity
    active_safeties: List[str]  # Active safety mechanisms
    stress_events_detected: List[str]  # Recent stress events
    fingerprint_matches: List[StressFingerprint]  # Historical pattern matches
    size_cap_multiplier: float  # Defensive size reduction
    entry_delay_multiplier: float  # Additional entry delay
    confirmation_requirement: int  # Extra confirmations needed
    components: Dict[str, float]
    confidence: float  # [0, 1]
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None


@dataclass
class CRMOutput:
    """
    Capital Resonance Matching output
    
    Ensures capital fits market liquidity and execution quality
    """
    exposure_cap_multiplier: float  # Maximum exposure scaling
    frequency_cap_multiplier: float  # Trade frequency scaling
    liquidity_fit_score: float  # [0, 1] how well capital fits market
    execution_quality_score: float  # [0, 1] expected execution quality
    volatility_resonance: float  # [0, 1] vol alignment with capital
    chaos_penalty: float  # [0, 1] chaos-based reduction
    venue_limits: Dict[str, float]  # Per-venue exposure limits
    components: Dict[str, float]
    confidence: float  # [0, 1]
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None


@dataclass
class CorrelationCluster:
    """Portfolio correlation cluster"""
    cluster_id: str
    symbols: List[str]
    avg_correlation: float  # [-1, +1]
    total_exposure: float  # Total $ exposure in cluster
    risk_contribution: float  # % of total portfolio risk


@dataclass
class HeatOutput:
    """
    Portfolio Heat Manager output
    
    Manages correlated exposure and risk budgets
    """
    allow_trade: bool  # Hard gate: yes/no
    adjusted_size_multiplier: float  # Size adjustment for heat
    correlation_clusters: List[CorrelationCluster]
    max_correlated_exposure: float  # Maximum allowed in any cluster
    current_heat: float  # [0, 1] current portfolio stress
    risk_budget_used: float  # [0, 1] % of risk budget consumed
    venue_exposure: Dict[str, float]  # Current exposure by venue
    reason_codes: List[str]
    components: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None


@dataclass
class EliteContext:
    """
    Complete elite stack context for decision-making
    
    Aggregates all elite engine outputs
    """
    # Wave Flow + Pitch (Foundation - already implemented)
    wave_state: Optional[str] = None
    wave_flow_score: Optional[float] = None
    chaos_score: Optional[float] = None
    pitch_value: Optional[float] = None
    pitch_regime: Optional[str] = None
    
    # Layer B: Intent + Liquidity
    intent: Optional[IntentOutput] = None
    liquidity_fields: Optional[LiquidityFieldOutput] = None
    
    # Layer C: Decision Engines
    oce: Optional[OCEOutput] = None
    shadow_paths: Optional[ShadowPathOutput] = None
    rmf: Optional[RMFOutput] = None
    
    # Layer D: Anti-Fragility
    afe: Optional[AFEOutput] = None
    
    # Layer E: Capital & Heat
    crm: Optional[CRMOutput] = None
    heat: Optional[HeatOutput] = None
    
    # Master control
    elite_enabled: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    bar_id: Optional[int] = None
    
    def get_final_action(self) -> str:
        """Get final trading action considering all factors"""
        # Priority hierarchy:
        # 1. Heat hard gate
        if self.heat and not self.heat.allow_trade:
            return "SKIP"
        
        # 2. RMF final decision (if available)
        if self.rmf:
            return self.rmf.final_action
        
        # 3. OCE decision (if RMF not available)
        if self.oce:
            return self.oce.oce_decision
        
        # 4. Fallback to wave/pitch
        if self.chaos_score and self.chaos_score > 0.8:
            return "SKIP"  # Too chaotic
        
        return "WAIT"  # Insufficient data
    
    def get_size_multiplier(self) -> float:
        """Get combined size multiplier from all engines"""
        multiplier = 1.0
        
        # AFE defensive sizing
        if self.afe:
            multiplier *= self.afe.size_cap_multiplier
        
        # CRM capital resonance
        if self.crm:
            multiplier *= self.crm.exposure_cap_multiplier
        
        # Heat correlation penalty
        if self.heat:
            multiplier *= self.heat.adjusted_size_multiplier
        
        return max(0.0, min(multiplier, 1.0))  # Bounded [0, 1]
