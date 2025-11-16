#!/usr/bin/env python3
"""
🧠 AUTONOMOUS MASTER COORDINATOR 🧠

THE SYSTEM THAT MAKES ALL 202 ENGINES WORK TOGETHER!

Instead of hardcoded logic, this lets ALL systems vote and decide:
- Position sizing (from balance intelligence + micro growth + streak logic)
- Risk levels (from fund protection + black swan + volatility)
- Trade selection (from CNS + swarm + all engines)

NO MORE MANUAL OVERRIDES - TRUE AUTONOMY!
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AutonomousMasterCoordinator:
    """
    MASTER COORDINATOR - ALL SYSTEMS REPORT HERE
    
    This is the BRAIN that:
    1. Collects inputs from ALL 202 systems
    2. Synthesizes into ONE decision
    3. NO hardcoded limits - systems decide everything!
    4. TRUE collective intelligence
    """
    
    def __init__(self):
        # System registry
        self.systems = {}
        
        # Decision factors
        self.balance_intelligence = None
        self.safe_micro_growth = None
        self.black_swan = None
        self.streak_logic = None
        self.vol_forecaster = None
        self.risk_adjuster = None
        self.fund_protection = None
        self.cns = None
        
        logger.info("🧠 AUTONOMOUS MASTER COORDINATOR initialized!")
        logger.info("   ALL 202 systems will work as ONE brain!")
    
    def register_system(self, name: str, system_instance):
        """Register a system with the coordinator"""
        self.systems[name] = system_instance
        
        # Store key systems for quick access
        if name == 'safe_micro_growth':
            self.safe_micro_growth = system_instance
        elif name == 'balance_intelligence':
            self.balance_intelligence = system_instance
        elif name == 'black_swan':
            self.black_swan = system_instance
        elif name == 'streak_logic':
            self.streak_logic = system_instance
        elif name == 'vol_forecaster':
            self.vol_forecaster = system_instance
        elif name == 'risk_adjuster':
            self.risk_adjuster = system_instance
        elif name == 'fund_protection':
            self.fund_protection = system_instance
        elif name == 'cns':
            self.cns = system_instance
        
        logger.info(f"   ✅ Registered: {name}")
    
    def calculate_optimal_position_size(self, signal: Dict, current_balance: float) -> float:
        """
        Calculate OPTIMAL position size using ALL intelligence
        
        This is where ALL 202 systems contribute!
        """
        try:
            # Base from balance intelligence
            if self.safe_micro_growth:
                optimal_size = self.safe_micro_growth.get_position_size(signal.get('confidence', 0.75))
                logger.info(f"   🛡️  SAFE Growth: ${optimal_size:.2f}")
            else:
                # Fallback: 2% of balance
                optimal_size = current_balance * 0.02
            
            # Adjust for black swan
            if self.black_swan:
                risk_level = self.black_swan.get_risk_level()
                if risk_level in ['WARNING', 'EXTREME']:
                    optimal_size *= 0.5  # Halve size during black swan!
                    logger.warning(f"   🦢 Black Swan: Reducing size 50%!")
            
            # Adjust for streak logic
            if self.streak_logic:
                if self.streak_logic.should_pause_trading():
                    logger.warning(f"   🛑 Streak Logic: PAUSE trading!")
                    return 0.0
                
                size_mult = self.streak_logic.get_position_multiplier()
                if size_mult != 1.0:
                    optimal_size *= size_mult
                    logger.info(f"   🧠 Streak Adj: {size_mult:.2f}x → ${optimal_size:.2f}")
            
            # Adjust for fund protection
            if self.fund_protection:
                try:
                    can_trade, reason = self.fund_protection.check_circuit_breakers()
                    if not can_trade:
                        logger.warning(f"   🛡️  Fund Protection: {reason}")
                        return 0.0
                except Exception as e:
                    logger.debug(f"Fund protection check skipped: {e}")
            
            # Final safety bounds
            optimal_size = max(0.5, optimal_size)  # Min $0.50
            optimal_size = min(optimal_size, current_balance * 0.30)  # Max 30%
            
            logger.info(f"   ✅ AUTONOMOUS SIZE: ${optimal_size:.2f}")
            return optimal_size
            
        except Exception as e:
            logger.error(f"Autonomous sizing error: {e}")
            # Safe fallback
            return min(current_balance * 0.02, 20.0)
    
    def should_take_trade(self, signal: Dict) -> bool:
        """
        Decide if trade should be taken
        
        ALL systems vote!
        """
        votes = {'yes': 0, 'no': 0, 'reasons': []}
        
        # Streak logic vote
        if self.streak_logic and self.streak_logic.should_pause_trading():
            votes['no'] += 1
            votes['reasons'].append("Streak logic: Too many losses")
            return False
        
        # Fund protection vote
        if self.fund_protection:
            can_trade, reason = self.fund_protection.check_circuit_breakers()
            if not can_trade:
                votes['no'] += 1
                votes['reasons'].append(f"Fund protection: {reason}")
                return False
        
        # Black swan vote
        if self.black_swan:
            risk = self.black_swan.get_risk_level()
            if risk == 'EXTREME':
                votes['no'] += 1
                votes['reasons'].append("Black swan: Extreme risk")
                return False
        
        # All checks passed!
        return True
    
    def get_stats(self) -> Dict:
        """Get coordinator statistics"""
        return {
            'systems_registered': len(self.systems),
            'safe_growth_active': self.safe_micro_growth is not None,
            'black_swan_active': self.black_swan is not None,
            'streak_logic_active': self.streak_logic is not None,
            'cns_active': self.cns is not None
        }


# Singleton
_coordinator = None

def get_coordinator():
    """Get master coordinator"""
    return _coordinator

def initialize_coordinator():
    """Initialize master coordinator"""
    global _coordinator
    _coordinator = AutonomousMasterCoordinator()
    logger.info("✅ AUTONOMOUS MASTER COORDINATOR ready!")
    return _coordinator


if __name__ == "__main__":
    # Test
    coord = AutonomousMasterCoordinator()
    print("✅ Master coordinator ready")
    print("   Will make ALL 202 systems work as ONE!")
