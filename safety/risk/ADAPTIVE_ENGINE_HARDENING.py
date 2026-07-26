#!/usr/bin/env python3
"""
ADAPTIVE_ENGINE_HARDENING.py
Comprehensive hardening for adaptive engines - 9 phases
Fixes all runtime errors while maintaining full autonomy
"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

# ============================================================================
# PHASE 1: CENTRALDATAHUB CONTRACT FIX
# ============================================================================

class CentralDataHubInterface:
    """Strict interface contract for CentralDataHub"""
    
    def size(self) -> int:
        """Return number of items in hub"""
        raise NotImplementedError
    
    def has(self, symbol: str) -> bool:
        """Check if symbol exists"""
        raise NotImplementedError
    
    def get(self, symbol: str, default=None) -> Any:
        """Get data for symbol"""
        raise NotImplementedError
    
    def snapshot(self) -> Dict:
        """Get complete snapshot"""
        raise NotImplementedError

class SafeDataHubWrapper:
    """Wrapper to make any data hub safe"""
    
    def __init__(self, hub):
        self.hub = hub
    
    def __len__(self):
        """Make hub iterable-compatible"""
        return self.size()
    
    def size(self) -> int:
        """Safe size getter"""
        if hasattr(self.hub, 'size'):
            return self.hub.size()
        elif hasattr(self.hub, '__len__'):
            return len(self.hub)
        elif hasattr(self.hub, 'data'):
            return len(self.hub.data) if hasattr(self.hub.data, '__len__') else 0
        elif hasattr(self.hub, 'cache'):
            return len(self.hub.cache) if hasattr(self.hub.cache, '__len__') else 0
        return 0
    
    def has(self, symbol: str) -> bool:
        if hasattr(self.hub, 'has'):
            return self.hub.has(symbol)
        return symbol in self.snapshot()
    
    def get(self, symbol: str, default=None):
        if hasattr(self.hub, 'get'):
            return self.hub.get(symbol, default)
        return self.snapshot().get(symbol, default)
    
    def snapshot(self) -> Dict:
        if hasattr(self.hub, 'snapshot'):
            return self.hub.snapshot()
        elif hasattr(self.hub, 'data'):
            return self.hub.data if isinstance(self.hub.data, dict) else {}
        return {}

# ============================================================================
# PHASE 2: PREVENT DOUBLE REGISTRATION
# ============================================================================

class IdempotentEngineRegistry:
    """Registry that prevents double registration"""
    
    def __init__(self):
        self.registered = set()
        self.initialized = set()
    
    def register_once(self, engine_name: str) -> bool:
        """
        Register engine if not already registered
        
        Returns:
            True if newly registered, False if already registered
        """
        if engine_name in self.registered:
            return False
        
        self.registered.add(engine_name)
        logger.info(f"Adaptive Engine {engine_name} registered")
        return True
    
    def mark_initialized(self, engine_name: str) -> bool:
        """
        Mark engine as initialized
        
        Returns:
            True if newly initialized, False if already initialized
        """
        if engine_name in self.initialized:
            logger.warning(f"Engine {engine_name} already initialized - skipping")
            return False
        
        self.initialized.add(engine_name)
        logger.info(f"Adaptive Engine {engine_name} initialized")
        return True
    
    def is_initialized(self, engine_name: str) -> bool:
        return engine_name in self.initialized

# Global registry
_engine_registry = IdempotentEngineRegistry()

def get_engine_registry():
    return _engine_registry

# ============================================================================
# PHASE 3: HARDEN ADAPTIVE ENGINE EXECUTION
# ============================================================================

class AdaptiveEngineHardening:
    """Wrapper to harden any adaptive engine"""
    
    def __init__(self, engine_name: str, reports_dir: str = "/root/bot/reports"):
        self.engine_name = engine_name
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.health_file = self.reports_dir / 'adaptive_engine_health.json'
        self.influence_weight = 1.0
        self.error_count = 0
        self.degraded = False
    
    def safe_execute(self, func, *args, **kwargs):
        """Execute engine function with exception handling"""
        try:
            result = func(*args, **kwargs)
            
            # Success - restore weight if degraded
            if self.degraded and self.error_count > 0:
                self.influence_weight = min(1.0, self.influence_weight + 0.1)
                if self.influence_weight >= 0.9:
                    self.degraded = False
                    logger.info(f"Engine {self.engine_name} recovered")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.degraded = True
            
            # Reduce influence temporarily
            self.influence_weight = max(0.1, self.influence_weight * 0.8)
            
            # Log degradation
            self._log_degradation(str(e))
            
            logger.warning(f"ADAPTIVE_ENGINE_DEGRADED: {self.engine_name} - {e}")
            logger.warning(f"  Influence reduced to {self.influence_weight:.2f}")
            
            # Return safe default
            return None
    
    def _log_degradation(self, error: str):
        """Log engine degradation event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'engine': self.engine_name,
            'event': 'ADAPTIVE_ENGINE_DEGRADED',
            'error': error,
            'influence_weight': self.influence_weight,
            'error_count': self.error_count
        }
        
        # Load existing health
        health = {}
        if self.health_file.exists():
            try:
                with open(self.health_file) as f:
                    health = json.load(f)
            except:
                pass
        
        # Update health
        health[self.engine_name] = event
        
        # Save
        with open(self.health_file, 'w') as f:
            json.dump(health, f, indent=2)

