#!/usr/bin/env python3
"""
DYNAMIC PAIR DISCOVERY
Auto-discovers hot trading pairs, removes dead ones
No hardcoded pairs - constantly refreshing trading universe
"""

import asyncio
import logging
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import ccxt

logger = logging.getLogger(__name__)


class DynamicPairDiscovery:
    """
    Discovers and maintains a dynamic list of active trading pairs
    - Scans all pairs on exchange
    - Filters for volume, volatility, momentum
    - Removes dead/slow pairs
    - Constantly refreshes (every 5 minutes)
    """
    
    def __init__(self, exchange, min_volume_24h: float = 50000):
        self.exchange = exchange
        self.min_volume_24h = min_volume_24h
        
        # Dynamic pair sets
        self.hot_pairs: Set[str] = set()        # High volume + volatility
        self.fast_pairs: Set[str] = set()       # Fast movers (>1% in 1h)
        self.stable_pairs: Set[str] = set()     # Stable volume pairs
        self.dead_pairs: Set[str] = set()       # Removed (low volume)
        
        # Pair metrics
        self.pair_metrics: Dict[str, Dict] = {}
        
        # Last refresh
        self.last_refresh = None
        self.refresh_interval = 300  # 5 minutes
        
        logger.info("🔍 Dynamic Pair Discovery initialized")
        logger.info(f"   Min 24h volume: ${min_volume_24h:,.0f}")
    
    async def discover_pairs(self) -> Dict[str, List[str]]:
        """
        Main discovery method - finds all tradeable pairs
        Returns categorized pairs
        """
        try:
            logger.info("🔍 Discovering trading pairs...")
            
            # Fetch all tickers
            tickers = await asyncio.to_thread(self.exchange.fetch_tickers)
            
            hot = []
            fast = []
            stable = []
            dead = []
            
            for symbol, ticker in tickers.items():
                # Only USDT pairs
                if not symbol.endswith('/USDT'):
                    continue
                
                # Skip perpetuals, futures
                if any(x in symbol for x in ['PERP', 'PERPETUAL', ':', '_']):
                    continue
                
                try:
                    # Get metrics
                    volume_24h = ticker.get('quoteVolume', 0) or 0
                    price = ticker.get('last', 0) or ticker.get('close', 0) or 0
                    change_24h = ticker.get('percentage', 0) or 0
                    
                    if not price or price <= 0:
                        continue
                    
                    # Calculate metrics
                    metrics = {
                        'symbol': symbol,
                        'price': price,
                        'volume_24h': volume_24h,
                        'change_24h': change_24h,
                        'last_updated': datetime.now()
                    }
                    
                    # Categorize
                    if volume_24h < self.min_volume_24h:
                        dead.append(symbol)
                        continue
                    
                    # Hot: High volume + significant change
                    if volume_24h > 500000 and abs(change_24h) > 2:
                        hot.append(symbol)
                        metrics['category'] = 'HOT'
                    
                    # Fast: Big price movement
                    elif abs(change_24h) > 5:
                        fast.append(symbol)
                        metrics['category'] = 'FAST'
                    
                    # Stable: Good volume, moderate movement
                    elif volume_24h > self.min_volume_24h:
                        stable.append(symbol)
                        metrics['category'] = 'STABLE'
                    
                    self.pair_metrics[symbol] = metrics
                    
                except Exception as e:
                    logger.debug(f"Error processing {symbol}: {e}")
                    continue
            
            # Update sets
            self.hot_pairs = set(hot)
            self.fast_pairs = set(fast)
            self.stable_pairs = set(stable)
            self.dead_pairs = set(dead)
            
            self.last_refresh = datetime.now()
            
            logger.info(f"✅ Pair discovery complete:")
            logger.info(f"   🔥 HOT pairs: {len(hot)} (high volume + volatility)")
            logger.info(f"   ⚡ FAST pairs: {len(fast)} (big movers)")
            logger.info(f"   📊 STABLE pairs: {len(stable)} (good volume)")
            logger.info(f"   💀 DEAD pairs: {len(dead)} (removed)")
            
            return {
                'hot': hot,
                'fast': fast,
                'stable': stable,
                'dead': dead
            }
            
        except Exception as e:
            logger.error(f"❌ Pair discovery error: {e}")
            return {'hot': [], 'fast': [], 'stable': [], 'dead': []}
    
    async def get_top_opportunities(self, limit: int = 20) -> List[Dict]:
        """Get top trading opportunities right now"""
        opportunities = []
        
        for symbol, metrics in self.pair_metrics.items():
            if symbol in self.dead_pairs:
                continue
            
            # Score each pair
            score = 0
            
            # Volume score (0-40 points)
            volume = metrics.get('volume_24h', 0)
            if volume > 10_000_000:
                score += 40
            elif volume > 1_000_000:
                score += 30
            elif volume > 500_000:
                score += 20
            elif volume > 100_000:
                score += 10
            
            # Volatility score (0-40 points)
            change = abs(metrics.get('change_24h', 0))
            if change > 10:
                score += 40
            elif change > 5:
                score += 30
            elif change > 2:
                score += 20
            elif change > 1:
                score += 10
            
            # Category bonus (0-20 points)
            category = metrics.get('category', '')
            if category == 'HOT':
                score += 20
            elif category == 'FAST':
                score += 15
            elif category == 'STABLE':
                score += 10
            
            opportunities.append({
                'symbol': symbol,
                'score': score,
                'volume_24h': volume,
                'change_24h': metrics.get('change_24h', 0),
                'category': category,
                'price': metrics.get('price', 0)
            })
        
        # Sort by score
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        return opportunities[:limit]
    
    async def should_trade_pair(self, symbol: str) -> bool:
        """Check if we should trade this pair"""
        # Dead pairs - never trade
        if symbol in self.dead_pairs:
            return False
        
        # Hot/Fast pairs - always trade
        if symbol in self.hot_pairs or symbol in self.fast_pairs:
            return True
        
        # Stable pairs - trade if volume is good
        if symbol in self.stable_pairs:
            metrics = self.pair_metrics.get(symbol, {})
            return metrics.get('volume_24h', 0) > self.min_volume_24h
        
        # Unknown pair - be cautious
        return False
    
    async def refresh_if_needed(self):
        """Refresh pairs if interval has passed"""
        if self.last_refresh is None:
            await self.discover_pairs()
            return
        
        elapsed = (datetime.now() - self.last_refresh).seconds
        if elapsed >= self.refresh_interval:
            logger.info("🔄 Refreshing pair discovery...")
            await self.discover_pairs()
    
    async def run_continuous_discovery(self):
        """Run continuous pair discovery loop"""
        logger.info("🔄 Starting continuous pair discovery...")
        
        while True:
            try:
                await self.discover_pairs()
                await asyncio.sleep(self.refresh_interval)
            except Exception as e:
                logger.error(f"Discovery loop error: {e}")
                await asyncio.sleep(60)
    
    def get_all_active_pairs(self) -> List[str]:
        """Get all currently active trading pairs"""
        return list(self.hot_pairs | self.fast_pairs | self.stable_pairs)
    
    def get_statistics(self) -> Dict:
        """Get discovery statistics"""
        return {
            'total_active': len(self.hot_pairs) + len(self.fast_pairs) + len(self.stable_pairs),
            'hot_pairs': len(self.hot_pairs),
            'fast_pairs': len(self.fast_pairs),
            'stable_pairs': len(self.stable_pairs),
            'dead_pairs': len(self.dead_pairs),
            'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None,
            'next_refresh_in': self.refresh_interval - (datetime.now() - self.last_refresh).seconds if self.last_refresh else 0
        }


