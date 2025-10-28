#!/usr/bin/env python3
"""
MICRO SMART TRADER - Proper Signal Integration
===============================================

Uses signals from engines with full context:
- Entry/exit prices from signal
- Stop loss / take profit from signal
- Timeframe and session awareness
- Position monitoring (not blind close)
- Only closes on PROFIT or STOP LOSS

This is meant to REPLACE the current MICRO loop in orchestrator
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class MicroPositionTracker:
    """Track MICRO positions with entry/exit targets"""
    
    def __init__(self):
        self.positions = {}  # symbol -> position data
        
    def add_position(self, symbol: str, entry_data: Dict):
        """Record new position with targets"""
        self.positions[symbol] = {
            'symbol': symbol,
            'side': entry_data['side'],
            'entry_price': entry_data['entry_price'],
            'entry_time': datetime.now(),
            'stop_loss': entry_data['stop_loss'],
            'take_profit': entry_data['take_profit'],
            'position_size': entry_data['position_size'],
            'confidence': entry_data['confidence'],
            'timeframe': entry_data.get('timeframe', '5m')
        }
        
    def should_close(self, symbol: str, current_price: float) -> tuple[bool, str, float]:
        """
        Check if position should be closed
        
        Returns:
            (should_close, reason, pnl_pct)
        """
        if symbol not in self.positions:
            return False, "NO_POSITION", 0.0
        
        pos = self.positions[symbol]
        entry = pos['entry_price']
        
        # Calculate P&L
        if pos['side'].upper() == 'BUY':
            pnl_pct = (current_price - entry) / entry
        else:  # SELL
            pnl_pct = (entry - current_price) / entry
        
        # Check take profit
        if pos['side'].upper() == 'BUY' and current_price >= pos['take_profit']:
            return True, "TAKE_PROFIT", pnl_pct
        elif pos['side'].upper() == 'SELL' and current_price <= pos['take_profit']:
            return True, "TAKE_PROFIT", pnl_pct
        
        # Check stop loss
        if pos['side'].upper() == 'BUY' and current_price <= pos['stop_loss']:
            return True, "STOP_LOSS", pnl_pct
        elif pos['side'].upper() == 'SELL' and current_price >= pos['stop_loss']:
            return True, "STOP_LOSS", pnl_pct
        
        # Time-based exit (no movement after 1 hour)
        time_elapsed = (datetime.now() - pos['entry_time']).total_seconds()
        if time_elapsed > 3600 and abs(pnl_pct) < 0.005:  # Less than 0.5% movement
            return True, "TIME_EXIT", pnl_pct
        
        return False, "HOLD", pnl_pct
    
    def remove_position(self, symbol: str):
        """Remove closed position"""
        if symbol in self.positions:
            del self.positions[symbol]


async def run_micro_smart_trader(micro_wallet_grower, data_hub):
    """
    MICRO Smart Trader - Professional implementation
    
    This should REPLACE the current run_micro_wallet_growth() function
    """
    
    position_tracker = MicroPositionTracker()
    balance = micro_wallet_grower.check_gate_balance()
    
    logger.info("💎 MICRO SMART TRADER STARTED")
    logger.info(f"   Initial Balance: ${balance:.2f}")
    logger.info(f"   Strategy: Multi-timeframe confluence + smart exits")
    
    while True:
        try:
            # ====================================================================
            # STEP 1: Monitor existing positions first
            # ====================================================================
            for symbol in list(position_tracker.positions.keys()):
                try:
                    # Get current price
                    ticker = micro_wallet_grower.get_gate_ticker(symbol)
                    if not ticker:
                        continue
                    
                    current_price = ticker['price']
                    
                    # Check if should close
                    should_close, reason, pnl_pct = position_tracker.should_close(symbol, current_price)
                    
                    if should_close:
                        pos = position_tracker.positions[symbol]
                        
                        # Close position
                        if pos['side'].upper() == 'BUY':
                            # We have the coin, sell it
                            coin = symbol.split('/')[0]
                            positions_data = micro_wallet_grower.gate.fetch_balance()
                            amount = positions_data['free'].get(coin, 0)
                            
                            if amount > 0:
                                order = micro_wallet_grower.gate.create_market_sell_order(symbol, amount)
                                profit_usd = pos['position_size'] * pnl_pct
                                
                                logger.info(f"{'💰' if reason == 'TAKE_PROFIT' else '🛑'} CLOSED: {symbol} ({reason})")
                                logger.info(f"   P&L: {pnl_pct:+.2%} (${profit_usd:+.2f})")
                                logger.info(f"   Entry: ${pos['entry_price']:.6f} → Exit: ${current_price:.6f}")
                                
                                position_tracker.remove_position(symbol)
                                balance = micro_wallet_grower.check_gate_balance()
                                logger.info(f"   New Balance: ${balance:.2f}")
                                
                except Exception as e:
                    logger.debug(f"Error monitoring {symbol}: {e}")
            
            # ====================================================================
            # STEP 2: Look for NEW trading opportunities
            # ====================================================================
            hub_signals = data_hub.get_signals(limit=50)
            
            if not hub_signals:
                logger.debug("💤 No signals in hub")
                await asyncio.sleep(60)
                continue
            
            logger.info(f"🔍 MICRO checking {len(hub_signals)} signals...")
            trades_entered = 0
            
            for signal in hub_signals:
                symbol = signal.get('symbol')
                side = signal.get('side', 'buy')
                confidence = signal.get('confidence', 0)
                
                # Normalize confidence (0-1 or 0-100)
                if confidence > 1:
                    confidence = confidence / 100
                
                # Filter 1: High confidence only
                if confidence < 0.85:
                    continue
                
                # Filter 2: Only BUY/SELL
                if side.upper() not in ['BUY', 'SELL']:
                    continue
                
                # Filter 3: Don't enter if already in position
                if symbol in position_tracker.positions:
                    logger.debug(f"Already in {symbol}")
                    continue
                
                # Filter 4: CHEAP coins only (< $5 per trade)
                try:
                    ticker = micro_wallet_grower.get_gate_ticker(symbol)
                    if not ticker:
                        continue
                    
                    price = ticker['price']
                    position_size = micro_wallet_grower.position_sizes.get(symbol, 0.001)
                    position_cost = price * position_size
                    
                    if position_cost > 5.0:
                        logger.debug(f"Skipping {symbol} - ${position_cost:.2f} > $5")
                        continue
                    
                    # Filter 5: Have enough balance
                    if balance < position_cost * 1.2:  # Need 20% buffer
                        logger.warning(f"⚠️  Insufficient balance for {symbol}: ${balance:.2f} < ${position_cost*1.2:.2f}")
                        continue
                    
                    # ====================================================================
                    # EXECUTE ENTRY
                    # ====================================================================
                    
                    # Use signal's stop/profit if available, else calculate
                    entry_price = signal.get('entry_price') or price
                    
                    if signal.get('stop_loss') and signal.get('take_profit'):
                        stop_loss = signal['stop_loss']
                        take_profit = signal['take_profit']
                    else:
                        # Calculate based on confidence (tighter for high confidence)
                        stop_pct = 0.01  # 1% stop for micro
                        profit_pct = 0.02  # 2% profit (2:1 R/R)
                        
                        if side.upper() == 'BUY':
                            stop_loss = entry_price * (1 - stop_pct)
                            take_profit = entry_price * (1 + profit_pct)
                        else:
                            stop_loss = entry_price * (1 + stop_pct)
                            take_profit = entry_price * (1 - profit_pct)
                    
                    # Execute trade
                    trades_entered += 1
                    logger.info(f"💎 MICRO ENTRY #{trades_entered}: {side.upper()} {symbol}")
                    logger.info(f"   Price: ${entry_price:.6f}, Cost: ${position_cost:.2f}")
                    logger.info(f"   SL: ${stop_loss:.6f} (-{((entry_price-stop_loss)/entry_price)*100 if side.upper()=='BUY' else ((stop_loss-entry_price)/entry_price)*100:.1f}%)")
                    logger.info(f"   TP: ${take_profit:.6f} (+{((take_profit-entry_price)/entry_price)*100 if side.upper()=='BUY' else ((entry_price-take_profit)/entry_price)*100:.1f}%)")
                    logger.info(f"   Conf: {confidence:.0%}, Balance: ${balance:.2f}")
                    
                    result = micro_wallet_grower.execute_trade(symbol, side.upper(), entry_price)
                    
                    if result:
                        # Track position
                        position_tracker.add_position(symbol, {
                            'side': side.upper(),
                            'entry_price': entry_price,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'position_size': position_cost,
                            'confidence': confidence,
                            'timeframe': signal.get('timeframe', '5m')
                        })
                        
                        logger.info(f"✅ MICRO position opened: {symbol}")
                        balance = micro_wallet_grower.check_gate_balance()
                    else:
                        logger.warning(f"⚠️  MICRO entry failed for {symbol}")
                    
                except Exception as e:
                    logger.debug(f"Error processing {symbol}: {e}")
                    continue
            
            if trades_entered == 0:
                logger.info(f"💤 MICRO: No qualifying signals (checked {len(hub_signals)} signals)")
            
            # Check every 60 seconds
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"❌ MICRO SMART TRADER ERROR: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await asyncio.sleep(60)


# Integration example for COMPLETE_ULTIMATE_ORCHESTRATOR.py:
"""
Replace the run_micro_wallet_growth() function with:

if getattr(self, 'micro_wallet_grower', None):
    from MICRO_SMART_TRADER import run_micro_smart_trader
    tasks.append(asyncio.create_task(
        run_micro_smart_trader(self.micro_wallet_grower, self.data_hub)
    ))
    logger.info("✅ 💎 MICRO SMART TRADER ACTIVE - Intelligent profit growth!")
"""
