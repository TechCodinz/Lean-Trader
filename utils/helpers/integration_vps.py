"""
Elite Stack Integration

Master coordinator that wires all elite engines together.
Provides single entry point for elite stack execution.

Call chain:
Data → Wave Flow → Pitch → Intent → Liquidity → OCE → SPS → RMF → AFE → CRM → Heat → Decision
"""

import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

from .models import EliteContext, SymbolClass
from .core.intent_engine import IntentEngine
from .core.liquidity_gravity import LiquidityGravityEngine
from .core.opportunity_cost_engine import OpportunityCostEngine
from .core.shadow_path_simulator import ShadowPathSimulator
from .core.regret_minimizer import RegretMinimizer
from .core.anti_fragility_engine import AntiFragilityEngine
from .core.capital_resonance import CapitalResonanceEngine
from .core.portfolio_heat_manager import PortfolioHeatManager
from .core.strategy_blender import StrategyBlender

logger = logging.getLogger(__name__)


class EliteStackIntegration:
    """
    Master elite stack coordinator
    
    Wires all engines and provides unified interface
    """
    
    def __init__(self,
                 enable_elite_stack: bool = True,
                 enable_intent: bool = True,
                 enable_liquidity: bool = True,
                 enable_oce: bool = True,
                 enable_sps: bool = True,
                 enable_rmf: bool = True,
                 enable_afe: bool = True,
                 enable_crm: bool = True,
                 enable_heat: bool = True,
                 enable_blending: bool = True):
        """
        Initialize Elite Stack Integration
        
        Args:
            enable_elite_stack: Master toggle
            enable_*: Individual module toggles
        """
        self.enable_elite_stack = enable_elite_stack
        self.enable_intent = enable_intent
        self.enable_liquidity = enable_liquidity
        self.enable_oce = enable_oce
        self.enable_sps = enable_sps
        self.enable_rmf = enable_rmf
        self.enable_afe = enable_afe
        self.enable_crm = enable_crm
        self.enable_heat = enable_heat
        self.enable_blending = enable_blending
        
        # Initialize engines
        self.intent_engine = IntentEngine() if enable_intent else None
        self.liquidity_engine = LiquidityGravityEngine() if enable_liquidity else None
        self.oce_engine = OpportunityCostEngine() if enable_oce else None
        self.sps_engine = ShadowPathSimulator() if enable_sps else None
        self.rmf_engine = RegretMinimizer() if enable_rmf else None
        self.afe_engine = AntiFragilityEngine() if enable_afe else None
        self.crm_engine = CapitalResonanceEngine() if enable_crm else None
        self.heat_manager = PortfolioHeatManager() if enable_heat else None
        self.strategy_blender = StrategyBlender() if enable_blending else None
        
        logger.info("=" * 80)
        logger.info("[OK] ELITE STACK INTEGRATION INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   Master enabled: {enable_elite_stack}")
        logger.info(f"   Intent: {enable_intent}")
        logger.info(f"   Liquidity: {enable_liquidity}")
        logger.info(f"   OCE: {enable_oce}")
        logger.info(f"   SPS: {enable_sps}")
        logger.info(f"   RMF: {enable_rmf}")
        logger.info(f"   AFE: {enable_afe}")
        logger.info(f"   CRM: {enable_crm}")
        logger.info(f"   Heat: {enable_heat}")
        logger.info(f"   Blending: {enable_blending}")
        logger.info("=" * 80)
    
    def evaluate_elite_context(self,
                               # Market data
                               ohlcv: pd.DataFrame,
                               current_price: float,
                               # Wave Flow + Pitch (from existing system)
                               wave_state: Optional[str],
                               wave_flow_score: float,
                               chaos_score: float,
                               pitch_value: float,
                               pitch_regime: Optional[str],
                               # Market conditions
                               volatility: float,
                               baseline_volatility: float,
                               # Symbol info
                               symbol: str,
                               venue_type: str,
                               symbol_class: SymbolClass,
                               # Portfolio context
                               portfolio_size: float,
                               # Strategy signals
                               trend_signal: float = 0.0,
                               mr_signal: float = 0.0,
                               breakout_signal: float = 0.0,
                               # Optional enhancements
                               spread_pct: Optional[float] = None,
                               gas_price: Optional[float] = None,
                               market_liquidity: Optional[float] = None,
                               orderbook: Optional[Dict] = None,
                               # Trade params
                               proposed_entry: Optional[float] = None,
                               proposed_size: Optional[float] = None,
                               proposed_direction: Optional[int] = None,
                               stop_loss_pct: float = 0.02,
                               take_profit_pct: float = 0.03,
                               expected_hold_hours: float = 2.0,
                               # Misc
                               bar_id: Optional[int] = None) -> EliteContext:
        """
        Evaluate complete elite stack context
        
        Returns EliteContext with all engine outputs + final decision
        """
        if not self.enable_elite_stack:
            return EliteContext(elite_enabled=False)
        
        try:
            # Layer B: Intent + Liquidity
            intent = None
            if self.enable_intent and self.intent_engine:
                intent = self.intent_engine.calculate_intent(
                    ohlcv, bar_id, orderbook
                )
            
            liquidity = None
            if self.enable_liquidity and self.liquidity_engine:
                liquidity = self.liquidity_engine.calculate_liquidity_field(
                    ohlcv, current_price, bar_id
                )
            
            # Layer C: OCE
            oce = None
            if self.enable_oce and self.oce_engine:
                # Calculate signal strength (from strategy blend or individual)
                signal_strength = max(abs(trend_signal), abs(mr_signal), abs(breakout_signal))
                
                oce = self.oce_engine.evaluate_opportunity(
                    signal_strength=signal_strength,
                    wave_flow_score=wave_flow_score,
                    chaos_score=chaos_score,
                    intent=intent,
                    liquidity=liquidity,
                    volatility=volatility,
                    spread_pct=spread_pct,
                    gas_cost=gas_price,
                    expected_hold_time_hours=expected_hold_hours,
                    bar_id=bar_id
                )
            
            # Layer C: Shadow Paths
            shadow_paths = None
            if self.enable_sps and self.sps_engine and proposed_entry:
                # Calculate trend bias
                trend_bias = intent.intent_bias if intent else 0.0
                
                shadow_paths = self.sps_engine.simulate_paths(
                    current_price=current_price,
                    volatility=volatility,
                    trend_bias=trend_bias,
                    wave_flow_score=wave_flow_score,
                    chaos_score=chaos_score,
                    entry_price=proposed_entry,
                    stop_loss_pct=stop_loss_pct,
                    take_profit_pct=take_profit_pct,
                    seed=bar_id,
                    bar_id=bar_id
                )
            
            # Layer C: RMF
            rmf = None
            if self.enable_rmf and self.rmf_engine and oce:
                # Get portfolio correlation (simplified)
                portfolio_correlation = 0.0  # TODO: Calculate from heat manager
                portfolio_heat_score = 0.0
                
                rmf = self.rmf_engine.minimize_regret(
                    oce=oce,
                    shadow_paths=shadow_paths,
                    portfolio_correlation=portfolio_correlation,
                    portfolio_heat=portfolio_heat_score,
                    symbol_class=symbol_class.value,
                    bar_id=bar_id
                )
            
            # Layer D: AFE
            afe = None
            if self.enable_afe and self.afe_engine:
                afe = self.afe_engine.evaluate_fragility(
                    ohlcv=ohlcv,
                    venue_type=venue_type,
                    symbol_class=symbol_class.value,
                    current_volatility=volatility,
                    baseline_volatility=baseline_volatility,
                    wave_state=wave_state,
                    pitch_regime=pitch_regime,
                    spread_pct=spread_pct,
                    gas_price=gas_price,
                    bar_id=bar_id
                )
            
            # Layer E: CRM
            crm = None
            if self.enable_crm and self.crm_engine:
                crm = self.crm_engine.evaluate_resonance(
                    venue_type=venue_type,
                    symbol_class=symbol_class.value,
                    portfolio_size=portfolio_size,
                    market_liquidity=market_liquidity,
                    current_volatility=volatility,
                    chaos_score=chaos_score,
                    spread_pct=spread_pct,
                    bar_id=bar_id
                )
            
            # Layer E: Heat
            heat = None
            if self.enable_heat and self.heat_manager and proposed_size and proposed_direction:
                heat = self.heat_manager.evaluate_heat(
                    proposed_symbol=symbol,
                    proposed_size=proposed_size,
                    proposed_direction=proposed_direction,
                    portfolio_size=portfolio_size,
                    bar_id=bar_id
                )
            
            # Build Elite Context
            context = EliteContext(
                wave_state=wave_state,
                wave_flow_score=wave_flow_score,
                chaos_score=chaos_score,
                pitch_value=pitch_value,
                pitch_regime=pitch_regime,
                intent=intent,
                liquidity_fields=liquidity,
                oce=oce,
                shadow_paths=shadow_paths,
                rmf=rmf,
                afe=afe,
                crm=crm,
                heat=heat,
                elite_enabled=True,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Elite stack evaluation error: {e}")
            return EliteContext(elite_enabled=False)
    
    def get_strategy_weights(self, context: EliteContext) -> Dict[str, float]:
        """
        Get strategy blend weights from elite context
        """
        if not self.enable_blending or not self.strategy_blender:
            return {'trend': 0.33, 'mean_reversion': 0.33, 'breakout': 0.34}
        
        if not context.intent or not context.liquidity_fields:
            return {'trend': 0.33, 'mean_reversion': 0.33, 'breakout': 0.34}
        
        return self.strategy_blender.blend_strategies(
            wave_state=context.wave_state,
            wave_flow_score=context.wave_flow_score or 0.5,
            chaos_score=context.chaos_score or 0.5,
            pitch_regime=context.pitch_regime,
            intent_bias=context.intent.intent_bias,
            intent_strength=context.intent.intent_strength,
            trap_risk=context.intent.trap_risk,
            liquidity_gravity=context.liquidity_fields.gravity_vector,
            sweep_risk=context.liquidity_fields.sweep_risk
        )
    
    def register_trade_execution(self,
                                symbol: str,
                                size: float,
                                direction: int,
                                venue_type: str):
        """
        Register trade execution with heat manager
        
        Call this when trade executes
        """
        if self.enable_heat and self.heat_manager:
            self.heat_manager.register_position(
                symbol=symbol,
                size=size,
                direction=direction,
                venue_type=venue_type
            )
    
    def register_trade_close(self, symbol: str):
        """
        Register trade close with heat manager
        
        Call this when position closes
        """
        if self.enable_heat and self.heat_manager:
            self.heat_manager.remove_position(symbol)
