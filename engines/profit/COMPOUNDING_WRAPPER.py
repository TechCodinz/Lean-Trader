#!/usr/bin/env python3
"""
COMPOUNDING_WRAPPER - Safe profit compounding integration
Scales position sizes as balance grows to accelerate profits
"""

import logging

logger = logging.getLogger(__name__)

class CompoundingAccelerator:
    """
    Simple but effective compounding logic
    - Tracks initial balance
    - Scales position sizes as balance grows
    - Conservative multipliers to avoid over-leveraging
    """
    
    def __init__(self):
        self.initial_balance = None
        self.logged_init = False
    
    def get_compounding_multiplier(self, current_balance, base_size):
        """
        Calculate how much to scale position size based on balance growth
        
        Conservative approach:
        - 2x balance = 1.5x position size (not 2x to preserve capital)
        - 5x balance = 2.0x position size
        - 10x balance = 2.5x position size
        - Caps at 3x multiplier for safety
        """
        try:
            # Set initial balance on first call
            if self.initial_balance is None:
                self.initial_balance = current_balance
                if not self.logged_init:
                    logger.info(f"[COMPOUNDING] Initial balance set: ${current_balance:.2f}")
                    self.logged_init = True
                return 1.0
            
            # Calculate growth factor
            if self.initial_balance <= 0:
                return 1.0
                
            growth_factor = current_balance / self.initial_balance
            
            # Conservative compounding curve
            if growth_factor < 1.5:
                # Not much growth yet, no scaling
                multiplier = 1.0
            elif growth_factor < 2.0:
                # 1.5x-2x growth = 1.2x sizing
                multiplier = 1.0 + ((growth_factor - 1.5) * 0.4)
            elif growth_factor < 3.0:
                # 2x-3x growth = 1.2x-1.6x sizing
                multiplier = 1.2 + ((growth_factor - 2.0) * 0.4)
            elif growth_factor < 5.0:
                # 3x-5x growth = 1.6x-2.0x sizing
                multiplier = 1.6 + ((growth_factor - 3.0) * 0.2)
            else:
                # 5x+ growth = 2.0x-2.5x sizing (capped)
                multiplier = min(2.5, 2.0 + ((growth_factor - 5.0) * 0.1))
            
            # Safety cap
            multiplier = min(3.0, max(1.0, multiplier))
            
            logger.info(f"[COMPOUNDING] Balance: ${current_balance:.2f} (from ${self.initial_balance:.2f}, {growth_factor:.2f}x) Position multiplier: {multiplier:.2f}x")
            
            return multiplier
            
        except Exception as e:
            logger.debug(f"[COMPOUNDING] Error (non-fatal): {e}")
            return 1.0

# Global instance
_compounding = CompoundingAccelerator()

def get_compounding_multiplier_safe(balance, base_size):
    """Safe wrapper for compounding"""
    try:
        return _compounding.get_compounding_multiplier(balance, base_size)
    except Exception as e:
        logger.debug(f"[COMPOUNDING] Error (fallback to 1.0x): {e}")
        return 1.0
