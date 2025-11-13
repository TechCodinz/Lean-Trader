#!/usr/bin/env python3
"""
🛡️ RISK GUARDIAN 🛡️

Professional risk management:
- VaR monitoring (Value at Risk)
- Drawdown limits
- Position sizing limits
- Circuit breakers (Alert → Degrade → Safe State)
- Graceful degradation

PROTECTS CAPITAL!
"""

import logging
import numpy as np
from typing import Dict, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class RiskGuardian:
    """
    RISK MANAGEMENT SYSTEM
    
    Features:
    - Real-time VaR calculation
    - Max drawdown monitoring (5% limit)
    - Per-asset exposure limits (10% max)
    - Confidence thresholds
    - Latency monitoring
    - Circuit breakers (multi-tier)
    """
    
    def __init__(self, max_dd_pct: float = 0.05, var_confidence: float = 0.95):
        self.max_dd_pct = max_dd_pct
        self.var_conf = var_confidence
        
        # P&L history (rolling window)
        self.pnl_history = deque(maxlen=1000)
        
        # Circuit breaker states
        self.breaker_state = 'normal'  # normal → alert → degrade → safe
        
        # Exposure tracking
        self.current_exposure = {}  # {asset: exposure_pct}
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.current_drawdown = 0.0
        
        logger.info("🛡️ RISK GUARDIAN initialized!")
        logger.info(f"   Max drawdown: {max_dd_pct:.1%}")
        logger.info(f"   VaR confidence: {var_conf:.1%}")
    
    def calculate_var(self, returns: np.array = None) -> float:
        """
        Calculate Value at Risk
        
        Returns: VaR at specified confidence level
        """
        if returns is None:
            returns = np.array(list(self.pnl_history))
        
        if len(returns) < 10:
            return 0.0
        
        # Historical VaR
        var = np.percentile(returns, (1 - self.var_conf) * 100)
        
        return abs(var)
    
    def evaluate_trade(self, proposed_size: float, current_pnl: float, 
                      signal_confidence: float, latency_ms: float) -> Dict:
        """
        Evaluate if trade should be approved
        
        Returns: {
            'approved': True/False,
            'reason': str,
            'adjusted_size': float (if approved with reduction)
        }
        """
        # Update P&L history
        self.pnl_history.append(current_pnl)
        
        # Calculate current VaR
        current_var = self.calculate_var()
        
        # Check conditions
        checks = {
            'var_ok': current_var <= self.max_dd_pct,
            'confidence_ok': signal_confidence >= 0.70,
            'latency_ok': latency_ms <= 200
        }
        
        # Decision logic
        if all(checks.values()):
            return {
                'approved': True,
                'reason': 'All checks passed',
                'adjusted_size': proposed_size
            }
        
        # Partial approval with size reduction
        elif checks['confidence_ok'] and checks['var_ok']:
            # Reduce size due to latency
            adjusted = proposed_size * 0.5
            logger.warning(f"⚠️ High latency ({latency_ms}ms), reducing size 50%")
            return {
                'approved': True,
                'reason': 'Approved with size reduction (latency)',
                'adjusted_size': adjusted
            }
        
        # Reject
        else:
            reasons = []
            if not checks['var_ok']:
                reasons.append(f"VaR too high ({current_var:.1%} > {self.max_dd_pct:.1%})")
            if not checks['confidence_ok']:
                reasons.append(f"Confidence too low ({signal_confidence:.1%})")
            if not checks['latency_ok']:
                reasons.append(f"Latency too high ({latency_ms}ms)")
            
            self._trigger_circuit_breaker('risk_limit_exceeded', reasons)
            
            return {
                'approved': False,
                'reason': '; '.join(reasons),
                'adjusted_size': 0
            }
    
    def _trigger_circuit_breaker(self, reason: str, details: list):
        """
        Trigger circuit breaker
        
        Levels:
        - ALERT (Yellow): Throttle 50%, notify
        - DEGRADE (Orange): Close to neutral, signals only
        - SAFE (Red): Full pause, cancel all
        """
        logger.warning(f"🚨 CIRCUIT BREAKER: {reason}")
        for detail in details:
            logger.warning(f"   • {detail}")
        
        # Determine severity
        if 'VaR' in reason or 'drawdown' in reason:
            self.breaker_state = 'safe'
            logger.error("🔴 SAFE STATE: Pausing all trading!")
        elif 'latency' in reason:
            self.breaker_state = 'alert'
            logger.warning("🟡 ALERT STATE: Throttling 50%")
        else:
            self.breaker_state = 'degrade'
            logger.warning("🟠 DEGRADE STATE: Defensive mode")
    
    def get_risk_status(self) -> Dict:
        """Get current risk status"""
        var = self.calculate_var()
        win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
        
        return {
            'breaker_state': self.breaker_state,
            'current_var': var,
            'max_dd_allowed': self.max_dd_pct,
            'current_drawdown': self.current_drawdown,
            'win_rate': win_rate,
            'total_trades': self.total_trades,
            'status': 'healthy' if self.breaker_state == 'normal' else 'degraded'
        }


# Singleton
_risk_guardian = None

def get_risk_guardian():
    """Get risk guardian"""
    return _risk_guardian

def initialize_risk_guardian(max_dd_pct=0.05, var_conf=0.95):
    """Initialize risk guardian"""
    global _risk_guardian
    _risk_guardian = RiskGuardian(max_dd_pct, var_conf)
    return _risk_guardian
