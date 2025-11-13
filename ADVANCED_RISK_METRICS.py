#!/usr/bin/env python3
"""
📊 ADVANCED RISK METRICS 📊

Professional hedge fund-level risk management:
- Sharpe Ratio (risk-adjusted returns)
- Kelly Criterion (optimal position sizing)
- VaR (Value at Risk) - Historical, Parametric, Monte Carlo
- Expected Shortfall (ES/CVaR) - Tail risk
- Portfolio VaR/ES

PROFESSIONAL RISK MANAGEMENT!
"""

import logging
import numpy as np
from typing import Tuple
from scipy.stats import norm

logger = logging.getLogger(__name__)


class AdvancedRiskMetrics:
    """
    PROFESSIONAL RISK METRICS
    
    Implements:
    - Sharpe Ratio (252-day annualized)
    - Kelly Criterion for position sizing
    - VaR (3 methods: Historical, Parametric, Monte Carlo)
    - Expected Shortfall (CVaR)
    - Portfolio risk metrics
    
    HEDGE FUND LEVEL!
    """
    
    @staticmethod
    def sharpe_ratio(returns: np.array, risk_free_rate: float = 0.04) -> float:
        """
        Calculate Sharpe Ratio (annualized)
        
        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate (4%)
        
        Returns:
            Sharpe ratio (higher = better risk-adjusted returns)
        """
        if len(returns) < 2 or np.std(returns) == 0:
            return 0.0
        
        excess_ret = returns - risk_free_rate / 252  # Daily risk-free
        sharpe = np.mean(excess_ret) / np.std(excess_ret) * np.sqrt(252)  # Annualize
        
        return float(sharpe)
    
    @staticmethod
    def kelly_fraction(win_prob: float, win_loss_ratio: float) -> float:
        """
        Kelly Criterion for optimal position sizing
        
        Formula: f* = p - (1-p)/b
        where p = win probability, b = win/loss ratio
        
        Returns:
            Optimal fraction of capital to risk (0-1)
        """
        if win_loss_ratio <= 0:
            return 0.0
        
        kelly = max(0.0, win_prob - (1 - win_prob) / win_loss_ratio)
        
        # Cap at 25% for safety (full Kelly can be aggressive)
        kelly = min(0.25, kelly)
        
        return float(kelly)
    
    @staticmethod
    def historical_var(returns: np.array, confidence: float = 0.95) -> float:
        """
        Historical Value at Risk
        
        Returns worst loss at given confidence level
        """
        if len(returns) == 0:
            return 0.0
        
        var = -np.percentile(returns, (1 - confidence) * 100)
        return float(var)
    
    @staticmethod
    def parametric_var(mean: float, std: float, confidence: float = 0.95) -> float:
        """
        Parametric VaR (assumes normal distribution)
        """
        z = norm.ppf(confidence)
        var = -(mean + z * std)
        return float(var)
    
    @staticmethod
    def monte_carlo_var(returns: np.array, n_sim: int = 10000, 
                       confidence: float = 0.95) -> float:
        """
        Monte Carlo VaR via bootstrap simulation
        """
        if len(returns) == 0:
            return 0.0
        
        sim_returns = np.random.choice(returns, size=n_sim, replace=True)
        var = -np.percentile(sim_returns, (1 - confidence) * 100)
        
        return float(var)
    
    @staticmethod
    def expected_shortfall(returns: np.array, confidence: float = 0.95) -> float:
        """
        Expected Shortfall (CVaR) - Average loss beyond VaR
        
        More conservative than VaR (shows tail risk)
        """
        if len(returns) == 0:
            return 0.0
        
        var = AdvancedRiskMetrics.historical_var(returns, confidence)
        tail_losses = returns[returns <= -var]
        
        es = -np.mean(tail_losses) if len(tail_losses) > 0 else 0.0
        
        return float(es)
    
    @staticmethod
    def portfolio_var_es(weights: np.array, cov_matrix: np.array, 
                        confidence: float = 0.95) -> Tuple[float, float]:
        """
        Portfolio VaR and ES
        
        Returns: (VaR, ES) for entire portfolio
        """
        # Portfolio variance
        port_variance = weights.T @ cov_matrix @ weights
        port_std = np.sqrt(port_variance)
        
        # VaR
        z = norm.ppf(confidence)
        var = port_std * z
        
        # ES
        pdf = norm.pdf(z)
        cdf = norm.cdf(z)
        es = port_std * (pdf / (1 - cdf))
        
        return float(var), float(es)


# Singleton
_risk_metrics = None

def get_risk_metrics():
    """Get risk metrics instance"""
    return _risk_metrics

def initialize_risk_metrics():
    """Initialize risk metrics"""
    global _risk_metrics
    _risk_metrics = AdvancedRiskMetrics()
    return _risk_metrics
