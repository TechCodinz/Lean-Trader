#!/usr/bin/env python3
"""
Find and fix where 'side' is being set incorrectly for BTC
"""

print("🔍 Checking where 'side' is set in position tracking...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Check lines around 1329 where we just fixed entry_price
print("1️⃣ Checking line 1329 (where position dict is created)...")
print()

for i in range(1327, 1333):
    if i < len(lines):
        print(f"  {i+1}: {lines[i]}")

print()

# Look for where side is set
print("2️⃣ Finding all places where 'side' is assigned...")
print()

for i, line in enumerate(lines, 1):
    if i >= 1310 and i <= 1340:  # Around close_position
        if 'side' in line and '=' in line:
            print(f"  Line {i}: {line.strip()}")

print()
print("=" * 70)
print("LIKELY ISSUE")
print("=" * 70)
print()
print("Line 1329 probably has:")
print("  'side': trade.get('side', 'buy')")
print()
print("But if trade.get('side') returns 'sell' incorrectly, P&L will be wrong!")
print()
print("Need to check INTELLIGENT_EXECUTION_ENGINE where trades are created...")
print()

# Check INTELLIGENT_EXECUTION_ENGINE
try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8') as f:
        exec_lines = f.read().split('\n')
    
    print("3️⃣ Checking INTELLIGENT_EXECUTION_ENGINE trade creation...")
    print()
    
    for i, line in enumerate(exec_lines, 1):
        if "'side'" in line and ('buy' in line or 'sell' in line):
            print(f"  Line {i}: {line.strip()}")
    
    print()
    
except FileNotFoundError:
    print("  INTELLIGENT_EXECUTION_ENGINE.py not found")

print()
print("=" * 70)
print("FIX STRATEGY")
print("=" * 70)
print()
print("Option 1: Force all trades to 'buy' (long only) in EXECUTION_ORCHESTRATOR")
print("Option 2: Check why INTELLIGENT_EXECUTION_ENGINE sets 'sell' for BTC")
print()
print("Applying Option 1 (safest) - force 'buy' for spot trading...")

