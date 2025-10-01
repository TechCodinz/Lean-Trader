"""
Production Fixes Module - Critical Safety Components for Trading Bot
This module provides essential safety mechanisms that were missing
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from collections import deque
from datetime import datetime, timedelta
import hashlib
import hmac
import decimal
from decimal import Decimal
import threading

logger = logging.getLogger(__name__)

# ============================================
# RATE LIMITING
# ============================================

class RateLimiter:
    """
    Thread-safe rate limiter for API calls
    Prevents exchange bans from too many requests
    """
    def __init__(self, max_calls: int = 10, period: float = 1.0):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self.lock = threading.Lock()
    
    def acquire(self, blocking: bool = True) -> bool:
        """
        Acquire permission to make a call
        Returns True if allowed, False if rate limit exceeded
        """
        while True:
            with self.lock:
                now = time.time()
                # Remove old calls outside the period
                while self.calls and self.calls[0] < now - self.period:
                    self.calls.popleft()
                
                # Check if we can make a call
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return True
                
                if not blocking:
                    return False
                
            # Wait a bit before trying again
            time.sleep(0.01)
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, *args):
        pass

# Global rate limiters per exchange
RATE_LIMITERS = {
    'binance': RateLimiter(1200, 60),  # 1200 requests per minute
    'bybit': RateLimiter(100, 60),     # 100 requests per minute
    'coinbase': RateLimiter(10, 1),    # 10 requests per second
    'default': RateLimiter(10, 1)      # Conservative default
}

def rate_limited(exchange: str = 'default'):
    """Decorator to rate limit function calls"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            limiter = RATE_LIMITERS.get(exchange, RATE_LIMITERS['default'])
            limiter.acquire()
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            limiter = RATE_LIMITERS.get(exchange, RATE_LIMITERS['default'])
            limiter.acquire()
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator

# ============================================
# ORDER VALIDATION
# ============================================

class OrderValidator:
    """
    Validates orders before sending to exchange
    Prevents invalid orders and protects funds
    """
    
    # Minimum order sizes per exchange (in USDT)
    MIN_ORDER_SIZES = {
        'binance': {
            'BTC/USDT': 10.0,
            'ETH/USDT': 10.0,
            'default': 10.0
        },
        'bybit': {
            'BTC/USDT': 1.0,
            'ETH/USDT': 1.0,
            'default': 1.0
        },
        'default': 10.0
    }
    
    # Price precision (decimal places)
    PRICE_PRECISION = {
        'BTC/USDT': 2,
        'ETH/USDT': 2,
        'BNB/USDT': 2,
        'default': 8
    }
    
    # Quantity precision (decimal places)
    QTY_PRECISION = {
        'BTC/USDT': 6,
        'ETH/USDT': 5,
        'BNB/USDT': 4,
        'default': 8
    }
    
    @classmethod
    def validate_order(cls, 
                      exchange: str,
                      symbol: str,
                      side: str,
                      order_type: str,
                      amount: float,
                      price: Optional[float] = None,
                      balance: Optional[float] = None) -> Dict[str, Any]:
        """
        Validate an order before execution
        Returns dict with 'valid' boolean and 'errors' list
        """
        errors = []
        
        # 1. Check side
        if side.upper() not in ['BUY', 'SELL']:
            errors.append(f"Invalid side: {side}")
        
        # 2. Check order type
        if order_type.upper() not in ['MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT']:
            errors.append(f"Invalid order type: {order_type}")
        
        # 3. Check minimum order size
        min_size = cls._get_min_order_size(exchange, symbol)
        order_value = amount * (price if price else 0)
        
        if price and order_value < min_size:
            errors.append(f"Order value ${order_value:.2f} below minimum ${min_size}")
        
        # 4. Check balance if provided
        if balance is not None and side.upper() == 'BUY' and price:
            required = amount * price * 1.001  # Include 0.1% fee
            if required > balance:
                errors.append(f"Insufficient balance: need ${required:.2f}, have ${balance:.2f}")
        
        # 5. Check amount precision
        qty_precision = cls.QTY_PRECISION.get(symbol, cls.QTY_PRECISION['default'])
        if not cls._check_precision(amount, qty_precision):
            errors.append(f"Amount {amount} exceeds precision {qty_precision} decimals")
        
        # 6. Check price precision
        if price:
            price_precision = cls.PRICE_PRECISION.get(symbol, cls.PRICE_PRECISION['default'])
            if not cls._check_precision(price, price_precision):
                errors.append(f"Price {price} exceeds precision {price_precision} decimals")
        
        # 7. Validate amount is positive
        if amount <= 0:
            errors.append(f"Amount must be positive: {amount}")
        
        # 8. Validate price is positive for limit orders
        if order_type.upper() in ['LIMIT', 'STOP_LIMIT'] and (not price or price <= 0):
            errors.append(f"Price required for {order_type} orders")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'formatted_amount': cls._format_precision(amount, qty_precision),
            'formatted_price': cls._format_precision(price, price_precision) if price else None
        }
    
    @staticmethod
    def _get_min_order_size(exchange: str, symbol: str) -> float:
        """Get minimum order size for exchange/symbol"""
        if exchange in OrderValidator.MIN_ORDER_SIZES:
            exchange_mins = OrderValidator.MIN_ORDER_SIZES[exchange]
            return exchange_mins.get(symbol, exchange_mins.get('default', 10.0))
        return OrderValidator.MIN_ORDER_SIZES.get('default', 10.0)
    
    @staticmethod
    def _check_precision(value: float, max_decimals: int) -> bool:
        """Check if value has acceptable decimal precision"""
        if value is None:
            return True
        str_value = f"{value:.10f}".rstrip('0').rstrip('.')
        if '.' in str_value:
            decimals = len(str_value.split('.')[1])
            return decimals <= max_decimals
        return True
    
    @staticmethod
    def _format_precision(value: Optional[float], precision: int) -> Optional[str]:
        """Format value to specified precision"""
        if value is None:
            return None
        return f"{value:.{precision}f}".rstrip('0').rstrip('.')

