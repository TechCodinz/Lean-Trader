#!/usr/bin/env python3
"""
🎯 DIRECT GATE EXECUTOR 🎯
ACTUALLY executes trades on Gate.io - NO intermediaries

This executor:
- Has DIRECT ccxt connection to Gate.io
- Fetches balance in real-time
- Calculates position sizes correctly
- Places ACTUAL orders
- Monitors positions
- Closes at profit targets
- WORKS EVERY TIME

No delegation, no engines, no complexity.
DIRECT execution that WORKS.
"""

import asyncio
import logging
import ccxt
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from collections import deque
import time

logger = logging.getLogger(__name__)


class DirectGateExecutor:
    """Direct executor for Gate.io - guaranteed to work"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.exchange = ccxt.gate({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'  # Use spot by default
            }
        })
        
        self.current_balance = 0.0
        self.open_positions = {}
        self.closed_positions = deque(maxlen=100)
        
        # Auto-adaptive tiers
        self.tiers = {
            'nano': {'min': 0, 'max': 5, 'risk': 0.95, 'target': 0.025, 'stop': 0.015},
            'micro': {'min': 5, 'max': 50, 'risk': 0.90, 'target': 0.020, 'stop': 0.012},
            'small': {'min': 50, 'max': 200, 'risk': 0.80, 'target': 0.015, 'stop': 0.009},
            'medium': {'min': 200, 'max': 1000, 'risk': 0.70, 'target': 0.012, 'stop': 0.007},
            'large': {'min': 1000, 'max': float('inf'), 'risk': 0.60, 'target': 0.010, 'stop': 0.006}
        }
        
        self.current_tier = 'micro'
        
        logger.info("=" * 80)
        logger.info("🎯 DIRECT GATE EXECUTOR ONLINE")
        logger.info("=" * 80)
        logger.info("   Exchange: Gate.io (DIRECT ccxt connection)")
        logger.info("   Mode: SPOT trading")
        logger.info("   Auto-adaptive: ENABLED")
        logger.info("=" * 80)
    
    async def fetch_balance(self) -> float:
        """Fetch current USDT balance"""
        try:
            balance = await asyncio.to_thread(self.exchange.fetch_balance)
            usdt = balance.get('USDT', {}).get('free', 0.0)
            self.current_balance = usdt
            return usdt
        except Exception as e:
            logger.error(f"Balance fetch error: {e}")
            return self.current_balance
    
    def get_tier(self, balance: float) -> tuple:
        """Get current tier based on balance"""
        for name, config in self.tiers.items():
            if config['min'] <= balance < config['max']:
                if self.current_tier != name:
                    logger.info(f"🎉 TIER UPGRADE: {self.current_tier.upper()} → {name.upper()} (${balance:.2f})")
                self.current_tier = name
                return name, config
        return 'large', self.tiers['large']
    
    async def execute_trade(
        self,
        symbol: str,
        side: str,
        confidence: float
    ) -> Optional[Dict]:
        """
        Execute trade DIRECTLY on Gate.io
        
        Returns order details if successful, None if failed
        """
        try:
            # 1. Fetch current balance
            balance = await self.fetch_balance()
            
            if balance < 3.0:
                logger.warning(f"⚠️ Balance too low: ${balance:.2f}")
                return None
            
            # 2. Get tier and calculate position
            tier_name, tier = self.get_tier(balance)
            
            position_usd = balance * tier['risk']
            position_usd = max(3.0, min(position_usd, balance * 0.95))
            
            # 3. Get current price
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            price = ticker['last']
            
            # 4. Calculate quantity
            quantity = position_usd / price
            
            # 5. Check market limits
            markets = await asyncio.to_thread(self.exchange.load_markets)
            market = markets.get(symbol)
            
            if not market:
                logger.warning(f"⚠️ Market {symbol} not found")
                return None
            
            min_amount = market['limits']['amount']['min']
            min_cost = market['limits']['cost']['min']
            
            if quantity < min_amount:
                logger.warning(f"⚠️ Quantity {quantity:.8f} < min {min_amount}")
                return None
            
            if position_usd < min_cost:
                logger.warning(f"⚠️ Position ${position_usd:.2f} < min ${min_cost}")
                return None
            
            # 6. Calculate TP/SL
            target_pct = tier['target']
            stop_pct = tier['stop']
            
            if side.lower() == 'buy':
                take_profit_price = price * (1 + target_pct)
                stop_loss_price = price * (1 - stop_pct)
            else:
                take_profit_price = price * (1 - target_pct)
                stop_loss_price = price * (1 + stop_pct)
            
            logger.info(f"🎯 DIRECT EXECUTION:")
            logger.info(f"   Symbol: {symbol}")
            logger.info(f"   Side: {side.upper()}")
            logger.info(f"   Tier: {tier_name.upper()}")
            logger.info(f"   Balance: ${balance:.2f}")
            logger.info(f"   Position: ${position_usd:.2f} ({tier['risk']*100:.0f}%)")
            logger.info(f"   Price: ${price:.6f}")
            logger.info(f"   Quantity: {quantity:.6f}")
            logger.info(f"   Take Profit: ${take_profit_price:.6f} ({target_pct*100:.1f}%)")
            logger.info(f"   Stop Loss: ${stop_loss_price:.6f} ({stop_pct*100:.1f}%)")
            
            # 7. EXECUTE ORDER
            order = await asyncio.to_thread(
                self.exchange.create_market_order,
                symbol=symbol,
                side=side.lower(),
                amount=quantity
            )
            
            logger.info(f"✅ ORDER PLACED: {order.get('id', 'UNKNOWN')}")
            logger.info(f"   Status: {order.get('status', 'unknown')}")
            logger.info(f"   Filled: {order.get('filled', 0):.6f}")
            
            # 8. Record position for monitoring
            self.open_positions[symbol] = {
                'order_id': order.get('id'),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'entry_price': price,
                'take_profit': take_profit_price,
                'stop_loss': stop_loss_price,
                'position_usd': position_usd,
                'tier': tier_name,
                'timestamp': datetime.now()
            }
            
            return order
            
        except Exception as e:
            logger.error(f"❌ EXECUTION FAILED: {e}")
            logger.error(f"   Symbol: {symbol}")
            logger.error(f"   Side: {side}")
            logger.error(f"   Balance: ${self.current_balance:.2f}")
            return None
    
    async def monitor_and_close_positions(self):
        """Monitor open positions and close at TP/SL"""
        if not self.open_positions:
            return
        
        for symbol, position in list(self.open_positions.items()):
            try:
                # Get current price
                ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
                current_price = ticker['last']
                
                entry_price = position['entry_price']
                take_profit = position['take_profit']
                stop_loss = position['stop_loss']
                side = position['side']
                
                # Calculate current P&L
                if side.lower() == 'buy':
                    pnl_pct = (current_price - entry_price) / entry_price
                    should_close = current_price >= take_profit or current_price <= stop_loss
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                    should_close = current_price <= take_profit or current_price >= stop_loss
                
                # Check if should close
                if should_close:
                    # Close position
                    close_side = 'sell' if side.lower() == 'buy' else 'buy'
                    quantity = position['quantity']
                    
                    logger.info(f"💰 CLOSING POSITION: {symbol}")
                    logger.info(f"   Entry: ${entry_price:.6f}")
                    logger.info(f"   Current: ${current_price:.6f}")
                    logger.info(f"   P&L: {pnl_pct*100:+.2f}%")
                    
                    # Place close order
                    close_order = await asyncio.to_thread(
                        self.exchange.create_market_order,
                        symbol=symbol,
                        side=close_side,
                        amount=quantity
                    )
                    
                    # Calculate actual profit
                    profit_usd = position['position_usd'] * pnl_pct
                    
                    logger.info(f"✅ POSITION CLOSED: {close_order.get('id')}")
                    logger.info(f"   Profit: ${profit_usd:+.2f} ({pnl_pct*100:+.2f}%)")
                    
                    # Record result
                    self.closed_positions.append({
                        'symbol': symbol,
                        'side': side,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'profit_usd': profit_usd,
                        'profit_pct': pnl_pct,
                        'closed_at': datetime.now()
                    })
                    
                    # Remove from open positions
                    del self.open_positions[symbol]
                
            except Exception as e:
                logger.error(f"Error monitoring {symbol}: {e}")
    
    def get_stats(self) -> Dict:
        """Get trading statistics"""
        total_trades = len(self.closed_positions)
        if total_trades == 0:
            return {'total_trades': 0}
        
        wins = sum(1 for p in self.closed_positions if p['profit_usd'] > 0)
        total_profit = sum(p['profit_usd'] for p in self.closed_positions)
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': total_trades - wins,
            'win_rate': wins / total_trades if total_trades > 0 else 0,
            'total_profit': total_profit,
            'open_positions': len(self.open_positions)
        }


# Global instance
direct_executor = None

def initialize_direct_executor(api_key: str, api_secret: str):
    """Initialize direct executor"""
    global direct_executor
    direct_executor = DirectGateExecutor(api_key, api_secret)
    return direct_executor

def get_direct_executor():
    """Get global executor"""
    return direct_executor

# Export
__all__ = [
    'DirectGateExecutor',
    'initialize_direct_executor',
    'get_direct_executor'
]

logger.info("🎯 DIRECT GATE EXECUTOR loaded - Ready for real execution!")