# ============================================================================
# PHASE 4: IBM QUANTUM ENGINE SAFE FALLBACK
# ============================================================================

class QuantumEngineSafeFallback:
    """Safe fallback for quantum engine"""
    
    def __init__(self):
        self.available = False
        self.degraded = False
        self.advisory_only = False
        
        try:
            import qiskit
            self.qiskit_version = qiskit.__version__
            self.available = True
            logger.info(f"Qiskit available: {self.qiskit_version}")
        except ImportError:
            logger.warning("Qiskit not available - quantum engine disabled")
            self.degraded = True
            self.advisory_only = True
    
    def safe_feature_map(self, *args, **kwargs):
        """Safe ZZFeatureMap with version compatibility"""
        if not self.available or self.advisory_only:
            return None
        
        try:
            from qiskit.circuit.library import ZZFeatureMap
            
            # Create feature map
            feature_map = ZZFeatureMap(*args, **kwargs)
            
            # Check if bind_parameters exists
            if not hasattr(feature_map, 'bind_parameters'):
                # Use assign_parameters instead
                if not hasattr(feature_map, 'assign_parameters'):
                    self._degrade_to_advisory()
                    return None
                
                # Wrap assign_parameters as bind_parameters
                feature_map.bind_parameters = feature_map.assign_parameters
            
            return feature_map
            
        except Exception as e:
            logger.error(f"Quantum feature map error: {e}")
            self._degrade_to_advisory()
            return None
    
    def _degrade_to_advisory(self):
        """Degrade to advisory mode"""
        if not self.advisory_only:
            self.advisory_only = True
            self.degraded = True
            logger.warning("Quantum engine degraded to advisory mode (compatibility)")

# ============================================================================
# PHASE 5: EXECUTION PRECHECK GATES
# ============================================================================

# Already implemented in EXECUTION_SAFETY_SYSTEM.py
# Import and use get_execution_gate()

# ============================================================================
# PHASE 6: SYMBOL & ROUTING SANITY
# ============================================================================