# ============================================
# WEBSOCKET RECONNECTION MANAGER
# ============================================

class WebSocketManager:
    """
    Manages WebSocket connections with automatic reconnection
    """
    def __init__(self, url: str, on_message: Callable, on_error: Optional[Callable] = None):
        self.url = url
        self.on_message = on_message
        self.on_error = on_error
        self.ws = None
        self.running = False
        self.reconnect_delay = 1
        self.max_reconnect_delay = 60
        self.reconnect_attempts = 0
        
    async def connect(self):
        """Connect to WebSocket with reconnection logic"""
        self.running = True
        
        while self.running:
            try:
                logger.info(f"Connecting to WebSocket: {self.url}")
                # This is a placeholder - actual implementation would use websockets library
                # import websockets
                # self.ws = await websockets.connect(self.url)
                
                self.reconnect_delay = 1  # Reset delay on successful connection
                self.reconnect_attempts = 0
                
                # Handle messages
                # async for message in self.ws:
                #     if self.on_message:
                #         await self.on_message(message)
                
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                if self.on_error:
                    self.on_error(e)
                
                # Exponential backoff for reconnection
                self.reconnect_attempts += 1
                delay = min(self.reconnect_delay * (2 ** self.reconnect_attempts), 
                           self.max_reconnect_delay)
                
                logger.info(f"Reconnecting in {delay} seconds (attempt {self.reconnect_attempts})")
                await asyncio.sleep(delay)
    
    async def disconnect(self):
        """Disconnect WebSocket"""
        self.running = False
        if self.ws:
            await self.ws.close()

# ============================================
# DECIMAL PRECISION FOR FINANCIAL CALCULATIONS
# ============================================

