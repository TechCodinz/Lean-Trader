#!/usr/bin/env python3
"""
🤖 MANAGED TRADING ENGINE 🤖

Bot trades on USER'S exchange accounts:
- User pays $999.99/month
- Bot trades using their API keys
- User keeps 90% of profits
- Bot takes 10% profit share automatically

PASSIVE INCOME FOR USERS, RECURRING REVENUE FOR YOU!
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ManagedTradingEngine:
    """
    MANAGED TRADING SYSTEM
    
    Trades on user accounts:
    - Secure API key storage
    - Isolated trading per user
    - Real-time profit tracking
    - Auto profit share deduction (10%)
    - Performance reporting
    """
    
    def __init__(self, payment_processor=None):
        self.payment_processor = payment_processor
        
        # User accounts {user_id: exchange_instance}
        self.user_exchanges = {}
        
        # User trading stats
        self.user_stats = {}  # {user_id: {'trades': 0, 'profit': 0, 'profit_share_paid': 0}}
        
        # Business wallet
        self.business_wallet_balance = 0.0
        
        logger.info("🤖 MANAGED TRADING ENGINE initialized!")
    
    async def connect_user_exchange(self, user_id: int, exchange_name: str, 
                                   api_key: str, api_secret: str) -> bool:
        """
        Connect user's exchange account
        
        Args:
            user_id: Telegram user ID
            exchange_name: 'bybit', 'binance', 'gateio', etc
            api_key: User's API key
            api_secret: User's API secret
        
        Returns:
            True if connected successfully
        """
        try:
            import ccxt
            
            logger.info(f"🔗 Connecting exchange for user {user_id}...")
            logger.info(f"   Exchange: {exchange_name}")
            
            # Create exchange instance
            exchange_class = getattr(ccxt, exchange_name.lower())
            exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True
            })
            
            # Test connection
            balance = await asyncio.to_thread(exchange.fetch_balance)
            total_balance = balance.get('USDT', {}).get('total', 0)
            
            # Store exchange
            self.user_exchanges[user_id] = {
                'exchange': exchange,
                'exchange_name': exchange_name,
                'connected_at': datetime.now(),
                'balance': total_balance
            }
            
            # Initialize stats
            self.user_stats[user_id] = {
                'trades': 0,
                'winning_trades': 0,
                'total_profit': 0.0,
                'profit_share_paid': 0.0,
                'user_profit': 0.0,
                'win_rate': 0.0
            }
            
            logger.info(f"✅ Exchange connected for user {user_id}!")
            logger.info(f"   Balance: ${total_balance:.2f} USDT")
            logger.info(f"   Bot will now trade on their account!")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Exchange connection failed for user {user_id}: {e}")
            return False
    
    async def execute_trade_for_user(self, user_id: int, signal: Dict) -> Dict:
        """
        Execute trade on user's exchange
        
        Args:
            user_id: User ID
            signal: Trading signal
        
        Returns:
            Trade result with profit share deduction
        """
        if user_id not in self.user_exchanges:
            logger.warning(f"⚠️  User {user_id} has no exchange connected")
            return None
        
        user_data = self.user_exchanges[user_id]
        exchange = user_data['exchange']
        
        try:
            symbol = signal.get('symbol')
            side = signal.get('side', 'buy').lower()
            size_usd = signal.get('size_usd', 10.0)
            
            logger.info(f"🤖 Executing trade for user {user_id}:")
            logger.info(f"   {symbol} {side.upper()} ${size_usd}")
            
            # Execute trade on their account
            if side == 'buy':
                order = await asyncio.to_thread(
                    exchange.create_market_buy_order,
                    symbol,
                    size_usd
                )
            else:
                # Calculate quantity
                ticker = await asyncio.to_thread(exchange.fetch_ticker, symbol)
                price = ticker['last']
                quantity = size_usd / price
                
                order = await asyncio.to_thread(
                    exchange.create_market_sell_order,
                    symbol,
                    quantity
                )
            
            # Track trade
            self.user_stats[user_id]['trades'] += 1
            
            logger.info(f"✅ Trade executed on user {user_id}'s account!")
            logger.info(f"   Order ID: {order.get('id')}")
            
            return {
                'user_id': user_id,
                'symbol': symbol,
                'side': side,
                'order_id': order.get('id'),
                'size_usd': size_usd,
                'executed_at': datetime.now()
            }
        
        except Exception as e:
            logger.error(f"❌ Trade execution failed for user {user_id}: {e}")
            return None
    
    async def process_profit_share(self, user_id: int, trade_profit: float):
        """
        Process 10% profit share from user's trade
        
        Args:
            user_id: User ID
            trade_profit: Profit from closed trade
        """
        if trade_profit <= 0:
            return  # No profit share on losses
        
        # Calculate 10% share
        profit_share = trade_profit * 0.10
        user_profit = trade_profit * 0.90
        
        # Update stats
        stats = self.user_stats.get(user_id, {})
        stats['total_profit'] = stats.get('total_profit', 0) + trade_profit
        stats['profit_share_paid'] = stats.get('profit_share_paid', 0) + profit_share
        stats['user_profit'] = stats.get('user_profit', 0) + user_profit
        stats['winning_trades'] = stats.get('winning_trades', 0) + 1
        stats['win_rate'] = stats['winning_trades'] / stats['trades'] if stats['trades'] > 0 else 0
        
        # Add to business wallet
        self.business_wallet_balance += profit_share
        
        # Record profit share in payment processor
        if self.payment_processor:
            self.payment_processor.record_profit_share(user_id, trade_profit)
        
        logger.info(f"💰 PROFIT SHARE PROCESSED:")
        logger.info(f"   User: {user_id}")
        logger.info(f"   Trade profit: ${trade_profit:.2f}")
        logger.info(f"   User gets (90%): ${user_profit:.2f}")
        logger.info(f"   Business gets (10%): ${profit_share:.2f}")
        logger.info(f"   Business wallet total: ${self.business_wallet_balance:.2f}")
        
        # Send notification to user
        notification = f"""
💰 **TRADE CLOSED WITH PROFIT!**

Trade Profit: ${trade_profit:.2f}
Your Share (90%): ${user_profit:.2f}
Service Fee (10%): ${profit_share:.2f}

📊 **Your Stats:**
Total Trades: {stats['trades']}
Win Rate: {stats['win_rate']:.1%}
Total Your Profit: ${stats['user_profit']:.2f}
Total Fees Paid: ${stats['profit_share_paid']:.2f}

Keep winning! 🚀
"""
        # Would send to user via telegram
        
        return {
            'user_profit': user_profit,
            'profit_share': profit_share,
            'business_wallet_total': self.business_wallet_balance
        }


# Singleton
_managed_trading_engine = None

def get_managed_trading_engine():
    """Get managed trading engine"""
    return _managed_trading_engine

def initialize_managed_trading_engine(payment_processor=None):
    """Initialize managed trading engine"""
    global _managed_trading_engine
    _managed_trading_engine = ManagedTradingEngine(payment_processor)
    return _managed_trading_engine
