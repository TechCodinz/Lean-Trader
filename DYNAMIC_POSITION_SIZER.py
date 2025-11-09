#!/usr/bin/env python3
"""
DYNAMIC POSITION SIZER - Grows account faster
Bigger positions on high-confidence trades, smaller on uncertain trades
"""

import logging
from typing import Dict, Optional
import math

logger = logging.getLogger(__name__)


class DynamicPositionSizer:
    """
    Advanced position sizing that adapts to:
    - Account balance
    - Trade confidence
    - Market volatility
    - Win rate history
    - Kelly Criterion optimization
    """
    
    def __init__(self, 
                 initial_balance: float = 1000.0,
                 base_risk_pct: float = 0.02,      # 2% base risk per trade
                 aggressive_mode: bool = True,     # Grow faster with high confidence
                 kelly_fraction: float = 0.25):    # Use 25% of Kelly (safer)
        
        self.balance = initial_balance
        self.base_risk_pct = base_risk_pct
        self.aggressive_mode = aggressive_mode
        self.kelly_fraction = kelly_fraction
        
        # Track performance for adaptive sizing
        self.trades_history = []
        self.win_rate = 0.60  # Default 60% win rate
        self.avg_win = 0.02   # Default 2% avg win
        self.avg_loss = 0.01  # Default 1% avg loss
        
        # Minimum/maximum position sizes
        self.min_position_usd = 5.0
        self.max_position_pct = 0.20  # Max 20% of account per trade
        
        logger.info("📊 Dynamic Position Sizer initialized")
        logger.info(f"   Balance: ${initial_balance:.2f}")
        logger.info(f"   Base Risk: {base_risk_pct*100:.0f}% per trade")
        logger.info(f"   Aggressive Mode: {aggressive_mode}")
        logger.info(f"   Kelly Fraction: {kelly_fraction*100:.0f}%")
    
    def calculate_position_size(self,
                                confidence: float,
                                volatility: float = 0.02,
                                stop_loss_pct: float = 0.01) -> Dict:
        """
        Calculate optimal position size using advanced techniques
        
        Returns: {
            'size_usd': float,
            'size_pct': float,
            'reasoning': str,
            'risk_amount': float,
        }
        """
        
        # 1. Base Risk Sizing (Fixed % of account)
        base_risk = self.balance * self.base_risk_pct
        base_size = base_risk / stop_loss_pct
        
        # 2. Kelly Criterion Adjustment
        kelly_size = self._kelly_position_size()
        
        # 3. Confidence Multiplier
        confidence_multiplier = self._confidence_multiplier(confidence)
        
        # 4. Volatility Adjustment (reduce size in high vol)
        volatility_adjustment = max(0.5, min(1.5, 1.0 / (1.0 + volatility * 10)))
        
        # 5. Combine all factors
        position_size = base_size * kelly_size * confidence_multiplier * volatility_adjustment
        
        # 6. Apply limits
        max_size = self.balance * self.max_position_pct
        position_size = max(self.min_position_usd, min(position_size, max_size))
        
        # Calculate actual risk
        actual_risk = position_size * stop_loss_pct
        risk_pct = (actual_risk / self.balance) * 100
        
        # Build reasoning
        reasoning = self._build_reasoning(
            confidence, volatility, stop_loss_pct,
            confidence_multiplier, volatility_adjustment,
            kelly_size
        )
        
        result = {
            'size_usd': position_size,
            'size_pct': (position_size / self.balance) * 100,
            'risk_amount': actual_risk,
            'risk_pct': risk_pct,
            'reasoning': reasoning,
            'confidence_multiplier': confidence_multiplier,
            'volatility_adjustment': volatility_adjustment,
            'kelly_factor': kelly_size,
        }
        
        logger.info(f"📊 Position Size Calculated:")
        logger.info(f"   Size: ${position_size:.2f} ({result['size_pct']:.1f}% of account)")
        logger.info(f"   Risk: ${actual_risk:.2f} ({risk_pct:.2f}%)")
        logger.info(f"   {reasoning}")
        
        return result
    
    def _kelly_position_size(self) -> float:
        """
        Calculate Kelly Criterion optimal fraction
        Kelly = (p * b - q) / b
        where p = win_prob, q = loss_prob, b = win/loss ratio
        """
        p = self.win_rate
        q = 1 - p
        b = self.avg_win / self.avg_loss if self.avg_loss > 0 else 2.0
        
        kelly_optimal = (p * b - q) / b
        kelly_optimal = max(0, min(kelly_optimal, 1.0))  # Clamp 0-100%
        
        # Use fractional Kelly for safety
        kelly = kelly_optimal * self.kelly_fraction
        
        return max(0.5, min(1.5, kelly / self.base_risk_pct))  # Return as multiplier
    
    def _confidence_multiplier(self, confidence: float) -> float:
        """Calculate position size multiplier based on confidence"""
        if not self.aggressive_mode:
            # Conservative: slight increase for high confidence
            return 0.8 + (confidence * 0.4)  # 0.8x to 1.2x
        
        # Aggressive: significant increase for high confidence
        if confidence >= 0.90:
            return 2.0  # Double size for 90%+ confidence
        elif confidence >= 0.85:
            return 1.5  # 50% larger for 85%+ confidence
        elif confidence >= 0.80:
            return 1.2  # 20% larger for 80%+ confidence
        elif confidence >= 0.75:
            return 1.0  # Normal size for 75%+ confidence
        else:
            return 0.7  # Reduce size for lower confidence
    
    def _build_reasoning(self, confidence, volatility, stop_loss,
                        confidence_mult, vol_adj, kelly_factor) -> str:
        """Build human-readable reasoning for position size"""
        reasons = []
        
        if confidence >= 0.90:
            reasons.append(f"Very high confidence ({confidence:.1%})")
        elif confidence >= 0.85:
            reasons.append(f"High confidence ({confidence:.1%})")
        elif confidence >= 0.80:
            reasons.append(f"Good confidence ({confidence:.1%})")
        else:
            reasons.append(f"Moderate confidence ({confidence:.1%})")
        
        if volatility > 0.03:
            reasons.append(f"High volatility ({volatility*100:.1f}%), reducing size")
        elif volatility < 0.01:
            reasons.append(f"Low volatility ({volatility*100:.1f}%), increasing size")
        
        if self.aggressive_mode and confidence >= 0.85:
            reasons.append(f"Aggressive sizing: {confidence_mult:.1f}x multiplier")
        
        if kelly_factor > 1.2:
            reasons.append(f"Kelly suggests larger position")
        elif kelly_factor < 0.8:
            reasons.append(f"Kelly suggests smaller position")
        
        return " | ".join(reasons)
    
    def update_balance(self, new_balance: float):
        """Update account balance"""
        old_balance = self.balance
        self.balance = new_balance
        change_pct = ((new_balance - old_balance) / old_balance) * 100
        
        logger.info(f"💰 Balance updated: ${old_balance:.2f} → ${new_balance:.2f} ({change_pct:+.2f}%)")
    
    def record_trade(self, profit_pct: float, was_win: bool):
        """Record trade result for adaptive sizing"""
        self.trades_history.append({
            'profit_pct': profit_pct,
            'was_win': was_win,
        })
        
        # Keep last 100 trades
        self.trades_history = self.trades_history[-100:]
        
        # Update statistics
        if len(self.trades_history) >= 10:  # Need at least 10 trades
            wins = [t for t in self.trades_history if t['was_win']]
            losses = [t for t in self.trades_history if not t['was_win']]
            
            self.win_rate = len(wins) / len(self.trades_history)
            
            if wins:
                self.avg_win = sum([t['profit_pct'] for t in wins]) / len(wins)
            
            if losses:
                self.avg_loss = abs(sum([t['profit_pct'] for t in losses]) / len(losses))
            
            logger.info(f"📈 Performance Updated:")
            logger.info(f"   Win Rate: {self.win_rate*100:.1f}%")
            logger.info(f"   Avg Win: {self.avg_win*100:.2f}%")
            logger.info(f"   Avg Loss: {self.avg_loss*100:.2f}%")
    
    def get_stats(self) -> Dict:
        """Get position sizing statistics"""
        return {
            'balance': self.balance,
            'trades_count': len(self.trades_history),
            'win_rate': self.win_rate,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'reward_risk_ratio': self.avg_win / self.avg_loss if self.avg_loss > 0 else 0,
        }


