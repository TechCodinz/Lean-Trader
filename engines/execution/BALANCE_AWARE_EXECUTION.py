#!/usr/bin/env python3
"""
BALANCE_AWARE_EXECUTION.py
Complete balance-aware execution system - 7 phases
Fixes: intelligent engine wiring, sizing bugs, symbol mismatches, CCXT semantics
"""

import logging
import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from EXCHANGE_ORDER_ADAPTER import normalize_market_order

logger = logging.getLogger(__name__)

# ============================================================================
# PHASE 2: BALANCE SNAPSHOT MANAGER (SINGLE SOURCE OF TRUTH)
# ============================================================================


def is_symbol_supported(exchange, symbol):
    try:
        if not hasattr(exchange, "markets") or not exchange.markets:
            exchange.load_markets()
        return symbol in exchange.markets
    except:
        return False

def get_min_notional_usdt(exchange, symbol, price):
    try:
        if not hasattr(exchange, "markets") or not exchange.markets:
            exchange.load_markets()
        m = exchange.markets.get(symbol, {})
        lim = m.get("limits", {})
        cost_min = lim.get("cost", {}).get("min")
        if cost_min:
            return float(cost_min)
        amt_min = lim.get("amount", {}).get("min")
        if amt_min and price > 0:
            return float(amt_min) * float(price)
        return 0.0
    except:
        return 0.0


class BalanceSnapshotManager:
    """Single source of truth for all balance queries"""
    
    def __init__(self, ttl_seconds: int = 2):
        self.ttl_seconds = ttl_seconds
        self.snapshots = {}  # venue_id -> {timestamp, balances}
        self.last_log = {}
    
    def get_free_quote_balance(self, exchange, venue_id: str, quote: str = "USDT") -> float:
        """Get free quote balance (e.g., USDT) for venue"""
        snapshot = self._get_snapshot(exchange, venue_id)
        
        free = snapshot.get(quote, {}).get('free', 0)
        
        # Log once per minute
        current_time = time.time()
        if venue_id not in self.last_log or (current_time - self.last_log[venue_id] > 60):
            reserved = snapshot.get(quote, {}).get('used', 0)
            logger.info(f"BALANCE venue={venue_id} free_{quote}={free:.4f} reserved_{quote}={reserved:.4f}")
            self.last_log[venue_id] = current_time
        
        return free
    
    def get_free_base_balance(self, exchange, venue_id: str, base: str) -> float:
        """Get free base currency balance for venue"""
        snapshot = self._get_snapshot(exchange, venue_id)
        return snapshot.get(base, {}).get('free', 0)
    
    def _get_snapshot(self, exchange, venue_id: str) -> Dict:
        """Get balance snapshot, refreshing if stale"""
        current_time = time.time()
        
        # Check if we have fresh snapshot
        if venue_id in self.snapshots:
            snapshot_data = self.snapshots[venue_id]
            if current_time - snapshot_data['timestamp'] < self.ttl_seconds:
                return snapshot_data['balances']
        
        # Refresh snapshot
        try:
            balance = exchange.fetch_balance()
            self.snapshots[venue_id] = {
                'timestamp': current_time,
                'balances': balance
            }
            return balance
        except Exception as e:
            logger.error(f"Balance fetch failed for {venue_id}: {e}")
            return {}

# ============================================================================
# PHASE 3: FIX ORDER SIZING (THE $835 BUG)
# ============================================================================

