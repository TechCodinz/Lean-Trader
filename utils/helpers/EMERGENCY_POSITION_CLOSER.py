#!/usr/bin/env python3
"""
EMERGENCY POSITION CLOSER

Closes orphaned/stuck positions that are wasting capital.
Positions get stuck when:
- Entry data not tracked (opened before Position Monitor started)
- Trade executed but not registered with AutoProfitTaker
- Position too old without movement

This script scans all open positions and closes those meeting emergency criteria.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import ccxt

logger = logging.getLogger(__name__)


class EmergencyPositionCloser:
    """
    Emergency closer for orphaned/stuck positions
    
    Criteria for emergency closure:
    - Position older than max_age_hours
    - Position value >= minimum order size
    - No catastrophic loss (P&L > max_loss_pct)
    """
    
    def __init__(self, exchange, max_age_hours: float = 2.0, max_loss_pct: float = -0.10):
        self.exchange = exchange
        self.max_age_hours = max_age_hours
        self.max_loss_pct = max_loss_pct  # -10% max loss before emergency close
        
        logger.info(f"[OK] Emergency Position Closer initialized")
        logger.info(f"   Max age: {max_age_hours} hours")
        logger.info(f"   Max loss: {max_loss_pct:.1%}")
    
    async def scan_and_close_orphaned(self) -> List[Dict[str, Any]]:
        """
        Scan for orphaned positions and close them
        
        Returns:
            List of closed position details
        """
        closed_positions = []
        
        try:
            # Fetch all open positions
            positions = await asyncio.to_thread(self.exchange.fetch_positions)
            
            if not positions:
                logger.debug("No open positions found")
                return closed_positions
            
            # Filter to active positions
            active_positions = [
                p for p in positions
                if float(p.get('contracts', 0) or 0) != 0
            ]
            
            if not active_positions:
                logger.debug("No active positions found")
                return closed_positions
            
            logger.info(f"Scanning {len(active_positions)} active positions for orphans...")
            
            for position in active_positions:
                try:
                    symbol = position['symbol']
                    contracts = float(position.get('contracts', 0))
                    side = position.get('side', '').lower()
                    entry_price = float(position.get('entryPrice', 0) or 0)
                    current_price = float(position.get('markPrice', 0) or position.get('lastPrice', 0) or 0)
                    notional_value = float(position.get('notional', 0) or (contracts * current_price))
                    timestamp = position.get('timestamp')
                    
                    # Skip if no entry price (can't calculate P&L)
                    if entry_price == 0:
                        logger.debug(f"{symbol}: No entry price, skipping")
                        continue
                    
                    # Calculate P&L
                    if side == 'long':
                        pnl_pct = (current_price - entry_price) / entry_price
                    elif side == 'short':
                        pnl_pct = (entry_price - current_price) / entry_price
                    else:
                        logger.warning(f"{symbol}: Unknown side '{side}', skipping")
                        continue
                    
                    # Check age (if timestamp available)
                    is_old = False
                    age_hours = None
                    if timestamp:
                        position_time = datetime.fromtimestamp(timestamp / 1000)
                        age = datetime.now() - position_time
                        age_hours = age.total_seconds() / 3600
                        is_old = age_hours > self.max_age_hours
                    
                    # Determine if should close
                    should_close = False
                    close_reason = ""
                    
                    # Rule 1: Old position without movement
                    if is_old:
                        should_close = True
                        close_reason = f"OLD POSITION ({age_hours:.1f}h > {self.max_age_hours}h)"
                    
                    # Rule 2: Catastrophic loss (override age requirement)
                    if pnl_pct < self.max_loss_pct:
                        should_close = True
                        close_reason = f"CATASTROPHIC LOSS ({pnl_pct:.1%})"
                    
                    # Rule 3: Dust position that's stuck
                    if notional_value < 5.0 and is_old:
                        should_close = True
                        close_reason = f"DUST POSITION (${notional_value:.2f})"
                    
                    if should_close:
                        logger.info(f"🚨 EMERGENCY CLOSE: {symbol} - {close_reason}")
                        logger.info(f"   Side: {side} | Entry: ${entry_price:.2f} | Current: ${current_price:.2f}")
                        logger.info(f"   P&L: {pnl_pct:.2%} | Value: ${notional_value:.2f}")
                        
                        # Close position
                        try:
                            if side == 'long':
                                # Close long = sell
                                cost = contracts * current_price
                                order = await asyncio.to_thread(
                                    self.exchange.create_market_sell_order,
                                    symbol,
                                    contracts
                                )
                            else:
                                # Close short = buy
                                cost = contracts * current_price
                                order = await asyncio.to_thread(
                                    self.exchange.create_market_buy_order,
                                    symbol,
                                    cost
                                )
                            
                            closed_data = {
                                'symbol': symbol,
                                'side': side,
                                'entry_price': entry_price,
                                'exit_price': current_price,
                                'contracts': contracts,
                                'pnl_pct': pnl_pct,
                                'reason': close_reason,
                                'age_hours': age_hours,
                                'timestamp': datetime.now()
                            }
                            
                            closed_positions.append(closed_data)
                            
                            logger.info(f"[OK] CLOSED: {symbol} | P&L: {pnl_pct:.2%}")
                            
                        except Exception as e:
                            logger.error(f"[X] Failed to close {symbol}: {e}")
                
                except Exception as e:
                    logger.error(f"Error processing position: {e}")
                    continue
            
            if closed_positions:
                logger.info(f"🎯 Emergency closer: {len(closed_positions)} positions closed")
            else:
                logger.info("[OK] No orphaned positions found")
            
        except Exception as e:
            logger.error(f"Emergency scan error: {e}")
        
        return closed_positions
    
    def get_stats(self) -> Dict[str, Any]:
        """Get emergency closer statistics"""
        return {
            'max_age_hours': self.max_age_hours,
            'max_loss_pct': self.max_loss_pct
        }


# Standalone execution
async def main():
    """Run emergency position closer standalone"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize exchange
    exchange = ccxt.bybit({
        'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
        'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
        'sandbox': True
    })
    
    # Create closer
    closer = EmergencyPositionCloser(exchange, max_age_hours=1.0)
    
    # Scan and close
    closed = await closer.scan_and_close_orphaned()
    
    if closed:
        print(f"\n🎯 Closed {len(closed)} orphaned positions:")
        for pos in closed:
            print(f"  - {pos['symbol']}: {pos['reason']} | P&L: {pos['pnl_pct']:.2%}")
    else:
        print("\n[OK] No orphaned positions found")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