class SymbolRoutingSanity:
    """Ensure symbols routed to compatible engines only"""
    
    def __init__(self):
        self.forex_commodities = set()
        self.crypto = set()
        self.routing_cache = {}
    
    def classify_symbol(self, symbol: str) -> str:
        """Classify symbol type"""
        # Forex pairs
        forex = ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'AUD', 'NZD', 'CAD']
        
        if '/' in symbol:
            base, quote = symbol.split('/')
            if base in forex and quote in forex:
                self.forex_commodities.add(symbol)
                return 'FOREX'
        
        # Commodities
        commodities = ['GOLD', 'SILVER', 'OIL', 'XAU', 'XAG', 'WTI']
        if any(c in symbol for c in commodities):
            self.forex_commodities.add(symbol)
            return 'COMMODITY'
        
        # Crypto
        self.crypto.add(symbol)
        return 'CRYPTO'
    
    def get_compatible_venue(self, symbol: str) -> str:
        """Get compatible venue for symbol"""
        symbol_type = self.classify_symbol(symbol)
        
        if symbol_type in ['FOREX', 'COMMODITY']:
            return 'MT5'
        else:
            return 'CCXT'
    
    def validate_routing(self, symbol: str, venue: str) -> bool:
        """Validate symbol can be routed to venue"""
        compatible_venue = self.get_compatible_venue(symbol)
        
        if venue != compatible_venue:
            logger.warning(f"Routing mismatch: {symbol} → {venue} (should be {compatible_venue})")
            return False
        
        return True

# ============================================================================
# PHASE 7: RUNTIME SAFETY BUG FIXES
# ============================================================================

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with zero check"""
    if denominator == 0 or abs(denominator) < 1e-10:
        return default
    return numerator / denominator

def safe_get_positions(obj, default=None):
    """Safe accessor for open_positions"""
    if default is None:
        default = {}
    
    if hasattr(obj, 'open_positions'):
        return obj.open_positions if obj.open_positions is not None else default
    return default

def ensure_symbol_assigned(symbol: Optional[str], default: str = "UNKNOWN") -> str:
    """Ensure symbol is assigned before use"""
    return symbol if symbol is not None else default

# ============================================================================
# PHASE 8: REPORTS DIRECTORY GUARANTEE
# ============================================================================

def ensure_reports_directory(base_dir: str = "/root/bot/reports") -> Path:
    """Ensure reports directory exists and is writable"""
    reports_path = Path(base_dir)
    
    try:
        reports_path.mkdir(parents=True, exist_ok=True)
        
        # Test writable
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
# UNIFIED HARDENING INITIALIZATION
# ============================================================================

def initialize_adaptive_engine_hardening():
    """Initialize all hardening modules"""
    logger.info("=" * 80)
    logger.info("ADAPTIVE ENGINE HARDENING INITIALIZATION")
    logger.info("=" * 80)
    
    # Phase 8: Ensure reports directory
    try:
        reports_dir = ensure_reports_directory()
        logger.info("✓ Reports directory ready")
    except Exception as e:
        logger.error(f"✗ Reports directory failed: {e}")
        return False
    
    # Phase 4: Initialize quantum fallback
    quantum_fallback = QuantumEngineSafeFallback()
    logger.info(f"✓ Quantum engine: {'available' if quantum_fallback.available else 'degraded to advisory'}")
    
    # Phase 6: Initialize routing sanity
    routing = SymbolRoutingSanity()
    logger.info("✓ Symbol routing sanity initialized")
    
    # Phase 2: Initialize registry
    registry = get_engine_registry()
    logger.info("✓ Idempotent engine registry initialized")
    
    logger.info("=" * 80)
    logger.info("ADAPTIVE ENGINE HARDENING: READY")
    logger.info("=" * 80)
    
    return True

# Global instances
_quantum_fallback = None
_routing_sanity = None

def get_quantum_fallback():
    global _quantum_fallback
    if _quantum_fallback is None:
        _quantum_fallback = QuantumEngineSafeFallback()
    return _quantum_fallback

def get_routing_sanity():
    global _routing_sanity
    if _routing_sanity is None:
        _routing_sanity = SymbolRoutingSanity()
    return _routing_sanity

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test initialization
    success = initialize_adaptive_engine_hardening()
    print(f"\nHardening initialized: {success}")
