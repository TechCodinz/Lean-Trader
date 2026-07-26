#!/usr/bin/env python3
"""
PHASE 7.6: CROSS-VENUE CAPITAL FLUIDITY

Prevents balance bleed across exchanges
Each venue has isolated capital tracking
"""

from typing import Dict, Any
from collections import defaultdict
import logging
import json

logger = logging.getLogger(__name__)

class CrossVenueCapitalManager:
    """
    Phase 7.6: Venue-Scoped Balance Management
    
    Prevents:
    - Gate.io balance used for Bybit trades
    - Balance confusion across venues
    - Capital double-counting
    
    Allows:
    - Same symbol on multiple venues simultaneously
    - Dynamic venue shifting based on opportunities
    - Per-venue position tracking
    """
    
    def __init__(self):
        # Venue-scoped balances
        self.venue_balances = {}  # {venue: balance}
        
        # Venue-scoped position tracking
        self.venue_positions = defaultdict(dict)  # {venue: {symbol: position}}
        
        # Capital allocation tracking
        self.venue_allocated = defaultdict(float)  # {venue: allocated_capital}
        
        # Integrity tracking
        self.integrity_log = []
        
    async def get_venue_balance(self, venue: str, exchange) -> float:
        """
        Get venue-specific balance
        
        Args:
            venue: 'bybit', 'gateio', 'binance', etc
            exchange: Exchange instance for this venue
            
        Returns:
            Available balance for this venue only
        """
        try:
            # Fetch fresh balance from exchange
            balance_info = await exchange.fetch_balance()
            
            if balance_info:
                usdt_balance = balance_info.get('USDT', {})
                if isinstance(usdt_balance, dict):
                    free_balance = usdt_balance.get('free', 0)
                else:
                    free_balance = float(usdt_balance) if usdt_balance else 0
                
                # Update venue balance cache
                self.venue_balances[venue] = free_balance
                
                logger.debug(f"   💰 {venue.upper()} balance: ${free_balance:.2f}")
                return free_balance
                
        except Exception as e:
            logger.warning(f"Could not fetch {venue} balance: {e}")
            
        # Fallback to cached
        return self.venue_balances.get(venue, 0)
    
    def allocate_capital(self, venue: str, symbol: str, amount: float) -> bool:
        """
        Allocate capital for a trade (venue-scoped)
        
        Returns: True if allocation successful, False if insufficient
        """
        available = self.venue_balances.get(venue, 0)
        allocated = self.venue_allocated.get(venue, 0)
        
        free_capital = available - allocated
        
        if amount > free_capital:
            logger.warning(f"   ❌ Insufficient {venue} capital: need ${amount:.2f}, have ${free_capital:.2f}")
            
            # Log integrity issue
            self.integrity_log.append({
                'type': 'insufficient_capital',
                'venue': venue,
                'symbol': symbol,
                'requested': amount,
                'available': free_capital,
                'allocated': allocated
            })
            
            return False
        
        # Allocate
        self.venue_allocated[venue] += amount
        logger.debug(f"   ✅ Allocated ${amount:.2f} on {venue} for {symbol}")
        
        return True
    
    def release_capital(self, venue: str, symbol: str, amount: float):
        """Release allocated capital back to venue pool"""
        self.venue_allocated[venue] = max(0, self.venue_allocated.get(venue, 0) - amount)
        logger.debug(f"   ↩️  Released ${amount:.2f} on {venue} for {symbol}")
    
    def track_position(self, venue: str, symbol: str, side: str, amount: float):
        """Track position opening (venue + symbol)"""
        if venue not in self.venue_positions:
            self.venue_positions[venue] = {}
        
        # Track position
        self.venue_positions[venue][symbol] = {
            'side': side,
            'amount': amount,
            'venue': venue
        }
    
    def can_trade_on_venue(self, venue: str, symbol: str, amount: float) -> tuple:
        """
        Check if trade can execute on venue
        
        Returns: (can_trade: bool, reason: str)
        """
        # Check balance
        available = self.venue_balances.get(venue, 0)
        allocated = self.venue_allocated.get(venue, 0)
        free = available - allocated
        
        if amount > free:
            return False, f"Insufficient capital on {venue}: ${free:.2f} available"
        
        # Check if already trading this symbol on this venue
        if venue in self.venue_positions:
            if symbol in self.venue_positions[venue]:
                # Allow - can have multiple positions on same symbol
                # Just track it
                pass
        
        return True, "OK"
    
    def get_venue_summary(self) -> Dict:
        """Get summary of all venues"""
        summary = {}
        
        for venue, balance in self.venue_balances.items():
            allocated = self.venue_allocated.get(venue, 0)
            positions = len(self.venue_positions.get(venue, {}))
            
            summary[venue] = {
                'total_balance': balance,
                'allocated': allocated,
                'free': balance - allocated,
                'active_positions': positions,
                'symbols': list(self.venue_positions.get(venue, {}).keys())
            }
        
        return summary
    
    def generate_integrity_report(self):
        """Generate venue balance integrity report"""
        summary = self.get_venue_summary()
        
        report = {
            'timestamp': __import__('time').time(),
            'venues': summary,
            'integrity_issues': self.integrity_log,
            'total_venues': len(self.venue_balances),
            'total_positions': sum(len(positions) for positions in self.venue_positions.values())
        }
        
        return report
    
    def save_integrity_report(self, filepath='/root/bot/logs/venue_balance_integrity_report.json'):
        """Save integrity report to file"""
        try:
            report = self.generate_integrity_report()
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📊 Venue integrity report saved: {filepath}")
            
            # Log summary
            for venue, data in report['venues'].items():
                logger.info(f"   {venue.upper()}: ${data['total_balance']:.2f} ({data['active_positions']} positions)")
                
        except Exception as e:
            logger.warning(f"Could not save integrity report: {e}")
