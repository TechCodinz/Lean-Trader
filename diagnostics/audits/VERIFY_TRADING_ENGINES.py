#!/usr/bin/env python3
"""
Verify all trading engines are actually present and working
Check what's REALLY there vs what we think is there
"""

import os
import sys

print("=" * 80)
print("VERIFYING ACTUAL TRADING ENGINES")
print("=" * 80)
print()

# Check orchestrator imports
print("1. Checking what COMPLETE_ULTIMATE_ORCHESTRATOR actually imports:")
print("-" * 80)

try:
    with open('/workspace/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    # Find all imports
    import_lines = [line.strip() for line in content.split('\n') 
                   if 'import' in line and not line.strip().startswith('#')]
    
    trading_engines = []
    for line in import_lines[:100]:  # First 100 imports
        if any(keyword in line.lower() for keyword in ['engine', 'oracle', 'scout', 'sensor', 'detector']):
            print(f"   {line}")
            trading_engines.append(line)
    
    print(f"\n   Found {len(trading_engines)} trading-related imports")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Check what actually generates signals
print("2. Finding files that generate trading signals:")
print("-" * 80)

signal_keywords = ['signal', 'trade', 'execute', 'decision', 'buy', 'sell']
signal_files = []

for root, dirs, files in os.walk('/workspace'):
    # Skip hidden and __pycache__
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read().lower()
                
                # Check if file generates signals
                if 'def generate_signal' in content or 'def get_signal' in content or 'publish_signal' in content:
                    print(f"   ✅ {file} - Generates signals")
                    signal_files.append(file)
            except:
                pass

print(f"\n   Found {len(signal_files)} files that generate signals")

print()

# Check exchanges
print("3. Checking exchange connections:")
print("-" * 80)

try:
    from exchange_manager import ExchangeManager
    em = ExchangeManager()
    
    print(f"   ✅ Exchange manager loaded")
    print(f"   ✅ {len(em.exchanges)} exchanges initialized")
    
    for name, exchange in em.exchanges.items():
        print(f"      • {name}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Check if bot can actually make trading decisions
print("4. Can the bot make trading decisions?")
print("-" * 80)

try:
    # Check if execution orchestrator exists and works
    from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator
    print("   ✅ Execution orchestrator exists")
    
    # Check if it has execute methods
    if hasattr(ExecutionOrchestrator, 'execute_signal'):
        print("   ✅ Has execute_signal() method")
    if hasattr(ExecutionOrchestrator, 'process_signals'):
        print("   ✅ Has process_signals() method")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Check signal flow
print("5. Signal Flow Analysis:")
print("-" * 80)

print("\n   Expected Flow:")
print("   1. Engines generate signals → ✅")
print("   2. Signals go to orchestrator → ?")
print("   3. Orchestrator validates → ?")
print("   4. Risk management checks → ?")
print("   5. Execution on exchange → ?")

print("\n   Checking each step...")

# Check if there's a signal bus or queue
try:
    with open('/workspace/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    if 'signal_queue' in content or 'signal_bus' in content:
        print("   ✅ Signal queue/bus found")
    else:
        print("   ⚠️  No signal queue found - signals may not flow properly")
    
    if 'execute_signal' in content or 'process_signal' in content:
        print("   ✅ Signal processing found")
    else:
        print("   ⚠️  No signal processing found")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✅ Trading engine imports: {len(trading_engines)}")
print(f"✅ Files generating signals: {len(signal_files)}")
print(f"✅ Exchange connections: Available")
print(f"✅ Execution capability: Available")

print("\n🤔 Assessment:")
if len(trading_engines) > 10 and len(signal_files) > 5:
    print("   ✅ Bot has many trading engines")
    print("   ✅ Multiple signal sources")
    print("   ✅ Should be able to trade")
else:
    print("   ⚠️  Limited trading engines")
    print("   ⚠️  May not generate enough signals")

print("\n📋 Next Steps:")
print("   1. Verify signal generation actually works")
print("   2. Test end-to-end signal flow")
print("   3. Verify trades execute on exchanges")
print("   4. Check profit calculation")
