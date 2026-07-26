#!/usr/bin/env python3
"""
TARGETED FIX for entry price issue

Bot is PROFITABLE (+70% in 3 min!) but prices are backwards!
This will find the EXACT code and fix it manually.
"""

import re

print("="*70)
print("🎯 TARGETED FIX - Entry Price Issue")
print("="*70)
print()

# ========================================
# STEP 1: FIND THE PROBLEM
# ========================================
print("STEP 1: Locating entry price code...")
print("-" * 70)

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        lines = f.readlines()
    
    # Find where "Final entry_price" is logged
    for i, line in enumerate(lines, 1):
        if 'Final entry_price' in line or 'final entry_price' in line.lower():
            print(f"   Found at line {i}: {line.strip()}")
            print()
            print("   Context (10 lines before):")
            for j in range(max(0, i-11), i):
                print(f"   {j+1:4d}: {lines[j].rstrip()}")
            break
    
    print()

except Exception as e:
    print(f"   [X] Error: {e}")
    print()

# ========================================
# STEP 2: SEARCH FOR ACTUAL_PRICE ASSIGNMENT
# ========================================
print("STEP 2: Finding where actual_price is set...")
print("-" * 70)

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        content = f.read()
    
    # Find all occurrences of actual_price assignment
    matches = re.finditer(r'actual_price\s*=\s*(.+)', content)
    
    found_any = False
    for match in matches:
        found_any = True
        # Find line number
        line_num = content[:match.start()].count('\n') + 1
        print(f"   Line {line_num}: actual_price = {match.group(1)[:80]}")
    
    if not found_any:
        print("    No 'actual_price' assignments found!")
        print("   Searching for 'entry_price' assignments instead...")
        
        matches = re.finditer(r'entry_price\s*=\s*(.+)', content)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            print(f"   Line {line_num}: entry_price = {match.group(1)[:80]}")
    
    print()

except Exception as e:
    print(f"   [X] Error: {e}")
    print()

# ========================================
# STEP 3: SHOW CURRENT TRADE EXECUTION FLOW
# ========================================
print("STEP 3: Current trade execution flow...")
print("-" * 70)

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        content = f.read()
    
    # Find the execute_trade method
    match = re.search(r'(def (?:_)?execute_trade.*?)(?=\n    def |\nclass |\Z)', content, re.DOTALL)
    
    if match:
        method_code = match.group(1)
        lines = method_code.split('\n')[:50]  # First 50 lines
        
        print("   First 50 lines of execute_trade method:")
        for i, line in enumerate(lines, 1):
            if 'actual_price' in line or 'entry_price' in line or 'order' in line:
                print(f"   >>> {i:3d}: {line}")
            elif i <= 20:  # Show first 20 lines regardless
                print(f"       {i:3d}: {line}")
    else:
        print("    Could not find execute_trade method")
    
    print()

except Exception as e:
    print(f"   [X] Error: {e}")
    print()

# ========================================
# STEP 4: PROVIDE MANUAL FIX INSTRUCTIONS
# ========================================
print("="*70)
print("📋 MANUAL FIX INSTRUCTIONS")
print("="*70)
print()
print("The automatic fix couldn't locate the exact code pattern.")
print("Here's what to do manually:")
print()
print("1. Open INTELLIGENT_EXECUTION_ENGINE.py")
print("2. Find where 'actual_price' is set after placing an order")
print("3. REPLACE the current logic with:")
print()
print("   # OLD (probably something like):")
print("   actual_price = order.get('average') or order.get('price') or entry_price")
print()
print("   # NEW (use current market price):")
print("   try:")
print("       ticker = exchange.fetch_ticker(symbol)")
print("       actual_price = ticker.get('last') or ticker.get('close') or entry_price")
print("       logger.info(f'Using market price: ${actual_price}')")
print("   except:")
print("       actual_price = entry_price")
print()
print("="*70)

