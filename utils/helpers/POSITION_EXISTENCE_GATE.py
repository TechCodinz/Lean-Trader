#!/usr/bin/env python3
"""
POSITION_EXISTENCE_GATE.py
Prevent TP/exit engines from operating without confirmed positions
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PositionExistenceGate:
    """Gate that prevents TP logic from running on non-existent positions"""
    
    def __init__(self, exchange):
        self.exchange = exchange
        self.confirmed_positions = {}  # trade_id -> position_info
    
    def confirm_position(self, trade_id: str, order_id: str, symbol: str, 
                         position_id: Optional[str] = None):
        """Confirm a position exists"""
        self.confirmed_positions[trade_id] = {
            'order_id': order_id,
            'symbol': symbol,
            'position_id': position_id,
            'confirmed': True
        }
        
        logger.info(f"[OK] POSITION CONFIRMED: {trade_id} ({symbol})")
    
    def verify_position_exists(self, trade_id: str) -> bool:
        """Verify position exists before allowing TP logic"""
        if trade_id not in self.confirmed_positions:
            logger.warning(f" TP_SKIPPED_NO_POSITION: {trade_id}")
            logger.warning(f"   Position not confirmed - cannot set TP")
            return False
        
        return True
    
    def can_set_tp(self, trade_id: str) -> tuple[bool, str]:
        """
        Check if TP can be set for this trade
        
        Returns:
            (can_set, reason)
        """
        if trade_id not in self.confirmed_positions:
            return False, "TP_SKIPPED_NO_POSITION"
        
        pos_info = self.confirmed_positions[trade_id]
        
        if not pos_info.get('confirmed'):
            return False, "TP_SKIPPED_UNCONFIRMED_POSITION"
        
        return True, "position_confirmed"
    
    def remove_position(self, trade_id: str):
        """Remove position after closing"""
        if trade_id in self.confirmed_positions:
            del self.confirmed_positions[trade_id]
            logger.info(f"Position removed from tracking: {trade_id}")

# Global instance
_position_gate = None

def get_position_gate(exchange):
    """Get global position gate"""
    global _position_gate
    if _position_gate is None:
        _position_gate = PositionExistenceGate(exchange)
    return _position_gate

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    import ccxt
    exchange = ccxt.bybit()
    
    gate = PositionExistenceGate(exchange)
    
    # Try to set TP without position
    can_set, reason = gate.can_set_tp('trade_001')
    print(f"Can set TP: {can_set}, Reason: {reason}")
    
    # Confirm position
    gate.confirm_position('trade_001', 'order_123', 'BTC/USDT')
    
    # Try again
    can_set, reason = gate.can_set_tp('trade_001')
    print(f"Can set TP: {can_set}, Reason: {reason}")
