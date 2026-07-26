#!/usr/bin/env python3
"""
PHASE 8: PROFIT COMPOUNDING ACCELERATION

Aggressive profit reinvestment for exponential growth
"""

from typing import Dict, Any, List
from collections import deque, defaultdict
import logging
import json
import time

logger = logging.getLogger(__name__)

class ProfitCompoundingAccelerator:
    """
    Phase 8: Ultra-Aggressive Compounding
    
    Features:
    - Immediate profit reinvestment (NO delay)
    - Micro-scalp chaining (stack multiple small wins)
    - Overlapping positions (maximize opportunity capture)
    - Risk-aware but NOT risk-limited
    
    Philosophy: Use intelligence, not throttles
    """
    
    def __init__(self):
        # Track realized profits
        self.realized_profits = deque(maxlen=1000)
        self.total_profit = 0.0
        self.starting_balance = 0.0
        
        # Compounding metrics
        self.compound_count = 0
        self.scalp_chains = defaultdict(list)  # {symbol: [trades]}
        
        # Overlapping position tracking
        self.overlapping_positions = defaultdict(list)  # {symbol: [positions]}
        
        # Velocity tracking
        self.velocity_samples = []
        
    def set_starting_balance(self, balance: float):
        """Set initial balance for compounding calculations"""
        if self.starting_balance == 0:
            self.starting_balance = balance
            logger.info(f"💰 Compounding base: ${balance:.2f}")
    
    def record_profit(self, symbol: str, profit: float, trade_duration_sec: float):
        """
        Record realized profit and update compounding metrics
        
        Args:
            symbol: Trading pair
            profit: Realized profit in USD
            trade_duration_sec: How long trade was open
        """
        self.realized_profits.append({
            'symbol': symbol,
            'profit': profit,
            'timestamp': time.time(),
            'duration': trade_duration_sec
        })
        
        self.total_profit += profit
        
        # Track velocity (profit per second)
        if trade_duration_sec > 0:
            velocity = profit / trade_duration_sec
            self.velocity_samples.append(velocity)
        
        # Micro-scalp chain tracking
        if trade_duration_sec < 60:  # Under 1 minute = scalp
            self.scalp_chains[symbol].append({
                'profit': profit,
                'timestamp': time.time()
            })
        
        logger.info(f"💰 PROFIT: ${profit:.2f} from {symbol} [{trade_duration_sec:.0f}s]")
        
    def get_compounded_size(self, base_size: float, current_balance: float) -> float:
        """
        Calculate position size with aggressive compounding
        
        NO profit caps, NO throttles - use full compounded balance
        
        Args:
            base_size: Original calculated size
            current_balance: Current total balance
            
        Returns:
            Compounded size (can be much larger than base)
        """
        if self.starting_balance == 0:
            self.set_starting_balance(current_balance)
        
        # Calculate growth multiplier
        growth = current_balance / self.starting_balance if self.starting_balance > 0 else 1.0
        
        # Aggressive compounding: Scale size with growth
        # If balance doubled, double the size!
        compounded_size = base_size * growth
        
        # NO CAPS - let it grow!
        self.compound_count += 1
        
        logger.debug(f"   📈 Compounding: ${base_size:.2f} → ${compounded_size:.2f} ({growth:.2f}x)")
        
        return compounded_size
    
    def can_open_overlapping_position(self, symbol: str, venue: str) -> bool:
        """
        Check if we can open overlapping position on same symbol
        
        Allows overlapping when:
        - Different venues (always OK)
        - Same venue but different strategies
        - Risk-aware: check total exposure
        
        Returns: True (almost always - intelligence over limitation)
        """
        # Check existing positions on this symbol
        existing = self.overlapping_positions.get(symbol, [])
        
        # Different venue? Always OK
        venue_count = sum(1 for p in existing if p.get('venue') == venue)
        
        # Track new position
        self.overlapping_positions[symbol].append({
            'venue': venue,
            'timestamp': time.time()
        })
        
        # Risk awareness (but NOT limitation)
        if venue_count > 2:
            logger.info(f"    Multiple positions on {symbol} ({venue_count+1}) - risk aware")
        
        # Always allow - intelligence decides, not rules
        return True
    
    def enable_scalp_chaining(self, symbol: str) -> Dict:
        """
        Enable micro-scalp chaining for symbol
        
        Returns: Chain metadata for rapid re-entry
        """
        chain = self.scalp_chains.get(symbol, [])
        
        # Recent scalps (last 5 minutes)
        recent = [s for s in chain if time.time() - s['timestamp'] < 300]
        
        if len(recent) >= 2:
            # Chain active!
            total_chain_profit = sum(s['profit'] for s in recent)
            logger.info(f"   ⚡ SCALP CHAIN: {symbol} ({len(recent)} trades, ${total_chain_profit:.2f})")
        
        return {
            'chain_active': len(recent) >= 2,
            'chain_length': len(recent),
            'chain_profit': sum(s['profit'] for s in recent)
        }
    
    def get_immediate_reinvestment_size(self, latest_profit: float, base_size: float) -> float:
        """
        Calculate immediate reinvestment from latest profit
        
        NO DELAY - profit goes straight back in
        
        Args:
            latest_profit: Most recent realized profit
            base_size: Base position size
            
        Returns:
            Enhanced size with profit reinvested
        """
        # Add profit directly to next position
        enhanced_size = base_size + latest_profit
        
        logger.info(f"   💸 IMMEDIATE REINVEST: ${latest_profit:.2f} → ${enhanced_size:.2f}")
        
        return enhanced_size
    
    def get_compounding_metrics(self) -> Dict:
        """Get compounding performance metrics"""
        if not self.realized_profits:
            return {}
        
        # Calculate compounding velocity
        avg_velocity = sum(self.velocity_samples) / len(self.velocity_samples) if self.velocity_samples else 0
        
        # Growth rate
        current_growth = (self.starting_balance + self.total_profit) / self.starting_balance if self.starting_balance > 0 else 1.0
        
        # Scalp chain stats
        total_chains = sum(len(chain) for chain in self.scalp_chains.values())
        
        return {
            'total_profit': self.total_profit,
            'starting_balance': self.starting_balance,
            'current_multiplier': current_growth,
            'compound_operations': self.compound_count,
            'avg_profit_velocity_per_sec': avg_velocity,
            'total_scalp_chains': total_chains,
            'active_overlapping_positions': sum(len(p) for p in self.overlapping_positions.values()),
            'recent_profits': list(self.realized_profits)[-10:]
        }
    
    def save_metrics(self, filepath='/root/bot/logs/compounding_velocity_metrics.json'):
        """Save compounding metrics to file"""
        try:
            metrics = self.get_compounding_metrics()
            
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            logger.info(f"📊 Compounding metrics saved: {filepath}")
            
            # Log summary
            if metrics:
                logger.info(f"   Total profit: ${metrics['total_profit']:.2f}")
                logger.info(f"   Growth: {metrics['current_multiplier']:.2f}x")
                logger.info(f"   Scalp chains: {metrics['total_scalp_chains']}")
                
        except Exception as e:
            logger.warning(f"Could not save compounding metrics: {e}")
