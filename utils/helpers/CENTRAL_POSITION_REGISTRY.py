#!/usr/bin/env python3
"""
Central Position Registry - Track ALL Positions Across ALL Engines
===================================================================

Problem: Each engine tracks positions separately
- MICRO tracks its own
- Steady Profit doesn't track
- Real Profit Bot tracks separately
- Risk of double-positions!

Solution: Single source of truth for all positions
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class CentralPositionRegistry:
    """
    Tracks ALL open positions across ALL engines
    Prevents:
    - Double-positioning (2 engines buying same coin)
    - Over-exposure (too much in correlated assets)
    - Conflicting trades (one buying while another selling)
    """
    
    def __init__(self):
        self.positions = {}  # symbol -> {engine, details}
        self.position_history = []
        
        logger.info("📊 Central Position Registry initialized")
    
    def add_position(self, engine_name: str, symbol: str, details: Dict):
        """
        Register a new position
        
        Args:
            engine_name: Which engine opened it (e.g., 'MICRO', 'STEADY_PROFIT')
            symbol: Trading pair (e.g., 'BTC/USDT')
            details: {side, entry_price, size, stop_loss, take_profit, etc.}
        """
        key = f"{engine_name}:{symbol}"
        
        # Check if already in position
        if self.is_in_position(symbol):
            existing = self.get_position(symbol)
            logger.warning(f"  {engine_name} trying to open {symbol} but {existing['engine']} already has it!")
            return False
        
        self.positions[key] = {
            'engine': engine_name,
            'symbol': symbol,
            'side': details['side'],
            'entry_price': details['entry_price'],
            'entry_time': datetime.now(),
            'size': details.get('size', 0),
            'stop_loss': details.get('stop_loss'),
            'take_profit': details.get('take_profit'),
            'confidence': details.get('confidence', 0),
            'status': 'open'
        }
        
        logger.info(f"📊 Position registered: {engine_name} - {symbol} {details['side']}")
        return True
    
    def is_in_position(self, symbol: str) -> bool:
        """Check if ANY engine has this position open"""
        for key, pos in self.positions.items():
            if pos['symbol'] == symbol and pos['status'] == 'open':
                return True
        return False
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position details for a symbol"""
        for key, pos in self.positions.items():
            if pos['symbol'] == symbol and pos['status'] == 'open':
                return pos
        return None
    
    def close_position(self, engine_name: str, symbol: str, exit_price: float, reason: str):
        """
        Close a position
        
        Args:
            engine_name: Which engine is closing
            symbol: Trading pair
            exit_price: Exit price
            reason: 'TAKE_PROFIT', 'STOP_LOSS', 'TIME_EXIT', etc.
        """
        key = f"{engine_name}:{symbol}"
        
        if key not in self.positions:
            logger.warning(f"  {engine_name} trying to close {symbol} but position not found!")
            return False
        
        pos = self.positions[key]
        
        # Calculate P&L
        if pos['side'].upper() == 'BUY':
            pnl_pct = (exit_price - pos['entry_price']) / pos['entry_price']
        else:
            pnl_pct = (pos['entry_price'] - exit_price) / pos['entry_price']
        
        pnl_usd = pos['size'] * pnl_pct
        
        # Update position
        pos['status'] = 'closed'
        pos['exit_price'] = exit_price
        pos['exit_time'] = datetime.now()
        pos['pnl_pct'] = pnl_pct
        pos['pnl_usd'] = pnl_usd
        pos['exit_reason'] = reason
        
        # Move to history
        self.position_history.append(pos.copy())
        
        # Remove from active
        del self.positions[key]
        
        emoji = "💰" if pnl_pct > 0 else "🛑"
        logger.info(f"{emoji} Position closed: {engine_name} - {symbol} ({reason})")
        logger.info(f"   P&L: {pnl_pct:+.2%} (${pnl_usd:+.2f})")
        
        return True
    
    def get_total_exposure(self, symbol: str) -> float:
        """Get total exposure to a symbol across ALL engines"""
        total = 0.0
        for pos in self.positions.values():
            if pos['symbol'] == symbol and pos['status'] == 'open':
                total += pos.get('size', 0)
        return total
    
    def get_open_positions_count(self) -> int:
        """Total open positions across all engines"""
        return sum(1 for pos in self.positions.values() if pos['status'] == 'open')
    
    def get_engine_positions(self, engine_name: str) -> List[Dict]:
        """Get all positions for a specific engine"""
        return [pos for key, pos in self.positions.items() 
                if pos['engine'] == engine_name and pos['status'] == 'open']
    
    def get_stats(self) -> Dict:
        """Get registry statistics"""
        total_open = self.get_open_positions_count()
        
        # Group by engine
        by_engine = defaultdict(int)
        for pos in self.positions.values():
            if pos['status'] == 'open':
                by_engine[pos['engine']] += 1
        
        # Calculate win rate from history
        if self.position_history:
            wins = sum(1 for p in self.position_history if p.get('pnl_pct', 0) > 0)
            win_rate = wins / len(self.position_history)
            total_pnl = sum(p.get('pnl_usd', 0) for p in self.position_history)
        else:
            win_rate = 0
            total_pnl = 0
        
        return {
            'total_open_positions': total_open,
            'positions_by_engine': dict(by_engine),
            'total_trades_closed': len(self.position_history),
            'win_rate': win_rate,
            'total_pnl': total_pnl
        }


# Integration into CentralDataHub:
"""
Add to COMPLETE_UNIFIED_ORCHESTRATOR.py CentralDataHub class:

from CENTRAL_POSITION_REGISTRY import CentralPositionRegistry

class CentralDataHub:
    def __init__(self):
        # ... existing code ...
        self.position_registry = CentralPositionRegistry()
        
    # Add helper methods
    def register_position(self, engine, symbol, details):
        return self.position_registry.add_position(engine, symbol, details)
    
    def close_position(self, engine, symbol, exit_price, reason):
        return self.position_registry.close_position(engine, symbol, exit_price, reason)
    
    def check_position_conflict(self, symbol):
        return self.position_registry.is_in_position(symbol)
"""
