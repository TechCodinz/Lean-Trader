#!/usr/bin/env python3
"""
PRE_TRADE_FUNDS_GATE.py
Pre-trade balance validation to prevent "Insufficient balance" errors
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class PreTradeFundsGate:
    """Validate sufficient balance before placing orders"""
    
    def __init__(self, exchange):
        self.exchange = exchange
        self.balance_cache = {}
        self.cache_age = 0
    
    def refresh_balance(self) -> Dict:
        """Refresh balance cache"""
        try:
            self.balance_cache = self.exchange.fetch_balance()
            self.cache_age = 0
            return self.balance_cache
        except Exception as e:
            logger.error(f"Balance refresh failed: {e}")
            return self.balance_cache
    
    def get_available_balance(self, currency: str = 'USDT') -> float:
        """Get available balance for currency"""
        # Refresh if stale (every 10 calls)
        self.cache_age += 1
        if self.cache_age > 10 or  not self.balance_cache:
            self.refresh_balance()
        
        return self.balance_cache.get(currency, {}).get('free', 0)
    
    def can_place_order(self, symbol: str, side: str, amount: float, 
                       price: Optional[float] = None) -> tuple[bool, str]:
        """
        Check if sufficient balance to place order
        
        Returns:
            (can_place, reason)
        """
        # Get quote currency (usually USDT)
        quote_currency = symbol.split('/')[1] if '/' in symbol else 'USDT'
        
        # Get available balance
        available = self.get_available_balance(quote_currency)
        
        # Calculate required balance
        if side.upper() == 'BUY':
            # For market buy, estimate cost
            if price:
                required = amount * price
            else:
                # Fetch current price
                try:
                    ticker = self.exchange.fetch_ticker(symbol)
                    current_price = ticker['last']
                    required = amount * current_price * 1.01  # 1% buffer
                except:
                    # Cannot determine - allow order to try
                    return True, "Price indeterminate - allowing order"
        else:
            # For sell, check base currency
            base_currency = symbol.split('/')[0]
            available = self.get_available_balance(base_currency)
            required = amount
        
        # Check sufficiency
        if available >= required:
            return True, f"Sufficient balance: ${available:.2f} >= ${required:.2f}"
        else:
            reason = f"Insufficient balance: ${available:.2f} < ${required:.2f} required"
            
            # Log the insufficiency event
            logger.warning(f"INSUFFICIENT_BALANCE: {symbol} {side} {amount}")
            logger.warning(f"   Required: ${required:.2f} {quote_currency}")
            logger.warning(f"   Available: ${available:.2f} {quote_currency}")
            logger.warning(f"   Shortfall: ${required - available:.2f}")
            
            return False, reason
    
    def validate_or_skip(self, symbol: str, side: str, amount: float,
                        price: Optional[float] = None) -> bool:
        """
        Validate funds and return True if can proceed, False if should skip
        
        Use this before every order:
            if not funds_gate.validate_or_skip(symbol, side, amount, price):
                logger.info("Skipping order due to insufficient balance")
                return None
        """
        can_place, reason = self.can_place_order(symbol, side, amount, price)
        
        if not can_place:
            logger.info(f"⏭️ SKIPPING ORDER: {reason}")
            # Do NOT reserve capital
            # Do NOT lock resources
            # Just skip gracefully
        
        return can_place

# Global instance
_funds_gate = None

def get_funds_gate(exchange):
    """Get global funds gate instance"""
    global _funds_gate
    if _funds_gate is None:
        _funds_gate = PreTradeFundsGate(exchange)
    return _funds_gate

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    import ccxt
    exchange = ccxt.bybit({'enableRateLimit': True})
    
    gate = PreTradeFundsGate(exchange)
    
    # Simulate check
    can_place, reason = gate.can_place_order('BTC/USDT', 'BUY', 0.001, 50000)
    print(f"Can place order: {can_place}")
    print(f"Reason: {reason}")
