#!/usr/bin/env python3
"""
💰 BALANCE-AWARE INTELLIGENCE
Intelligent balance detection and optimal trade selection for maximum growth
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class BalanceAwareIntelligence:
    """
    🧠 INTELLIGENT BALANCE DETECTION & TRADE OPTIMIZATION
    
    Automatically detects wallet balance and selects optimal trades to grow it faster.
    
    Features:
    - Smart balance detection across exchanges
    - Optimal trade size calculation
    - Growth-optimized strategy selection
    - Risk scaling based on balance
    """
    
    def __init__(self):
        self.balance_thresholds = {
            'micro': (0, 10),        # $0-10: Ultra-safe micro trades
            'small': (10, 100),      # $10-100: Conservative growth
            'medium': (100, 1000),   # $100-1K: Balanced approach
            'large': (1000, 10000),  # $1K-10K: Aggressive growth
            'whale': (10000, float('inf'))  # $10K+: Diversified portfolio
        }
        
        self.strategy_by_balance = {
            'micro': {
                'strategies': ['micro_scalping', 'high_frequency'],
                'risk_per_trade': 0.02,  # 2% max risk
                'min_profit_target': 0.005,  # 0.5% min profit
                'max_trades_per_hour': 20,
                'compound_frequency': 'every_trade'
            },
            'small': {
                'strategies': ['scalping', 'momentum', 'breakout'],
                'risk_per_trade': 0.03,  # 3% max risk
                'min_profit_target': 0.01,  # 1% min profit
                'max_trades_per_hour': 15,
                'compound_frequency': 'every_5_trades'
            },
            'medium': {
                'strategies': ['scalping', 'swing', 'arbitrage', 'momentum'],
                'risk_per_trade': 0.05,  # 5% max risk
                'min_profit_target': 0.015,  # 1.5% min profit
                'max_trades_per_hour': 10,
                'compound_frequency': 'daily'
            },
            'large': {
                'strategies': ['swing', 'arbitrage', 'funding_rate', 'basis_trading'],
                'risk_per_trade': 0.04,  # 4% max risk
                'min_profit_target': 0.02,  # 2% min profit
                'max_trades_per_hour': 8,
                'compound_frequency': 'daily'
            },
            'whale': {
                'strategies': ['swing', 'arbitrage', 'market_making', 'portfolio'],
                'risk_per_trade': 0.03,  # 3% max risk
                'min_profit_target': 0.025,  # 2.5% min profit
                'max_trades_per_hour': 5,
                'compound_frequency': 'weekly'
            }
        }
        
        self.current_balance = 0.0
        self.current_tier = 'micro'
        self.balance_history = []
        
        logger.info("💰 Balance-Aware Intelligence initialized")
    
    def detect_balance(self, exchanges: List[object]) -> float:
        """
        Detect total balance across all exchanges
        
        Args:
            exchanges: List of exchange objects
            
        Returns:
            Total balance in USD
        """
        total_balance = 0.0
        
        for exchange in exchanges:
            try:
                # Fetch balance from exchange
                balance = exchange.fetch_balance()
                
                # Get USDT/USD balance
                if 'USDT' in balance['total']:
                    total_balance += balance['total']['USDT']
                if 'USD' in balance['total']:
                    total_balance += balance['total']['USD']
                
                # Convert other assets to USD (approximate)
                for currency, amount in balance['total'].items():
                    if currency not in ['USDT', 'USD'] and amount > 0:
                        try:
                            # Try to get price
                            ticker = exchange.fetch_ticker(f"{currency}/USDT")
                            total_balance += amount * ticker['last']
                        except:
                            pass  # Skip if can't get price
                
            except Exception as e:
                logger.warning(f"Could not fetch balance from {exchange.id}: {e}")
        
        self.current_balance = total_balance
        self.balance_history.append({
            'balance': total_balance,
            'timestamp': datetime.now()
        })
        
        # Determine tier
        for tier, (min_bal, max_bal) in self.balance_thresholds.items():
            if min_bal <= total_balance < max_bal:
                self.current_tier = tier
                break
        
        logger.info(f"💰 Balance detected: ${total_balance:.2f} (Tier: {self.current_tier})")
        return total_balance
    
    def get_optimal_strategies(self) -> List[str]:
        """Get optimal strategies for current balance"""
        strategies = self.strategy_by_balance[self.current_tier]['strategies']
        logger.info(f"📊 Optimal strategies for {self.current_tier} tier: {strategies}")
        return strategies
    
    def calculate_position_size(self, confidence: float = 0.85) -> float:
        """
        Calculate optimal position size based on balance and confidence
        
        Args:
            confidence: Signal confidence (0-1)
            
        Returns:
            Position size in USD
        """
        tier_config = self.strategy_by_balance[self.current_tier]
        base_risk = tier_config['risk_per_trade']
        
        # Scale risk by confidence
        adjusted_risk = base_risk * confidence
        
        # Calculate position size
        position_size = self.current_balance * adjusted_risk
        
        # Apply minimum position size
        min_position = {
            'micro': 0.1,
            'small': 1.0,
            'medium': 10.0,
            'large': 50.0,
            'whale': 100.0
        }
        
        position_size = max(position_size, min_position[self.current_tier])
        
        logger.debug(f"💵 Position size: ${position_size:.2f} (confidence: {confidence:.2%})")
        return position_size
    
    def should_compound_now(self, trades_since_last: int = 0) -> bool:
        """Check if should compound profits now"""
        tier_config = self.strategy_by_balance[self.current_tier]
        compound_freq = tier_config['compound_frequency']
        
        if compound_freq == 'every_trade':
            return True
        elif compound_freq == 'every_5_trades':
            return trades_since_last >= 5
        elif compound_freq == 'daily':
            # Check if 24h since last compound
            if self.balance_history:
                last_check = self.balance_history[-1]['timestamp']
                return (datetime.now() - last_check).seconds > 86400
            return False
        elif compound_freq == 'weekly':
            if self.balance_history:
                last_check = self.balance_history[-1]['timestamp']
                return (datetime.now() - last_check).days >= 7
            return False
        
        return False
    
    def get_growth_recommendations(self) -> Dict:
        """Get recommendations to maximize balance growth"""
        tier_config = self.strategy_by_balance[self.current_tier]
        
        recommendations = {
            'current_balance': self.current_balance,
            'current_tier': self.current_tier,
            'optimal_strategies': tier_config['strategies'],
            'risk_per_trade': tier_config['risk_per_trade'],
            'min_profit_target': tier_config['min_profit_target'],
            'max_trades_per_hour': tier_config['max_trades_per_hour'],
            'compound_frequency': tier_config['compound_frequency'],
            'next_tier': self._get_next_tier(),
            'balance_needed_for_next_tier': self._get_next_tier_balance()
        }
        
        logger.info(f"📈 Growth recommendations: {recommendations}")
        return recommendations
    
    def _get_next_tier(self) -> str:
        """Get next tier name"""
        tiers = list(self.balance_thresholds.keys())
        current_idx = tiers.index(self.current_tier)
        if current_idx < len(tiers) - 1:
            return tiers[current_idx + 1]
        return self.current_tier
    
    def _get_next_tier_balance(self) -> float:
        """Get balance needed for next tier"""
        next_tier = self._get_next_tier()
        if next_tier != self.current_tier:
            return self.balance_thresholds[next_tier][0]
        return float('inf')
    
    def calculate_time_to_next_tier(self, avg_daily_profit_pct: float = 0.05) -> int:
        """
        Calculate days needed to reach next tier
        
        Args:
            avg_daily_profit_pct: Average daily profit percentage (default 5%)
            
        Returns:
            Estimated days to next tier
        """
        next_balance = self._get_next_tier_balance()
        if next_balance == float('inf'):
            return -1
        
        # Compound growth formula: FV = PV * (1 + r)^n
        # Solve for n: n = log(FV/PV) / log(1 + r)
        import math
        days = math.log(next_balance / self.current_balance) / math.log(1 + avg_daily_profit_pct)
        
        logger.info(f"⏱️  Estimated {int(days)} days to {self._get_next_tier()} tier (${next_balance:.2f})")
        return int(days)


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    intelligence = BalanceAwareIntelligence()
    
    # Simulate different balance tiers
    for balance in [5, 50, 500, 5000, 50000]:
        intelligence.current_balance = balance
        
        # Determine tier
        for tier, (min_bal, max_bal) in intelligence.balance_thresholds.items():
            if min_bal <= balance < max_bal:
                intelligence.current_tier = tier
                break
        
        print(f"\n{'='*70}")
        print(f"Balance: ${balance}")
        print(f"Tier: {intelligence.current_tier}")
        print(f"Optimal strategies: {intelligence.get_optimal_strategies()}")
        print(f"Position size (85% confidence): ${intelligence.calculate_position_size(0.85):.2f}")
        print(f"Days to next tier: {intelligence.calculate_time_to_next_tier()}")
        print(f"Growth recommendations: {intelligence.get_growth_recommendations()}")
