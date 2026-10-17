#!/usr/bin/env python3
"""
BALANCE TIER COORDINATOR
Intelligently activates/deactivates engines based on wallet balance
Grows from micro scalper → full engine arsenal as balance increases
"""

import asyncio
import logging
from typing import Dict, List, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EngineTier:
    """Engine activation tier"""
    min_balance: float
    max_balance: float
    active_engines: List[str]
    strategy: str


class BalanceTierCoordinator:
    """
    Coordinates which engines are active based on balance
    Starts with minimal engines, adds more as balance grows
    """
    
    def __init__(self, initial_balance: float = 0.0):
        self.current_balance = initial_balance
        self.active_engines: Set[str] = set()
        self.current_tier = None
        
        # Define tiers - which engines to use at each balance level
        self.tiers = {
            'nano': EngineTier(
                min_balance=0,
                max_balance=10,
                active_engines=[
                    'AGGRESSIVE_MICRO_SCALPER',  # PRIMARY - Fast micro gains
                    'DYNAMIC_PAIR_DISCOVERY',     # Find hot pairs
                    'OPPORTUNITY_SCANNER',        # Catch fast movers
                ],
                strategy='MICRO_SCALP_ONLY'
            ),
            'micro': EngineTier(
                min_balance=10,
                max_balance=50,
                active_engines=[
                    'AGGRESSIVE_MICRO_SCALPER',
                    'DYNAMIC_PAIR_DISCOVERY',
                    'OPPORTUNITY_SCANNER',
                    'SMART_SCALPING',             # Add smarter scalping
                    'ARBITRAGE',                  # Risk-free profits
                    'NEWS_TRADING',               # Momentum trades
                ],
                strategy='SCALP_PLUS_ARBITRAGE'
            ),
            'small': EngineTier(
                min_balance=50,
                max_balance=200,
                active_engines=[
                    'AGGRESSIVE_MICRO_SCALPER',
                    'SMART_SCALPING',
                    'DYNAMIC_PAIR_DISCOVERY',
                    'OPPORTUNITY_SCANNER',
                    'ARBITRAGE',
                    'NEWS_TRADING',
                    'SESSION_AWARE',              # Session-based trading
                    'SENTIENT_SCALPING',          # Collective intelligence
                    'MONEY_PRINTER',              # Pairs trading
                ],
                strategy='DIVERSIFIED_SCALPING'
            ),
            'medium': EngineTier(
                min_balance=200,
                max_balance=1000,
                active_engines=[
                    # All scalpers
                    'AGGRESSIVE_MICRO_SCALPER',
                    'SMART_SCALPING',
                    'SENTIENT_SCALPING',
                    'ULTRA_SCALPING',
                    # Discovery & Analysis
                    'DYNAMIC_PAIR_DISCOVERY',
                    'OPPORTUNITY_SCANNER',
                    'BRAIN_ADVISOR',
                    'HIVEMIND',
                    # Profit engines
                    'ARBITRAGE',
                    'MONEY_PRINTER',
                    'NEWS_TRADING',
                    'SESSION_AWARE',
                    'HEDGE_FUND_ARSENAL',
                    'FOREX_TRADING',
                ],
                strategy='FULL_SCALPING_PLUS_STRATEGIES'
            ),
            'large': EngineTier(
                min_balance=1000,
                max_balance=float('inf'),
                active_engines=[
                    # ALL ENGINES - Full power!
                    'AGGRESSIVE_MICRO_SCALPER',
                    'SMART_SCALPING',
                    'SENTIENT_SCALPING',
                    'ULTRA_SCALPING',
                    'DYNAMIC_PAIR_DISCOVERY',
                    'OPPORTUNITY_SCANNER',
                    'BRAIN_ADVISOR',
                    'HIVEMIND',
                    'ARBITRAGE',
                    'MONEY_PRINTER',
                    'NEWS_TRADING',
                    'SESSION_AWARE',
                    'HEDGE_FUND_ARSENAL',
                    'FOREX_TRADING',
                    'DEX_MOON_SPOTTER',
                    'EVOLUTION_ENGINE',
                    'QUANTUM_PREDICTOR',
                    'SWARM_INTELLIGENCE',
                    'ULTRA_RARE_ENGINES',
                    'DIVINE_INTELLIGENCE',
                ],
                strategy='FULL_ARSENAL'
            )
        }
        
        logger.info("🎯 Balance Tier Coordinator initialized")
        logger.info(f"   Starting balance: ${initial_balance:.2f}")
        self._update_tier()
    
    def _update_tier(self):
        """Update current tier based on balance"""
        for tier_name, tier in self.tiers.items():
            if tier.min_balance <= self.current_balance < tier.max_balance:
                if self.current_tier != tier_name:
                    old_tier = self.current_tier
                    self.current_tier = tier_name
                    self.active_engines = set(tier.active_engines)
                    
                    if old_tier:
                        logger.info("")
                        logger.info("🎉 " + "="*60)
                        logger.info(f"   TIER UPGRADE: {old_tier.upper()} → {tier_name.upper()}")
                        logger.info(f"   Balance: ${self.current_balance:.2f}")
                        logger.info(f"   Active Engines: {len(self.active_engines)}")
                        logger.info(f"   Strategy: {tier.strategy}")
                        logger.info("   " + "="*60)
                        logger.info("")
                    else:
                        logger.info(f"✅ Starting tier: {tier_name.upper()}")
                        logger.info(f"   Active engines: {len(self.active_engines)}")
                        logger.info(f"   Strategy: {tier.strategy}")
                
                return tier
        
        return self.tiers['nano']
    
    def update_balance(self, new_balance: float):
        """Update balance and check for tier changes"""
        old_balance = self.current_balance
        self.current_balance = new_balance
        
        # Check for tier change
        old_tier = self.current_tier
        self._update_tier()
        
        # Log significant changes
        if new_balance > old_balance * 1.1:
            logger.info(f"💰 Balance grew 10%+: ${old_balance:.2f} → ${new_balance:.2f}")
        elif new_balance < old_balance * 0.9:
            logger.warning(f"⚠️  Balance dropped 10%+: ${old_balance:.2f} → ${new_balance:.2f}")
    
    def should_engine_run(self, engine_name: str) -> bool:
        """Check if an engine should be active at current balance"""
        return engine_name in self.active_engines
    
    def get_active_engines(self) -> List[str]:
        """Get list of currently active engines"""
        return list(self.active_engines)
    
    def get_tier_info(self) -> Dict:
        """Get current tier information"""
        tier = self.tiers.get(self.current_tier)
        return {
            'tier': self.current_tier,
            'balance': self.current_balance,
            'strategy': tier.strategy if tier else 'UNKNOWN',
            'active_engines': list(self.active_engines),
            'engine_count': len(self.active_engines)
        }
    
    def get_recommended_position_size(self) -> float:
        """Get recommended position size for current tier"""
        # Micro tiers use most of balance per trade
        # Higher tiers use less per trade (more diversification)
        tier = self.tiers.get(self.current_tier)
        
        if self.current_tier == 'nano':
            return self.current_balance * 0.95  # Use 95% - go hard!
        elif self.current_tier == 'micro':
            return self.current_balance * 0.80  # 80%
        elif self.current_tier == 'small':
            return self.current_balance * 0.50  # 50%
        elif self.current_tier == 'medium':
            return self.current_balance * 0.25  # 25%
        else:
            return self.current_balance * 0.10  # 10% - conservative


# Global instance
_tier_coordinator = None

def initialize_tier_coordinator(initial_balance: float = 0.0):
    """Initialize the global tier coordinator"""
    global _tier_coordinator
    _tier_coordinator = BalanceTierCoordinator(initial_balance)
    return _tier_coordinator

def get_tier_coordinator() -> BalanceTierCoordinator:
    """Get the global tier coordinator"""
    return _tier_coordinator


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    coordinator = BalanceTierCoordinator(5.0)
    print(f"\nTier: {coordinator.current_tier}")
    print(f"Active engines: {coordinator.active_engines}")
    
    # Simulate growth
    for balance in [5, 15, 60, 250, 1500]:
        print(f"\n{'='*60}")
        print(f"Balance: ${balance}")
        coordinator.update_balance(balance)
        print(f"Tier: {coordinator.current_tier}")
        print(f"Active engines: {len(coordinator.active_engines)}")