class FinancialCalculator:
    """
    Use Decimal for precise financial calculations
    Prevents floating point errors in money calculations
    """
    
    @staticmethod
    def calculate_order_value(amount: float, price: float) -> Decimal:
        """Calculate order value with precise decimals"""
        return Decimal(str(amount)) * Decimal(str(price))
    
    @staticmethod
    def calculate_fee(amount: float, fee_rate: float = 0.001) -> Decimal:
        """Calculate trading fee"""
        return Decimal(str(amount)) * Decimal(str(fee_rate))
    
    @staticmethod
    def calculate_pnl(entry_price: float, exit_price: float, 
                     amount: float, side: str, fee_rate: float = 0.001) -> Decimal:
        """Calculate profit/loss with fees"""
        entry = Decimal(str(entry_price))
        exit = Decimal(str(exit_price))
        qty = Decimal(str(amount))
        fee = Decimal(str(fee_rate))
        
        if side.upper() == 'BUY':
            gross_pnl = (exit - entry) * qty
        else:  # SELL/SHORT
            gross_pnl = (entry - exit) * qty
        
        # Subtract fees (entry and exit)
        total_fees = (entry * qty * fee) + (exit * qty * fee)
        net_pnl = gross_pnl - total_fees
        
        return net_pnl
    
    @staticmethod
    def round_to_precision(value: float, precision: int) -> Decimal:
        """Round value to specified decimal places"""
        quantizer = Decimal(10) ** -precision
        return Decimal(str(value)).quantize(quantizer, rounding=decimal.ROUND_DOWN)

# ============================================
# SQL INJECTION PREVENTION
# ============================================

class SafeDatabase:
    """
    Safe database operations preventing SQL injection
    """
    
    @staticmethod
    def safe_execute(cursor, query: str, params: tuple = None):
        """
        Execute query with parameterized inputs
        NEVER use string formatting or concatenation in SQL!
        """
        # Always use parameterized queries
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor
    
    @staticmethod
    def sanitize_table_name(name: str) -> str:
        """
        Sanitize table name (can't be parameterized)
        Only allow alphanumeric and underscore
        """
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            raise ValueError(f"Invalid table name: {name}")
        return name
    
    @staticmethod
    def build_safe_insert(table: str, data: Dict[str, Any]) -> tuple:
        """
        Build safe INSERT query with placeholders
        Returns (query, params)
        """
        table = SafeDatabase.sanitize_table_name(table)
        
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        return query, tuple(values)

# ============================================
# CIRCUIT BREAKER
# ============================================

