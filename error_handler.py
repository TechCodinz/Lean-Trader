"""
Comprehensive Error Handler for Production Trading Bot
Handles all errors, exceptions, and recovery mechanisms
"""

import logging
import traceback
import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, Dict, List
from functools import wraps
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    NETWORK = "network"
    EXCHANGE = "exchange"
    DATABASE = "database"
    TRADING = "trading"
    SYSTEM = "system"
    CONFIGURATION = "configuration"
    ML_MODEL = "ml_model"
    NOTIFICATION = "notification"

class TradingError(Exception):
    """Base exception for trading errors"""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 category: ErrorCategory = ErrorCategory.SYSTEM):
        self.message = message
        self.severity = severity
        self.category = category
        self.timestamp = datetime.now()
        super().__init__(self.message)

class ExchangeError(TradingError):
    """Exchange-related errors"""
    def __init__(self, message: str, exchange: str = None):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.EXCHANGE)
        self.exchange = exchange

class RiskError(TradingError):
    """Risk management errors"""
    def __init__(self, message: str):
        super().__init__(message, ErrorSeverity.CRITICAL, ErrorCategory.TRADING)

class ConfigurationError(TradingError):
    """Configuration errors"""
    def __init__(self, message: str):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.CONFIGURATION)

class ErrorHandler:
    """Comprehensive error handler with recovery mechanisms"""
    
    def __init__(self, notification_manager=None, config=None):
        self.notification_manager = notification_manager
        self.config = config
        self.error_log = []
        self.error_counts = {}
        self.recovery_attempts = {}
        self.circuit_breakers = {}
        self.max_errors_per_minute = 10
        self.max_recovery_attempts = 3
        self.error_file = Path("logs/errors.json")
        self.load_error_history()
    
    def load_error_history(self):
        """Load error history from file"""
        try:
            if self.error_file.exists():
                with open(self.error_file, 'r') as f:
                    data = json.load(f)
                    self.error_counts = data.get('counts', {})
                    # Keep only recent errors
                    cutoff = datetime.now() - timedelta(days=7)
                    self.error_log = [
                        e for e in data.get('log', [])
                        if datetime.fromisoformat(e.get('timestamp', '')) > cutoff
                    ]
        except Exception as e:
            logger.warning(f"Could not load error history: {e}")
    
    def save_error_history(self):
        """Save error history to file"""
        try:
            self.error_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for serialization
            log_data = []
            for error in self.error_log[-1000:]:  # Keep last 1000 errors
                if isinstance(error, dict):
                    log_data.append(error)
                else:
                    log_data.append({
                        'timestamp': error.timestamp.isoformat() if hasattr(error, 'timestamp') else datetime.now().isoformat(),
                        'message': str(error),
                        'category': error.category.value if hasattr(error, 'category') else 'unknown',
                        'severity': error.severity.value if hasattr(error, 'severity') else 'medium'
                    })
            
            data = {
                'counts': self.error_counts,
                'log': log_data
            }
            
            with open(self.error_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save error history: {e}")
    
    async def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """
        Handle an error with appropriate recovery mechanisms
        Returns True if error was handled successfully
        """
        try:
            # Classify the error
            severity, category = self._classify_error(error)
            
            # Log the error
            self._log_error(error, severity, category, context)
            
            # Check circuit breaker
            if self._is_circuit_open(category):
                logger.warning(f"Circuit breaker open for {category}")
                return False
            
            # Update error counts
            self._update_error_counts(category)
            
            # Check if we should trip circuit breaker
            if self._should_trip_circuit(category):
                await self._trip_circuit_breaker(category)
                return False
            
            # Attempt recovery based on error type
            recovered = await self._attempt_recovery(error, category, context)
            
            # Send notification for critical errors
            if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                await self._send_error_notification(error, severity, category, context)
            
            # Save error history
            self.save_error_history()
            
            return recovered
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            return False
    
    def _classify_error(self, error: Exception) -> tuple:
        """Classify error by severity and category"""
        if isinstance(error, TradingError):
            return error.severity, error.category
        
        # Network errors
        if any(x in str(error).lower() for x in ['timeout', 'connection', 'network']):
            return ErrorSeverity.MEDIUM, ErrorCategory.NETWORK
        
        # Exchange errors
        if any(x in str(error).lower() for x in ['exchange', 'api', 'rate limit']):
            return ErrorSeverity.HIGH, ErrorCategory.EXCHANGE
        
        # Database errors
        if any(x in str(error).lower() for x in ['database', 'sql', 'connection pool']):
            return ErrorSeverity.HIGH, ErrorCategory.DATABASE
        
        # Trading errors
        if any(x in str(error).lower() for x in ['order', 'position', 'balance', 'insufficient']):
            return ErrorSeverity.CRITICAL, ErrorCategory.TRADING
        
        # Default
        return ErrorSeverity.MEDIUM, ErrorCategory.SYSTEM
    
    def _log_error(self, error: Exception, severity: ErrorSeverity, 
                   category: ErrorCategory, context: Dict[str, Any] = None):
        """Log error with full details"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity.value,
            'category': category.value,
            'message': str(error),
            'type': type(error).__name__,
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.error_log.append(error_info)
        
        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR [{category.value}]: {error}")
        elif severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH SEVERITY ERROR [{category.value}]: {error}")
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY ERROR [{category.value}]: {error}")
        else:
            logger.info(f"LOW SEVERITY ERROR [{category.value}]: {error}")
        
        if context:
            logger.debug(f"Error context: {json.dumps(context, default=str)}")
    
    def _update_error_counts(self, category: ErrorCategory):
        """Update error counts for rate limiting"""
        key = category.value
        now = datetime.now()
        
        if key not in self.error_counts:
            self.error_counts[key] = []
        
        # Remove old entries (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        self.error_counts[key] = [
            t for t in self.error_counts[key]
            if datetime.fromisoformat(t) > cutoff
        ]
        
        # Add current error
        self.error_counts[key].append(now.isoformat())
    
    def _should_trip_circuit(self, category: ErrorCategory) -> bool:
        """Check if circuit breaker should be tripped"""
        key = category.value
        if key in self.error_counts:
            return len(self.error_counts[key]) >= self.max_errors_per_minute
        return False
    
    async def _trip_circuit_breaker(self, category: ErrorCategory):
        """Trip circuit breaker for a category"""
        key = category.value
        self.circuit_breakers[key] = {
            'opened_at': datetime.now(),
            'duration': timedelta(minutes=5)  # Default 5 minute cooldown
        }
        
        logger.critical(f"Circuit breaker tripped for {category.value}")
        
        if self.notification_manager:
            await self.notification_manager.send_notification(
                "🔴 Circuit Breaker Tripped",
                f"Too many errors in {category.value}. System paused for 5 minutes."
            )
    
    def _is_circuit_open(self, category: ErrorCategory) -> bool:
        """Check if circuit breaker is open"""
        key = category.value
        if key in self.circuit_breakers:
            breaker = self.circuit_breakers[key]
            if datetime.now() < breaker['opened_at'] + breaker['duration']:
                return True
            else:
                # Circuit can be closed
                del self.circuit_breakers[key]
        return False
    
    async def _attempt_recovery(self, error: Exception, category: ErrorCategory, 
                                context: Dict[str, Any] = None) -> bool:
        """Attempt to recover from error"""
        key = f"{category.value}_{type(error).__name__}"
        
        # Track recovery attempts
        if key not in self.recovery_attempts:
            self.recovery_attempts[key] = 0
        
        if self.recovery_attempts[key] >= self.max_recovery_attempts:
            logger.error(f"Max recovery attempts reached for {key}")
            return False
        
        self.recovery_attempts[key] += 1
        
        # Recovery strategies by category
        if category == ErrorCategory.NETWORK:
            return await self._recover_network_error(error, context)
        elif category == ErrorCategory.EXCHANGE:
            return await self._recover_exchange_error(error, context)
        elif category == ErrorCategory.DATABASE:
            return await self._recover_database_error(error, context)
        elif category == ErrorCategory.TRADING:
            return await self._recover_trading_error(error, context)
        else:
            return await self._recover_generic_error(error, context)
    
    async def _recover_network_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Recover from network errors"""
        logger.info("Attempting network error recovery...")
        
        # Wait and retry
        await asyncio.sleep(5)
        
        # Reset connection if possible
        if context and 'connection' in context:
            try:
                await context['connection'].reset()
                return True
            except:
                pass
        
        return False
    
    async def _recover_exchange_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Recover from exchange errors"""
        logger.info("Attempting exchange error recovery...")
        
        # Rate limit errors - wait longer
        if 'rate' in str(error).lower():
            await asyncio.sleep(60)
            return True
        
        # API errors - wait and retry
        await asyncio.sleep(10)
        return False
    
    async def _recover_database_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Recover from database errors"""
        logger.info("Attempting database error recovery...")
        
        # Try to reconnect
        if context and 'database' in context:
            try:
                await context['database'].reconnect()
                return True
            except:
                pass
        
        return False
    
    async def _recover_trading_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Recover from trading errors"""
        logger.info("Attempting trading error recovery...")
        
        # For trading errors, usually need manual intervention
        # But we can try to cancel pending orders
        if context and 'bot' in context:
            try:
                await context['bot'].cancel_all_orders()
                return True
            except:
                pass
        
        return False
    
    async def _recover_generic_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Generic error recovery"""
        logger.info("Attempting generic error recovery...")
        
        # Wait and hope it resolves
        await asyncio.sleep(5)
        return False
    
    async def _send_error_notification(self, error: Exception, severity: ErrorSeverity,
                                      category: ErrorCategory, context: Dict[str, Any]):
        """Send error notification"""
        if not self.notification_manager:
            return
        
        try:
            message = f"""
🚨 ERROR ALERT

Severity: {severity.value.upper()}
Category: {category.value}
Error: {str(error)}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Context: {json.dumps(context or {}, default=str, indent=2)[:500]}

Action Required: Please check the system logs.
"""
            
            await self.notification_manager.send_notification(
                f"🚨 {severity.value.upper()} ERROR",
                message
            )
        except Exception as e:
            logger.error(f"Could not send error notification: {e}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        stats = {
            'total_errors': len(self.error_log),
            'errors_by_category': {},
            'errors_by_severity': {},
            'recent_errors': [],
            'circuit_breakers': {},
            'recovery_attempts': self.recovery_attempts
        }
        
        # Count by category and severity
        for error in self.error_log:
            cat = error.get('category', 'unknown')
            sev = error.get('severity', 'unknown')
            
            stats['errors_by_category'][cat] = stats['errors_by_category'].get(cat, 0) + 1
            stats['errors_by_severity'][sev] = stats['errors_by_severity'].get(sev, 0) + 1
        
        # Recent errors (last 10)
        stats['recent_errors'] = self.error_log[-10:]
        
        # Circuit breaker status
        for key, breaker in self.circuit_breakers.items():
            remaining = (breaker['opened_at'] + breaker['duration'] - datetime.now()).total_seconds()
            stats['circuit_breakers'][key] = {
                'status': 'open',
                'remaining_seconds': max(0, remaining)
            }
        
        return stats
    
    def clear_error_counts(self, category: ErrorCategory = None):
        """Clear error counts for a category or all"""
        if category:
            self.error_counts[category.value] = []
        else:
            self.error_counts = {}
        
        self.recovery_attempts = {}
        logger.info(f"Error counts cleared for {category.value if category else 'all categories'}")

def with_error_handler(error_handler: ErrorHandler):
    """Decorator for functions with error handling"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                }
                handled = await error_handler.handle_error(e, context)
                if not handled:
                    raise
                return None
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                }
                asyncio.create_task(error_handler.handle_error(e, context))
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class SafeExecutor:
    """Safe executor for critical operations"""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
    
    async def execute(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Execute function safely with error handling"""
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            context = {
                'function': func.__name__,
                'args': str(args)[:200],
                'kwargs': str(kwargs)[:200]
            }
            await self.error_handler.handle_error(e, context)
            return None
    
    async def execute_with_retry(self, func: Callable, *args, 
                                 max_retries: int = 3, 
                                 delay: float = 1.0, **kwargs) -> Optional[Any]:
        """Execute function with retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
        
        # All retries failed
        if last_error:
            context = {
                'function': func.__name__,
                'attempts': max_retries,
                'args': str(args)[:200],
                'kwargs': str(kwargs)[:200]
            }
            await self.error_handler.handle_error(last_error, context)
        
        return None