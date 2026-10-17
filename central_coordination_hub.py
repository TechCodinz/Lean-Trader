#!/usr/bin/env python3
"""
🎯 CENTRAL COORDINATION HUB 🎯

Coordinates ALL systems to work in PERFECT UNISON!

Problem: Systems working independently
- Signal generators: Use hardcoded pairs
- Router: Discovers different pairs
- Execution: Tries to trade unavailable pairs
- Result: 296 failures!

Solution: Central hub that ALL systems query!
- Maintains master pair list
- Updates from router discoveries
- Signal generators query hub
- Execution validates against hub
- PERFECT COORDINATION!
"""

import logging
from typing import Dict, List, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class CentralCoordinationHub:
    """
    CENTRAL COORDINATION SYSTEM
    
    Single source of truth for:
    - Available pairs per exchange
    - Connected exchanges
    - Active strategies per pair
    - System status
    
    ALL SYSTEMS QUERY THIS HUB!
    """
    
    def __init__(self):
        # Master pair registry
        self.available_pairs = {}  # {exchange: set(pairs)}
        
        # Connected exchanges (with API keys)
        self.connected_exchanges = set()
        
        # Active pairs (filtered and ready to trade)
        self.active_trading_pairs = set()
        
        # System status
        self.system_status = {
            'router': False,
            'execution': False,
            'signal_generators': {},
            'last_update': None
        }
        
        logger.info("🎯 CENTRAL COORDINATION HUB initialized!")
    
    def register_exchange(self, exchange_name: str, has_connection: bool = True):
        """Register exchange as available"""
        if has_connection:
            self.connected_exchanges.add(exchange_name)
            logger.info(f"   ✅ Registered: {exchange_name}")
        else:
            logger.info(f"   ⚠️ No connection: {exchange_name}")
    
    def update_available_pairs(self, exchange: str, pairs: List[str]):
        """
        Update available pairs for an exchange
        
        Called by router after discovery
        """
        self.available_pairs[exchange] = set(pairs)
        
        logger.info(f"📊 Updated pairs for {exchange}: {len(pairs)} pairs")
        
        # Update active trading pairs
        self._recalculate_active_pairs()
    
    def _recalculate_active_pairs(self):
        """
        Recalculate which pairs we can actually trade
        
        Only pairs on CONNECTED exchanges!
        """
        old_count = len(self.active_trading_pairs)
        self.active_trading_pairs.clear()
        
        # Only include pairs from connected exchanges
        for exchange in self.connected_exchanges:
            if exchange in self.available_pairs:
                self.active_trading_pairs.update(self.available_pairs[exchange])
        
        logger.info(f"🔄 Active trading pairs updated:")
        logger.info(f"   Before: {old_count}")
        logger.info(f"   After: {len(self.active_trading_pairs)}")
        logger.info(f"   Connected exchanges: {len(self.connected_exchanges)}")
        
        # Log sample
        sample = list(self.active_trading_pairs)[:10]
        logger.info(f"   Sample: {', '.join(sample)}")
    
    def get_tradeable_pairs(self) -> List[str]:
        """
        Get list of pairs that can actually be traded
        
        CALL THIS from signal generators!
        """
        pairs = list(self.active_trading_pairs)
        
        logger.debug(f"📋 Returning {len(pairs)} tradeable pairs")
        
        return pairs
    
    def can_trade_pair(self, symbol: str) -> bool:
        """
        Check if a specific pair can be traded
        
        CALL THIS before creating signals!
        """
        can_trade = symbol in self.active_trading_pairs
        
        if not can_trade:
            logger.debug(f"   ⚠️ {symbol} not in active pairs")
        
        return can_trade
    
    def get_exchange_for_pair(self, symbol: str) -> str:
        """
        Get which exchange has this pair
        
        CALL THIS from execution!
        """
        for exchange, pairs in self.available_pairs.items():
            if symbol in pairs and exchange in self.connected_exchanges:
                return exchange
        
        return None
    
    def get_coordination_status(self) -> Dict:
        """Get coordination status"""
        return {
            'connected_exchanges': list(self.connected_exchanges),
            'total_available_pairs': sum(len(pairs) for pairs in self.available_pairs.values()),
            'active_trading_pairs': len(self.active_trading_pairs),
            'coordination_score': len(self.active_trading_pairs) / max(sum(len(p) for p in self.available_pairs.values()), 1),
            'last_update': self.system_status['last_update']
        }


# Singleton
_coordination_hub = None

def get_coordination_hub():
    """Get central coordination hub"""
    global _coordination_hub
    if _coordination_hub is None:
        _coordination_hub = CentralCoordinationHub()
    return _coordination_hub

def initialize_coordination_hub():
    """Initialize central coordination hub"""
    global _coordination_hub
    _coordination_hub = CentralCoordinationHub()
    return _coordination_hub
