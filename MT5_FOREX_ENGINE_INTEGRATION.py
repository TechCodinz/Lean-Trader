#!/usr/bin/env python3
"""
🌍💱 MT5 FOREX ENGINE INTEGRATION 💱🌍

STEP 5: Integrates MT5 forex pairs with trading engine

FEATURES:
- Dynamically loads pairs from merged_forex_pairs.json
- Routes forex to MT5 (when available)
- Routes crypto to crypto exchanges
- No hardcoded pairs!
- Auto-updates when pairs change
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MT5ForexEngineIntegration:
    """
    🌍 MT5 Forex Engine Integration
    
    Connects MT5 forex sync with trading engines
    Routes pairs intelligently based on type
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.merged_pairs_file = self.data_dir / "merged_forex_pairs.json"
        
        # Loaded pairs
        self.forex_pairs = []
        self.forex_symbols = []
        self.pair_metadata = {}
        
        # Load pairs
        self._load_pairs()
        
        logger.info("=" * 80)
        logger.info("🌍 MT5 FOREX ENGINE INTEGRATION LOADED")
        logger.info("=" * 80)
        logger.info(f"   Forex pairs loaded: {len(self.forex_pairs)}")
        logger.info(f"   Source: {self.merged_pairs_file}")
        logger.info("=" * 80)
    
    def _load_pairs(self):
        """Load pairs from merged file"""
        if not self.merged_pairs_file.exists():
            logger.warning(f"⚠️  {self.merged_pairs_file} not found")
            logger.warning("   Run MT5 sync first: python3 mt5_forex_sync.py")
            return
        
        try:
            with open(self.merged_pairs_file, 'r') as f:
                self.forex_pairs = json.load(f)
            
            # Extract symbols
            self.forex_symbols = [p['symbol'] for p in self.forex_pairs]
            
            # Build metadata lookup
            self.pair_metadata = {p['symbol']: p for p in self.forex_pairs}
            
            # Also index by base_symbol (without +)
            for p in self.forex_pairs:
                if 'base_symbol' in p:
                    self.pair_metadata[p['base_symbol']] = p
            
            logger.info(f"   ✅ Loaded {len(self.forex_pairs)} forex pairs")
        
        except Exception as e:
            logger.error(f"   ❌ Failed to load pairs: {e}")
    
    def is_forex_pair(self, symbol: str) -> bool:
        """Check if symbol is a forex pair"""
        return symbol in self.forex_symbols or symbol in self.pair_metadata
    
    def get_forex_metadata(self, symbol: str) -> Optional[Dict]:
        """Get metadata for a forex pair"""
        return self.pair_metadata.get(symbol)
    
    def get_all_tradable_symbols(self) -> List[str]:
        """Get all tradable forex symbols"""
        return self.forex_symbols.copy()
    
    def get_pairs_for_trading_engine(self) -> List[Dict]:
        """
        Get pairs formatted for trading engine
        
        Returns list ready to be used by trading logic
        """
        return self.forex_pairs.copy()
    
    def reload_pairs(self):
        """Reload pairs from file (call after sync)"""
        logger.info("🔄 Reloading forex pairs...")
        self._load_pairs()
        logger.info(f"   ✅ Reloaded {len(self.forex_pairs)} pairs")
    
    def should_trade_on_mt5(self, symbol: str) -> bool:
        """
        Determine if symbol should be traded on MT5
        
        Returns True for forex pairs, False for crypto
        """
        # Forex codes
        forex_codes = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']
        
        # Check if it's in our forex list
        if self.is_forex_pair(symbol):
            return True
        
        # Check if it looks like forex
        if '/' in symbol:
            parts = symbol.split('/')
            if len(parts) == 2:
                base, quote = parts
                # Remove + if present
                base = base.replace('+', '')
                quote = quote.replace('+', '')
                
                if base in forex_codes and quote in forex_codes:
                    return True
        
        # Not forex
        return False
    
    def get_routing_info(self, symbol: str) -> Dict:
        """
        Get routing information for a symbol
        
        Returns which exchange and market type to use
        """
        if self.should_trade_on_mt5(symbol):
            return {
                'exchange_type': 'mt5',
                'market_type': 'forex',
                'symbol': symbol,
                'metadata': self.get_forex_metadata(symbol)
            }
        else:
            # Crypto pair
            return {
                'exchange_type': 'crypto',
                'market_type': 'spot' if '/USDT' in symbol else 'unknown',
                'symbol': symbol,
                'metadata': None
            }


# Singleton
_mt5_integration = None

def get_mt5_forex_integration():
    """Get or create MT5 forex integration"""
    global _mt5_integration
    if _mt5_integration is None:
        _mt5_integration = MT5ForexEngineIntegration()
    return _mt5_integration


if __name__ == '__main__':
    # Test
    integration = get_mt5_forex_integration()
    
    print("\n" + "=" * 80)
    print("🧪 MT5 FOREX ENGINE INTEGRATION TEST")
    print("=" * 80)
    
    print(f"\nTotal forex pairs: {len(integration.forex_symbols)}")
    
    # Test routing
    test_symbols = ['EURUSD+', 'BTC/USDT', 'EUR/USD', 'GOLD']
    
    print("\nRouting test:")
    for sym in test_symbols:
        routing = integration.get_routing_info(sym)
        print(f"  {sym:15} → {routing['exchange_type']:8} ({routing['market_type']})")
    
    print("\n✅ Integration test complete!")
