"""
Regret Minimization Framework (RMF)

Final gated decision layer combining OCE, SPS, and portfolio considerations.
Minimizes regret by choosing action with lowest potential regret.

Decision hierarchy: Heat gate → RMF analysis → Final action (TAKE/SKIP/WAIT)
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..models import RMFOutput, OCEOutput, ShadowPathOutput

logger = logging.getLogger(__name__)


class RegretMinimizer:
    """
    Final decision gate with regret minimization
    
    Integrates all elite stack signals for final TAKE/SKIP/WAIT
    """
    
    def __init__(self,
                 regret_threshold: float = 0.6,
                 correlation_penalty_weight: float = 0.3):
        """
        Initialize Regret Minimization Framework
        
        Args:
            regret_threshold: Max acceptable regret score
            correlation_penalty_weight: Weight for correlation penalty
        """
        self.regret_threshold = regret_threshold
        self.correlation_penalty_weight = correlation_penalty_weight
        
        logger.info("[OK] RegretMinimizer initialized")
        logger.info(f"   Regret threshold: {regret_threshold}")
    
    def minimize_regret(self,
                       oce: OCEOutput,
                       shadow_paths: Optional[ShadowPathOutput],
                       portfolio_correlation: float = 0.0,
                       portfolio_heat: float = 0.0,
                       symbol_class: str = "unknown",
                       bar_id: Optional[int] = None) -> RMFOutput:
        """
        Make final decision minimizing regret
        
        Args:
            oce: Opportunity Cost Engine output
            shadow_paths: Shadow Path Simulator output
            portfolio_correlation: Correlation with existing positions [-1,+1]
            portfolio_heat: Current portfolio heat [0,1]
            symbol_class: Symbol classification
            bar_id: Optional bar ID
        
        Returns:
            RMFOutput with final action and regret analysis
        """
        try:
            # Calculate regret for each action
            regret_take = self._calc_regret_if_take(
                oce, shadow_paths, portfolio_correlation, portfolio_heat
            )
            
            regret_skip = self._calc_regret_if_skip(
                oce, shadow_paths, portfolio_correlation
            )
            
            # Correlation penalty (penalizes correlated positions)
            correlation_penalty = self._calc_correlation_penalty(
                portfolio_correlation, portfolio_heat
            )
            
            # Diversification bonus (rewards uncorrelated opportunities)
            diversification_bonus = self._calc_diversification_bonus(
                portfolio_correlation, oce.expected_edge_score
            )
            
            # Adjust regrets
            regret_take_adjusted = regret_take + correlation_penalty
            regret_skip_adjusted = regret_skip - diversification_bonus
            
            # Make decision based on minimum regret
            final_action, reason_codes = self._make_final_decision(
                regret_take_adjusted,
                regret_skip_adjusted,
                oce,
                shadow_paths,
                portfolio_heat
            )
            
            # Action confidence
            action_confidence = self._calc_action_confidence(
                regret_take_adjusted,
                regret_skip_adjusted,
                oce.confidence,
                shadow_paths.confidence if shadow_paths else 0.5
            )
            
            components = {
                'base_regret_take': regret_take,
                'base_regret_skip': regret_skip,
                'regret_take_adjusted': regret_take_adjusted,
                'regret_skip_adjusted': regret_skip_adjusted,
                'portfolio_correlation': portfolio_correlation,
                'portfolio_heat': portfolio_heat
            }
            
            return RMFOutput(
                final_action=final_action,
                regret_take=regret_take_adjusted,
                regret_skip=regret_skip_adjusted,
                correlation_penalty=correlation_penalty,
                diversification_bonus=diversification_bonus,
                action_confidence=action_confidence,
                components=components,
                reason_codes=reason_codes,
                timestamp=datetime.now(),
                bar_id=bar_id
            )
            
        except Exception as e:
            logger.error(f"RMF decision error: {e}")
            return self._get_neutral_output(bar_id)
    
    def _calc_regret_if_take(self,
                            oce: OCEOutput,
                            shadow_paths: Optional[ShadowPathOutput],
                            portfolio_correlation: float,
                            portfolio_heat: float) -> float:
        """
        Calculate regret if we TAKE and it fails
        
        Regret = potential loss + opportunity cost of capital lock
        """
        regret = 0.0
        
        # OCE risk tells us downside potential
        regret += oce.risk_cost * 0.4
        
        # Shadow paths expected drawdown
        if shadow_paths:
            regret += shadow_paths.take_expected_dd * 0.3
        else:
            regret += 0.15  # Default penalty
        
        # Capital lock cost
        regret += oce.capital_lock_cost * 0.2
        
        # Portfolio heat penalty (don't add to hot portfolio)
        regret += portfolio_heat * 0.1
        
        return float(np.clip(regret, 0.0, 1.0))
    
    def _calc_regret_if_skip(self,
                            oce: OCEOutput,
                            shadow_paths: Optional[ShadowPathOutput],
                            portfolio_correlation: float) -> float:
        """
        Calculate regret if we SKIP and it wins
        
        Regret = missed gains + diversification cost
        """
        regret = 0.0
        
        # OCE edge tells us upside potential
        regret += oce.expected_edge_score * 0.5
        
        # Shadow paths opportunity cost
        if shadow_paths:
            regret += shadow_paths.skip_opportunity_cost * 0.4
        else:
            regret += 0.2  # Default
        
        # Diversification cost (if uncorrelated, SKIP costs more)
        if portfolio_correlation < 0.3:  # Uncorrelated
            regret += 0.1
        
        return float(np.clip(regret, 0.0, 1.0))
    
    def _calc_correlation_penalty(self,
                                  portfolio_correlation: float,
                                  portfolio_heat: float) -> float:
        """
        Calculate penalty for adding correlated position
        
        High correlation + high heat = high penalty
        """
        # Correlation penalty (positive correlation is bad)
        corr_penalty = max(portfolio_correlation, 0.0) * 0.5
        
        # Heat amplifies penalty
        corr_penalty *= (1.0 + portfolio_heat)
        
        penalty = corr_penalty * self.correlation_penalty_weight
        
        return float(np.clip(penalty, 0.0, 1.0))
    
    def _calc_diversification_bonus(self,
                                   portfolio_correlation: float,
                                   edge_score: float) -> float:
        """
        Calculate bonus for uncorrelated opportunity
        
        Low correlation + high edge = high bonus
        """
        # Uncorrelated is good
        uncorr_score = 1.0 - abs(portfolio_correlation)
        
        # Bonus scales with edge quality
        bonus = uncorr_score * edge_score * 0.2
        
        return float(np.clip(bonus, 0.0, 0.3))  # Cap at 0.3
    
    def _make_final_decision(self,
                            regret_take: float,
                            regret_skip: float,
                            oce: OCEOutput,
                            shadow_paths: Optional[ShadowPathOutput],
                            portfolio_heat: float) -> tuple:
        """
        Make final decision based on minimum regret
        
        Returns: (action, reason_codes)
        """
        reasons = []
        
        # Hard gates first
        
        # Extreme portfolio heat → SKIP
        if portfolio_heat > 0.9:
            return "SKIP", ["Portfolio heat critical > 0.9"]
        
        # OCE already said SKIP for good reason → respect it
        if oce.oce_decision == "SKIP" and oce.expected_edge_score < 0.3:
            return "SKIP", ["OCE SKIP + weak edge"]
        
        # Regret analysis
        regret_diff = abs(regret_take - regret_skip)
        
        # If regrets are similar, WAIT for clarity
        if regret_diff < 0.15:
            action = "WAIT"
            reasons.append(f"Similar regret (diff={regret_diff:.2f}), waiting")
            return action, reasons
        
        # Choose minimum regret
        if regret_take < regret_skip:
            action = "TAKE"
            reasons.append(f"Lower regret to TAKE ({regret_take:.2f} vs {regret_skip:.2f})")
            
            # Add supporting reasons
            if oce.expected_edge_score > 0.65:
                reasons.append(f"Strong edge {oce.expected_edge_score:.2f}")
            
            if shadow_paths and shadow_paths.components.get('take_win_rate', 0) > 0.6:
                reasons.append(f"High win rate {shadow_paths.components['take_win_rate']:.1%}")
        
        else:
            action = "SKIP"
            reasons.append(f"Lower regret to SKIP ({regret_skip:.2f} vs {regret_take:.2f})")
            
            # Add supporting reasons
            if oce.risk_cost > 0.7:
                reasons.append(f"High risk cost {oce.risk_cost:.2f}")
            
            if shadow_paths and shadow_paths.take_expected_dd > 0.08:
                reasons.append(f"High expected DD {shadow_paths.take_expected_dd:.1%}")
        
        # Final regret check
        chosen_regret = min(regret_take, regret_skip)
        if chosen_regret > self.regret_threshold:
            action = "WAIT"
            reasons = [f"All regrets too high ({chosen_regret:.2f} > {self.regret_threshold})"]
        
        return action, reasons
    
    def _calc_action_confidence(self,
                               regret_take: float,
                               regret_skip: float,
                               oce_confidence: float,
                               sps_confidence: float) -> float:
        """
        Calculate confidence in final action
        
        High confidence when:
        - Regrets are clearly different
        - Input confidence is high
        """
        # Regret clarity (larger difference = higher confidence)
        regret_clarity = abs(regret_take - regret_skip)
        
        # Avg input confidence
        input_confidence = (oce_confidence + sps_confidence) / 2.0
        
        # Combined
        confidence = 0.5 * regret_clarity / 0.5 + 0.5 * input_confidence
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _get_neutral_output(self, bar_id: Optional[int] = None) -> RMFOutput:
        """Return neutral output when decision fails"""
        return RMFOutput(
            final_action="WAIT",
            regret_take=0.5,
            regret_skip=0.5,
            correlation_penalty=0.0,
            diversification_bonus=0.0,
            action_confidence=0.0,
            components={},
            reason_codes=["RMF calculation failed, defaulting to WAIT"],
            timestamp=datetime.now(),
            bar_id=bar_id
        )
