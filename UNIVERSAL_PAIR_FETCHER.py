#!/usr/bin/env python3
"""
UNIVERSAL PAIR FETCHER
Single source of truth for ALL trading pairs across all engines
Completely replaces hardcoded pair lists
"""

import asyncio
import logging
from typing import List, Dict, Set, Optional
from datetime import datetime, timedelta
import ccxt

logger = logging.getLogger(__name__)


class UniversalPairFetcher:
    """
    Fetches ALL available trading pairs from exchange
    Used by ALL engines - no more hardcoded pairs!
    """
    
    def __init__(self, exchange):
        self.exchange = exchange
        self.all_pairs: List[str] = []
        self.pair_metrics: Dict[str, Dict] = {}
        self.last_fetch = None
        self.fetch_interval = 300  # 5 minutes
        
        # Categorized pairs
        self.top_volume_pairs: List[str] = []
        self.high_volatility_pairs: List[str] = []
        self.major_pairs: List[str] = []
        
        logger.info("🌍 Universal Pair Fetcher initialized")
    
    async def fetch_all_pairs(self) -> List[str]:
        """
        Fetch ALL tradeable USDT pairs from exchange
        Returns COMPLETE list of active pairs
        """
        try:
            logger.info("🔍 Fetching ALL trading pairs from exchange...")
            
            # Fetch all markets
            markets = await asyncio.to_thread(self.exchange.load_markets)
            
            # Fetch all tickers
            tickers = await asyncio.to_thread(self.exchange.fetch_tickers)
            
            all_usdt_pairs = []
            
            for symbol, market in markets.items():
                # Only USDT pairs
                if not symbol.endswith('/USDT'):
                    continue
                
                # Skip futures, perpetuals, options
                if market.get('type') not in ['spot', None]:
                    continue
                
                if any(x in symbol for x in ['PERP', 'PERPETUAL', ':', '-']):
                    continue
                
                # Check if active
                if not market.get('active', True):
                    continue
                
                # Get ticker data
                ticker = tickers.get(symbol, {})
                volume_24h = ticker.get('quoteVolume', 0) or 0
                price = ticker.get('last', 0) or ticker.get('close', 0) or 0
                change_24h = ticker.get('percentage', 0) or 0
                
                if price <= 0:
                    continue
                
                # Store metrics
                self.pair_metrics[symbol] = {
                    'volume_24h': volume_24h,
                    'price': price,
                    'change_24h': change_24h,
                    'last_updated': datetime.now()
                }
                
                all_usdt_pairs.append(symbol)
            
            self.all_pairs = all_usdt_pairs
            self.last_fetch = datetime.now()
            
            # Categorize pairs
            self._categorize_pairs()
            
            logger.info(f"✅ Fetched {len(all_usdt_pairs)} total USDT pairs")
            logger.info(f"   📊 Top volume: {len(self.top_volume_pairs)}")
            logger.info(f"   📈 High volatility: {len(self.high_volatility_pairs)}")
            logger.info(f"   ⭐ Major pairs: {len(self.major_pairs)}")
            
            return all_usdt_pairs
            
        except Exception as e:
            logger.error(f"❌ Error fetching pairs: {e}")
            return []
    
    def _categorize_pairs(self):
        """Categorize pairs by volume, volatility, etc."""
        # Sort by volume
        pairs_by_volume = sorted(
            self.pair_metrics.items(),
            key=lambda x: x[1]['volume_24h'],
            reverse=True
        )
        
        # Top 50 by volume
        self.top_volume_pairs = [p[0] for p in pairs_by_volume[:50]]
        
        # High volatility (>5% change)
        self.high_volatility_pairs = [
            symbol for symbol, metrics in self.pair_metrics.items()
            if abs(metrics['change_24h']) > 5
        ]
        
        # Major pairs (always include these)
        majors = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT']
        self.major_pairs = [p for p in majors if p in self.all_pairs]
    
    async def get_pairs_for_strategy(self, strategy: str, limit: int = None) -> List[str]:
        """
        Get pairs optimized for specific strategy
        
        Args:
            strategy: 'all', 'high_volume', 'volatile', 'major', 'scalping', 'arbitrage'
            limit: Max number of pairs to return
        
        Returns:
            List of trading pairs
        """
        await self.refresh_if_needed()
        
        if strategy == 'all':
            pairs = self.all_pairs
        elif strategy == 'high_volume':
            pairs = self.top_volume_pairs
        elif strategy == 'volatile':
            pairs = self.high_volatility_pairs
        elif strategy == 'major':
            pairs = self.major_pairs
        elif strategy == 'scalping':
            # High volume + reasonable volatility
            pairs = [
                p for p in self.top_volume_pairs
                if 1 < abs(self.pair_metrics.get(p, {}).get('change_24h', 0)) < 10
            ]
        elif strategy == 'arbitrage':
            # Top volume pairs (for liquidity)
            pairs = self.top_volume_pairs[:30]
        else:
            pairs = self.all_pairs
        
        if limit:
            pairs = pairs[:limit]
        
        logger.debug(f"📊 {strategy} strategy: {len(pairs)} pairs")
        return pairs
    
    async def refresh_if_needed(self):
        """Refresh pairs if interval has passed"""
        if self.last_fetch is None:
            await self.fetch_all_pairs()
            return
        
        elapsed = (datetime.now() - self.last_fetch).seconds
        if elapsed >= self.fetch_interval:
            logger.info("🔄 Refreshing pair list...")
            await self.fetch_all_pairs()
    
    def get_pair_count(self) -> int:
        """Get total number of available pairs"""
        return len(self.all_pairs)
    
    def is_pair_active(self, symbol: str) -> bool:
        """Check if a pair is active"""
        return symbol in self.all_pairs


# Global instance
_universal_fetcher = None

def initialize_universal_fetcher(exchange):
    """Initialize global universal pair fetcher"""
    global _universal_fetcher
    _universal_fetcher = UniversalPairFetcher(exchange)
    return _universal_fetcher

def get_universal_fetcher():
    """Get global universal pair fetcher"""
    return _universal_fetcher


async def get_pairs(strategy: str = 'all', limit: int = None) -> List[str]:
    """
    Convenience function to get pairs
    Used by all engines instead of hardcoded lists
    """
    fetcher = get_universal_fetcher()
    if not fetcher:
        logger.error("Universal fetcher not initialized!")
        return []
    
    return await fetcher.get_pairs_for_strategy(strategy, limit)


if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    
    exchange = ccxt.gate({
        'apiKey': os.getenv('GATE_API_KEY'),
        'secret': os.getenv('GATE_API_SECRET'),
    })
    
    fetcher = UniversalPairFetcher(exchange)
    
    async def test():
        pairs = await fetcher.fetch_all_pairs()
        print(f"\n✅ Total pairs: {len(pairs)}")
        
        for strategy in ['high_volume', 'volatile', 'scalping', 'arbitrage']:
            strat_pairs = await fetcher.get_pairs_for_strategy(strategy, limit=10)
            print(f"\n{strategy}: {len(strat_pairs)} pairs")
            for p in strat_pairs[:5]:
                metrics = fetcher.pair_metrics.get(p, {})
                print(f"  {p:15} Vol: ${metrics.get('volume_24h', 0):>12,.0f}  Change: {metrics.get('change_24h', 0):>6.2f}%")
    
    asyncio.run(test())
