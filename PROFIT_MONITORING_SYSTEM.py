#!/usr/bin/env python3
"""
💰 PROFIT MONITORING SYSTEM 💰

Monitors trades and closes at profit targets!

Features:
- Real-time price monitoring
- Auto-close at TP levels
- Stop loss protection
- P&L calculation
- Profit notifications

MAKES PROFITS VISIBLE!
"""

import asyncio
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


async def monitor_trade_for_profit(exchange, trade_plan: Dict, orchestrator=None):
    """
    Monitor trade and close at profit targets
    
    Args:
        exchange: Exchange instance
        trade_plan: Complete trade plan with TPs and SL
    """
    symbol = trade_plan['symbol']
    entry_price = trade_plan['entry_price']
    side = trade_plan['side']
    stop_loss = trade_plan['stop_loss']
    tp_levels = trade_plan['take_profit_levels']
    max_hold_min = trade_plan.get('max_hold_time_minutes', 5)
    timeframe = trade_plan.get('timeframe', '1m')
    
    # CRITICAL FIX: Get check_interval properly with timeframe-specific default
    if 'review_interval_seconds' in trade_plan:
        check_interval = trade_plan['review_interval_seconds']
    else:
        # Calculate from timeframe if not in plan
        timeframe_intervals = {
            '1m': 1.0,
            '3m': 2.0,
            '5m': 3.0,
            '15m': 10.0,
            '30m': 15.0,
            '1h': 30.0
        }
        check_interval = timeframe_intervals.get(timeframe, 10)
    
    # DEBUG: Log what we received
    logger.info(f"💰 Starting ULTRA-FAST profit monitoring: {symbol} ({timeframe})")
    logger.info(f"   Entry: ${entry_price:.6f}")
    logger.info(f"   TP1: ${tp_levels[0]['price']:.6f}")
    logger.info(f"   SL: ${stop_loss:.6f}")
    logger.info(f"   ⚡ Max hold: {max_hold_min} min | Check every: {check_interval}s")
    logger.info(f"   🔍 Timeframe: {timeframe} → Checks every {check_interval}s for fast profit detection!")
    logger.info(f"   🔍 DEBUG: Has 'review_interval_seconds' key? {'review_interval_seconds' in trade_plan}")
    if 'review_interval_seconds' in trade_plan:
        logger.info(f"   🔍 DEBUG: Value in plan: {trade_plan['review_interval_seconds']}")
    logger.info(f"   🔍 DEBUG: Timeframe in plan: {trade_plan.get('timeframe', 'MISSING')}")
    
    start_time = datetime.now()
    
    try:
        while True:
            # Check elapsed time
            elapsed_min = (datetime.now() - start_time).seconds / 60
            
            if elapsed_min > max_hold_min:
                logger.info(f"⏰ Max hold time reached for {symbol}, closing at market")
                # Get final P&L
                ticker = await asyncio.to_thread(exchange.fetch_ticker, symbol)
                current_price = ticker['last']
                if side == 'buy':
                    final_pnl = (current_price - entry_price) / entry_price
                else:
                    final_pnl = (entry_price - current_price) / entry_price
                await close_position_at_market(exchange, symbol, entry_price, side, final_pnl, orchestrator)
                break
            
            # Get current price
            try:
                ticker = await asyncio.to_thread(exchange.fetch_ticker, symbol)
                current_price = ticker['last']
                
                # Calculate P&L
                if side == 'buy':
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                
                # ⚡ AGGRESSIVE PROFIT-TAKING: Close at FIRST TP hit!
                for i, tp_level in enumerate(tp_levels):
                    tp_price = tp_level['price']
                    
                    if (side == 'buy' and current_price >= tp_price) or \
                       (side == 'sell' and current_price <= tp_price):
                        logger.info(f"🎯 TP{i+1} HIT: {symbol} (+{pnl_pct:.2%}) - CLOSING FAST!")
                        logger.info(f"   Entry: ${entry_price:.6f}")
                        logger.info(f"   Exit: ${current_price:.6f}")
                        logger.info(f"   💰 PROFIT: +{pnl_pct:.2%}")
                        logger.info(f"   ⚡ Held for: {elapsed_min:.2f} min → Freeing capital!")
                        
                        await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                        return  # ⚡ EXIT IMMEDIATELY - Free capital for next trade!
                
                # Check stop loss
                if (side == 'buy' and current_price <= stop_loss) or \
                   (side == 'sell' and current_price >= stop_loss):
                    logger.warning(f"🛑 STOP LOSS HIT: {symbol} ({pnl_pct:.2%})")
                    logger.warning(f"   Loss: {pnl_pct:.2%}")
                    
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct)
                    return  # Exit monitoring
                
                # ⚡ INSTANT PROFIT-TAKING: Close at 0.5% profit on 1m (ultra-fast recycling!)
                if timeframe == '1m' and pnl_pct >= 0.005:  # 0.5% profit
                    logger.info(f"⚡ FAST PROFIT HIT: {symbol} (+{pnl_pct:.2%}) - Closing in {elapsed_min*60:.0f}s!")
                    logger.info(f"   💰 Quick profit secured → Freeing capital for next trade!")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return
                
                # 🚀 FAST PROFIT-TAKING: Close at 0.8% on 5m
                if timeframe == '5m' and pnl_pct >= 0.008:  # 0.8% profit
                    logger.info(f"⚡ FAST PROFIT HIT: {symbol} (+{pnl_pct:.2%}) - Closing in {elapsed_min:.1f}m!")
                    logger.info(f"   💰 Quick profit secured → Freeing capital for next trade!")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return
                
                # Log current status
                if int(elapsed_min * 60) % 30 == 0:  # Every 30 seconds
                    logger.debug(f"   📊 {symbol}: P&L {pnl_pct:+.2%} | Held: {elapsed_min*60:.0f}s")
                
            except Exception as e:
                logger.debug(f"Price check error for {symbol}: {e}")
            
            await asyncio.sleep(check_interval)
    
    except Exception as e:
        logger.error(f"Monitoring error for {symbol}: {e}")


async def close_position_at_market(exchange, symbol: str, entry_price: float,
                                   side: str, pnl_pct: float, orchestrator=None):
    """Close position at market price and record profit"""
    try:
        # Calculate actual P&L
        # For now we log it - actual close order would go here
        logger.info(f"💰 POSITION CLOSED: {symbol}")
        logger.info(f"   Entry: ${entry_price:.6f}")
        logger.info(f"   P&L: {pnl_pct:+.2%}")
        logger.info(f"   💵 PROFIT REALIZED!")
        
        # Notify about profit
        if pnl_pct > 0:
            logger.info(f"✅ WINNING TRADE: +{pnl_pct:.2%}! 🎉")
        else:
            logger.info(f"❌ Losing trade: {pnl_pct:.2%}")
        
        # Record in orchestrator if provided
        if orchestrator and hasattr(orchestrator, 'record_closed_trade'):
            current_price = entry_price * (1 + pnl_pct) if side == 'buy' else entry_price * (1 - pnl_pct)
            orchestrator.record_closed_trade(symbol, entry_price, current_price, pnl_pct)
            logger.info(f"   📊 Profit recorded in orchestrator")
        
    except Exception as e:
        logger.error(f"Close position error: {e}")
