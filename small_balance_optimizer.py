#!/usr/bin/env python3
"""
Small Balance Optimizer - Optimizes settings for accounts under $100
Specifically configured for $48 starting balance to reach $1000+
"""

import json
import logging

logger = logging.getLogger(__name__)

class SmallBalanceOptimizer:
    """Optimizes trading parameters for small balances"""
    
    def __init__(self, starting_balance=48):
        self.balance = starting_balance
        self.settings = self.calculate_optimal_settings()
        
    def calculate_optimal_settings(self):
        """Calculate optimal settings based on balance"""
        
        settings = {}
        
        if self.balance < 50:
            # ULTRA AGGRESSIVE - For $48 balance
            settings = {
                # Position Sizing
                'position_size_pct': 0.20,  # 20% per position ($9.60)
                'max_positions': 4,          # 4 concurrent positions
                'min_position_size': 5,      # $5 minimum
                'max_position_size': 20,     # $20 maximum initially
                
                # Risk Management
                'risk_per_trade': 0.15,      # 15% risk (aggressive)
                'stop_loss': 0.04,           # 4% stop loss
                'take_profit': 0.015,        # 1.5% take profit (quick)
                'trailing_stop': 0.02,       # 2% trailing
                
                # Arbitrage
                'min_arbitrage_profit': 0.0008,  # 0.08% minimum
                'arbitrage_speed': 'instant',    # No delays
                'arbitrage_aggressive': True,    # Take all opportunities
                
                # Features
                'use_leverage': True,        # Use 2-3x leverage carefully
                'compound_mode': 'aggressive',  # Reinvest everything
                'trade_frequency': 'high',   # Maximum trades
                
                # Special Small Balance Features
                'micro_trades': True,         # Enable $5-10 trades
                'scalping_mode': True,        # Quick in/out trades
                'focus_pairs': ['BTC/USDT', 'ETH/USDT'],  # High liquidity
                'avoid_fees': True,           # Use maker orders
                
                # Growth Targets
                'daily_target_pct': 5,        # Aim for 5% daily
                'weekly_target_pct': 40,      # 40% weekly
                'monthly_target_pct': 200,    # 200% monthly (3x)
            }
            
        elif self.balance < 100:
            # AGGRESSIVE - For $50-100
            settings = {
                'position_size_pct': 0.15,
                'max_positions': 5,
                'risk_per_trade': 0.10,
                'stop_loss': 0.03,
                'take_profit': 0.02,
                'min_arbitrage_profit': 0.001,
                'daily_target_pct': 4,
            }
            
        elif self.balance < 500:
            # MODERATE - For $100-500
            settings = {
                'position_size_pct': 0.10,
                'max_positions': 8,
                'risk_per_trade': 0.05,
                'stop_loss': 0.02,
                'take_profit': 0.03,
                'min_arbitrage_profit': 0.0015,
                'daily_target_pct': 3,
            }
            
        else:
            # STANDARD - For $500+
            settings = {
                'position_size_pct': 0.05,
                'max_positions': 10,
                'risk_per_trade': 0.02,
                'stop_loss': 0.02,
                'take_profit': 0.05,
                'min_arbitrage_profit': 0.002,
                'daily_target_pct': 2,
            }
            
        return settings
        
    def get_growth_strategy(self):
        """Returns specific strategy for growing small balance"""
        
        if self.balance < 50:
            return {
                'week_1': {
                    'focus': 'Micro arbitrage only',
                    'target': '$48 → $60',
                    'strategy': 'Take every 0.1%+ arbitrage opportunity',
                    'positions': '$5-10 per trade',
                    'frequency': '20-30 trades per day'
                },
                'week_2': {
                    'focus': 'Add scalping',
                    'target': '$60 → $80',
                    'strategy': 'Arbitrage + quick scalps',
                    'positions': '$10-15 per trade',
                    'frequency': '30-40 trades per day'
                },
                'week_3_4': {
                    'focus': 'Scale up',
                    'target': '$80 → $150',
                    'strategy': 'All strategies enabled',
                    'positions': '$15-25 per trade',
                    'frequency': '40-50 trades per day'
                },
                'month_2': {
                    'focus': 'Momentum trading',
                    'target': '$150 → $400',
                    'strategy': 'Larger positions, trending pairs',
                    'positions': '$30-50 per trade',
                    'frequency': '30-40 trades per day'
                },
                'month_3': {
                    'focus': 'Full deployment',
                    'target': '$400 → $1000',
                    'strategy': 'All features, multiple exchanges',
                    'positions': '$50-100 per trade',
                    'frequency': '20-30 trades per day'
                }
            }
        return {}
        
    def apply_to_bot(self, bot_config):
        """Apply optimized settings to bot configuration"""
        
        for key, value in self.settings.items():
            bot_config[key] = value
            
        logger.info(f"✅ Optimized for ${self.balance} balance")
        logger.info(f"   Daily target: {self.settings.get('daily_target_pct')}%")
        logger.info(f"   Position size: {self.settings.get('position_size_pct')*100}%")
        logger.info(f"   Max positions: {self.settings.get('max_positions')}")
        
        return bot_config

# Auto-apply when imported
def optimize_for_small_balance(pipeline, balance=48):
    """Integrate small balance optimizer into pipeline"""
    
    optimizer = SmallBalanceOptimizer(balance)
    
    # Apply settings
    if hasattr(pipeline, 'config'):
        pipeline.config = optimizer.apply_to_bot(pipeline.config)
    
    # Add growth strategy
    pipeline.growth_strategy = optimizer.get_growth_strategy()
    
    # Enable special features for small balance
    pipeline.micro_trading_enabled = True
    pipeline.aggressive_mode = True
    pipeline.compound_everything = True
    
    logger.info(f"💎 Small Balance Mode Activated!")
    logger.info(f"   Starting: ${balance}")
    logger.info(f"   Target: $1000+ in 3-4 months")
    logger.info(f"   Strategy: Ultra-aggressive compound growth")
    
    return pipeline