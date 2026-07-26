#!/usr/bin/env python3
"""
💰 AUTO PROFIT TAKER
Automatically closes positions when they hit profit targets
This is WHY trades aren't closing - we need this!
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AutoProfitTaker:
    """
    Monitors open positions and closes them when profit targets hit
    
    This is CRITICAL - without this, positions never close!
    """
    
    def __init__(self, exchange, data_hub):
        self.exchange = exchange
        self.data_hub = data_hub
        
        # Track open positions
        self.open_positions = {}  # symbol -> position_data
        
        # Profit taking settings
        self.profit_targets = {
            'quick_scalp': 0.002,  # 0.3% for quick scalps
            'normal': 0.005,  # 1% for normal trades
            'swing': 0.03,  # 3% for swing trades
        }
        
        self.stop_loss = 0.015  # 1.5% stop loss
        
        # Performance tracking
        self.total_closed = 0
        self.total_profit = 0.0
        self.winning_closes = 0
        
        logger.info("💰 Auto Profit Taker initialized")
        logger.info(f"   Quick scalp target: {self.profit_targets['quick_scalp']:.1%}")
        logger.info(f"   Normal target: {self.profit_targets['normal']:.1%}")
        logger.info(f"   Stop loss: {self.stop_loss:.1%}")
        
        # Position scaling settings
        self.enable_scaling = True  # Enable partial closes
        self.scale_out_pct = 0.5    # Close 50% at first TP

    
    def register_position(self, symbol: str, side: str, entry_price: float, 
                         size: float, strategy: str = 'normal'):
        """
        Register a new position that was opened
        """
        self.open_positions[symbol] = {
            'side': side,
            'entry_price': entry_price,
            'size': size,
            'strategy': strategy,
            'opened_at': datetime.now(),
            'profit_target': self.profit_targets.get(strategy, self.profit_targets['normal']),
            'scaled_out': False,  # Track if 50% already closed
            'remaining_size': size  # Track remaining position size
        }

        
        logger.info(f"📝 Position registered: {symbol} {side}")
        logger.info(f"   Entry: ${entry_price:.4f}")
        logger.info(f"   Target: {self.profit_targets.get(strategy, 0.01):.1%}")
    
    async def check_and_close_positions(self):
        """
        Check all open positions and close if profit/loss targets hit
        
        Returns list of closed positions
        """
        closed_positions = []
        
        if not self.open_positions:
            return closed_positions
        
        for symbol in list(self.open_positions.keys()):
            try:
                position = self.open_positions[symbol]
                
                # Get current price
                ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
                current_price = ticker['last']
                
                # Calculate P&L
                entry_price = position['entry_price']
                side = position['side']
                
                if side.lower() == 'buy':
                    # Long position
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    # Short position
                    pnl_pct = (entry_price - current_price) / entry_price
                
                profit_target = position['profit_target']
                
                # Check if should close
                should_close = False
                close_reason = ""
                
                if pnl_pct >= profit_target:
                    should_close = True
                    close_reason = f"PROFIT TARGET HIT: {pnl_pct:.2%}"
                elif pnl_pct <= -self.stop_loss:
                    should_close = True
                    close_reason = f"STOP LOSS HIT: {pnl_pct:.2%}"
                elif (datetime.now() - position['opened_at']).total_seconds() > 3600:
                    # Time stop - close after 1 hour regardless
                    should_close = True
                    close_reason = f"TIME STOP: 1 hour (P&L: {pnl_pct:.2%})"
                
                if should_close:
                    # Close position
                    size = position['size']
                    
                    if side.lower() == 'buy':
                        # Close long = sell
                        order = await asyncio.to_thread(
                            self.exchange.create_market_sell_order,
                            symbol,
                            size
                        )
                    else:
                        # Close short = buy
                        cost = current_price * size
                        order = await asyncio.to_thread(
                            self.exchange.create_market_buy_order,
                            symbol,
                            cost
                        )
                    
                    # Calculate actual profit
                    profit_usd = entry_price * size * pnl_pct
                    
                    # Record closure
                    self.total_closed += 1
                    self.total_profit += profit_usd
                    if profit_usd > 0:
                        self.winning_closes += 1
                    
                    closed_data = {
                        'symbol': symbol,
                        'side': side,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'size': size,
                        'pnl_pct': pnl_pct,
                        'profit_usd': profit_usd,
                        'reason': close_reason,
                        'duration': (datetime.now() - position['opened_at']).total_seconds()
                    }
                    
                    closed_positions.append(closed_data)
                    
                    logger.info(f"💰 POSITION CLOSED: {symbol}")
                    logger.info(f"   {close_reason}")
                    logger.info(f"   Profit: ${profit_usd:.2f} ({pnl_pct:.2%})")
                    logger.info(f"   Duration: {closed_data['duration']/60:.1f} minutes")
                    
                    # Remove from tracking
                    del self.open_positions[symbol]
            
            except Exception as e:
                logger.debug(f"Position check error for {symbol}: {e}")
        
        return closed_positions
    
    def get_stats(self) -> Dict:
        """Get profit taking statistics"""
        return {
            'open_positions': len(self.open_positions),
            'total_closed': self.total_closed,
            'winning_closes': self.winning_closes,
            'win_rate': self.winning_closes / max(self.total_closed, 1) * 100,
            'total_profit': self.total_profit,
            'avg_profit': self.total_profit / max(self.total_closed, 1)
        }
