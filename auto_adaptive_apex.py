#!/usr/bin/env python3
"""
⚡ AUTO-ADAPTIVE APEX ⚡
AUTOMATICALLY adjusts to balance changes in REAL-TIME

Features:
- Auto-fetches balance every trade
- Auto-detects tier based on current balance
- Auto-adjusts position sizes
- Auto-adjusts risk levels
- Auto-adjusts profit targets
- Auto-celebrates tier upgrades
- Works for SPOT trading (no leverage needed)
- Scales infinitely as balance grows

NO MANUAL CONFIGURATION NEEDED - IT ADAPTS ITSELF!
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import deque
import statistics

logger = logging.getLogger(__name__)


class AutoAdaptiveApex:
    """
    Fully automatic self-adjusting trading system
    Monitors balance and adapts in real-time
    """
    
    def __init__(self, exchange):
        self.exchange = exchange
        self.current_balance = 0.0
        self.starting_balance = 0.0
        self.last_balance_check = None
        self.balance_check_interval = 30  # Check every 30 seconds
        
        # Auto-adaptive tiers for SPOT trading (no leverage)
        self.spot_tiers = {
            'nano': {
                'min': 0, 'max': 5,
                'risk_pct': 0.95,  # Use 95% of balance (aggressive)
                'target_profit': 0.025,  # 2.5% target
                'stop_loss': 0.015,  # 1.5% stop
                'trades_per_hour': 30,  # High frequency
                'min_confidence': 0.75
            },
            'micro': {
                'min': 5, 'max': 50,
                'risk_pct': 0.90,  # 90% of balance
                'target_profit': 0.020,  # 2.0% target
                'stop_loss': 0.012,  # 1.2% stop
                'trades_per_hour': 25,
                'min_confidence': 0.75
            },
            'small': {
                'min': 50, 'max': 200,
                'risk_pct': 0.80,  # 80% of balance
                'target_profit': 0.015,  # 1.5% target
                'stop_loss': 0.009,  # 0.9% stop
                'trades_per_hour': 20,
                'min_confidence': 0.75
            },
            'medium': {
                'min': 200, 'max': 1000,
                'risk_pct': 0.70,  # 70% of balance
                'target_profit': 0.012,  # 1.2% target
                'stop_loss': 0.007,  # 0.7% stop
                'trades_per_hour': 15,
                'min_confidence': 0.75
            },
            'large': {
                'min': 1000, 'max': 5000,
                'risk_pct': 0.60,  # 60% of balance
                'target_profit': 0.010,  # 1.0% target
                'stop_loss': 0.006,  # 0.6% stop
                'trades_per_hour': 12,
                'min_confidence': 0.75
            },
            'xlarge': {
                'min': 5000, 'max': 20000,
                'risk_pct': 0.50,  # 50% of balance
                'target_profit': 0.008,  # 0.8% target
                'stop_loss': 0.005,  # 0.5% stop
                'trades_per_hour': 10,
                'min_confidence': 0.75
            },
            'mega': {
                'min': 20000, 'max': float('inf'),
                'risk_pct': 0.40,  # 40% of balance
                'target_profit': 0.006,  # 0.6% target
                'stop_loss': 0.004,  # 0.4% stop
                'trades_per_hour': 8,
                'min_confidence': 0.80
            }
        }
        
        self.current_tier = None
        self.tier_history = deque(maxlen=100)
        self.balance_history = deque(maxlen=1000)
        
        logger.info("=" * 80)
        logger.info("⚡ AUTO-ADAPTIVE APEX ONLINE ⚡")
        logger.info("=" * 80)
        logger.info("   Mode: SPOT Trading (no leverage)")
        logger.info("   Auto-adjustment: ENABLED")
        logger.info("   Balance monitoring: REAL-TIME")
        logger.info("")
        logger.info("   🎯 Will automatically adjust as balance grows!")
        logger.info("=" * 80)
    
    async def fetch_current_balance(self) -> float:
        """Fetch current balance from exchange"""
        try:
            balance = await asyncio.to_thread(self.exchange.fetch_balance)
            usdt_balance = balance.get('USDT', {}).get('total', 0.0)
            
            # Record balance
            self.balance_history.append({
                'balance': usdt_balance,
                'timestamp': datetime.now()
            })
            
            # Set starting balance if first time
            if self.starting_balance == 0:
                self.starting_balance = usdt_balance
                logger.info(f"💰 Starting balance detected: ${usdt_balance:.2f}")
            
            self.current_balance = usdt_balance
            self.last_balance_check = datetime.now()
            
            return usdt_balance
            
        except Exception as e:
            logger.error(f"Balance fetch error: {e}")
            return self.current_balance
    
    def get_current_tier(self, balance: float) -> tuple:
        """Get tier for current balance"""
        for tier_name, config in self.spot_tiers.items():
            if config['min'] <= balance < config['max']:
                # Check if tier changed
                if self.current_tier != tier_name:
                    if self.current_tier is not None:
                        logger.info(f"🎉 TIER UPGRADE: {self.current_tier.upper()} → {tier_name.upper()}")
                        logger.info(f"   Balance: ${balance:.2f}")
                        logger.info(f"   New position size: {config['risk_pct']*100:.0f}% of balance")
                        logger.info(f"   New target: {config['target_profit']*100:.1f}%")
                    
                    self.current_tier = tier_name
                    self.tier_history.append({
                        'tier': tier_name,
                        'balance': balance,
                        'timestamp': datetime.now()
                    })
                
                return tier_name, config
        
        return 'mega', self.spot_tiers['mega']
    
    async def optimize_trade_auto(self, signal: Dict) -> Optional[Dict]:
        """
        Automatically optimize trade based on CURRENT balance
        Fetches balance, detects tier, calculates optimal parameters
        """
        # Fetch latest balance
        current_balance = await self.fetch_current_balance()
        
        if current_balance < 3.0:
            logger.warning(f"⚠️ Balance too low: ${current_balance:.2f} (need $3+ minimum)")
            return None
        
        # Get current tier
        tier_name, tier_config = self.get_current_tier(current_balance)
        
        # Get signal details
        symbol = signal.get('symbol', 'UNKNOWN')
        confidence = signal.get('confidence', 0.75)
        side = signal.get('side', 'BUY')
        
        # Check minimum confidence for tier
        if confidence < tier_config['min_confidence']:
            logger.debug(f"❌ {symbol}: Confidence {confidence:.1%} below tier minimum {tier_config['min_confidence']:.1%}")
            return None
        
        # Calculate position size (auto-adjusted to current balance)
        position_size = current_balance * tier_config['risk_pct']
        position_size = max(position_size, 3.0)  # Gate.io minimum
        position_size = min(position_size, current_balance * 0.95)  # Safety cap
        
        # Calculate expected outcomes
        target_profit_pct = tier_config['target_profit']
        stop_loss_pct = tier_config['stop_loss']
        
        expected_profit = position_size * target_profit_pct
        fees = position_size * 0.004  # 0.4% total fees
        net_profit = expected_profit - fees
        
        # Fee check
        if net_profit <= fees * 1.5:
            logger.debug(f"❌ {symbol}: Net profit ${net_profit:.4f} too small vs fees ${fees:.4f}")
            return None
        
        # Calculate growth projection
        new_balance = current_balance + net_profit
        growth_pct = (new_balance / current_balance - 1) * 100
        
        logger.info(f"✅ AUTO-ADAPTIVE TRADE OPTIMIZED: {symbol}")
        logger.info(f"   Tier: {tier_name.upper()} (auto-detected)")
        logger.info(f"   Balance: ${current_balance:.2f} (live from exchange)")
        logger.info(f"   Position: ${position_size:.2f} ({tier_config['risk_pct']*100:.0f}% auto-adjusted)")
        logger.info(f"   Target: {target_profit_pct*100:.1f}% (${expected_profit:.2f})")
        logger.info(f"   Net profit: ${net_profit:.2f} after fees")
        logger.info(f"   New balance: ${new_balance:.2f} (+{growth_pct:.1f}%)")
        
        return {
            'tier': tier_name,
            'balance': current_balance,
            'position_size': position_size,
            'risk_percentage': tier_config['risk_pct'] * 100,
            'target_profit_pct': target_profit_pct,
            'stop_loss_pct': stop_loss_pct,
            'expected_profit': expected_profit,
            'net_profit': net_profit,
            'fees': fees,
            'new_balance_projected': new_balance,
            'growth_projected_pct': growth_pct,
            'auto_adjusted': True
        }
    
    def get_growth_stats(self) -> Dict:
        """Get growth statistics"""
        if not self.balance_history or self.starting_balance == 0:
            return {}
        
        total_growth = (self.current_balance / self.starting_balance - 1) * 100
        
        # Calculate growth velocity ($ per hour)
        if len(self.balance_history) >= 2:
            time_span = (self.balance_history[-1]['timestamp'] - self.balance_history[0]['timestamp']).total_seconds() / 3600
            balance_change = self.balance_history[-1]['balance'] - self.balance_history[0]['balance']
            growth_per_hour = balance_change / time_span if time_span > 0 else 0
        else:
            growth_per_hour = 0
        
        return {
            'starting_balance': self.starting_balance,
            'current_balance': self.current_balance,
            'total_growth_pct': total_growth,
            'total_profit': self.current_balance - self.starting_balance,
            'growth_per_hour': growth_per_hour,
            'current_tier': self.current_tier,
            'tier_upgrades': len(self.tier_history)
        }
    
    async def run_auto_balance_monitor(self):
        """Background task that monitors balance and logs updates"""
        logger.info("👁️ Starting auto-balance monitor...")
        
        while True:
            try:
                await asyncio.sleep(self.balance_check_interval)
                
                old_balance = self.current_balance
                new_balance = await self.fetch_current_balance()
                
                if new_balance != old_balance:
                    change = new_balance - old_balance
                    change_pct = (change / old_balance * 100) if old_balance > 0 else 0
                    
                    logger.info(f"💰 Balance Update: ${old_balance:.2f} → ${new_balance:.2f} ({change:+.4f}, {change_pct:+.2f}%)")
                    
                    # Check for tier change
                    self.get_current_tier(new_balance)
                    
                    # Log stats periodically
                    stats = self.get_growth_stats()
                    if stats.get('total_growth_pct', 0) > 0:
                        logger.info(f"📊 Growth Stats: +${stats['total_profit']:.2f} ({stats['total_growth_pct']:.1f}%) | ${stats['growth_per_hour']:.2f}/hour")
                
            except Exception as e:
                logger.debug(f"Balance monitor error: {e}")
                await asyncio.sleep(60)


# Global instance
auto_adaptive_apex = None

def initialize_auto_adaptive_apex(exchange):
    """Initialize auto-adaptive APEX"""
    global auto_adaptive_apex
    auto_adaptive_apex = AutoAdaptiveApex(exchange)
    return auto_adaptive_apex

def get_auto_adaptive_apex():
    """Get global instance"""
    return auto_adaptive_apex

async def optimize_trade_auto_adaptive(signal: Dict) -> Optional[Dict]:
    """Optimize trade with auto-adaptation"""
    global auto_adaptive_apex
    if not auto_adaptive_apex:
        logger.warning("⚠️ Auto-adaptive APEX not initialized")
        return None
    
    return await auto_adaptive_apex.optimize_trade_auto(signal)

# Export
__all__ = [
    'AutoAdaptiveApex',
    'initialize_auto_adaptive_apex',
    'get_auto_adaptive_apex',
    'optimize_trade_auto_adaptive'
]

logger.info("⚡ AUTO-ADAPTIVE APEX loaded - Self-adjusting intelligence!")
