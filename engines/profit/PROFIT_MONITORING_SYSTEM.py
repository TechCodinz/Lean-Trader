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
    
    start_time = datetime.now()
    
    try:
        while True:
            try:
                # Get current price FIRST (before checking time) - prioritize profit detection!
                ticker = await asyncio.to_thread(exchange.fetch_ticker, symbol)
                current_price = ticker['last']
                
                # Calculate P&L
                if side == 'buy':
                    pnl_pct = (current_price - entry_price) / entry_price
                else:
                    pnl_pct = (entry_price - current_price) / entry_price
                
                # ⚡>> INSTANT PROFIT-TAKING: Close at 0.15% on 1m (ULTRA-FAST recycling!)
                if timeframe == '1m' and pnl_pct >= 0.0015:  # 0.15% profit
                    logger.info(f"⚡>> INSTANT PROFIT: {symbol} (+{pnl_pct:.2%}) - Closing IMMEDIATELY!")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return
                
                # >> FAST PROFIT-TAKING: Close at 0.4% on 5m
                if timeframe == '5m' and pnl_pct >= 0.004:  # 0.4% profit
                    logger.info(f"⚡>> FAST PROFIT: {symbol} (+{pnl_pct:.2%}) - Closing IMMEDIATELY!")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return
                
                # 🎯 FAST PROFIT-TAKING: Close at 1.2% on 15m
                if timeframe == '15m' and pnl_pct >= 0.012:  # 1.2% profit
                    logger.info(f"⚡ FAST PROFIT: {symbol} (+{pnl_pct:.2%}) - Closing IMMEDIATELY!")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return
                
                # ⚡ AGGRESSIVE PROFIT-TAKING: Close at FIRST TP hit!
                for i, tp_level in enumerate(tp_levels):
                    tp_price = tp_level['price']
                    
                    if (side == 'buy' and current_price >= tp_price) or \
                       (side == 'sell' and current_price <= tp_price):
                        logger.info(f"🎯 TP{i+1} HIT: {symbol} (+{pnl_pct:.2%}) - CLOSING FAST!")
                        logger.info(f"   Entry: ${entry_price:.6f}")
                        logger.info(f"   Exit: ${current_price:.6f}")
                        logger.info(f"   💰 PROFIT: +{pnl_pct:.2%}")
                        elapsed_min = (datetime.now() - start_time).seconds / 60
                        logger.info(f"   ⚡ Held for: {elapsed_min:.2f} min → Freeing capital!")
                        
                        await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                        return  # ⚡ EXIT IMMEDIATELY - Free capital for next trade!
                
                # 🔮 INTELLIGENT EXIT: Exit BEFORE massive stop-loss hits!
                if pnl_pct <= -0.006:  # 0.6% loss - VERY EARLY exit!
                    elapsed_min = (datetime.now() - start_time).seconds / 60
                    logger.warning(f"🛑>> EARLY STOP: {symbol} ({pnl_pct:.2%}) - Closing at 0.6% to preserve capital!")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return
                
                # Check stop loss (backup only - should rarely hit with early exits!)
                if (side == 'buy' and current_price <= stop_loss) or \
                   (side == 'sell' and current_price >= stop_loss):
                    elapsed_min = (datetime.now() - start_time).seconds / 60
                    logger.warning(f"🛑 STOP LOSS HIT: {symbol} ({pnl_pct:.2%})")
                    logger.warning(f"   Loss: {pnl_pct:.2%} | Held: {elapsed_min:.2f} min")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return  # Exit monitoring
                
                # 🧟 STALE POSITION CHECK: Close if profit > 0.1% and held > 3 mins
                elapsed_min = (datetime.now() - start_time).seconds / 60
                if elapsed_min > 3 and pnl_pct > 0.001:
                    logger.info(f"🧟 STALE PROFIT: {symbol} (+{pnl_pct:.2%}) held > 3m - Closing to free capital")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return
                
                # 🔥 FIX: STRICT max hold time!
                if elapsed_min > max_hold_min:
                    logger.info(f"⏰ Max hold time reached for {symbol} ({elapsed_min:.1f} min > {max_hold_min:.1f} min), closing at market")
                    logger.info(f"   📊 Final P&L: {pnl_pct:.2%}")
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                    return
                
            except Exception as e:
                logger.debug(f"Price check error for {symbol}: {e}")
            
            # 🔥 CRITICAL FIX: Sleep MUST be inside the while loop!
            await asyncio.sleep(check_interval)
    
    except Exception as e:
        logger.error(f"Monitoring error for {symbol}: {e}")