class BalanceAwareSizer:
    """Size orders based on actual available balance"""
    
    def __init__(self, max_balance_utilization: float = 0.15, 
                 absolute_max_per_trade: float = 10.0):
        """
        Args:
            max_balance_utilization: Max % of balance per trade (0.15 = 15%)
            absolute_max_per_trade: Absolute max USD per trade (testnet: $10)
        """
        self.max_balance_utilization = max_balance_utilization
        self.absolute_max_per_trade = absolute_max_per_trade
        
        self.reports_dir = Path("/root/bot/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.precheck_log = self.reports_dir / 'execution_prechecks.jsonl'
    
    def compute_safe_cost(self, symbol: str, venue_id: str, desired_cost: float,
                          free_balance: float, exchange, 
                          clamp_mode: bool = True) -> Tuple[bool, Dict]:
        """
        Compute safe order cost within balance constraints
        
        Args:
            symbol: Trading symbol
            venue_id: Venue identifier
            desired_cost: Strategy's desired cost
            free_balance: Available quote balance
            exchange: CCXT exchange object
            clamp_mode: If True, clamp to max; if False, skip if over
        
        Returns:
            (can_execute, params_or_reason)
        """
        # Hard cap based on balance
        max_cost_from_balance = free_balance * self.max_balance_utilization
        max_cost = min(max_cost_from_balance, self.absolute_max_per_trade)
        
        # Check if desired exceeds max
        if desired_cost > max_cost:
            if clamp_mode:
                clamped_cost = max_cost
                logger.info(f"ORDER_SIZE_CLAMPED: {symbol} ${desired_cost:.2f} → ${clamped_cost:.2f}")
            else:
                self._log_precheck(symbol, venue_id, desired_cost, 0, free_balance, "SKIP_OVER_MAX")
                return False, {'reason': 'DESIRED_COST_EXCEEDS_MAX', 'desired': desired_cost, 'max': max_cost}
        else:
            clamped_cost = desired_cost
        
        # Check exchange minimum notional
        try:
            markets = exchange.load_markets()
            if symbol not in markets:
                return False, {'reason': 'SYMBOL_NOT_IN_MARKETS'}
            
            market = markets[symbol]
            min_cost = market.get('limits', {}).get('cost', {}).get('min', 0)
            
            if clamped_cost < min_cost:
                self._log_precheck(symbol, venue_id, desired_cost, clamped_cost, free_balance, "ORDER_TOO_SMALL")
                logger.info(f"⏭️ SKIP {symbol}: ORDER_TOO_SMALL required_min_cost=${min_cost:.2f} clamped_cost=${clamped_cost:.2f}")
                return False, {'reason': 'ORDER_TOO_SMALL', 'min_cost': min_cost, 'clamped_cost': clamped_cost}
        
        except Exception as e:
            logger.warning(f"Could not check min_cost for {symbol}: {e}")
        
        # All checks passed
        self._log_precheck(symbol, venue_id, desired_cost, clamped_cost, free_balance, "OK")
        
        return True, {'cost': clamped_cost, 'free_balance': free_balance}
    
    def _log_precheck(self, symbol: str, venue_id: str, desired_cost: float,
                     clamped_cost: float, free_balance: float, decision: str):
        """Log execution precheck"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event': 'EXECUTION_PRECHECK',
            'symbol': symbol,
            'venue': venue_id,
            'desired_cost': round(desired_cost, 2),
            'clamped_cost': round(clamped_cost, 2),
            'free_balance': round(free_balance, 2),
            'decision': decision
        }
        
        with open(self.precheck_log, 'a') as f:
            f.write(json.dumps(event) + '\n')

# ============================================================================
# PHASE 4: SYMBOL SUPPORT CHECK PER VENUE
# ============================================================================

class VenueMarketCache:
    """Cache symbol support per venue with TTL"""
    
    def __init__(self, cache_ttl_minutes: int = 10, suppress_ttl_minutes: int = 10):
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.suppress_ttl = timedelta(minutes=suppress_ttl_minutes)
        
        self.markets_cache = {}  # venue_id -> {timestamp, markets}
        self.suppressed = {}  # (venue_id, symbol) -> timestamp
        
        self.reports_dir = Path("/root/bot/reports")
        self.skip_log = self.reports_dir / 'execution_skips.jsonl'
    
    def is_symbol_supported(self, exchange, venue_id: str, symbol: str) -> Tuple[bool, str]:
        """
        Check if symbol is supported on venue
        
        Returns:
            (supported, reason)
        """
        # Check suppression first
        suppress_key = (venue_id, symbol)
        if suppress_key in self.suppressed:
            age = datetime.now() - self.suppressed[suppress_key]
            if age < self.suppress_ttl:
                return False, f"SUPPRESSED (retry in {(self.suppress_ttl - age).seconds}s)"
            else:
                # TTL expired, remove suppression
                del self.suppressed[suppress_key]
        
        # Get markets
        markets = self._get_markets(exchange, venue_id)
        
        if symbol not in markets:
            # Suppress this symbol for this venue
            self.suppressed[suppress_key] = datetime.now()
            self._log_skip(venue_id, symbol, "SYMBOL_NOT_SUPPORTED")
            return False, "SYMBOL_NOT_SUPPORTED"
        
        market = markets[symbol]
        
        # Check if active
        if not market.get('active', True):
            self.suppressed[suppress_key] = datetime.now()
            self._log_skip(venue_id, symbol, "MARKET_INACTIVE")
            return False, "MARKET_INACTIVE"
        
        return True, "OK"
    
    def _get_markets(self, exchange, venue_id: str) -> Dict:
        """Get markets dictionary, using cache"""
        current_time = datetime.now()
        
        # Check cache
        if venue_id in self.markets_cache:
            cache_data = self.markets_cache[venue_id]
            if current_time - cache_data['timestamp'] < self.cache_ttl:
                return cache_data['markets']
        
        # Refresh cache
        try:
            markets = exchange.load_markets()
            self.markets_cache[venue_id] = {
                'timestamp': current_time,
                'markets': markets
            }
            return markets
        except Exception as e:
            logger.error(f"Failed to load markets for {venue_id}: {e}")
            return {}
    
    def _log_skip(self, venue_id: str, symbol: str, reason: str):
        """Log skipped symbol"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event': 'EXECUTION_SKIPPED',
            'venue': venue_id,
            'symbol': symbol,
            'reason': reason
        }
        
        with open(self.skip_log, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        logger.info(f"⏭️ SKIP {venue_id} {symbol}: {reason}")

# ============================================================================
# PHASE 5: FIX CCXT MARKET BUY SEMANTICS (Gate.io)
# ============================================================================

def place_market_buy(exchange, symbol: str, cost_usdt: float) -> Dict:
    """
    Place market buy order with correct CCXT semantics per exchange
    
    Args:
        exchange: CCXT exchange object
        symbol: Trading symbol
        cost_usdt: USD cost to spend
    
    Returns:
        Order result dict
    """
    # Exchanges that require createMarketBuyOrderRequiresPrice=False
    quote_amount_exchanges = ['gateio', 'gate']
    
    exchange_id = exchange.id.lower()
    
    if any(ex in exchange_id for ex in quote_amount_exchanges):
        # Gate.io style: amount = quote quantity (cost), no price needed
        if 'createMarketBuyOrderRequiresPrice' not in exchange.options:
            exchange.options['createMarketBuyOrderRequiresPrice'] = False
        
        logger.info(f"Placing market buy on {exchange_id}: {symbol} cost=${cost_usdt:.2f} (quote amount)")
        
        return exchange.create_order(
            symbol,
            'market',
            'buy',
            cost_usdt,  # amount = cost (quote quantity)
            None  # no price for market orders
        )
    
    else:
        # Standard CCXT: amount = base quantity, compute from price
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        
        amount = cost_usdt / price
        
        # Round to precision
        markets = exchange.load_markets()
        if symbol in markets:
            precision = markets[symbol].get('precision', {}).get('amount', 8)
            amount = round(amount, precision)
        
        logger.info(f"Placing market buy on {exchange_id}: {symbol} amount={amount} (@ ~${price:.2f})")
        
        return exchange.create_order(
            symbol,
            'market',
            'buy',
            amount,
            None
        )

# ============================================================================
# UNIFIED BALANCE-AWARE EXECUTION SYSTEM
# ============================================================================

class BalanceAwareExecutionSystem:
    """Complete balance-aware execution coordinating all phases"""
    
    def __init__(self, exchange, venue_id: str):
        self.exchange = exchange
        self.venue_id = venue_id
        
        # Phase 2: Balance manager
        self.balance_manager = BalanceSnapshotManager()
        
        # Phase 3: Sizer
        self.sizer = BalanceAwareSizer()
        
        # Phase 4: Market cache
        self.market_cache = VenueMarketCache()
        
        logger.info(f"Balance-Aware Execution System initialized for {venue_id}")
    
    def execute_trade(self, symbol: str, side: str, desired_cost: float) -> Tuple[bool, any]:
        """
        Execute trade with full balance awareness
        
        Returns:
            (success, order_or_reason)
        """
        # Phase 4: Check symbol supported
        supported, reason = self.market_cache.is_symbol_supported(self.exchange, self.venue_id, symbol)
        
        if not supported:
            return False, f"Symbol check: {reason}"
        
        # Phase 2: Get balance
        free_balance = self.balance_manager.get_free_quote_balance(self.exchange, self.venue_id, "USDT")
        
        # Phase 3: Compute safe cost
        can_size, sizing_result = self.sizer.compute_safe_cost(
            symbol, self.venue_id, desired_cost, free_balance, self.exchange
        )
        
        if not can_size:
            return False, f"Sizing: {sizing_result.get('reason')}"
        
        safe_cost = sizing_result['cost']
        
        # Phase 5: Place order with correct semantics
        try:
            if side.upper() == 'BUY':
                order = place_market_buy(self.exchange, symbol, safe_cost)
            else:
                # Sell logic (simplified - not implemented here)
                raise NotImplementedError("Sell logic placeholder")
            
            logger.info(f"[OK] ORDER PLACED: {symbol} {side} ${safe_cost:.2f}")
            
            return True, order
            
        except Exception as e:
            logger.warning(f"⏭️ EXECUTION FAILED: {symbol} - {e}")
            return False, str(e)

# Global instances
_balance_systems = {}

def get_balance_aware_system(exchange, venue_id: str) -> BalanceAwareExecutionSystem:
    """Get or create balance-aware system for venue"""
    global _balance_systems
    
    if venue_id not in _balance_systems:
        _balance_systems[venue_id] = BalanceAwareExecutionSystem(exchange, venue_id)
    
    return _balance_systems[venue_id]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Balance-Aware Execution System")
    print("Phases implemented:")
    print("  2. Balance Snapshot Manager") 
    print("  3. Balance-Aware Sizer (fixes $835 bug)")
    print("  4. Venue Market Cache (symbol support)")
    print("  5. CCXT Market Buy Fix (Gate.io)")
    print("\nReady to integrate")
