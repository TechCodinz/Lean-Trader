"""
🔍 DYNAMIC MARKET SCANNER
Automatically discovers trending pairs and expands trading universe in real-time

Features:
- Scans exchanges for high-volume pairs
- Detects trending coins (24h volume spike, price movement)
- Auto-adds new profitable opportunities
- Removes dead/low-volume pairs
- Updates universe every hour
"""

import asyncio
import ccxt.async_support as ccxt
from typing import Dict, List, Set
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


class DynamicMarketScanner:
    """
    Continuously scans exchanges for trending pairs
    Expands trading universe beyond static 5 coins
    """
    
    def __init__(self, exchanges: Dict[str, ccxt.Exchange], data_hub):
        self.exchanges = exchanges
        self.data_hub = data_hub
        
        # Dynamic universe
        self.active_pairs = set()
        self.trending_pairs = deque(maxlen=50)  # Top 50 trending
        self.volume_leaders = deque(maxlen=30)  # Top 30 by volume
        
        # Scanning config - ADAPTIVE (determined by situational awareness)
        # NO HARDCODED VALUES - All determined collectively!
        self.min_24h_volume_usd = None  # Set by situational awareness
        self.min_price_change_pct = None  # Set by situational awareness
        self.rescan_interval = 3600  # 1 hour base (adjusted by system)
        self.include_all_pairs = None  # Decided collectively by engines
        
        # Adaptive mode - gets set by SUPREME SITUATIONAL AWARENESS
        self.adaptive_mode = 'balanced'  # balanced/aggressive/conservative
        
        # Collective decision system
        self.situational_awareness = None  # Will be wired
        self.last_collective_decision = None
        
        # Stats
        self.last_scan = None
        self.scan_count = 0
        
        logger.info("🔍 Dynamic Market Scanner initialized")
        logger.info(f"   Mode: ADAPTIVE (collective decision-making)")
        logger.info(f"   Settings: Determined by situational awareness")
        logger.info(f"   Hybrid: No hardcoded gating!")
    
    async def run_continuous_scanning(self):
        """Main scanning loop - runs forever"""
        logger.info("🔍 Starting continuous market scanning...")
        
        # FIRST SCAN IMMEDIATELY!
        try:
            logger.info("🔍 Initial scan - discovering ALL pairs from all exchanges...")
            await self.scan_all_exchanges()
            logger.info(f"✅ Initial scan complete! Found {len(self.active_pairs)} tradable pairs")
        except Exception as e:
            logger.warning(f"Initial scan error: {e}")
        
        while True:
            try:
                await self.scan_all_exchanges()
                
                self.scan_count += 1
                self.last_scan = datetime.now()
                
                logger.info(f"🔍 Scan #{self.scan_count} complete")
                logger.info(f"   Active pairs: {len(self.active_pairs)}")
                logger.info(f"   Trending: {len(self.trending_pairs)}")
                logger.info(f"   Volume leaders: {len(self.volume_leaders)}")
                
                # Wait before next scan
                await asyncio.sleep(self.rescan_interval)
                
            except Exception as e:
                logger.error(f"Dynamic scanner error: {e}")
                await asyncio.sleep(300)  # Wait 5 min on error
    
    async def scan_all_exchanges(self):
        """Scan all connected exchanges for opportunities"""
        
        if not self.exchanges:
            logger.warning("⚠️  No exchanges connected for dynamic scanning")
            return
        
        # 🧠 STEP 1: Get collective decision on scanning parameters
        await self._get_collective_scanning_decision()
        
        new_opportunities = set()
        all_pairs_found = []
        
        # CRITICAL FIX: The exchanges are already ccxt objects from arbitrage engine
        # Just use them directly!
        actual_exchanges = self.exchanges
        
        logger.info(f"🔍 Scanning {len(actual_exchanges)} exchanges for ALL pairs...")
        
        # Check if they're ccxt exchanges
        first_exchange = next(iter(actual_exchanges.values())) if actual_exchanges else None
        if first_exchange and not hasattr(first_exchange, 'fetch_tickers'):
            logger.warning("⚠️  Exchanges are not ccxt objects, creating fallback...")
            actual_exchanges = await self._create_fallback_exchanges()
        
        for exchange_name, exchange in actual_exchanges.items():
            try:
                logger.info(f"🔍 Scanning {exchange_name}...")
                
                # Get all tickers (check if method exists)
                if not hasattr(exchange, 'fetch_tickers'):
                    logger.warning(f"   {exchange_name} doesn't have fetch_tickers, skipping")
                    continue
                
                # Handle both async and sync exchanges
                if hasattr(exchange, 'fetch_tickers'):
                    # FIXED: Call the function with () 
                    tickers = await asyncio.to_thread(exchange.fetch_tickers)
                    
                    # If tickers is a coroutine (async exchange), await it properly
                    if asyncio.iscoroutine(tickers):
                        tickers = await tickers
                else:
                    logger.warning(f"   {exchange_name} doesn't support fetch_tickers")
                    continue
                
                # Ensure tickers is a dict
                if not isinstance(tickers, dict):
                    logger.warning(f"   {exchange_name} returned invalid tickers (type: {type(tickers)})")
                    continue
                
                # Filter for USDT pairs only
                # FIXED: More flexible filtering for different exchange formats
                usdt_pairs = {}
                for symbol, ticker in tickers.items():
                    # Include if it's a USDT pair
                    if '/USDT' in symbol:
                        # Exclude futures/perps ONLY if they have specific markers
                        # Bybit uses different notation, so be more selective
                        if exchange_name == 'bybit':
                            # Bybit: Include all /USDT pairs (spot and linear)
                            usdt_pairs[symbol] = ticker
                        else:
                            # Other exchanges: Exclude if has : (futures notation)
                            if ':' not in symbol:
                                usdt_pairs[symbol] = ticker
                
                logger.info(f"   Found {len(usdt_pairs)} USDT pairs on {exchange_name}")
                all_pairs_found.extend(list(usdt_pairs.keys()))
                
                # Analyze each pair
                for symbol, ticker in usdt_pairs.items():
                    try:
                        # Get volume and price change
                        volume_24h = ticker.get('quoteVolume', 0)  # Volume in USDT
                        price_change_pct = ticker.get('percentage', 0)
                        
                        # ULTRA-RELAXED: Include ALL pairs OR check volume
                        if self.include_all_pairs or volume_24h >= self.min_24h_volume_usd:
                            # Add to opportunities
                            new_opportunities.add(symbol)
                            
                            # Track as volume leader
                            if len(self.volume_leaders) < 30 or volume_24h > min([
                                t[1] for t in self.volume_leaders
                            ], default=0):
                                self.volume_leaders.append((symbol, volume_24h, exchange_name))
                            
                            # Check if trending (big price move)
                            if abs(price_change_pct) >= self.min_price_change_pct:
                                self.trending_pairs.append({
                                    'symbol': symbol,
                                    'exchange': exchange_name,
                                    'volume_24h': volume_24h,
                                    'price_change_pct': price_change_pct,
                                    'discovered_at': datetime.now()
                                })
                                
                                logger.info(
                                    f"   🔥 TRENDING: {symbol} "
                                    f"{price_change_pct:+.1f}% "
                                    f"(${volume_24h/1e6:.1f}M volume)"
                                )
                    
                    except Exception as e:
                        # Skip individual ticker errors
                        continue
                
            except Exception as e:
                logger.error(f"Error scanning {exchange_name}: {e}")
                continue
        
        # Update active pairs
        old_count = len(self.active_pairs)
        self.active_pairs.update(new_opportunities)
        new_count = len(self.active_pairs)
        
        if new_count > old_count:
            logger.info(f"✅ Added {new_count - old_count} new pairs to universe")
            logger.info(f"   Total active pairs: {new_count}")
    
    def get_active_universe(self) -> List[str]:
        """Get current active trading universe"""
        return sorted(list(self.active_pairs))
    
    def get_trending_opportunities(self, limit: int = 20) -> List[Dict]:
        """Get top trending pairs"""
        # Sort by absolute price change
        sorted_trending = sorted(
            self.trending_pairs,
            key=lambda x: abs(x['price_change_pct']),
            reverse=True
        )
        return list(sorted_trending)[:limit]
    
    def get_volume_leaders(self, limit: int = 20) -> List[tuple]:
        """Get pairs with highest volume"""
        sorted_volume = sorted(
            self.volume_leaders,
            key=lambda x: x[1],  # Sort by volume
            reverse=True
        )
        return list(sorted_volume)[:limit]
    
    async def _get_collective_scanning_decision(self):
        """
        🧠 Get scanning parameters from COLLECTIVE intelligence
        No hardcoded values - all adaptive!
        """
        from COLLECTIVE_SCANNING_DECISION import CollectiveScanningDecision
        
        # Get parameters from collective decision
        params = await CollectiveScanningDecision.get_scanning_parameters(
            self.situational_awareness
        )
        
        # Apply to scanner (adaptive, not hardcoded!)
        self.adaptive_mode = params['mode']
        self.min_24h_volume_usd = params['min_volume_usd']
        self.min_price_change_pct = params['min_price_change_pct']
        self.include_all_pairs = params['include_all_pairs']
        self.last_collective_decision = params
        
        return params
    
    def _extract_ccxt_exchanges(self) -> Dict:
        """Extract actual ccxt exchange objects from engines"""
        ccxt_exchanges = {}
        
        for name, obj in self.exchanges.items():
            try:
                # Check if it's already a ccxt exchange
                if hasattr(obj, 'fetch_tickers') and callable(obj.fetch_tickers):
                    ccxt_exchanges[name] = obj
                # Check if it has an 'exchange' attribute (engine with embedded exchange)
                elif hasattr(obj, 'exchange') and obj.exchange:
                    if hasattr(obj.exchange, 'fetch_tickers'):
                        ccxt_exchanges[name] = obj.exchange
                        logger.info(f"   ✅ Extracted exchange from {name} engine")
            except Exception as e:
                logger.debug(f"   Skipping {name}: {str(e)[:50]}")
                continue
        
        return ccxt_exchanges
    
    async def _create_fallback_exchanges(self) -> Dict:
        """Create fresh exchange connections as fallback"""
        import ccxt.async_support as ccxt
        import os
        
        fallback = {}
        
        # Try Gate.io (user's main exchange)
        if os.getenv('GATE_API_KEY'):
            try:
                fallback['gateio'] = ccxt.gateio({
                    'apiKey': os.getenv('GATE_API_KEY'),
                    'secret': os.getenv('GATE_SECRET'),
                    'enableRateLimit': True
                })
                logger.info("   ✅ Created Gate.io connection")
            except Exception as e:
                logger.warning(f"   ⚠️  Gate.io: {str(e)[:50]}")
        
        # Try Binance (public API, no auth needed for tickers)
        try:
            fallback['binance'] = ccxt.binance({
                'enableRateLimit': True
            })
            logger.info("   ✅ Created Binance connection (public)")
        except Exception as e:
            logger.warning(f"   ⚠️  Binance: {str(e)[:50]}")
        
        # Try other exchanges if API keys exist
        exchange_configs = {
            'mexc': ('MEXC_API_KEY', 'MEXC_SECRET'),
            'okx': ('OKX_API_KEY', 'OKX_SECRET'),
            'kucoin': ('KUCOIN_API_KEY', 'KUCOIN_SECRET'),
        }
        
        for exchange_name, (key_var, secret_var) in exchange_configs.items():
            if os.getenv(key_var):
                try:
                    exchange_class = getattr(ccxt, exchange_name)
                    fallback[exchange_name] = exchange_class({
                        'apiKey': os.getenv(key_var),
                        'secret': os.getenv(secret_var),
                        'enableRateLimit': True
                    })
                    logger.info(f"   ✅ Created {exchange_name.upper()} connection")
                except Exception as e:
                    logger.debug(f"   ⚠️  {exchange_name}: {str(e)[:50]}")
        
        return fallback
    
    def get_stats(self) -> Dict:
        """Get scanner statistics"""
        return {
            'active_pairs': len(self.active_pairs),
            'trending_count': len(self.trending_pairs),
            'volume_leaders': len(self.volume_leaders),
            'scan_count': self.scan_count,
            'last_scan': self.last_scan.isoformat() if self.last_scan else None,
            'exchanges_scanned': len(self.exchanges)
        }
    
    async def publish_trending_signals(self):
        """Publish trending pairs as signals to data hub"""
        
        top_trending = self.get_trending_opportunities(limit=10)
        
        for trend in top_trending:
            signal = {
                'type': 'trending',
                'symbol': trend['symbol'],
                'side': 'BUY' if trend['price_change_pct'] > 0 else 'SELL',
                'confidence': min(abs(trend['price_change_pct']) / 10, 0.95),  # Cap at 95%
                'source': 'DynamicScanner',
                'reasoning': f"Trending {trend['price_change_pct']:+.1f}% with ${trend['volume_24h']/1e6:.1f}M volume",
                'timestamp': datetime.now()
            }
            
            await self.data_hub.publish_signal(signal)
        
        if top_trending:
            logger.info(f"📢 Published {len(top_trending)} trending signals to data hub")