# Global instance
_pair_discovery = None

def initialize_pair_discovery(exchange, min_volume: float = 50000):
    """Initialize global pair discovery"""
    global _pair_discovery
    _pair_discovery = DynamicPairDiscovery(exchange, min_volume)
    return _pair_discovery

def get_pair_discovery():
    """Get global pair discovery instance"""
    return _pair_discovery


def get_discovery_engine(exchange, min_volume=50000):
    """Alias for compatibility - returns pair discovery engine"""
    return initialize_pair_discovery(exchange, min_volume)


if __name__ == "__main__":
    # Test
    import os
    logging.basicConfig(level=logging.INFO)
    
    exchange = ccxt.gate({
        'apiKey': os.getenv('GATE_API_KEY'),
        'secret': os.getenv('GATE_API_SECRET'),
    })
    
    discovery = DynamicPairDiscovery(exchange)
    
    async def test():
        pairs = await discovery.discover_pairs()
        print(f"\nDiscovered {len(pairs['hot'])} hot pairs")
        
        opps = await discovery.get_top_opportunities(10)
        print("\nTop 10 opportunities:")
        for opp in opps:
            print(f"  {opp['symbol']:15} Score: {opp['score']:3} Vol: ${opp['volume_24h']:>12,.0f} Change: {opp['change_24h']:>6.2f}%")
    
    asyncio.run(test())