async def close_position_at_market(exchange, symbol: str, entry_price: float,
                                   side: str, pnl_pct: float, orchestrator=None):
    """🔥 FIX: Actually close position at market price and record profit"""
    try:
        logger.info(f"💰 CLOSING POSITION: {symbol}")
        logger.info(f"   Entry: ${entry_price:.6f}")
        logger.info(f"   P&L: {pnl_pct:+.2%}")
        
        # 🔥 CRITICAL FIX: Get position size from orchestrator or trade plan
        position_size = None
        position_quantity = None
        
        if orchestrator:
            # Try to get position from orchestrator's risk manager
            if hasattr(orchestrator, 'risk_manager') and orchestrator.risk_manager:
                if symbol in orchestrator.risk_manager.open_positions:
                    position = orchestrator.risk_manager.open_positions[symbol]
                    position_size = position.get('size_usd', 0)
                    position_quantity = position.get('size', 0)
                    logger.info(f"   📊 Position size: ${position_size:.2f} (quantity: {position_quantity})")
        
        # If we don't have size, try to get from exchange balance
        if not position_quantity or position_quantity <= 0:
            try:
                balance = await asyncio.to_thread(exchange.fetch_balance)
                base_currency = symbol.split('/')[0]  # e.g., 'BTC' from 'BTC/USDT'
                if base_currency in balance:
                    base_bal = balance[base_currency]
                    if isinstance(base_bal, dict):
                        position_quantity = base_bal.get('free', 0)
                    else:
                        position_quantity = float(base_bal) if base_bal else 0
                    logger.info(f"   📊 Got quantity from balance: {position_quantity}")
            except Exception as e:
                logger.warning(f"     Could not get position quantity: {e}")
        
        # 🔥 ACTUALLY CLOSE THE POSITION ON EXCHANGE!
        if position_quantity and position_quantity > 0:
            # Determine close side (opposite of entry side)
            close_side = 'sell' if side.lower() == 'buy' else 'buy'
            
            logger.info(f"   >> Executing close order: {close_side} {position_quantity} {symbol}")
            
            try:
                # Create market order to close position
                close_order = await asyncio.to_thread(
                    exchange.create_market_order,
                    symbol=symbol,
                    side=close_side,
                    amount=position_quantity
                )
                
                logger.info(f"[OK] POSITION CLOSED ON EXCHANGE: {symbol}")
                logger.info(f"   Order ID: {close_order.get('id', 'N/A')}")
                logger.info(f"   💵 PROFIT REALIZED: {pnl_pct:+.2%}")
                
                # Notify about profit
                if pnl_pct > 0:
                    logger.info(f"[OK] WINNING TRADE: +{pnl_pct:.2%}! 🎉")
                else:
                    logger.info(f"[X] Losing trade: {pnl_pct:.2%}")
                
                # Record in orchestrator if provided
                if orchestrator:
                    # Use orchestrator's close_position method to update tracking
                    if hasattr(orchestrator, 'close_position'):
                        current_price = entry_price * (1 + pnl_pct) if side == 'buy' else entry_price * (1 - pnl_pct)
                        pnl_usd = orchestrator.close_position(symbol, current_price)
                        logger.info(f"   📊 P&L recorded: ${pnl_usd:+.2f}")
                    elif hasattr(orchestrator, 'record_closed_trade'):
                        current_price = entry_price * (1 + pnl_pct) if side == 'buy' else entry_price * (1 - pnl_pct)
                        orchestrator.record_closed_trade(symbol, entry_price, current_price, pnl_pct)
                        logger.info(f"   📊 Profit recorded in orchestrator")
                
            except Exception as e:
                logger.error(f"   [X] Failed to close position on exchange: {e}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"     Cannot close: No position quantity found for {symbol}")
            logger.warning(f"   Position may already be closed or not tracked properly")
        
    except Exception as e:
        logger.error(f"Close position error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