class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures
    """
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def call(self, func, *args, **kwargs):
        """
        Call function through circuit breaker
        """
        with self.lock:
            # Check if circuit should be reset
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = 'HALF_OPEN'
                    self.failure_count = 0
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset if in HALF_OPEN
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'
                    self.failure_count = 0
                
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                    logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
                
                raise e

# ============================================
# EXCHANGE-SPECIFIC FIXES
# ============================================

class ExchangeSpecificFixes:
    """
    Exchange-specific requirements and fixes
    """
    
    @staticmethod
    def binance_timestamp_sync():
        """
        Binance requires timestamp to be within 5000ms of server time
        """
        import requests
        try:
            response = requests.get('https://api.binance.com/api/v3/time')
            server_time = response.json()['serverTime']
            local_time = int(time.time() * 1000)
            time_diff = server_time - local_time
            
            if abs(time_diff) > 5000:
                logger.warning(f"Time sync issue with Binance: {time_diff}ms difference")
                # Adjust system time or use server time for requests
                return server_time
            return local_time
        except:
            return int(time.time() * 1000)
    
    @staticmethod
    def bybit_sign_request(params: Dict[str, Any], secret: str) -> str:
        """
        Generate signature for Bybit API requests
        """
        # Sort parameters by key
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # Generate signature
        signature = hmac.new(
            secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature

# ============================================
# POSITION RECONCILIATION
# ============================================

class PositionReconciler:
    """
    Reconcile internal position tracking with exchange
    """
    
    @staticmethod
    async def reconcile_positions(internal_positions: Dict, exchange_client) -> Dict[str, Any]:
        """
        Compare internal positions with exchange positions
        """
        discrepancies = []
        
        try:
            # Fetch positions from exchange
            exchange_positions = await exchange_client.fetch_positions()
            
            # Convert to dict for comparison
            exchange_dict = {pos['symbol']: pos for pos in exchange_positions}
            
            # Check each internal position
            for symbol, internal_pos in internal_positions.items():
                if symbol not in exchange_dict:
                    discrepancies.append({
                        'symbol': symbol,
                        'issue': 'Position exists internally but not on exchange',
                        'internal': internal_pos,
                        'exchange': None
                    })
                else:
                    exchange_pos = exchange_dict[symbol]
                    
                    # Compare quantities
                    if abs(internal_pos['amount'] - exchange_pos['contracts']) > 0.00001:
                        discrepancies.append({
                            'symbol': symbol,
                            'issue': 'Quantity mismatch',
                            'internal_qty': internal_pos['amount'],
                            'exchange_qty': exchange_pos['contracts']
                        })
            
            # Check for positions on exchange not tracked internally
            for symbol, exchange_pos in exchange_dict.items():
                if symbol not in internal_positions:
                    discrepancies.append({
                        'symbol': symbol,
                        'issue': 'Position on exchange but not tracked internally',
                        'internal': None,
                        'exchange': exchange_pos
                    })
            
            return {
                'reconciled': len(discrepancies) == 0,
                'discrepancies': discrepancies,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Position reconciliation failed: {e}")
            return {
                'reconciled': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# ============================================
# MEMORY LEAK PREVENTION
# ============================================

class MemoryManager:
    """
    Prevent memory leaks in long-running bot
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.data_queues = {}
    
    def add_data(self, key: str, data: Any):
        """
        Add data with automatic cleanup of old entries
        """
        if key not in self.data_queues:
            self.data_queues[key] = deque(maxlen=self.max_history)
        
        self.data_queues[key].append({
            'timestamp': datetime.now(),
            'data': data
        })
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """
        Remove data older than specified hours
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        for key, queue in self.data_queues.items():
            # Remove old entries
            while queue and queue[0]['timestamp'] < cutoff:
                queue.popleft()
    
    def get_memory_usage(self) -> Dict[str, int]:
        """
        Get current memory usage stats
        """
        import sys
        
        stats = {}
        for key, queue in self.data_queues.items():
            stats[key] = {
                'count': len(queue),
                'size_bytes': sys.getsizeof(queue)
            }
        
        return stats

# ============================================
# MAIN SAFETY WRAPPER
# ============================================

class ProductionSafetyWrapper:
    """
    Wrap any trading bot with production safety features
    """
    
    def __init__(self, bot, exchange_name: str = 'default'):
        self.bot = bot
        self.exchange_name = exchange_name
        self.rate_limiter = RATE_LIMITERS.get(exchange_name, RATE_LIMITERS['default'])
        self.circuit_breaker = CircuitBreaker()
        self.memory_manager = MemoryManager()
        self.validator = OrderValidator()
        
    async def safe_place_order(self, symbol: str, side: str, order_type: str,
                               amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Place order with all safety checks
        """
        # 1. Validate order
        validation = self.validator.validate_order(
            self.exchange_name,
            symbol,
            side,
            order_type,
            amount,
            price
        )
        
        if not validation['valid']:
            logger.error(f"Order validation failed: {validation['errors']}")
            return {'success': False, 'errors': validation['errors']}
        
        # 2. Rate limiting
        self.rate_limiter.acquire()
        
        # 3. Circuit breaker
        try:
            result = await self.circuit_breaker.call(
                self.bot.place_order,
                symbol,
                side,
                order_type,
                validation['formatted_amount'],
                validation['formatted_price']
            )
            
            # 4. Log for audit
            self.memory_manager.add_data('orders', {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'amount': amount,
                'price': price,
                'result': result
            })
            
            return {'success': True, 'result': result}
            
        except Exception as e:
            logger.error(f"Order failed: {e}")
            return {'success': False, 'error': str(e)}

# ============================================
# USAGE EXAMPLE
# ============================================

def integrate_safety_features(bot):
    """
    Integrate all safety features into existing bot
    """
    # Wrap the bot with safety features
    safe_bot = ProductionSafetyWrapper(bot, exchange_name='bybit')
    
    # Replace unsafe methods with safe ones
    original_place_order = bot.place_order
    
    async def safe_place_order_wrapper(*args, **kwargs):
        return await safe_bot.safe_place_order(*args, **kwargs)
    
    bot.place_order = safe_place_order_wrapper
    
    # Add reconciliation
    async def reconcile_positions_periodically():
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            result = await PositionReconciler.reconcile_positions(
                bot.positions, 
                bot.exchange
            )
            if not result['reconciled']:
                logger.warning(f"Position discrepancies: {result['discrepancies']}")
    
    # Start reconciliation task
    asyncio.create_task(reconcile_positions_periodically())
    
    return bot

print("✅ Production safety features loaded successfully!")
print("Use integrate_safety_features(bot) to add safety to your bot")