#!/usr/bin/env python3
"""
🧠 INTELLIGENT EXCHANGE ROUTER 🧠

SMART routing system that:
- Discovers available pairs on ALL exchanges (including forex on Bybit TradFi!)
- Routes signals to the correct exchange/market automatically
- Adapts trading patterns based on market type
- Monitors for new listings
- Uses AI to understand exchange capabilities

NO MORE BLOCKING PAIRS - ROUTES THEM INTELLIGENTLY!
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from collections import defaultdict
import os

logger = logging.getLogger(__name__)


class IntelligentExchangeRouter:
    """
    INTELLIGENT EXCHANGE ROUTING
    
    Features:
    - Discovers ALL pairs on ALL exchanges dynamically
    - Routes forex pairs to Bybit TradFi
    - Routes crypto to spot/futures/perpetual
    - Detects new listings
    - Adapts patterns per market type
    - Uses AI for discovery when needed
    
    THE BOT FINDS THE RIGHT EXCHANGE FOR EVERY PAIR!
    """
    
    def __init__(self, exchanges: Dict[str, Any], ai_consultation=None, mode='live'):
        """
        Initialize intelligent router
        
        Args:
            exchanges: Dict of exchange instances {'bybit': exchange_obj, ...}
            ai_consultation: AI system for querying exchange capabilities
            mode: Trading mode ('testnet' or 'live')
        """
        self.exchanges = exchanges
        self.ai_consultation = ai_consultation
        self.mode = mode  # Track if we're in testnet or live mode
        
        logger.info(f"🧠 Router initialized in {mode.upper()} mode")
        
        # Discovered pairs per exchange per market type
        self.exchange_pairs = defaultdict(lambda: defaultdict(set))
        # Format: {exchange: {market_type: set(pairs)}}
        # Example: {'bybit': {'spot': {'BTC/USDT', ...}, 'tradfi': {'GBPAUD', ...}}}
        
        # Market type detection patterns
        self.market_patterns = {
            'forex': ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD'],
            'commodities': ['OIL', 'GOLD', 'SILVER', 'USOIL', 'UKOIL', 'XAUUSD', 'XAGUSD'],
            'crypto': ['BTC', 'ETH', 'USDT', 'USDC'],
            'indices': ['SPX', 'NDX', 'US30', 'US500', 'DE40']
        }
        
        # Last discovery time per exchange
        self.last_discovery = {}
        self.discovery_interval = 3600  # Rediscover every hour
        
        # New listings detected
        self.new_listings = []
        
        # Pattern adaptations per market type
        self.market_patterns_config = {
            'forex': {
                'lot_size_multiplier': 1.0,
                'leverage_max': 100,
                'stop_loss_pct': 0.005,  # 0.5% (forex moves slower)
                'take_profit_pct': 0.015,  # 1.5%
                'session_awareness': True  # Critical for forex!
            },
            'crypto': {
                'lot_size_multiplier': 1.0,
                'leverage_max': 10,
                'stop_loss_pct': 0.02,  # 2%
                'take_profit_pct': 0.04,  # 4%
                'session_awareness': False
            },
            'commodities': {
                'lot_size_multiplier': 0.8,
                'leverage_max': 50,
                'stop_loss_pct': 0.01,  # 1%
                'take_profit_pct': 0.03,  # 3%
                'session_awareness': True
            },
            'indices': {
                'lot_size_multiplier': 1.2,
                'leverage_max': 20,
                'stop_loss_pct': 0.015,  # 1.5%
                'take_profit_pct': 0.035,  # 3.5%
                'session_awareness': True
            }
        }
        
        logger.info("🧠 INTELLIGENT EXCHANGE ROUTER initialized!")
        logger.info(f"   Monitoring {len(exchanges)} exchanges")
        logger.info("   Will discover ALL pairs including forex, commodities, indices")
    
    async def discover_all_pairs(self):
        """
        Discover ALL available pairs on ALL exchanges
        Including crypto, forex (TradFi), commodities, indices
        """
        logger.info("🔍 Discovering ALL pairs across ALL exchanges...")
        
        tasks = []
        for exchange_name, exchange in self.exchanges.items():
            tasks.append(self._discover_exchange_pairs(exchange_name, exchange))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log summary
        total_pairs = sum(
            len(pairs) 
            for exchange_data in self.exchange_pairs.values()
            for pairs in exchange_data.values()
        )
        
        logger.info(f"✅ DISCOVERY COMPLETE: {total_pairs} pairs across {len(self.exchanges)} exchanges!")
        
        # Show detailed breakdown
        for exchange_name, markets in self.exchange_pairs.items():
            total_for_exchange = sum(len(pairs) for pairs in markets.values())
            if total_for_exchange > 0:
                logger.info(f"   📊 {exchange_name}: {total_for_exchange} pairs total")
                for market_type, pairs in markets.items():
                    if pairs:
                        # Show first few pairs as examples
                        sample_pairs = list(pairs)[:3]
                        logger.info(f"      └─ {market_type}: {len(pairs)} pairs (e.g., {', '.join(sample_pairs)})")
        
        # Important message about testnet
        if self.mode == 'testnet':
            testnet_count = sum(
                len(pairs) 
                for ex, markets in self.exchange_pairs.items() 
                if 'testnet' in ex.lower()
                for pairs in markets.values()
            )
            logger.info(f"   🧪 TESTNET MODE: {testnet_count} pairs available on testnet exchanges")
            logger.info(f"      → Bot will ONLY trade pairs that exist on testnet!")
            logger.info(f"      → Signals for non-testnet pairs will be skipped (by design)")
    
    async def _discover_exchange_pairs(self, exchange_name: str, exchange: Any):
        """Discover all pairs on specific exchange"""
        try:
            logger.info(f"   🔍 Discovering {exchange_name}...")
            
            # Get actual exchange object (might be wrapped in engine)
            actual_exchange = exchange
            if hasattr(exchange, 'exchange'):
                actual_exchange = exchange.exchange
            elif hasattr(exchange, 'gate'):
                actual_exchange = exchange.gate
            elif hasattr(exchange, 'bot'):
                actual_exchange = exchange.bot
            
            # Check if this is a real exchange with load_markets
            if not hasattr(actual_exchange, 'load_markets'):
                logger.debug(f"   ⏭️  {exchange_name} is not a ccxt exchange, skipping")
                return
            
            # Load markets
            markets = await asyncio.to_thread(actual_exchange.load_markets)
            
            # Categorize by market type
            for symbol, market in markets.items():
                if not market.get('active', True):
                    continue
                
                # Detect market type
                market_type = self._detect_market_type(symbol, market)
                
                # Add to discovered pairs
                self.exchange_pairs[exchange_name][market_type].add(symbol)
            
            self.last_discovery[exchange_name] = datetime.now()
            
            # Log what we found
            for market_type, pairs in self.exchange_pairs[exchange_name].items():
                if pairs:
                    logger.info(f"      {market_type}: {len(pairs)} pairs")
        
        except Exception as e:
            logger.error(f"   ❌ {exchange_name} discovery failed: {e}")
    
    def _detect_market_type(self, symbol: str, market: Dict) -> str:
        """
        Detect market type from symbol
        
        Returns: 'spot', 'futures', 'perpetual', 'tradfi', 'forex', 'commodities', 'indices'
        """
        symbol_upper = symbol.upper()
        
        # Check market info first
        if market.get('type'):
            mtype = market['type'].lower()
            if mtype in ['spot', 'futures', 'swap', 'perpetual']:
                return mtype
        
        # Detect forex (currency pairs)
        for curr in self.market_patterns['forex']:
            if curr in symbol_upper and '/' not in symbol_upper:
                return 'forex'
            # Also check pairs like EUR/USD, GBP/USD
            if symbol.count('/') == 1:
                base, quote = symbol.split('/')
                if base in self.market_patterns['forex'] and quote in self.market_patterns['forex']:
                    return 'forex'
        
        # Detect commodities
        for comm in self.market_patterns['commodities']:
            if comm in symbol_upper:
                return 'commodities'
        
        # Detect indices
        for idx in self.market_patterns['indices']:
            if idx in symbol_upper:
                return 'indices'
        
        # Check if perpetual/futures
        if 'PERP' in symbol_upper or '-PERP' in symbol_upper:
            return 'perpetual'
        if 'FUT' in symbol_upper or market.get('future'):
            return 'futures'
        
        # Default to spot for crypto
        return 'spot'
    
    async def route_signal(self, signal: Dict) -> Optional[Dict]:
        """
        INTELLIGENTLY ROUTE signal to correct exchange/market
        
        Args:
            signal: Trading signal with symbol
        
        Returns:
            {
                'exchange': 'bybit',
                'market_type': 'forex',
                'symbol': 'GBPAUD',
                'pattern': {...},  # Adapted pattern for this market type
                'available': True
            }
            Or None if pair not available anywhere
        """
        symbol = signal.get('symbol') or signal.get('pair', '')
        if not symbol:
            return None
        
        logger.info(f"🧠 Routing signal: {symbol}")
        
        # Find all exchanges that have this pair
        available_routes = []
        
        for exchange_name, markets in self.exchange_pairs.items():
            for market_type, pairs in markets.items():
                if symbol in pairs or symbol.replace('/', '') in pairs:
                    available_routes.append({
                        'exchange': exchange_name,
                        'market_type': market_type,
                        'symbol': symbol
                    })
        
        if not available_routes:
            logger.info(f"   ⏭️  {symbol} not discovered on any exchange")
            logger.info(f"      🔍 Router checked: {', '.join(self.exchange_pairs.keys())}")
            logger.info(f"      💡 Pair may not be listed or discovery incomplete")
            
            # Try AI discovery if available
            if self.ai_consultation:
                logger.info(f"   🤖 Asking AI where to find {symbol}...")
                ai_route = await self._ask_ai_for_exchange(symbol)
                if ai_route:
                    return ai_route
            
            return None
        
        # Choose best route (prefer testnet if available, then by market type priority)
        best_route = self._choose_best_route(available_routes, signal)
        
        # If no suitable route (e.g., testnet mode but pair not on testnet)
        if not best_route:
            logger.info(f"   ⏭️  {symbol} not available on suitable exchange (mode: {self.mode})")
            return None
        
        # Get adapted pattern for this market type
        pattern = self._get_adapted_pattern(best_route['market_type'], signal)
        
        best_route['pattern'] = pattern
        best_route['available'] = True
        
        logger.info(f"   ✅ Routed to: {best_route['exchange']} {best_route['market_type']}")
        logger.info(f"   📊 Pattern adapted for {best_route['market_type']}")
        
        return best_route
    
    def _choose_best_route(self, routes: List[Dict], signal: Dict) -> Dict:
        """
        Choose best exchange/market for this signal
        
        HYBRID INTELLIGENCE:
        - Router discovers what pairs each exchange has
        - In testnet mode: Routes ONLY to testnet IF pair exists there
        - In live mode: Routes to best exchange that HAS the pair
        """
        # 🧪 TESTNET MODE: Prefer testnet exchanges
        if self.mode == 'testnet':
            testnet_routes = [r for r in routes if 'testnet' in r['exchange'].lower()]
            if testnet_routes:
                routes = testnet_routes
                logger.info(f"   🧪 Testnet mode: Found on testnet → routing to testnet")
            else:
                # Pair discovered on live exchanges but not testnet
                symbol = signal.get('symbol') or signal.get('pair', '')
                logger.info(f"   🧪 Testnet mode: {symbol} not on testnet (only on live exchanges)")
                logger.info(f"      Available on: {', '.join([r['exchange'] for r in routes])}")
                logger.info(f"      ⏭️  Skipping (testnet mode, pair not on testnet)")
                return None
        
        # Priority order
        priority = {
            'testnet': 100,  # Prefer testnet if in testnet mode
            'spot': 90,
            'forex': 85,
            'perpetual': 80,
            'futures': 75,
            'commodities': 70,
            'indices': 70
        }
        
        # Score routes
        scored = []
        for route in routes:
            score = priority.get(route['market_type'], 50)
            
            # Prefer certain exchanges
            if 'testnet' in route['exchange'].lower():
                score += 20
            elif route['exchange'] in ['bybit', 'binance', 'gate']:
                score += 10
            
            scored.append((score, route))
        
        # Return highest scored
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
    
    def _get_adapted_pattern(self, market_type: str, signal: Dict) -> Dict:
        """Get trading pattern adapted to market type"""
        base_pattern = self.market_patterns_config.get(market_type, self.market_patterns_config['crypto'])
        
        # Clone and customize
        pattern = base_pattern.copy()
        
        # Add signal-specific adjustments
        confidence = signal.get('confidence', 0.5)
        if confidence > 1:
            confidence = confidence / 100
        
        # Adjust based on confidence
        pattern['lot_size_multiplier'] *= (0.5 + confidence)
        
        return pattern
    
    async def _ask_ai_for_exchange(self, symbol: str) -> Optional[Dict]:
        """Use AI to find where a symbol is available"""
        try:
            context = {
                'query': f"Where can I trade {symbol}? Which exchange and market type?",
                'symbol': symbol
            }
            
            response = await self.ai_consultation.consult_strategy(context)
            
            # Parse AI response for exchange/market info
            # This is simplified - would parse AI text response
            if response and not response.get('skipped'):
                logger.info(f"   🤖 AI found potential route for {symbol}")
                # Would extract exchange and market type from AI response
                return None  # Placeholder
            
        except Exception as e:
            logger.debug(f"AI route discovery failed: {e}")
        
        return None
    
    async def detect_new_listings(self):
        """Detect newly listed pairs"""
        logger.info("🔍 Checking for new listings...")
        
        for exchange_name, exchange in self.exchanges.items():
            try:
                # Get current pairs
                markets = await asyncio.to_thread(exchange.load_markets)
                current_pairs = set(markets.keys())
                
                # Get previously known pairs
                known_pairs = set()
                for market_type, pairs in self.exchange_pairs.get(exchange_name, {}).items():
                    known_pairs.update(pairs)
                
                # Find new ones
                new_pairs = current_pairs - known_pairs
                
                if new_pairs:
                    logger.info(f"   🆕 {exchange_name}: {len(new_pairs)} new listings!")
                    for symbol in list(new_pairs)[:5]:  # Log first 5
                        logger.info(f"      • {symbol}")
                    
                    # Record new listings
                    for symbol in new_pairs:
                        market = markets[symbol]
                        market_type = self._detect_market_type(symbol, market)
                        self.exchange_pairs[exchange_name][market_type].add(symbol)
                        
                        self.new_listings.append({
                            'exchange': exchange_name,
                            'symbol': symbol,
                            'market_type': market_type,
                            'detected_at': datetime.now()
                        })
            
            except Exception as e:
                logger.debug(f"New listing check failed for {exchange_name}: {e}")
    
    async def start_monitoring_loop(self):
        """
        Continuously monitor for new listings
        Runs every 1 hour to detect new pairs on exchanges
        """
        logger.info("🔄 Starting continuous new listing monitoring...")
        
        while True:
            try:
                # Check for new listings
                await self.detect_new_listings()
                
                # Also refresh pair discovery if it's been too long
                for exchange_name, last_time in self.last_discovery.items():
                    if (datetime.now() - last_time).total_seconds() > self.discovery_interval:
                        logger.info(f"🔄 Re-discovering pairs for {exchange_name}...")
                        await self.discover_all_pairs()
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(300)  # Wait 5 min on error before retry
    
    def get_routing_stats(self) -> Dict:
        """Get routing statistics"""
        total_pairs = sum(
            len(pairs)
            for exchange_data in self.exchange_pairs.values()
            for pairs in exchange_data.values()
        )
        
        market_type_counts = defaultdict(int)
        for exchange_data in self.exchange_pairs.values():
            for market_type, pairs in exchange_data.items():
                market_type_counts[market_type] += len(pairs)
        
        return {
            'total_exchanges': len(self.exchanges),
            'total_pairs': total_pairs,
            'pairs_by_market_type': dict(market_type_counts),
            'new_listings_today': len([
                l for l in self.new_listings 
                if (datetime.now() - l['detected_at']).days == 0
            ]),
            'last_discovery': {
                ex: time.isoformat() 
                for ex, time in self.last_discovery.items()
            }
        }


# Singleton
_intelligent_router = None

def get_intelligent_router():
    """Get intelligent router instance"""
    global _intelligent_router
    return _intelligent_router

def initialize_intelligent_router(exchanges: Dict[str, Any], ai_consultation=None, mode='live'):
    """Initialize intelligent router"""
    global _intelligent_router
    if _intelligent_router is None:
        _intelligent_router = IntelligentExchangeRouter(exchanges, ai_consultation, mode)
        logger.info(f"✅ Intelligent Router singleton created with {len(exchanges)} exchanges ({mode.upper()} mode)")
    return _intelligent_router
