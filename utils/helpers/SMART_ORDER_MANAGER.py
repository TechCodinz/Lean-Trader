#!/usr/bin/env python3
"""
SMART ORDER MANAGER - Intelligent order placement
Uses limit orders for 80% fee reduction (0.01% vs 0.15%)
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class SmartOrderManager:
    """
    Smart order placement with limit orders, fee optimization, and retries
    """
    
    def __init__(self, exchange, use_limit_orders: bool = True):
        self.exchange = exchange
        self.use_limit_orders = use_limit_orders
        self.pending_orders = {}
        
        # Fee rates
        self.maker_fee = 0.0001  # 0.01% (limit orders)
        self.taker_fee = 0.00075  # 0.075% (market orders)
        
        # Configuration
        self.limit_order_timeout = 30  # seconds to wait for fill
        self.price_improvement_pct = 0.0005  # 0.05% better than market
        self.max_retries = 3
        
        logger.info("🎯 Smart Order Manager initialized")
        if use_limit_orders:
            logger.info(f"   💰 Using LIMIT orders (maker fee: {self.maker_fee*100:.2f}%)")
        else:
            logger.info(f"   ⚡ Using MARKET orders (taker fee: {self.taker_fee*100:.2f}%)")
    
    async def place_smart_order(self, 
                                symbol: str,
                                side: str,
                                amount: float,
                                price: float = None,
                                stop_loss: float = None,
                                take_profit: float = None) -> Dict:
        """
        Place order intelligently:
        - Uses limit orders by default (cheaper fees)
        - Falls back to market if limit doesn't fill
        - Adds stop loss and take profit automatically
        """
        
        try:
            # Get current market price if not provided
            if not price:
                ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
                if side == 'buy':
                    price = ticker['ask']
                else:
                    price = ticker['bid']
            
            # Calculate limit order price (slightly better than market)
            if self.use_limit_orders:
                if side == 'buy':
                    # Bid slightly above current bid (more likely to fill as maker)
                    limit_price = price * (1 + self.price_improvement_pct)
                else:
                    # Ask slightly below current ask
                    limit_price = price * (1 - self.price_improvement_pct)
                
                logger.info(f"📝 Placing LIMIT {side.upper()} order: {symbol}")
                logger.info(f"   Amount: {amount:.8f} | Price: ${limit_price:.8f}")
                
                # Place limit order
                order = await self._place_limit_with_retry(symbol, side, amount, limit_price)
                
                if order:
                    # Wait for fill or timeout
                    filled = await self._wait_for_fill(order['id'], symbol, timeout=self.limit_order_timeout)
                    
                    if filled:
                        logger.info(f"[OK] LIMIT order filled: {symbol} @ ${limit_price:.8f}")
                        
                        # Add stop loss and take profit
                        if stop_loss or take_profit:
                            await self._add_exit_orders(symbol, side, amount, order['price'], stop_loss, take_profit)
                        
                        return {
                            'success': True,
                            'order': order,
                            'order_type': 'limit',
                            'fee_pct': self.maker_fee,
                        }
                    else:
                        # Limit order didn't fill, cancel and use market
                        logger.warning(f"  LIMIT order timeout, switching to MARKET: {symbol}")
                        try:
                            await asyncio.to_thread(self.exchange.cancel_order, order['id'], symbol)
                        except:
                            pass
                        
                        # Fall through to market order
            
            # Market order (instant fill, higher fees)
            logger.info(f"⚡ Placing MARKET {side.upper()} order: {symbol}")
            logger.info(f"   Amount: {amount:.8f}")
            
            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol,
                'market',
                side,
                amount
            )
            
            logger.info(f"[OK] MARKET order filled: {symbol}")
            
            # Add stop loss and take profit
            if stop_loss or take_profit:
                await self._add_exit_orders(symbol, side, amount, order.get('price', price), stop_loss, take_profit)
            
            return {
                'success': True,
                'order': order,
                'order_type': 'market',
                'fee_pct': self.taker_fee,
            }
            
        except Exception as e:
            logger.error(f"[X] Order placement error: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    async def _place_limit_with_retry(self, symbol: str, side: str, amount: float, price: float, retry: int = 0) -> Optional[Dict]:
        """Place limit order with retry logic"""
        try:
            order = await asyncio.to_thread(
                self.exchange.create_order,
                symbol,
                'limit',
                side,
                amount,
                price
            )
            return order
            
        except Exception as e:
            if retry < self.max_retries:
                logger.warning(f"  Limit order failed (attempt {retry+1}/{self.max_retries}), retrying...")
                await asyncio.sleep(1)
                return await self._place_limit_with_retry(symbol, side, amount, price, retry + 1)
            else:
                logger.error(f"[X] Limit order failed after {self.max_retries} retries: {e}")
                return None
    
    async def _wait_for_fill(self, order_id: str, symbol: str, timeout: int = 30) -> bool:
        """Wait for order to fill or timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                order = await asyncio.to_thread(self.exchange.fetch_order, order_id, symbol)
                
                if order['status'] == 'closed':
                    return True
                elif order['status'] == 'canceled':
                    return False
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"[X] Error checking order status: {e}")
                await asyncio.sleep(2)
        
        return False  # Timeout
    
    async def _add_exit_orders(self, symbol: str, entry_side: str, amount: float, entry_price: float, 
                               stop_loss_pct: float = None, take_profit_pct: float = None):
        """Add stop loss and take profit orders"""
        try:
            exit_side = 'sell' if entry_side == 'buy' else 'buy'
            
            # Calculate stop loss and take profit prices
            if entry_side == 'buy':
                if stop_loss_pct:
                    sl_price = entry_price * (1 - stop_loss_pct)
                if take_profit_pct:
                    tp_price = entry_price * (1 + take_profit_pct)
            else:
                if stop_loss_pct:
                    sl_price = entry_price * (1 + stop_loss_pct)
                if take_profit_pct:
                    tp_price = entry_price * (1 - take_profit_pct)
            
            # Place stop loss
            if stop_loss_pct:
                try:
                    sl_order = await asyncio.to_thread(
                        self.exchange.create_order,
                        symbol,
                        'stop',
                        exit_side,
                        amount,
                        sl_price
                    )
                    logger.info(f"🛡️  Stop Loss set @ ${sl_price:.8f}")
                except Exception as e:
                    logger.warning(f"  Stop loss placement failed: {e}")
            
            # Place take profit
            if take_profit_pct:
                try:
                    tp_order = await asyncio.to_thread(
                        self.exchange.create_order,
                        symbol,
                        'limit',
                        exit_side,
                        amount,
                        tp_price
                    )
                    logger.info(f"🎯 Take Profit set @ ${tp_price:.8f}")
                except Exception as e:
                    logger.warning(f"  Take profit placement failed: {e}")
                    
        except Exception as e:
            logger.error(f"[X] Exit orders error: {e}")
    
    def calculate_fee_savings(self, trade_value: float) -> Dict:
        """Calculate fee savings from using limit vs market orders"""
        market_fee = trade_value * self.taker_fee
        limit_fee = trade_value * self.maker_fee
        savings = market_fee - limit_fee
        savings_pct = (savings / market_fee) * 100
        
        return {
            'market_fee': market_fee,
            'limit_fee': limit_fee,
            'savings': savings,
            'savings_pct': savings_pct,
        }


# Example usage
if __name__ == '__main__':
    print("=" * 80)
    print("🎯 SMART ORDER MANAGER - FEE SAVINGS CALCULATOR")
    print("=" * 80)
    print()
    
    manager = SmartOrderManager(None, use_limit_orders=True)
    
    # Calculate savings for different trade sizes
    trade_sizes = [10, 50, 100, 500, 1000]
    
    print("Trade Size | Market Fee | Limit Fee | Savings | Savings %")
    print("-" * 70)
    
    for size in trade_sizes:
        fees = manager.calculate_fee_savings(size)
        print(f"${size:6.0f}    | ${fees['market_fee']:6.3f}    | ${fees['limit_fee']:5.3f}    | ${fees['savings']:5.3f}  | {fees['savings_pct']:5.1f}%")
    
    print()
    print("=" * 80)
    print("💡 KEY INSIGHT:")
    print("   Using LIMIT orders saves 87% on fees!")
    print("   On $1000 worth of trades: Save $0.65 per trade")
    print("   100 trades/day = $65/day = $1,950/month in fee savings!")
    print("=" * 80)
