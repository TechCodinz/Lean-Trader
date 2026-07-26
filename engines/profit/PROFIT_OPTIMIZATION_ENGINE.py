#!/usr/bin/env python3
"""
PROFIT OPTIMIZATION ENGINE
Integrates advanced profit-focused trading logic
"""
import time
import numpy as np
from typing import Dict, Tuple, List

class LatencyMonitor:
    """Monitor execution latency to ensure fast order placement"""
    def __init__(self):
        self.latencies = []
        self.alert_threshold = 0.100  # 100ms threshold
        
    def measure_execution(self, signal_time: float, order_id: str) -> bool:
        current = time.time()
        latency = current - signal_time
        self.latencies.append(latency)
        
        if latency > self.alert_threshold:
            print(f" HIGH LATENCY: {latency:.4f}s for order {order_id}")
            return False
        return True
    
    def get_average_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)


class SlippageDetector:
    """Calculate and track slippage on executed trades"""
    
    @staticmethod
    def calculate_slippage(expected_price: float, executed_price: float, side: str) -> float:
        """Calculate slippage percentage"""
        slippage_pct = ((executed_price - expected_price) / expected_price) * 100
        # For sells, positive slippage means we got less
        if side.lower() == 'sell':
            slippage_pct = -slippage_pct
        return slippage_pct
    
    @staticmethod
    def is_acceptable(slippage: float, max_allowed: float = 0.5) -> bool:
        """Check if slippage is within acceptable range"""
        return abs(slippage) <= max_allowed


class ProfitGate:
    """Gate-keeper that only allows profitable trades"""
    
    MIN_EXPECTED_PROFIT = 0.0003  # Minimum 3 basis points (0.03%)
    MIN_PROBABILITY = 0.55  # Minimum 55% confidence
    
    @staticmethod
    def should_execute_trade(signal: Dict, market_context: Dict = None) -> Tuple[bool, str]:
        """
        Determine if trade should execute based on profit probability
        
        Returns:
            (can_trade: bool, reason: str)
        """
        # Get signal confidence and expected profit
        confidence = signal.get('confidence', 0) / 100.0  # Convert to decimal
        target_profit = signal.get('target_profit', 0.005)  # Default 0.5%
        
        # Calculate expected profit
        expected_profit = confidence * target_profit
        
        # Factor in costs (fees + estimated slippage)
        trading_fees = 0.0008  # 8 basis points (0.08% - typical for spot)
        estimated_slippage = 0.0002  # 2 basis points
        total_costs = trading_fees + estimated_slippage
        
        # Net expected profit
        net_profit = expected_profit - total_costs
        
        # Check minimum profit threshold
        if net_profit < ProfitGate.MIN_EXPECTED_PROFIT:
            return False, f"Insufficient profit margin: {net_profit:.4f} < {ProfitGate.MIN_EXPECTED_PROFIT}"
        
        # Check probability/confidence
        if confidence < ProfitGate.MIN_PROBABILITY:
            return False, f"Low confidence: {confidence:.2%} < {ProfitGate.MIN_PROBABILITY:.0%}"
        
        return True, f"Expected profit: {net_profit:.4f} ({confidence:.0%} confidence)"


class KellyCriterionSizer:
    """Optimal position sizing using Kelly Criterion"""
    
    @staticmethod
    def calculate_position_size(
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        total_capital: float,
        kelly_fraction: float = 0.5
    ) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        
        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning trade %
            avg_loss: Average losing trade %
            total_capital: Total account balance
            kelly_fraction: Fraction of Kelly to use (0.5 = half-Kelly for safety)
        
        Returns:
            Optimal position size in dollars
        """
        if avg_loss == 0 or win_rate == 0:
            # Fallback to conservative sizing
            return total_capital * 0.02  # 2%
        
        # Calculate win/loss ratio
        win_loss_ratio = abs(avg_win / avg_loss)
        
        # Kelly Formula: f = (p*b - q) / b
        # Where: p = win_rate, q = 1-p, b = win/loss ratio
        kelly_f = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Apply safety fraction (half-Kelly recommended)
        conservative_f = kelly_f * kelly_fraction
        
        # Cap between 1-10% of capital for safety
        capped_f = max(0.01, min(0.10, conservative_f))
        
        # Calculate position size
        position_size = total_capital * capped_f
        
        return position_size


class AdaptiveExitEngine:
    """Dynamic trailing stop and exit optimization"""
    
    def __init__(self):
        self.trailing_configs = {
            'sniper': {'activation': 0.0012, 'trail': 0.0005},     # Activate at 0.12%, trail 0.05% (ULTRA FAST)
            'aggressive': {'activation': 0.005, 'trail': 0.003},   # Activate at 0.5%, trail 0.3%
            'moderate': {'activation': 0.01, 'trail': 0.005},      # Activate at 1%, trail 0.5%
            'conservative': {'activation': 0.02, 'trail': 0.01}    # Activate at 2%, trail 1%
        }
    
    def dynamic_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        volatility: float,
        side: str = 'long'
    ) -> float:
        """
        Calculate dynamic trailing stop based on volatility
        
        Returns:
            Stop price, or None if not activated
        """
        # Select config based on volatility
        if volatility > 0.05:  # High volatility (>5%)
            config = self.trailing_configs['conservative']
        elif volatility > 0.02:  # Medium volatility (2-5%)
            config = self.trailing_configs['moderate']
        elif volatility > 0.01:  # Low volatility (1-2%)
            config = self.trailing_configs['aggressive']
        else:  # Ultra low volatility or standard scalp (<1%) -> SNIPER MODE
            config = self.trailing_configs['sniper']
        
        # Calculate current profit %
        if side.lower() == 'long':
            profit_pct = (current_price - entry_price) / entry_price
        else:
            profit_pct = (entry_price - current_price) / entry_price
        
        # Check if trailing should activate
        if profit_pct > config['activation']:
            # Calculate trailing stop
            if side.lower() == 'long':
                stop_price = current_price * (1 - config['trail'])
            else:
                stop_price = current_price * (1 + config['trail'])
            return stop_price
        
        return None


# Convenience function for quick integration
def validate_trade_for_profit(signal: Dict, stats: Dict = None) -> Tuple[bool, str]:
    """
    Quick validation function for trade profitability
    
    Args:
        signal: Trade signal dict with 'confidence', 'target_profit', etc.
        stats: Trading statistics dict with 'win_rate', 'avg_win', 'avg_loss'
    
    Returns:
        (should_trade: bool, reason: str)
    """
    # Use profit gate for validation
    can_trade, reason = ProfitGate.should_execute_trade(signal)
    
    return can_trade, reason


if __name__ == "__main__":
    # Test the modules
    print("[OK] Profit Optimization Engine loaded successfully")
    
    # Test profit gate
    test_signal = {
        'symbol': 'BTC/USDT',
        'side': 'buy',
        'confidence': 75,
        'target_profit': 0.01
    }
    
    can_trade, reason = validate_trade_for_profit(test_signal)
    print(f"\nTest Signal: {can_trade} - {reason}")
