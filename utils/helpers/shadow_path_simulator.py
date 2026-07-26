"""
Shadow Path Simulator (SPS)

Lightweight forward scenario simulation for opportunity cost analysis.
Simulates N paths forward using recent volatility and regime.
Deterministic with seeded random for backtest reproducibility.

Outputs: Expected returns, drawdowns, and regret scores for TAKE vs SKIP.
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..models import ShadowScenario, ShadowPathOutput

logger = logging.getLogger(__name__)


class ShadowPathSimulator:
    """
    Forward scenario simulation for decision support
    
    Simulates N paths to estimate TAKE vs SKIP outcomes
    """
    
    def __init__(self,
                 n_scenarios: int = 50,
                 forward_bars: int = 20,
                 confidence_level: float = 0.8):
        """
        Initialize Shadow Path Simulator
        
        Args:
            n_scenarios: Number of paths to simulate
            forward_bars: Bars to simulate forward
            confidence_level: Confidence level for estimates
        """
        self.n_scenarios = n_scenarios
        self.forward_bars = forward_bars
        self.confidence_level = confidence_level
        
        logger.info("[OK] ShadowPathSimulator initialized")
        logger.info(f"   Scenarios: {n_scenarios}")
        logger.info(f"   Forward bars: {forward_bars}")
    
    def simulate_paths(self,
                      current_price: float,
                      volatility: float,
                      trend_bias: float,
                      wave_flow_score: float,
                      chaos_score: float,
                      entry_price: float,
                      stop_loss_pct: float,
                      take_profit_pct: float,
                      seed: Optional[int] = None,
                      bar_id: Optional[int] = None) -> ShadowPathOutput:
        """
        Simulate forward paths for TAKE vs SKIP decision
        
        Args:
            current_price: Current market price
            volatility: Current volatility (ATR % or std)
            trend_bias: [-1,+1] trend direction
            wave_flow_score: Wave flow score [0,1]
            chaos_score: Chaos score [0,1]
            entry_price: Proposed entry price
            stop_loss_pct: Stop loss % (e.g., 0.02 = 2%)
            take_profit_pct: Take profit % (e.g., 0.03 = 3%)
            seed: Random seed for determinism
            bar_id: Optional bar ID
        
        Returns:
            ShadowPathOutput with scenarios and regret analysis
        """
        try:
            # Seed for determinism in backtests
            if seed is not None or bar_id is not None:
                np.random.seed(seed if seed is not None else bar_id)
            
            # Generate scenarios
            take_scenarios = self._simulate_take_scenarios(
                current_price, entry_price, volatility, trend_bias,
                wave_flow_score, chaos_score, stop_loss_pct, take_profit_pct
            )
            
            skip_scenarios = self._simulate_skip_scenarios(
                current_price, volatility, trend_bias, wave_flow_score
            )
            
            # Calculate expected values
            take_expected_return = self._calc_expected_value(
                take_scenarios, 'expected_return'
            )
            take_expected_dd = self._calc_expected_value(
                take_scenarios, 'expected_drawdown'
            )
            
            skip_opportunity_cost = self._calc_skip_opportunity_cost(
                skip_scenarios, entry_price, take_profit_pct
            )
            
            # Regret score
            regret_score = self._calc_regret_score(
                take_expected_return, skip_opportunity_cost, take_expected_dd
            )
            
            # Confidence based on scenario variance
            confidence = self._calc_confidence(take_scenarios, skip_scenarios)
            
            components = {
                'take_win_rate': self._calc_win_rate(take_scenarios),
                'take_avg_return': take_expected_return,
                'skip_missed_gains': skip_opportunity_cost,
                'scenario_variance': np.std([s.expected_return for s in take_scenarios])
            }
            
            return ShadowPathOutput(
                take_scenarios=take_scenarios,
                skip_scenarios=skip_scenarios,
                take_expected_return=take_expected_return,
                take_expected_dd=take_expected_dd,
                skip_opportunity_cost=skip_opportunity_cost,
                regret_score=regret_score,
                components=components,
                confidence=confidence,
                simulation_count=self.n_scenarios,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"Shadow path simulation error: {e}")
            return self._get_neutral_output(bar_id)
    
    def _simulate_take_scenarios(self,
                                 current_price: float,
                                 entry_price: float,
                                 volatility: float,
                                 trend_bias: float,
                                 wave_flow_score: float,
                                 chaos_score: float,
                                 stop_loss_pct: float,
                                 take_profit_pct: float) -> List[ShadowScenario]:
        """
        Simulate TAKE scenarios (enter trade)
        
        Model: Random walk with drift (trend bias) and volatility
        """
        scenarios = []
        
        # Adjust drift based on wave flow
        drift_adj = trend_bias * wave_flow_score
        
        # Adjust volatility based on chaos
        vol_adj = volatility * (1.0 + chaos_score * 0.5)
        
        for i in range(self.n_scenarios):
            # Simulate path
            path = self._generate_price_path(
                entry_price, drift_adj, vol_adj, self.forward_bars
            )
            
            # Check for SL/TP hit
            returns = (path - entry_price) / entry_price
            
            # Stop loss
            sl_level = -stop_loss_pct
            tp_level = take_profit_pct
            
            hit_sl = np.any(returns <= sl_level)
            hit_tp = np.any(returns >= tp_level)
            
            if hit_sl:
                final_return = sl_level
                max_dd = sl_level
            elif hit_tp:
                final_return = tp_level
                max_dd = np.min(returns)
            else:
                # Exit at end of simulation
                final_return = returns[-1]
                max_dd = np.min(returns)
            
            # Probability (simplified: all equal for now)
            probability = 1.0 / self.n_scenarios
            
            scenarios.append(ShadowScenario(
                expected_return=final_return,
                expected_drawdown=abs(max_dd),
                probability=probability,
                path_id=i
            ))
        
        return scenarios
    
    def _simulate_skip_scenarios(self,
                                 current_price: float,
                                 volatility: float,
                                 trend_bias: float,
                                 wave_flow_score: float) -> List[ShadowScenario]:
        """
        Simulate SKIP scenarios (stay in cash)
        
        Models what would have happened if we didn't enter
        """
        scenarios = []
        
        drift_adj = trend_bias * wave_flow_score
        
        for i in range(self.n_scenarios):
            # Simulate path from current price
            path = self._generate_price_path(
                current_price, drift_adj, volatility, self.forward_bars
            )
            
            # Opportunity: what we missed
            final_price = path[-1]
            missed_return = (final_price - current_price) / current_price
            
            probability = 1.0 / self.n_scenarios
            
            scenarios.append(ShadowScenario(
                expected_return=missed_return,
                expected_drawdown=0.0,  # No risk if not in trade
                probability=probability,
                path_id=i
            ))
        
        return scenarios
    
    def _generate_price_path(self,
                            start_price: float,
                            drift: float,
                            volatility: float,
                            n_bars: int) -> np.ndarray:
        """
        Generate single price path using geometric Brownian motion
        
        P(t+1) = P(t) * exp((drift - 0.5*vol^2) + vol*Z)
        where Z ~ N(0,1)
        """
        path = np.zeros(n_bars)
        path[0] = start_price
        
        for i in range(1, n_bars):
            z = np.random.normal(0, 1)
            log_return = (drift - 0.5 * volatility**2) + volatility * z
            path[i] = path[i-1] * np.exp(log_return)
        
        return path
    
    def _calc_expected_value(self,
                            scenarios: List[ShadowScenario],
                            field: str) -> float:
        """Calculate probability-weighted expected value"""
        if not scenarios:
            return 0.0
        
        total = sum(getattr(s, field) * s.probability for s in scenarios)
        return float(total)
    
    def _calc_skip_opportunity_cost(self,
                                   skip_scenarios: List[ShadowScenario],
                                   entry_price: float,
                                   take_profit_pct: float) -> float:
        """
        Calculate opportunity cost of skipping
        
        What % of scenarios would have been profitable?
        """
        if not skip_scenarios:
            return 0.0
        
        # Count profitable scenarios
        profitable = [s for s in skip_scenarios if s.expected_return > 0]
        
        # Weight by probability
        opp_cost = sum(s.expected_return * s.probability for s in profitable)
        
        return float(min(opp_cost, take_profit_pct))  # Cap at TP
    
    def _calc_regret_score(self,
                          take_expected_return: float,
                          skip_opportunity_cost: float,
                          take_expected_dd: float) -> float:
        """
        Calculate regret score [0,1]
        
        High = high regret potential
        """
        # Regret if we TAKE but it fails
        take_regret = take_expected_dd / 0.1  # Normalize to 10% max DD
        
        # Regret if we SKIP but it wins
        skip_regret = skip_opportunity_cost / 0.05  # Normalize to 5% missed
        
        # Combined regret (worse of the two)
        regret = max(take_regret, skip_regret)
        
        return float(np.clip(regret, 0.0, 1.0))
    
    def _calc_win_rate(self, scenarios: List[ShadowScenario]) -> float:
        """Calculate win rate from scenarios"""
        if not scenarios:
            return 0.5
        
        winners = sum(1 for s in scenarios if s.expected_return > 0)
        return winners / len(scenarios)
    
    def _calc_confidence(self,
                        take_scenarios: List[ShadowScenario],
                        skip_scenarios: List[ShadowScenario]) -> float:
        """
        Calculate confidence based on scenario consistency
        
        Low variance = high confidence
        """
        if not take_scenarios:
            return 0.0
        
        # Calculate variance of outcomes
        returns = [s.expected_return for s in take_scenarios]
        variance = np.std(returns)
        
        # Lower variance = higher confidence
        confidence = 1.0 - min(variance / 0.1, 1.0)  # 10% std = low conf
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _get_neutral_output(self, bar_id: Optional[int] = None) -> ShadowPathOutput:
        """Return neutral output when simulation fails"""
        return ShadowPathOutput(
            take_scenarios=[],
            skip_scenarios=[],
            take_expected_return=0.0,
            take_expected_dd=0.05,
            skip_opportunity_cost=0.0,
            regret_score=0.5,
            components={},
            confidence=0.0,
            simulation_count=0,
            timestamp=datetime.now(),
            bar_id=bar_id
        )
