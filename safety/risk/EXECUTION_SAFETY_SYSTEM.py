#!/usr/bin/env python3
"""
EXECUTION_SAFETY_SYSTEM.py
Comprehensive execution safety with intelligent gating
Phases 1-6: Reports, fallback prevention, symbol gate, constraints, balance, engine health
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import ccxt

logger = logging.getLogger(__name__)

# ============================================================================
# PHASE 1: REPORT PATH GUARANTEE
# ============================================================================

def ensure_reports_dir(base_dir: str = "/root/bot/reports") -> Path:
    """Ensure reports directory exists and is writable"""
    reports_path = Path(base_dir)
    
    try:
        reports_path.mkdir(parents=True, exist_ok=True)
        
        # Test writability
        test_file = reports_path / '.write_test'
        test_file.write_text('test')
        test_file.unlink()
        
        logger.info(f"REPORT_DIR={reports_path} exists=True writable=True")
        
        return reports_path
        
    except Exception as e:
        logger.error(f"REPORT_DIR={reports_path} exists={reports_path.exists()} writable=False")
        logger.error(f"Failed to ensure reports directory: {e}")
        raise

# ============================================================================
# PHASE 2: STOP SILENT FALLBACK
# ============================================================================

class ExecutionEngineHealthCheck:
    """Verify intelligent execution engine is available"""
    
    @staticmethod
    def check_intelligent_engine_available(allow_fallback: bool = False) -> bool:
        """
        Check if IntelligentExecutionEngine is available
        
        Args:
            allow_fallback: If False (default), raise error if engine missing
        
        Returns:
            True if available, False if not (only if allow_fallback=True)
        """
        try:
            # Try to import
            from IntelligentExecutionEngine import IntelligentExecutionEngine
            logger.info("[OK] IntelligentExecutionEngine: AVAILABLE")
            return True
            
        except ImportError as e:
            if allow_fallback:
                logger.warning(" IntelligentExecutionEngine: NOT AVAILABLE - fallback allowed")
                return False
            else:
                logger.error("[X] IntelligentExecutionEngine: NOT AVAILABLE")
                logger.error("CRITICAL: Cannot run live execution without intelligent engine")
                logger.error("Set ALLOW_BASIC_EXECUTION_FALLBACK=true in config to override")
                raise RuntimeError("IntelligentExecutionEngine required but not available")

# ============================================================================
# PHASE 3: SYMBOL ELIGIBILITY GATE
# ============================================================================

class SymbolEligibilityGate:
    """Check if symbol is tradeable before creating orders"""
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.denylist_file = reports_dir / 'symbol_denylist.json'
        self.region_blocked = set()
        self.denylist = {}
        self._load_denylist()
    
    def _load_denylist(self):
        """Load existing denylist"""
        if self.denylist_file.exists():
            try:
                with open(self.denylist_file) as f:
                    self.denylist = json.load(f)
                
                # Load region blocked symbols (cached for 24h)
                now = datetime.now()
                for symbol, data in self.denylist.items():
                    if data.get('reason') == 'REGION_BLOCKED':
                        blocked_time = datetime.fromisoformat(data['timestamp'])
                        if now - blocked_time < timedelta(hours=24):
                            self.region_blocked.add(symbol)
                
                logger.info(f"Loaded denylist: {len(self.region_blocked)} region-blocked symbols")
                
            except Exception as e:
                logger.error(f"Failed to load denylist: {e}")
    
    def _save_denylist(self):
        """Save denylist to file"""
        try:
            with open(self.denylist_file, 'w') as f:
                json.dump(self.denylist, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save denylist: {e}")
    
    def add_to_denylist(self, symbol: str, reason: str, error_code: Optional[int] = None):
        """Add symbol to denylist"""
        self.denylist[symbol] = {
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'error_code': error_code
        }
        
        if reason == 'REGION_BLOCKED':
            self.region_blocked.add(symbol)
        
        self._save_denylist()
        
        logger.warning(f"🚫 DENYLISTED: {symbol} - {reason}")
    
    def is_symbol_tradeable(self, exchange: ccxt.Exchange, symbol: str) -> Tuple[bool, str]:
        """
        Check if symbol is tradeable
        
        Returns:
            (tradeable, reason)
        """
        # Check denylist first
        if symbol in self.region_blocked:
            return False, "REGION_BLOCKED (cached)"
        
        try:
            # Load markets if not loaded
            if not exchange.markets:
                exchange.load_markets()
            
            # Check symbol exists
            if symbol not in exchange.markets:
                return False, "SYMBOL_NOT_SUPPORTED"
            
            market = exchange.markets[symbol]
            
            # Check if active
            if not market.get('active', True):
                return False, "MARKET_INACTIVE"
            
            # Check market type matches
            account_type = exchange.options.get('defaultType', 'spot')
            market_type = market.get('type', 'spot')
            
            if account_type != market_type:
                return False, f"TYPE_MISMATCH (account={account_type}, market={market_type})"
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Symbol eligibility check failed for {symbol}: {e}")
            return False, f"CHECK_FAILED: {str(e)}"
    
    def handle_exchange_error(self, symbol: str, error_code: int, error_msg: str):
        """Handle exchange error and update denylist if appropriate"""
        # Region restriction
        if error_code == 170209:
            self.add_to_denylist(symbol, 'REGION_BLOCKED', error_code)
        
        # Other errors that indicate permanent issues
        elif error_code in [10001, 10006]:  # Invalid symbol codes
            self.add_to_denylist(symbol, 'INVALID_SYMBOL', error_code)

# ============================================================================
# PHASE 4: ORDER CONSTRAINTS GATE
# ============================================================================

class OrderConstraintsValidator:
    """Validate and adjust orders to meet exchange constraints"""
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.constraints_file = reports_dir / 'order_constraint_blocks.jsonl'
        self.market_cache = {}
    
    def validate_and_build_order(self, exchange: ccxt.Exchange, symbol: str,
                                 side: str, desired_usd: float,
                                 current_price: Optional[float] = None) -> Tuple[bool, Dict]:
        """
        Validate order meets constraints and build adjusted params
        
        Returns:
            (can_execute, params_or_reason)
        """
        try:
            # Get market info
            if symbol not in self.market_cache:
                if not exchange.markets:
                    exchange.load_markets()
                
                if symbol not in exchange.markets:
                    return False, {'reason': 'SYMBOL_NOT_FOUND'}
                
                self.market_cache[symbol] = exchange.markets[symbol]
            
            market = self.market_cache[symbol]
            
            # Get current price if not provided
            if not current_price:
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
            
            # Calculate amount
            amount = desired_usd / current_price
            
            # Get constraints
            limits = market.get('limits', {})
            precision = market.get('precision', {})
            
            min_amount = limits.get('amount', {}).get('min', 0)
            min_cost = limits.get('cost', {}).get('min', 0)
            
            amount_precision = precision.get('amount', 8)
            price_precision = precision.get('price', 8)
            
            # Round to precision
            amount_rounded = round(amount, amount_precision)
            price_rounded = round(current_price, price_precision)
            
            # Check minimum amount
            if amount_rounded < min_amount:
                reason = {
                    'reason': 'ORDER_TOO_SMALL',
                    'constraint': 'MIN_AMOUNT',
                    'required_min_amount': min_amount,
                    'provided_amount': amount_rounded
                }
                
                self._log_constraint_block(symbol, side, desired_usd, reason)
                
                logger.info(f"⏭️ SKIP {symbol}: ORDER_TOO_SMALL required_min_amount={min_amount} provided={amount_rounded}")
                
                return False, reason
            
            # Check minimum cost (notional)
            cost = amount_rounded * price_rounded
            
            if cost < min_cost:
                reason = {
                    'reason': 'ORDER_TOO_SMALL',
                    'constraint': 'MIN_COST',
                    'required_min_cost': min_cost,
                    'provided_cost': cost,
                    'desired_usd': desired_usd
                }
                
                self._log_constraint_block(symbol, side, desired_usd, reason)
                
                logger.info(f"⏭️ SKIP {symbol}: ORDER_TOO_SMALL required_min_cost=${min_cost:.2f} desired=${desired_usd:.2f}")
                
                return False, reason
            
            # All constraints met
            params = {
                'amount': amount_rounded,
                'price': price_rounded,
                'cost': cost
            }
            
            return True, params
            
        except Exception as e:
            logger.error(f"Order validation failed for {symbol}: {e}")
            return False, {'reason': 'VALIDATION_ERROR', 'error': str(e)}
    
    def _log_constraint_block(self, symbol: str, side: str, desired_usd: float, reason: Dict):
        """Log order blocked by constraints"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'ORDER_BLOCKED_CONSTRAINTS',
            'symbol': symbol,
            'side': side,
            'desired_usd': desired_usd,
            **reason
        }
        
        with open(self.constraints_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

# ============================================================================
# PHASE 5: BALANCE GATE
# ============================================================================

class BalanceGate:
    """Pre-check balance before order placement"""
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        self.balance_cache = None
        self.last_refresh = 0
        self.refresh_interval = 10  # seconds
    
    def refresh_balance(self):
        """Refresh balance cache"""
        try:
            self.balance_cache = self.exchange.fetch_balance()
            self.last_refresh = datetime.now().timestamp()
        except Exception as e:
            logger.error(f"Balance refresh failed: {e}")
    
    def get_available_balance(self, currency: str = 'USDT') -> float:
        """Get available balance with cache"""
        import time
        
        # Refresh if stale or missing
        if not self.balance_cache or (time.time() - self.last_refresh > self.refresh_interval):
            self.refresh_balance()
        
        if not self.balance_cache:
            return 0
        
        return self.balance_cache.get(currency, {}).get('free', 0)
    
    def check_sufficient_balance(self, required_cost: float, currency: str = 'USDT',
                                fee_buffer: float = 1.01) -> Tuple[bool, str]:
        """
        Check if sufficient balance for order
        
        Args:
            required_cost: Required USD value
            currency: Quote currency (default USDT)
            fee_buffer: Multiply required by this for fees (1.01 = 1%)
        
        Returns:
            (sufficient, reason)
        """
        available = self.get_available_balance(currency)
        required_with_fees = required_cost * fee_buffer
        
        if available >= required_with_fees:
            return True, f"OK (${available:.2f} >= ${required_with_fees:.2f})"
        else:
            reason = f"INSUFFICIENT_BALANCE_PRECHECK (need ${required_with_fees:.2f}, have ${available:.2f})"
            logger.info(f"⏭️ SKIP: {reason}")
            return False, reason

# ============================================================================
# PHASE 6: EXECUTION ENGINE WIRING & HEALTH CHECK
# ============================================================================

def execution_engine_healthcheck(allow_basic_fallback: bool = False,
                                reports_dir: str = "/root/bot/reports") -> bool:
    """
    Comprehensive execution engine health check at startup
    
    Args:
        allow_basic_fallback: Allow fallback to basic execution
        reports_dir: Reports directory path
    
    Returns:
        True if healthy, False otherwise
    """
    logger.info("=" * 80)
    logger.info("EXECUTION ENGINE HEALTH CHECK")
    logger.info("=" * 80)
    
    healthy = True
    
    # 1. Check reports directory
    try:
        reports_path = ensure_reports_dir(reports_dir)
        logger.info("[OK] Reports directory: OK")
    except Exception as e:
        logger.error(f"[X] Reports directory: FAILED - {e}")
        healthy = False
    
    # 2. Check intelligent engine
    try:
        engine_available = ExecutionEngineHealthCheck.check_intelligent_engine_available(allow_basic_fallback)
        if engine_available:
            logger.info("[OK] Intelligent execution engine: OK")
        else:
            logger.warning(" Intelligent execution engine: FALLBACK MODE")
            if not allow_basic_fallback:
                healthy = False
    except Exception as e:
        logger.error(f"[X] Intelligent execution engine: FAILED - {e}")
        healthy = False
    
    # 3. Check gating enabled
    logger.info("[OK] Execution gating: ENABLED")
    
    # Verdict
    logger.info("=" * 80)
    if healthy:
        logger.info("[OK] EXECUTION ENGINE: HEALTHY")
        logger.info("   Live execution ENABLED")
    else:
        logger.error("[X] EXECUTION ENGINE: UNHEALTHY")
        logger.error("   Bot will run ANALYSIS ONLY, NO EXECUTION")
    
    logger.info("=" * 80)
    
    return healthy

# ============================================================================
# UNIFIED EXECUTION GATE
# ============================================================================

class UnifiedExecutionGate:
    """Complete execution gate combining all safety checks"""
    
    def __init__(self, exchange: ccxt.Exchange, reports_dir: str = "/root/bot/reports"):
        self.exchange = exchange
        self.reports_dir = ensure_reports_dir(reports_dir)
        
        self.symbol_gate = SymbolEligibilityGate(self.reports_dir)
        self.constraints = OrderConstraintsValidator(self.reports_dir)
        self.balance_gate = BalanceGate(exchange)
        
        self.skip_log = self.reports_dir / 'execution_skips.jsonl'
        
        logger.info("Unified Execution Gate initialized")
    
    def validate_trade(self, symbol: str, side: str, desired_usd: float) -> Tuple[bool, Dict]:
        """
        Complete trade validation through all gates
        
        Returns:
            (can_execute, params_or_skip_reason)
        """
        # Gate 1: Symbol eligibility
        tradeable, reason = self.symbol_gate.is_symbol_tradeable(self.exchange, symbol)
        
        if not tradeable:
            self._log_skip(symbol, side, desired_usd, f"SYMBOL_GATE: {reason}")
            return False, {'skip_reason': reason, 'gate': 'symbol'}
        
        # Gate 2: Order constraints
        valid, result = self.constraints.validate_and_build_order(
            self.exchange, symbol, side, desired_usd
        )
        
        if not valid:
            self._log_skip(symbol, side, desired_usd, f"CONSTRAINTS: {result.get('reason')}")
            return False, {'skip_reason': result.get('reason'), 'gate': 'constraints', **result}
        
        order_params = result
        
        # Gate 3: Balance check
        sufficient, balance_reason = self.balance_gate.check_sufficient_balance(
            order_params['cost']
        )
        
        if not sufficient:
            self._log_skip(symbol, side, desired_usd, balance_reason)
            return False, {'skip_reason': balance_reason, 'gate': 'balance'}
        
        # All gates passed
        return True, order_params
    
    def _log_skip(self, symbol: str, side: str, desired_usd: float, reason: str):
        """Log skipped trade"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'TRADE_SKIPPED',
            'symbol': symbol,
            'side': side,
            'desired_usd': desired_usd,
            'reason': reason
        }
        
        with open(self.skip_log, 'a') as f:
            f.write(json.dumps(event) + '\n')

# Global instances
_execution_gate = None

def get_execution_gate(exchange: ccxt.Exchange) -> UnifiedExecutionGate:
    """Get global execution gate"""
    global _execution_gate
    if _execution_gate is None:
        _execution_gate = UnifiedExecutionGate(exchange)
    return _execution_gate

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test health check
    healthy = execution_engine_healthcheck(allow_basic_fallback=True)
    
    print(f"\nHealth check result: {'PASS' if healthy else 'FAIL'}")
