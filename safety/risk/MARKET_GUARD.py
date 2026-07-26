"""
MARKET_GUARD.py - Execution Invariant: Symbol Must Exist
This is NOT gating - it prevents ccxt BadSymbol errors
"""

import ccxt
import logging
from typing import Dict, Optional
import time

logger = logging.getLogger(__name__)

class MarketGuard:
    """Ensures symbols exist before attempting orders"""
    
    def __init__(self):
        self.market_cache: Dict[str, Dict] = {}  # exchange_id -> {symbol: True}
        self.cache_ttl = 600  # 10 minutes
        self.last_load: Dict[str, float] = {}
        
    def ensure_markets_loaded(self, exchange) -> None:
        """Load markets once with TTL caching"""
        exchange_id = exchange.id
        now = time.time()
        
        # Check if cache is still valid
        if exchange_id in self.last_load:
            if now - self.last_load[exchange_id] < self.cache_ttl:
                return  # Cache still valid
        
        try:
            logger.info(f"🔄 Loading markets for {exchange_id}...")
            markets = exchange.load_markets()
            self.market_cache[exchange_id] = {symbol: True for symbol in markets.keys()}
            self.last_load[exchange_id] = now
            logger.info(f"✅ Loaded {len(markets)} markets for {exchange_id}")
        except Exception as e:
            logger.error(f"❌ Failed to load markets for {exchange_id}: {e}")
            # Keep old cache if load fails
    
    def market_exists(self, exchange, symbol: str) -> bool:
        """Check if symbol exists on exchange"""
        self.ensure_markets_loaded(exchange)
        exchange_id = exchange.id
        
        if exchange_id not in self.market_cache:
            return False
        
        return symbol in self.market_cache[exchange_id]
    
    def get_min_cost(self, exchange, symbol: str) -> Optional[float]:
        """Get minimum cost for symbol"""
        try:
            self.ensure_markets_loaded(exchange)
            market = exchange.market(symbol)
            return market.get('limits', {}).get('cost', {}).get('min')
        except Exception:
            return None

# Global instance
market_guard = MarketGuard()

