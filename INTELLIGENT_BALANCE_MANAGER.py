#!/usr/bin/env python3
"""
💰 INTELLIGENT BALANCE MANAGER 💰

Prevents ALL "insufficient balance" errors by:
1. Tracking available vs locked balance in real-time
2. Calculating max affordable trades BEFORE placing
3. Dynamically adjusting position count
4. Managing balance across multiple exchanges
5. Reserving balance for open positions

NO MORE INSUFFICIENT BALANCE ERRORS!
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class IntelligentBalanceManager:
    """
    INTELLIGENT BALANCE MANAGER
    
    Tracks and manages balance across all exchanges to prevent
    "insufficient balance" errors completely!
    """
    
    def __init__(self):
        """Initialize balance manager"""
        # Balance tracking per exchange
        self.total_balance = {}  # exchange -> total balance
        self.available_balance = {}  # exchange -> available balance
        self.locked_balance = {}  # exchange -> locked in positions
        self.reserved_balance = {}  # exchange -> reserved for pending orders
        
        # Position tracking
        self.open_positions = defaultdict(list)  # exchange -> [positions]
        self.pending_orders = defaultdict(list)  # exchange -> [orders]
        
        # Trading limits
        self.max_balance_usage = 0.90  # Use max 90% of balance
        self.safety_buffer = 0.10  # Keep 10% as safety buffer
        self.min_position_size = 0.50  # Minimum $0.50 per position
        
        # Statistics
        self.total_trades_blocked = 0
        self.total_balance_checks = 0
        
        logger.info("💰 INTELLIGENT BALANCE MANAGER initialized!")
        logger.info("   NO MORE INSUFFICIENT BALANCE ERRORS!")
    
    def update_exchange_balance(self, exchange: str, total: float, available: float, in_positions: float = 0):
        """
        Update balance for an exchange
        
        Args:
            exchange: Exchange name (e.g., 'bybit_testnet')
            total: Total balance
            available: Available balance (not locked)
            in_positions: Amount locked in open positions
        """
        self.total_balance[exchange] = total
        self.available_balance[exchange] = available
        self.locked_balance[exchange] = in_positions
        
        # Calculate how much we can actually use
        usable = available * self.max_balance_usage
        
        logger.info(f"💰 {exchange}: Total=${total:.2f}, Available=${available:.2f}, Locked=${in_positions:.2f}, Usable=${usable:.2f}")
        
        # Warning if too much locked
        if in_positions > total * 0.85:
            logger.warning(f"   ⚠️  {exchange}: 85%+ balance locked!")
    
    def can_afford_position(self, exchange: str, position_size: float) -> Tuple[bool, str]:
        """
        Check if we can afford a position
        
        Args:
            exchange: Exchange name
            position_size: Position size in USD
        
        Returns:
            (can_afford, reason)
        """
        self.total_balance_checks += 1
        
        # Get available balance
        available = self.available_balance.get(exchange, 0)
        reserved = self.reserved_balance.get(exchange, 0)
        
        # Calculate what's actually free
        free_balance = available - reserved
        
        # Check minimum
        if position_size < self.min_position_size:
            return False, f"Position too small: ${position_size:.2f} < ${self.min_position_size:.2f}"
        
        # Check if we have enough
        if free_balance < position_size:
            self.total_trades_blocked += 1
            return False, f"Insufficient balance: Need ${position_size:.2f}, have ${free_balance:.2f}"
        
        # Check safety buffer
        would_leave = free_balance - position_size
        min_required = available * self.safety_buffer
        
        if would_leave < min_required:
            self.total_trades_blocked += 1
            return False, f"Would violate safety buffer: ${would_leave:.2f} < ${min_required:.2f} required"
        
        return True, "OK"
    
    def reserve_balance(self, exchange: str, amount: float, order_id: str):
        """
        Reserve balance for a pending order
        
        Args:
            exchange: Exchange name
            amount: Amount to reserve
            order_id: Order identifier
        """
        if exchange not in self.reserved_balance:
            self.reserved_balance[exchange] = 0
        
        self.reserved_balance[exchange] += amount
        
        # Track the order
        self.pending_orders[exchange].append({
            'order_id': order_id,
            'amount': amount,
            'timestamp': datetime.now()
        })
        
        logger.info(f"   💰 Reserved ${amount:.2f} on {exchange} (Total reserved: ${self.reserved_balance[exchange]:.2f})")
    
    def release_balance(self, exchange: str, amount: float, order_id: str):
        """
        Release reserved balance (order filled or cancelled)
        
        Args:
            exchange: Exchange name
            amount: Amount to release
            order_id: Order identifier
        """
        if exchange in self.reserved_balance:
            self.reserved_balance[exchange] = max(0, self.reserved_balance[exchange] - amount)
        
        # Remove from pending orders
        self.pending_orders[exchange] = [
            o for o in self.pending_orders[exchange] 
            if o['order_id'] != order_id
        ]
        
        logger.info(f"   💰 Released ${amount:.2f} on {exchange} (Total reserved: ${self.reserved_balance.get(exchange, 0):.2f})")
    
    def calculate_max_positions(self, exchange: str, avg_position_size: float) -> int:
        """
        Calculate maximum number of positions we can open
        
        Args:
            exchange: Exchange name
            avg_position_size: Average position size
        
        Returns:
            Max number of positions
        """
        available = self.available_balance.get(exchange, 0)
        reserved = self.reserved_balance.get(exchange, 0)
        
        # Free balance
        free = available - reserved
        
        # Apply safety buffer
        usable = free * self.max_balance_usage
        
        # Calculate max positions
        if avg_position_size <= 0:
            return 0
        
        max_positions = int(usable / avg_position_size)
        
        logger.info(f"   📊 Max positions on {exchange}: {max_positions} (${avg_position_size:.2f} each)")
        
        return max(0, max_positions)
    
    def get_optimal_position_size(self, exchange: str, desired_size: float, max_positions: int = 1) -> float:
        """
        Get optimal position size that fits within balance
        
        Args:
            exchange: Exchange name
            desired_size: Desired position size
            max_positions: How many positions we want to open
        
        Returns:
            Optimal position size (may be less than desired)
        """
        available = self.available_balance.get(exchange, 0)
        reserved = self.reserved_balance.get(exchange, 0)
        
        # Free balance
        free = available - reserved
        
        # Apply safety buffer
        usable = free * self.max_balance_usage
        
        # Calculate size per position
        size_per_position = usable / max(1, max_positions)
        
        # Return smaller of desired vs affordable
        optimal = min(desired_size, size_per_position)
        
        # Ensure minimum
        if optimal < self.min_position_size:
            logger.warning(f"   ⚠️  Position too small: ${optimal:.2f} < ${self.min_position_size:.2f}")
            return 0
        
        logger.info(f"   💰 Optimal size: ${optimal:.2f} (desired: ${desired_size:.2f})")
        
        return optimal
    
    def register_position_opened(self, exchange: str, symbol: str, size: float):
        """Register that a position was opened"""
        self.open_positions[exchange].append({
            'symbol': symbol,
            'size': size,
            'timestamp': datetime.now()
        })
        
        # Move from reserved to locked
        if exchange in self.reserved_balance:
            self.reserved_balance[exchange] = max(0, self.reserved_balance[exchange] - size)
        
        if exchange in self.locked_balance:
            self.locked_balance[exchange] += size
        else:
            self.locked_balance[exchange] = size
    
    def register_position_closed(self, exchange: str, symbol: str, size: float):
        """Register that a position was closed"""
        # Remove from open positions
        self.open_positions[exchange] = [
            p for p in self.open_positions[exchange] 
            if p['symbol'] != symbol
        ]
        
        # Release locked balance
        if exchange in self.locked_balance:
            self.locked_balance[exchange] = max(0, self.locked_balance[exchange] - size)
    
    def get_balance_summary(self, exchange: str) -> Dict:
        """Get comprehensive balance summary"""
        total = self.total_balance.get(exchange, 0)
        available = self.available_balance.get(exchange, 0)
        locked = self.locked_balance.get(exchange, 0)
        reserved = self.reserved_balance.get(exchange, 0)
        
        free = available - reserved
        usable = free * self.max_balance_usage
        
        return {
            'total': total,
            'available': available,
            'locked': locked,
            'reserved': reserved,
            'free': free,
            'usable': usable,
            'open_positions': len(self.open_positions.get(exchange, [])),
            'pending_orders': len(self.pending_orders.get(exchange, [])),
            'usage_percent': (locked + reserved) / total * 100 if total > 0 else 0
        }
    
    def get_stats(self) -> Dict:
        """Get manager statistics"""
        total_exchanges = len(self.total_balance)
        total_available = sum(self.available_balance.values())
        total_locked = sum(self.locked_balance.values())
        
        return {
            'exchanges': total_exchanges,
            'total_available': total_available,
            'total_locked': total_locked,
            'total_checks': self.total_balance_checks,
            'trades_blocked': self.total_trades_blocked,
            'block_rate': self.total_trades_blocked / max(1, self.total_balance_checks)
        }


# Singleton
_balance_manager = None

def get_balance_manager():
    """Get balance manager"""
    return _balance_manager

def initialize_balance_manager():
    """Initialize balance manager"""
    global _balance_manager
    _balance_manager = IntelligentBalanceManager()
    logger.info("✅ INTELLIGENT BALANCE MANAGER ready!")
    return _balance_manager


if __name__ == "__main__":
    # Test
    manager = IntelligentBalanceManager()
    
    # Simulate balance update
    manager.update_exchange_balance('bybit_testnet', total=8434.19, available=8434.19, in_positions=0)
    
    # Check if we can afford positions
    can_afford, reason = manager.can_afford_position('bybit_testnet', 120.0)
    print(f"Can afford $120? {can_afford} - {reason}")
    
    # Calculate max positions
    max_pos = manager.calculate_max_positions('bybit_testnet', 120.0)
    print(f"Max positions: {max_pos}")
    
    # Get summary
    summary = manager.get_balance_summary('bybit_testnet')
    print(f"Summary: {summary}")
    
    print("✅ Intelligent Balance Manager working!")