# Example usage
if __name__ == '__main__':
    print("=" * 80)
    print("📊 DYNAMIC POSITION SIZER - SIMULATION")
    print("=" * 80)
    print()
    
    sizer = DynamicPositionSizer(
        initial_balance=1000.0,
        base_risk_pct=0.02,
        aggressive_mode=True
    )
    
    # Test different confidence levels
    test_scenarios = [
        {'confidence': 0.95, 'volatility': 0.015, 'description': '95% confidence, low vol'},
        {'confidence': 0.85, 'volatility': 0.020, 'description': '85% confidence, normal vol'},
        {'confidence': 0.75, 'volatility': 0.030, 'description': '75% confidence, high vol'},
        {'confidence': 0.65, 'volatility': 0.020, 'description': '65% confidence, normal vol'},
    ]
    
    print("SCENARIO ANALYSIS:")
    print("-" * 80)
    
    for scenario in test_scenarios:
        result = sizer.calculate_position_size(
            confidence=scenario['confidence'],
            volatility=scenario['volatility'],
            stop_loss_pct=0.01
        )
        
        print(f"\n{scenario['description']}:")
        print(f"  Position Size: ${result['size_usd']:.2f} ({result['size_pct']:.1f}% of account)")
        print(f"  Risk: ${result['risk_amount']:.2f} ({result['risk_pct']:.2f}%)")
        print(f"  Confidence Mult: {result['confidence_multiplier']:.2f}x")
        print(f"  Volatility Adj: {result['volatility_adjustment']:.2f}x")
    
    print()
    print("=" * 80)
    print("💡 KEY INSIGHTS:")
    print("   - High confidence (95%) = 2x larger position")
    print("   - Good confidence (85%) = 1.5x larger position")
    print("   - Low confidence (65%) = 0.7x smaller position")
    print("   - High volatility reduces all positions")
    print("=" * 80)
    print()
    print("🚀 EXPECTED RESULT:")
    print("   Account grows FASTER by maximizing high-confidence trades")
    print("   while minimizing risk on uncertain trades!")
    print("=" * 80)
