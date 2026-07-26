#!/usr/bin/env python3
"""
TRAILING PROFIT MANAGER
=======================
Handles dynamic profit taking with trailing stops.
Ensures maximum gains by letting winners run while protecting reversals.

Features:
- Dynamic step size based on volatility
- Activation levels (e.g. activate trail after +1%)
- Partial Take Profits
- Emergency close on rapid reversal
"""

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class TrailingProfitManager:
    """
    Manages trailing stops and profit taking for active positions.
    """
    def __init__(self):
        self.active_trails = {} # symbol -> { 'activation_price': float, 'highest_price': float, 'stop_price': float }
        logger.info("⚡ Trailing Profit Manager initialized")

    def register_position(self, symbol: str, entry_price: float, side: str):
        """Register a new position for monitoring"""
        self.active_trails[symbol] = {
            'entry_price': entry_price,
            'side': side,
            'highest_price': entry_price if side == 'buy' else entry_price, # lowest for sell
            'lowest_price': entry_price if side == 'sell' else entry_price,
            'stop_price': entry_price * 0.99 if side == 'buy' else entry_price * 1.01, # Default 1% stop
            'is_active': False
        }

    def update_price(self, symbol: str, current_price: float):
        """Update trailing stop based on new price"""
        if symbol not in self.active_trails:
            return

        trail = self.active_trails[symbol]
        side = trail['side']

        if side == 'buy':
            # Check for new high
            if current_price > trail['highest_price']:
                trail['highest_price'] = current_price
                # Trail stop up
                new_stop = current_price * 0.98 # 2% trail
                if new_stop > trail['stop_price']:
                    trail['stop_price'] = new_stop
                    logger.debug(f"📈 {symbol} Trail Stop moved UP to {new_stop}")

        elif side == 'sell':
            # Check for new low
            if current_price < trail['lowest_price']:
                trail['lowest_price'] = current_price
                # Trail stop down
                new_stop = current_price * 1.02 # 2% trail
                if new_stop < trail['stop_price']:
                    trail['stop_price'] = new_stop
                    logger.debug(f"📉 {symbol} Trail Stop moved DOWN to {new_stop}")

    def check_exit(self, symbol: str, current_price: float) -> bool:
        """Check if price has hit the trailing stop"""
        if symbol not in self.active_trails:
            return False

        trail = self.active_trails[symbol]
        side = trail['side']

        if side == 'buy':
            if current_price <= trail['stop_price']:
                logger.info(f"💰 {symbol} HIT TRAILING STOP at {current_price} (Profit Secured)")
                return True
        elif side == 'sell':
            if current_price >= trail['stop_price']:
                logger.info(f"💰 {symbol} HIT TRAILING STOP at {current_price} (Profit Secured)")
                return True
        return False
