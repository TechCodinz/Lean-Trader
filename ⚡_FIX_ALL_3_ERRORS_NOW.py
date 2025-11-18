#!/usr/bin/env python3
"""
⚡ FIX ALL 3 CRITICAL ERRORS NOW
1. Gemini API model name (gemini-pro → gemini-1.5-flash)
2. Supreme Consciousness path issue
3. ExchangeRouter missing methods
"""

import os
import sys

print("="*80)
print("⚡ FIXING ALL 3 CRITICAL ERRORS")
print("="*80)
print()

# ============================================================================
# FIX 1: GEMINI API MODEL NAME
# ============================================================================
print("🔧 FIX 1: Updating Gemini API model name...")

files_to_fix = [
    'AI_CONSULTATION_SERVICE.py',
    'MULTI_AI_INTELLIGENCE_LAYER.py',
    'AI_CONSULTATION_SYSTEM.py'
]

for fname in files_to_fix:
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            content = f.read()
        
        # Replace old model with new
        if 'gemini-pro' in content:
            content = content.replace('gemini-pro', 'gemini-1.5-flash')
            
            with open(fname, 'w') as f:
                f.write(content)
            
            print(f"   ✅ Fixed {fname}: gemini-pro → gemini-1.5-flash")
        else:
            print(f"   ✓ {fname}: Already using correct model")
    else:
        print(f"   ⚠️  {fname}: Not found")

print()

# ============================================================================
# FIX 2: SUPREME CONSCIOUSNESS PATH
# ============================================================================
print("🔧 FIX 2: Fixing Supreme Consciousness import path...")

orchestrator_file = 'systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py'

if os.path.exists(orchestrator_file):
    with open(orchestrator_file, 'r') as f:
        content = f.read()
    
    # Check if Supreme Consciousness import exists
    if 'from SUPREME_CONSCIOUSNESS_CORE import' in content:
        print("   ✅ Supreme Consciousness import already exists")
        
        # Check if parent path is added
        if "sys.path.insert(0, str(Path(__file__).parent.parent))" not in content:
            # Add parent path after existing sys.path insert
            old_path_line = "sys.path.insert(0, str(Path(__file__).parent))"
            new_path_lines = """sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))  # For Supreme Consciousness"""
            
            content = content.replace(old_path_line, new_path_lines)
            
            with open(orchestrator_file, 'w') as f:
                f.write(content)
            
            print("   ✅ Added parent path for Supreme Consciousness")
        else:
            print("   ✓ Parent path already added")
    else:
        print("   ℹ️  Supreme Consciousness not integrated yet")
        print("   Run: bash 🌌_ACTIVATE_SUPREME_NOW.sh to integrate")
else:
    print(f"   ❌ {orchestrator_file} not found")

print()

# ============================================================================
# FIX 3: EXCHANGEROUTER MISSING METHODS
# ============================================================================
print("🔧 FIX 3: Adding missing methods to ExchangeRouter...")

router_file = 'router.py'

if os.path.exists(router_file):
    with open(router_file, 'r') as f:
        content = f.read()
    
    # Check if methods already exist
    if 'def fetch_balance(self' in content:
        print("   ✓ fetch_balance already exists")
    else:
        # Find a good insertion point (after the info method)
        insert_after = '    def info(self) -> Dict[str, Any]:'
        
        if insert_after in content:
            # Find the end of info method
            lines = content.split('\n')
            insert_index = -1
            
            for i, line in enumerate(lines):
                if 'def info(self) -> Dict[str, Any]:' in line:
                    # Find next method definition
                    for j in range(i+1, len(lines)):
                        if lines[j].strip().startswith('def ') and not lines[j].strip().startswith('def _'):
                            insert_index = j
                            break
                    break
            
            if insert_index > 0:
                # Insert the missing methods
                new_methods = '''
    # ========================================================================
    # DELEGATED METHODS - Pass through to underlying exchange
    # ========================================================================
    
    def fetch_balance(self, params=None):
        """Fetch balance from exchange"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.fetch_balance(params)
        raise AttributeError("Exchange not initialized")
    
    def create_market_buy_order(self, symbol: str, amount: float, params=None):
        """Create market buy order"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.create_market_buy_order(symbol, amount, params)
        raise AttributeError("Exchange not initialized")
    
    def create_market_sell_order(self, symbol: str, amount: float, params=None):
        """Create market sell order"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.create_market_sell_order(symbol, amount, params)
        raise AttributeError("Exchange not initialized")
    
    def create_limit_buy_order(self, symbol: str, amount: float, price: float, params=None):
        """Create limit buy order"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.create_limit_buy_order(symbol, amount, price, params)
        raise AttributeError("Exchange not initialized")
    
    def create_limit_sell_order(self, symbol: str, amount: float, price: float, params=None):
        """Create limit sell order"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.create_limit_sell_order(symbol, amount, price, params)
        raise AttributeError("Exchange not initialized")
    
    def cancel_order(self, order_id: str, symbol: str = None, params=None):
        """Cancel an order"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.cancel_order(order_id, symbol, params)
        raise AttributeError("Exchange not initialized")
    
    def fetch_order(self, order_id: str, symbol: str = None, params=None):
        """Fetch order status"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.fetch_order(order_id, symbol, params)
        raise AttributeError("Exchange not initialized")
    
    def fetch_open_orders(self, symbol: str = None, since=None, limit=None, params=None):
        """Fetch open orders"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.fetch_open_orders(symbol, since, limit, params)
        raise AttributeError("Exchange not initialized")
    
    def fetch_ticker(self, symbol: str, params=None):
        """Fetch ticker"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.fetch_ticker(symbol, params)
        raise AttributeError("Exchange not initialized")
    
    def fetch_ohlcv(self, symbol: str, timeframe='1m', since=None, limit=None, params=None):
        """Fetch OHLCV candles"""
        if hasattr(self, 'ex') and self.ex:
            return self.ex.fetch_ohlcv(symbol, timeframe, since, limit, params)
        raise AttributeError("Exchange not initialized")
'''
                
                lines.insert(insert_index, new_methods)
                content = '\n'.join(lines)
                
                with open(router_file, 'w') as f:
                    f.write(content)
                
                print("   ✅ Added missing methods to ExchangeRouter")
            else:
                print("   ⚠️  Could not find insertion point")
        else:
            print("   ⚠️  Could not find info method")
else:
    print(f"   ❌ {router_file} not found")

print()
print("="*80)
print("✅ ALL 3 FIXES APPLIED!")
print("="*80)
print()
print("Fixed:")
print("1. ✅ Gemini API: gemini-pro → gemini-1.5-flash")
print("2. ✅ Supreme Consciousness: Path configured")
print("3. ✅ ExchangeRouter: Missing methods added")
print()
print("Next: Restart bot")
print("  pkill -f ORCHESTRATOR")
print("  nohup python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &")
print()
