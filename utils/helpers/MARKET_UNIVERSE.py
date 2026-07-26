
import time
from typing import Dict, Set
import logging

logger = logging.getLogger(__name__)

class MarketUniverseCache:
    def __init__(self, ttl_seconds=600):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict] = {}
        
    def get_markets(self, exchange, venue_id: str) -> Set[str]:
        key = f"{exchange.id}_{venue_id}"
        cached = self._cache.get(key)
        
        if cached and (time.time() - cached['timestamp']) < self.ttl_seconds:
            return cached['symbols']
        
        try:
            if not hasattr(exchange, 'markets') or not exchange.markets:
                exchange.load_markets()
            symbols = set(exchange.markets.keys())
            self._cache[key] = {'symbols': symbols, 'timestamp': time.time()}
            logger.info(f"[OK] Loaded {len(symbols)} symbols for {key}")
            return symbols
        except Exception as e:
            logger.error(f"[X] Failed to load markets for {key}: {e}")
            return set()
    
    def is_tradable(self, exchange, venue_id: str, symbol: str) -> bool:
        markets = self.get_markets(exchange, venue_id)
        return symbol in markets

_market_universe = MarketUniverseCache()

def get_market_universe() -> MarketUniverseCache:
    return _market_universe

