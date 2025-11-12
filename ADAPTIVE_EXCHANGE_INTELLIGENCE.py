#!/usr/bin/env python3
"""
🧠 ADAPTIVE EXCHANGE INTELLIGENCE 🧠

The bot that KNOWS:
- Which pairs exist on which exchanges
- Balance on each exchange  
- Rules, fees, limits per exchange
- Optimal exchange for each trade
- Adapts strategy per exchange

AUTONOMOUS, ADAPTIVE, AWARE!
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import os

logger = logging.getLogger(__name__)


class AdaptiveExchangeIntelligence:
    """
    The bot's AWARENESS of all exchanges
    
    Knows:
    - All available pairs per exchange
    - Balance on each exchange
    - Min order sizes, fees, limits
    - Trading rules and patterns
    - Optimal routing
    
    ADAPTS IN REAL-TIME!
    """
    
    def __init__(self, exchanges: Dict[str, Any]):
        """
        Initialize with all available exchanges
        
        Args:
            exchanges: Dict of {'exchange_name': exchange_instance}
        """
        self.exchanges = exchanges
        
        # Exchange intelligence database
        self.pair_availability = {}  # {exchange: [list of pairs]}
        self.balances = {}  # {exchange: {asset: balance}}
        self.exchange_rules = {}  # {exchange: {rules}}
        self.fee_structures = {}  # {exchange: {fees}}
        self.min_order_sizes = {}  # {exchange: {pair: min_size}}
        
        # Performance tracking per exchange
        self.exchange_performance = defaultdict(lambda: {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit': 0.0,
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'best_pairs': []
        })
        
        # Last update times
        self.last_pair_scan = {}
        self.last_balance_check = {}
        
        logger.info("🧠 ADAPTIVE EXCHANGE INTELLIGENCE initialized!")
        logger.info(f"   Monitoring {len(exchanges)} exchanges")
    
    async def discover_all_pairs(self):
        """
        Discover ALL tradeable pairs on ALL exchanges
        
        This is the bot's AWARENESS of what it can trade!
        """
        logger.info("🔍 Discovering pairs across ALL exchanges...")
        
        discovery_tasks = []
        for exchange_name, exchange in self.exchanges.items():
            discovery_tasks.append(self._discover_exchange_pairs(exchange_name, exchange))
        
        results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
        
        total_pairs = sum(len(pairs) for pairs in self.pair_availability.values())
        logger.info(f"✅ Discovered {total_pairs} pairs across {len(self.exchanges)} exchanges!")
        
        # Log summary per exchange
        for exchange_name, pairs in self.pair_availability.items():
            logger.info(f"   📊 {exchange_name}: {len(pairs)} pairs")
    
    async def _discover_exchange_pairs(self, exchange_name: str, exchange: Any):
        """Discover pairs on specific exchange"""
        try:
            logger.info(f"   🔍 Scanning {exchange_name}...")
            
            # Load markets
            markets = await asyncio.to_thread(exchange.load_markets)
            
            # Extract tradeable pairs
            pairs = [symbol for symbol, market in markets.items() 
                    if market.get('active', True) and market.get('spot', True)]
            
            self.pair_availability[exchange_name] = pairs
            self.last_pair_scan[exchange_name] = datetime.now()
            
            logger.info(f"   ✅ {exchange_name}: {len(pairs)} pairs discovered")
            
            # Learn exchange rules
            await self._learn_exchange_rules(exchange_name, exchange, markets)
            
            return pairs
            
        except Exception as e:
            logger.error(f"   ❌ {exchange_name} discovery failed: {e}")
            self.pair_availability[exchange_name] = []
            return []
    
    async def _learn_exchange_rules(self, exchange_name: str, exchange: Any, markets: Dict):
        """
        Learn exchange-specific rules, patterns, limits
        
        The bot UNDERSTANDS each exchange's personality!
        """
        try:
            rules = {
                'exchange_name': exchange_name,
                'exchange_id': exchange.id,
                'has_testnet': hasattr(exchange, 'set_sandbox_mode'),
                'rate_limit': exchange.rateLimit,
                'capabilities': {
                    'spot': exchange.has.get('spot', False),
                    'margin': exchange.has.get('margin', False),
                    'futures': exchange.has.get('futures', False),
                    'swap': exchange.has.get('swap', False),
                },
                'learned_at': datetime.now().isoformat()
            }
            
            # Learn fee structure
            if hasattr(exchange, 'fees'):
                self.fee_structures[exchange_name] = exchange.fees
                rules['maker_fee'] = exchange.fees.get('trading', {}).get('maker', 0.001)
                rules['taker_fee'] = exchange.fees.get('trading', {}).get('taker', 0.001)
            
            # Learn minimum order sizes per pair (sample)
            min_sizes = {}
            for symbol, market in list(markets.items())[:100]:  # Sample 100 pairs
                if 'limits' in market and 'amount' in market['limits']:
                    min_sizes[symbol] = market['limits']['amount'].get('min', 0.0001)
            
            self.min_order_sizes[exchange_name] = min_sizes
            rules['sample_min_orders'] = len(min_sizes)
            
            self.exchange_rules[exchange_name] = rules
            
            logger.info(f"   🧠 Learned {exchange_name} rules:")
            logger.info(f"      Spot: {rules['capabilities']['spot']}")
            logger.info(f"      Futures: {rules['capabilities']['futures']}")
            logger.info(f"      Maker fee: {rules.get('maker_fee', 'N/A')}")
            logger.info(f"      Min order sizes: {len(min_sizes)} pairs")
            
        except Exception as e:
            logger.error(f"   ⚠️ Failed to learn {exchange_name} rules: {e}")
    
    async def check_all_balances(self):
        """
        Check balance on ALL exchanges
        
        The bot KNOWS how much it can trade on each exchange!
        """
        logger.info("💰 Checking balances across ALL exchanges...")
        
        balance_tasks = []
        for exchange_name, exchange in self.exchanges.items():
            balance_tasks.append(self._check_exchange_balance(exchange_name, exchange))
        
        await asyncio.gather(*balance_tasks, return_exceptions=True)
        
        # Log summary
        total_usdt = 0
        for exchange_name, balance in self.balances.items():
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            total_usdt += usdt_balance
            if usdt_balance > 0:
                logger.info(f"   💰 {exchange_name}: ${usdt_balance:.2f} USDT")
        
        logger.info(f"✅ Total USDT across all exchanges: ${total_usdt:.2f}")
        return total_usdt
    
    async def _check_exchange_balance(self, exchange_name: str, exchange: Any):
        """Check balance on specific exchange"""
        try:
            balance = await asyncio.to_thread(exchange.fetch_balance)
            self.balances[exchange_name] = balance
            self.last_balance_check[exchange_name] = datetime.now()
            
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            if usdt_balance > 0:
                logger.info(f"   ✅ {exchange_name}: ${usdt_balance:.2f} USDT available")
            
            return balance
            
        except Exception as e:
            logger.error(f"   ❌ {exchange_name} balance check failed: {e}")
            self.balances[exchange_name] = {}
            return {}
    
    def find_pair_exchanges(self, symbol: str) -> List[str]:
        """
        Find which exchanges have this pair
        
        Returns: List of exchange names that support this pair
        """
        available_exchanges = []
        
        for exchange_name, pairs in self.pair_availability.items():
            if symbol in pairs:
                available_exchanges.append(exchange_name)
        
        return available_exchanges
    
    def get_optimal_exchange(self, symbol: str, required_balance: float = 10.0) -> Optional[str]:
        """
        Choose OPTIMAL exchange for this trade
        
        Considers:
        - Pair availability
        - Balance available
        - Fees
        - Historical performance
        - Exchange rules
        
        Returns: Best exchange name or None
        """
        # Find exchanges with this pair
        available = self.find_pair_exchanges(symbol)
        
        if not available:
            logger.warning(f"   ⚠️ {symbol} not available on any exchange!")
            return None
        
        # Score each exchange
        scores = {}
        for exchange_name in available:
            score = 0
            
            # 1. Has enough balance? (CRITICAL)
            balance = self.balances.get(exchange_name, {}).get('USDT', {}).get('free', 0)
            if balance < required_balance:
                continue  # Skip if insufficient balance
            score += min(balance / required_balance, 10)  # Up to +10 points
            
            # 2. Lower fees = better
            rules = self.exchange_rules.get(exchange_name, {})
            taker_fee = rules.get('taker_fee', 0.001)
            score += (1 - taker_fee) * 5  # Up to +5 points
            
            # 3. Historical performance on this exchange
            perf = self.exchange_performance[exchange_name]
            score += perf.get('win_rate', 0) * 5  # Up to +5 points
            
            # 4. Exchange reliability
            if exchange_name in ['gateio', 'bybit', 'binance']:
                score += 3  # Prefer major exchanges
            
            scores[exchange_name] = score
        
        if not scores:
            logger.warning(f"   ⚠️ No exchange has sufficient balance for {symbol}")
            return None
        
        # Return highest scoring exchange
        optimal = max(scores, key=scores.get)
        logger.info(f"   🎯 Optimal exchange for {symbol}: {optimal} (score: {scores[optimal]:.1f})")
        
        return optimal
    
    def get_exchange_balance(self, exchange_name: str, asset: str = 'USDT') -> float:
        """Get available balance on specific exchange"""
        return self.balances.get(exchange_name, {}).get(asset, {}).get('free', 0.0)
    
    def can_trade_on_exchange(self, exchange_name: str, symbol: str, amount_usd: float) -> bool:
        """
        Check if we CAN trade this pair on this exchange
        
        Checks:
        - Pair exists
        - Sufficient balance
        - Meets minimum order size
        """
        # Check pair availability
        if symbol not in self.pair_availability.get(exchange_name, []):
            return False
        
        # Check balance
        balance = self.get_exchange_balance(exchange_name)
        if balance < amount_usd:
            return False
        
        # Check minimum order size
        min_size = self.min_order_sizes.get(exchange_name, {}).get(symbol, 1.0)
        if amount_usd < min_size:
            return False
        
        return True
    
    def record_trade_result(self, exchange_name: str, symbol: str, profit: float):
        """
        Record trade result for learning
        
        The bot LEARNS which exchanges work best!
        """
        perf = self.exchange_performance[exchange_name]
        perf['total_trades'] += 1
        perf['total_profit'] += profit
        
        if profit > 0:
            perf['winning_trades'] += 1
        
        # Update metrics
        perf['win_rate'] = perf['winning_trades'] / perf['total_trades']
        perf['avg_profit'] = perf['total_profit'] / perf['total_trades']
        
        # Track best pairs on this exchange
        if symbol not in perf['best_pairs'] and profit > 0:
            perf['best_pairs'].append(symbol)
            if len(perf['best_pairs']) > 10:
                perf['best_pairs'] = perf['best_pairs'][:10]
        
        logger.info(f"   📊 {exchange_name} updated: {perf['win_rate']:.1%} win rate, "
                   f"${perf['avg_profit']:.2f} avg profit")
    
    def get_intelligence_summary(self) -> Dict:
        """
        Get complete intelligence summary
        
        What the bot KNOWS about all exchanges
        """
        total_pairs = sum(len(pairs) for pairs in self.pair_availability.values())
        total_balance = sum(
            bal.get('USDT', {}).get('free', 0) 
            for bal in self.balances.values()
        )
        
        return {
            'total_exchanges': len(self.exchanges),
            'total_pairs_available': total_pairs,
            'total_balance_usdt': total_balance,
            'exchanges': {
                name: {
                    'pairs': len(self.pair_availability.get(name, [])),
                    'balance_usdt': self.balances.get(name, {}).get('USDT', {}).get('free', 0),
                    'win_rate': self.exchange_performance[name]['win_rate'],
                    'total_trades': self.exchange_performance[name]['total_trades'],
                }
                for name in self.exchanges.keys()
            }
        }


# Singleton
_adaptive_intelligence = None

def get_adaptive_intelligence():
    """Get the adaptive intelligence instance"""
    return _adaptive_intelligence

def initialize_adaptive_intelligence(exchanges: Dict[str, Any]):
    """Initialize adaptive intelligence with exchanges"""
    global _adaptive_intelligence
    _adaptive_intelligence = AdaptiveExchangeIntelligence(exchanges)
    return _adaptive_intelligence
