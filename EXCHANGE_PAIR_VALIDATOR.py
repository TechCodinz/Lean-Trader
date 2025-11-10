#!/usr/bin/env python3
"""
✅ EXCHANGE PAIR VALIDATOR
Validates trading pairs before execution to avoid "pair not supported" errors
"""

import logging
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class ExchangePairValidator:
    """
    ✅ INTELLIGENT PAIR VALIDATION
    
    Prevents "pair not supported" errors by:
    - Caching supported pairs per exchange
    - Auto-refreshing pair lists
    - Pre-validating before trade execution
    - Suggesting alternative pairs
    """
    
    def __init__(self):
        # Cache of supported pairs per exchange
        self.supported_pairs: Dict[str, Set[str]] = {}
        
        # Last refresh time per exchange
        self.last_refresh: Dict[str, datetime] = {}
        
        # Refresh interval (15 minutes)
        self.refresh_interval = timedelta(minutes=15)
        
        # Pair aliases (common alternative names)
        self.pair_aliases = {
            'BTC/USDT': ['BTC/USD', 'BTCUSDT', 'XBT/USDT', 'XBT/USD'],
            'ETH/USDT': ['ETH/USD', 'ETHUSDT'],
            'BNB/USDT': ['BNB/USD', 'BNBUSDT'],
            'SOL/USDT': ['SOL/USD', 'SOLUSDT'],
            'AVAX/USDT': ['AVAX/USD', 'AVAXUSDT'],
        }
        
        # Fallback pairs (always try these if requested pair fails)
        self.fallback_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
        
        logger.info("✅ Exchange Pair Validator initialized")
    
    async def refresh_supported_pairs(self, exchange: object) -> Set[str]:
        """
        Refresh list of supported pairs for an exchange
        
        Args:
            exchange: Exchange object (ccxt)
            
        Returns:
            Set of supported pairs
        """
        try:
            exchange_id = exchange.id
            
            # Load markets
            await exchange.load_markets()
            
            # Get all symbols
            supported = set(exchange.symbols)
            
            # Cache it
            self.supported_pairs[exchange_id] = supported
            self.last_refresh[exchange_id] = datetime.now()
            
            logger.info(f"✅ Refreshed {len(supported)} pairs for {exchange_id}")
            return supported
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh pairs for {exchange.id}: {e}")
            return set()
    
    async def get_supported_pairs(self, exchange: object, force_refresh: bool = False) -> Set[str]:
        """
        Get supported pairs (from cache or fresh)
        
        Args:
            exchange: Exchange object
            force_refresh: Force refresh even if cache is fresh
            
        Returns:
            Set of supported pairs
        """
        exchange_id = exchange.id
        
        # Check if need refresh
        need_refresh = (
            force_refresh or
            exchange_id not in self.supported_pairs or
            exchange_id not in self.last_refresh or
            datetime.now() - self.last_refresh[exchange_id] > self.refresh_interval
        )
        
        if need_refresh:
            return await self.refresh_supported_pairs(exchange)
        
        return self.supported_pairs.get(exchange_id, set())
    
    async def is_pair_supported(self, exchange: object, pair: str) -> bool:
        """
        Check if a pair is supported on an exchange
        
        Args:
            exchange: Exchange object
            pair: Trading pair (e.g., 'BTC/USDT')
            
        Returns:
            True if supported, False otherwise
        """
        supported = await self.get_supported_pairs(exchange)
        
        # Direct check
        if pair in supported:
            return True
        
        # Check aliases
        if pair in self.pair_aliases:
            for alias in self.pair_aliases[pair]:
                if alias in supported:
                    logger.info(f"✅ Found alias {alias} for {pair} on {exchange.id}")
                    return True
        
        return False
    
    async def validate_and_get_pair(self, exchange: object, pair: str) -> Optional[str]:
        """
        Validate pair and return the correct format
        
        Args:
            exchange: Exchange object
            pair: Requested trading pair
            
        Returns:
            Valid pair format or None if not supported
        """
        supported = await self.get_supported_pairs(exchange)
        
        # Direct match
        if pair in supported:
            return pair
        
        # Check aliases
        if pair in self.pair_aliases:
            for alias in self.pair_aliases[pair]:
                if alias in supported:
                    logger.info(f"✅ Using alias {alias} for {pair} on {exchange.id}")
                    return alias
        
        # Try normalized format (BTC/USDT vs BTCUSDT)
        normalized = pair.replace('/', '')
        for supported_pair in supported:
            if supported_pair.replace('/', '') == normalized:
                logger.info(f"✅ Found normalized match {supported_pair} for {pair}")
                return supported_pair
        
        logger.warning(f"⚠️  Pair {pair} not supported on {exchange.id}")
        return None
    
    async def get_alternative_pairs(self, exchange: object, pair: str) -> List[str]:
        """
        Get alternative pairs if requested one is not supported
        
        Args:
            exchange: Exchange object
            pair: Requested pair
            
        Returns:
            List of alternative pairs
        """
        supported = await self.get_supported_pairs(exchange)
        alternatives = []
        
        # Extract base currency
        base = pair.split('/')[0] if '/' in pair else pair[:3]
        
        # Find pairs with same base
        for supported_pair in supported:
            if supported_pair.startswith(base + '/'):
                alternatives.append(supported_pair)
        
        # Add fallback pairs
        for fallback in self.fallback_pairs:
            if fallback in supported and fallback not in alternatives:
                alternatives.append(fallback)
        
        logger.info(f"💡 Alternative pairs for {pair}: {alternatives[:5]}")
        return alternatives[:5]  # Top 5
    
    async def validate_trade(self, exchange: object, pair: str, silent: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate a trade before execution
        
        Args:
            exchange: Exchange object
            pair: Trading pair
            silent: Don't log if pair not supported
            
        Returns:
            (is_valid, corrected_pair)
        """
        # Try to get valid pair
        valid_pair = await self.validate_and_get_pair(exchange, pair)
        
        if valid_pair:
            return True, valid_pair
        
        if not silent:
            logger.warning(f"❌ Cannot trade {pair} on {exchange.id} - not supported")
            
            # Suggest alternatives
            alternatives = await self.get_alternative_pairs(exchange, pair)
            if alternatives:
                logger.info(f"💡 Try these instead: {alternatives}")
        
        return False, None
    
    async def filter_valid_pairs(self, exchange: object, pairs: List[str]) -> List[str]:
        """
        Filter a list of pairs to only include supported ones
        
        Args:
            exchange: Exchange object
            pairs: List of pairs to check
            
        Returns:
            List of valid pairs
        """
        valid_pairs = []
        
        for pair in pairs:
            is_valid, corrected_pair = await self.validate_trade(exchange, pair, silent=True)
            if is_valid:
                valid_pairs.append(corrected_pair)
        
        logger.info(f"✅ Filtered {len(pairs)} pairs → {len(valid_pairs)} valid on {exchange.id}")
        return valid_pairs
    
    def get_stats(self) -> Dict:
        """Get validator statistics"""
        total_pairs = sum(len(pairs) for pairs in self.supported_pairs.values())
        
        return {
            'exchanges_cached': len(self.supported_pairs),
            'total_pairs_cached': total_pairs,
            'last_refresh_times': {
                exchange: time.isoformat()
                for exchange, time in self.last_refresh.items()
            }
        }


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        validator = ExchangePairValidator()
        
        # Simulate exchange with supported pairs
        class MockExchange:
            id = 'binance'
            symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'AVAX/USDT']
            
            async def load_markets(self):
                pass
        
        exchange = MockExchange()
        
        # Test validation
        print("\n" + "="*70)
        print("Testing pair validation:")
        
        test_pairs = ['BTC/USDT', 'BTC/USD', 'DOGE/USDT', 'ETH/USDT']
        for pair in test_pairs:
            is_valid, corrected = await validator.validate_trade(exchange, pair)
            print(f"{pair}: {'✅ Valid' if is_valid else '❌ Invalid'} {f'(use {corrected})' if corrected else ''}")
        
        # Test alternatives
        print("\n" + "="*70)
        print("Testing alternatives:")
        alternatives = await validator.get_alternative_pairs(exchange, 'DOGE/USDT')
        print(f"Alternatives for DOGE/USDT: {alternatives}")
        
        # Test filtering
        print("\n" + "="*70)
        print("Testing filtering:")
        all_pairs = ['BTC/USDT', 'DOGE/USDT', 'ETH/USDT', 'SHIB/USDT', 'SOL/USDT']
        valid = await validator.filter_valid_pairs(exchange, all_pairs)
        print(f"Filtered {all_pairs} → {valid}")
        
        # Stats
        print("\n" + "="*70)
        print("Stats:", validator.get_stats())
    
    asyncio.run(test())
