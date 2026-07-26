"""
Opportunity Cost Engine (OCE)

Evaluates trade opportunity quality vs alternative uses of capital.
Gates trades based on multi-factor scoring: edge, risk, capital lock, execution cost.

Decision logic: TAKE if score > threshold, SKIP if poor, WAIT if marginal.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime
import logging

from ..models import OCEOutput, IntentOutput, LiquidityFieldOutput

logger = logging.getLogger(__name__)


class OpportunityCostEngine:
    """
    Multi-factor trade opportunity evaluation
    
    Decides TAKE/SKIP/WAIT based on opportunity quality
    """
    
    def __init__(self,
                 take_threshold: float = 0.6,
                 skip_threshold: float = 0.3,
                 enable_execution_cost: bool = True):
        """
        Initialize Opportunity Cost Engine
        
        Args:
            take_threshold: Minimum score to TAKE trade
            skip_threshold: Below this, SKIP trade
            enable_execution_cost: Include spread/gas in calculation
        """
        self.take_threshold = take_threshold
        self.skip_threshold = skip_threshold
        self.enable_execution_cost = enable_execution_cost
        
        logger.info("[OK] OpportunityCostEngine initialized")
        logger.info(f"   TAKE threshold: {take_threshold}")
        logger.info(f"   SKIP threshold: {skip_threshold}")
    
    def evaluate_opportunity(self,
                            signal_strength: float,
                            wave_flow_score: float,
                            chaos_score: float,
                            intent: Optional[IntentOutput],
                            liquidity: Optional[LiquidityFieldOutput],
                            volatility: float,
                            spread_pct: Optional[float] = None,
                            gas_cost: Optional[float] = None,
                            expected_hold_time_hours: float = 2.0,
                            bar_id: Optional[int] = None) -> OCEOutput:
        """
        Evaluate trade opportunity
        
        Args:
            signal_strength: Strategy signal strength [0,1]
            wave_flow_score: Wave flow score [0,1]
            chaos_score: Market chaos [0,1]
            intent: Market intent output
            liquidity: Liquidity field output
            volatility: Current volatility (ATR % or similar)
            spread_pct: Bid-ask spread % (CEX/FOREX)
            gas_cost: Gas cost in $ (DEX)
            expected_hold_time_hours: Expected trade duration
            bar_id: Optional bar ID
        
        Returns:
            OCEOutput with decision and scoring
        """
        try:
            # Calculate component scores
            edge_score = self._calc_expected_edge(
                signal_strength, wave_flow_score, intent, liquidity
            )
            
            risk_cost = self._calc_risk_cost(
                chaos_score, volatility, liquidity
            )
            
            capital_lock_cost = self._calc_capital_lock_cost(
                expected_hold_time_hours, volatility
            )
            
            execution_cost = 0.0
            if self.enable_execution_cost:
                execution_cost = self._calc_execution_cost(
                    spread_pct, gas_cost, volatility
                )
            
            # Overall OCE score (higher = better opportunity)
            oce_score = self._calc_oce_score(
                edge_score, risk_cost, capital_lock_cost, execution_cost
            )
            
            # Make decision
            decision, reason_codes = self._make_decision(
                oce_score, edge_score, risk_cost, chaos_score, intent
            )
            
            # Confidence
            confidence = self._calc_confidence(
                intent, liquidity, wave_flow_score
            )
            
            components = {
                'edge_score': edge_score,
                'risk_cost': risk_cost,
                'capital_lock_cost': capital_lock_cost,
                'execution_cost': execution_cost
            }
            
            return OCEOutput(
                oce_decision=decision,
                oce_score=oce_score,
                expected_edge_score=edge_score,
                risk_cost=risk_cost,
                capital_lock_cost=capital_lock_cost,
                execution_cost=execution_cost,
                reason_codes=reason_codes,
                components=components,
                confidence=confidence,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"OCE evaluation error: {e}")
            return self._get_neutral_output(bar_id)
    
    def _calc_expected_edge(self,
                           signal_strength: float,
                           wave_flow_score: float,
                           intent: Optional[IntentOutput],
                           liquidity: Optional[LiquidityFieldOutput]) -> float:
        """
        Calculate expected edge [0,1]
        
        Combines: signal quality, wave flow alignment, intent confirmation, liquidity support
        """
        # Base: signal strength
        edge = signal_strength * 0.4
        
        # Wave flow bonus (impulse is good)
        edge += wave_flow_score * 0.3
        
        # Intent alignment bonus
        if intent:
            # High intent strength and low trap risk = good
            intent_bonus = intent.intent_strength * (1.0 - intent.trap_risk)
            edge += intent_bonus * 0.2
        else:
            edge += 0.1  # Neutral if missing
        
        # Liquidity support (gravity alignment)
        if liquidity:
            # Low sweep risk = good
            liquidity_bonus = 1.0 - liquidity.sweep_risk
            edge += liquidity_bonus * 0.1
        else:
            edge += 0.05  # Neutral
        
        return float(np.clip(edge, 0.0, 1.0))
    
    def _calc_risk_cost(self,
                       chaos_score: float,
                       volatility: float,
                       liquidity: Optional[LiquidityFieldOutput]) -> float:
        """
        Calculate risk cost [0,1]
        
        Higher = more risky (bad)
        """
        # Chaos penalty
        risk = chaos_score * 0.5
        
        # Volatility penalty (normalize to typical range)
        vol_normalized = min(volatility / 0.03, 1.0)  # 3% = high vol
        risk += vol_normalized * 0.3
        
        # Sweep risk penalty
        if liquidity:
            risk += liquidity.sweep_risk * 0.2
        else:
            risk += 0.1  # Slight penalty if unknown
        
        return float(np.clip(risk, 0.0, 1.0))
    
    def _calc_capital_lock_cost(self,
                                expected_hold_hours: float,
                                volatility: float) -> float:
        """
        Calculate capital lock cost [0,1]
        
        Longer holds + higher vol = higher cost
        """
        # Time cost (normalize to 24h)
        time_cost = min(expected_hold_hours / 24.0, 1.0) * 0.6
        
        # Vol increases holding risk
        vol_normalized = min(volatility / 0.03, 1.0)
        time_cost += vol_normalized * 0.4
        
        return float(np.clip(time_cost, 0.0, 1.0))
    
    def _calc_execution_cost(self,
                            spread_pct: Optional[float],
                            gas_cost: Optional[float],
                            volatility: float) -> float:
        """
        Calculate execution cost [0,1]
        
        Includes: spread, slippage estimate, gas (DEX)
        """
        cost = 0.0
        
        # Spread cost (CEX/FOREX)
        if spread_pct is not None:
            spread_normalized = min(spread_pct / 0.001, 1.0)  # 0.1% = high
            cost += spread_normalized * 0.4
        
        # Slippage estimate (based on volatility)
        slippage_estimate = min(volatility / 0.02, 1.0)
        cost += slippage_estimate * 0.3
        
        # Gas cost (DEX)
        if gas_cost is not None:
            gas_normalized = min(gas_cost / 50.0, 1.0)  # $50 = expensive
            cost += gas_normalized * 0.3
        
        return float(np.clip(cost, 0.0, 1.0))
    
    def _calc_oce_score(self,
                       edge_score: float,
                       risk_cost: float,
                       capital_lock_cost: float,
                       execution_cost: float) -> float:
        """
        Calculate overall OCE score [0,1]
        
        Score = Edge - (Risk + Lock + Execution)
        """
        # Edge is good, costs are bad
        score = edge_score - (risk_cost * 0.4 + capital_lock_cost * 0.3 + execution_cost * 0.3)
        
        # Normalize to [0,1]
        score = (score + 1.0) / 2.0  # Map [-1,1] to [0,1]
        
        return float(np.clip(score, 0.0, 1.0))
    
    def _make_decision(self,
                      oce_score: float,
                      edge_score: float,
                      risk_cost: float,
                      chaos_score: float,
                      intent: Optional[IntentOutput]) -> tuple:
        """
        Make final TAKE/SKIP/WAIT decision
        
        Returns: (decision, reason_codes)
        """
        reasons = []
        
        # TAKE if score exceeds threshold
        if oce_score >= self.take_threshold:
            decision = "TAKE"
            reasons.append(f"OCE score {oce_score:.2f} >= {self.take_threshold}")
            
            if edge_score > 0.7:
                reasons.append("Strong edge detected")
            if intent and intent.intent_strength > 0.7:
                reasons.append("Strong intent confirmation")
        
        # SKIP if score below threshold or critical issues
        elif oce_score < self.skip_threshold:
            decision = "SKIP"
            reasons.append(f"OCE score {oce_score:.2f} < {self.skip_threshold}")
            
            if edge_score < 0.3:
                reasons.append("Weak edge")
            if risk_cost > 0.7:
                reasons.append("High risk cost")
        
        # Additional SKIP conditions
        elif chaos_score > 0.8:
            decision = "SKIP"
            reasons.append(f"Extreme chaos {chaos_score:.2f}")
        
        elif intent and intent.trap_risk > 0.8:
            decision = "SKIP"
            reasons.append(f"High trap risk {intent.trap_risk:.2f}")
        
        # WAIT for marginal scores
        else:
            decision = "WAIT"
            reasons.append(f"Marginal score {oce_score:.2f}, waiting for clarity")
        
        return decision, reasons
    
    def _calc_confidence(self,
                        intent: Optional[IntentOutput],
                        liquidity: Optional[LiquidityFieldOutput],
                        wave_flow_score: float) -> float:
        """Calculate confidence in OCE decision"""
        confidence = 0.5  # Base
        
        # More data = higher confidence
        if intent:
            confidence += 0.2 * intent.confidence
        
        if liquidity:
            confidence += 0.2 * liquidity.confidence
        
        # Strong wave flow signals = higher confidence
        if wave_flow_score != 0.5:  # Not neutral
            confidence += 0.1
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _get_neutral_output(self, bar_id: Optional[int] = None) -> OCEOutput:
        """Return neutral output when calculation fails"""
        return OCEOutput(
            oce_decision="WAIT",
            oce_score=0.5,
            expected_edge_score=0.5,
            risk_cost=0.5,
            capital_lock_cost=0.5,
            execution_cost=0.5,
            reason_codes=["Insufficient data for OCE evaluation"],
            components={},
            confidence=0.0,
            timestamp=datetime.now(),
            bar_id=bar_id
        )
