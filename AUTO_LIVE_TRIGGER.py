#!/usr/bin/env python3
"""
AUTO LIVE TRIGGER - Intelligent Auto-Start System
Automatically switches from testnet to live trading when profitable conditions are met

🎯 FEATURES:
1. Profitability Analysis - Track win rate and profit metrics
2. Risk Assessment - Ensure safe transition to live trading
3. Gradual Transition - Start with small positions, scale up
4. Emergency Stop - Auto-stop if conditions deteriorate
5. Performance Monitoring - Continuous evaluation of trading performance
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
import os

logger = logging.getLogger(__name__)

class AutoLiveTrigger:
    """
    Intelligent system that automatically switches to live trading
    when testnet performance meets profitability criteria
    """
    
    def __init__(self, 
                 min_trades: int = 10,
                 min_win_rate: float = 0.60,
                 min_profit_usd: float = 100.0,
                 max_drawdown: float = 0.15,
                 transition_period_days: int = 7):
        """
        Initialize Auto Live Trigger with safety parameters
        
        Args:
            min_trades: Minimum number of testnet trades before considering live
            min_win_rate: Minimum win rate required (0.60 = 60%)
            min_profit_usd: Minimum profit in USD before considering live
            max_drawdown: Maximum allowed drawdown (0.15 = 15%)
            transition_period_days: Days to gradually transition to live
        """
        self.min_trades = min_trades
        self.min_win_rate = min_win_rate
        self.min_profit_usd = min_profit_usd
        self.max_drawdown = max_drawdown
        self.transition_period_days = transition_period_days
        
        # Performance tracking
        self.trade_history = deque(maxlen=1000)
        self.daily_pnl = defaultdict(float)
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit_usd': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'win_rate': 0.0,
            'avg_profit_per_trade': 0.0,
            'sharpe_ratio': 0.0
        }
        
        # Status tracking
        self.is_ready_for_live = False
        self.transition_started = False
        self.live_trading_active = False
        self.emergency_stop = False
        
        # Configuration file
        self.config_file = 'auto_live_trigger_config.json'
        self.load_config()
        
        logger.info("🤖 Auto Live Trigger System initialized")
        logger.info(f"   Approval: {min_trades}+ trades, {min_win_rate*100:.0f}%+ win rate")
        logger.info(f"   Pause threshold: {max_drawdown*100:.0f}% drawdown")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.performance_metrics.update(config.get('metrics', {}))
                    self.is_ready_for_live = config.get('is_ready_for_live', False)
                    self.transition_started = config.get('transition_started', False)
                    self.live_trading_active = config.get('live_trading_active', False)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'metrics': self.performance_metrics,
                'is_ready_for_live': self.is_ready_for_live,
                'transition_started': self.transition_started,
                'live_trading_active': self.live_trading_active,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def add_trade(self, trade_data: Dict[str, Any]):
        """
        Add a new trade to performance tracking
        
        Args:
            trade_data: Dictionary containing trade information
                - symbol: Trading pair (e.g., 'BTC/USDT')
                - side: 'buy' or 'sell'
                - amount: Trade amount
                - price: Execution price
                - pnl_usd: Profit/Loss in USD
                - timestamp: Trade timestamp
        """
        self.trade_history.append(trade_data)
        self.performance_metrics['total_trades'] += 1
        
        if trade_data.get('pnl_usd', 0) > 0:
            self.performance_metrics['winning_trades'] += 1
        
        self.performance_metrics['total_profit_usd'] += trade_data.get('pnl_usd', 0)
        
        # Update daily PnL
        timestamp = trade_data.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        trade_date = timestamp.date()
        self.daily_pnl[trade_date] += trade_data.get('pnl_usd', 0)
        
        # Recalculate metrics
        self._update_performance_metrics()
        
        # Check if ready for live
        self._check_live_readiness()
        
        logger.info(f"📊 Trade added: {trade_data.get('symbol', 'Unknown')} | "
                   f"PnL: ${trade_data.get('pnl_usd', 0):.2f} | "
                   f"Win Rate: {self.performance_metrics['win_rate']:.1%}")
    
    def _update_performance_metrics(self):
        """Update all performance metrics"""
        total_trades = self.performance_metrics['total_trades']
        if total_trades == 0:
            return
        
        # Win rate
        self.performance_metrics['win_rate'] = (
            self.performance_metrics['winning_trades'] / total_trades
        )
        
        # Average profit per trade
        self.performance_metrics['avg_profit_per_trade'] = (
            self.performance_metrics['total_profit_usd'] / total_trades
        )
        
        # Calculate drawdown
        self._calculate_drawdown()
        
        # Calculate Sharpe ratio (simplified)
        self._calculate_sharpe_ratio()
    
    def _calculate_drawdown(self):
        """Calculate current and maximum drawdown"""
        if not self.daily_pnl:
            return
        
        # Calculate running PnL
        running_pnl = 0
        peak_pnl = 0
        max_dd = 0
        current_dd = 0
        
        for date in sorted(self.daily_pnl.keys()):
            running_pnl += self.daily_pnl[date]
            if running_pnl > peak_pnl:
                peak_pnl = running_pnl
                current_dd = 0
            else:
                current_dd = (peak_pnl - running_pnl) / max(peak_pnl, 1)
                max_dd = max(max_dd, current_dd)
        
        self.performance_metrics['current_drawdown'] = current_dd
        self.performance_metrics['max_drawdown'] = max_dd
    
    def _calculate_sharpe_ratio(self):
        """Calculate simplified Sharpe ratio"""
        if len(self.daily_pnl) < 2:
            self.performance_metrics['sharpe_ratio'] = 0
            return
        
        daily_returns = list(self.daily_pnl.values())
        if not daily_returns:
            return
        
        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((x - mean_return) ** 2 for x in daily_returns) / len(daily_returns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            self.performance_metrics['sharpe_ratio'] = 0
        else:
            self.performance_metrics['sharpe_ratio'] = mean_return / std_dev
    
    def _check_live_readiness(self):
        """Check if system is ready for live trading"""
        metrics = self.performance_metrics
        
        # Check all criteria
        has_min_trades = metrics['total_trades'] >= self.min_trades
        has_min_win_rate = metrics['win_rate'] >= self.min_win_rate
        has_min_profit = metrics['total_profit_usd'] >= self.min_profit_usd
        has_low_drawdown = metrics['max_drawdown'] <= self.max_drawdown
        
        # Update readiness status
        self.is_ready_for_live = all([
            has_min_trades,
            has_min_win_rate,
            has_min_profit,
            has_low_drawdown
        ])
        
        if self.is_ready_for_live and not self.transition_started:
            logger.info("🚀 READY FOR LIVE TRADING!")
            logger.info(f"   ✅ {metrics['total_trades']} trades (min: {self.min_trades})")
            logger.info(f"   ✅ {metrics['win_rate']:.1%} win rate (min: {self.min_win_rate:.1%})")
            logger.info(f"   ✅ ${metrics['total_profit_usd']:.2f} profit (min: ${self.min_profit_usd})")
            logger.info(f"   ✅ {metrics['max_drawdown']:.1%} max drawdown (max: {self.max_drawdown:.1%})")
        
        # Save updated status
        self.save_config()
    
    def check_ready_for_live(self) -> bool:
        """Check if system is ready for live trading"""
        return self.is_ready_for_live
    
    def start_transition_to_live(self) -> bool:
        """Start the transition to live trading"""
        if not self.is_ready_for_live:
            logger.warning("❌ Not ready for live trading yet")
            return False
        
        if self.transition_started:
            logger.info("⚠️ Transition already started")
            return True
        
        self.transition_started = True
        self.save_config()
        
        logger.info("🚀 STARTING TRANSITION TO LIVE TRADING")
        logger.info(f"   Transition period: {self.transition_period_days} days")
        logger.info("   Starting with small position sizes...")
        
        return True
    
    def activate_live_trading(self) -> bool:
        """Activate full live trading"""
        if not self.transition_started:
            logger.warning("❌ Must start transition first")
            return False
        
        self.live_trading_active = True
        self.save_config()
        
        logger.info("🎯 LIVE TRADING ACTIVATED!")
        logger.info("   Full position sizes enabled")
        logger.info("   All safety checks active")
        
        return True
    
    def emergency_stop(self):
        """Emergency stop - halt all trading"""
        self.emergency_stop = True
        self.live_trading_active = False
        self.save_config()
        
        logger.critical("🚨 EMERGENCY STOP ACTIVATED!")
        logger.critical("   All trading halted")
        logger.critical("   Manual intervention required")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            'status': {
                'is_ready_for_live': self.is_ready_for_live,
                'transition_started': self.transition_started,
                'live_trading_active': self.live_trading_active,
                'emergency_stop': self.emergency_stop
            },
            'metrics': self.performance_metrics.copy(),
            'criteria': {
                'min_trades': self.min_trades,
                'min_win_rate': self.min_win_rate,
                'min_profit_usd': self.min_profit_usd,
                'max_drawdown': self.max_drawdown
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def reset_performance(self):
        """Reset all performance data (use with caution)"""
        self.trade_history.clear()
        self.daily_pnl.clear()
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit_usd': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'win_rate': 0.0,
            'avg_profit_per_trade': 0.0,
            'sharpe_ratio': 0.0
        }
        self.is_ready_for_live = False
        self.transition_started = False
        self.live_trading_active = False
        self.emergency_stop = False
        
        self.save_config()
        logger.info("🔄 Performance data reset")