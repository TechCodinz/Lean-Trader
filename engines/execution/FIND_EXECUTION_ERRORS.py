#!/usr/bin/env python3
"""
Find the actual execution errors
"""

import re
from collections import Counter

print("🔍 Finding execution errors...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Find all execution errors
error_pattern = r'Testnet execution failed.*?bybit.*?(\{.*?\}|[^\n]+)'
errors = re.findall(error_pattern, log, re.DOTALL | re.IGNORECASE)

if errors:
    print(f"Found {len(errors)} execution errors")
    print()
    
    # Categorize errors
    error_types = Counter()
    for error in errors[:50]:  # First 50
        error_str = str(error)
        if 'Insufficient balance' in error_str:
            error_types['Insufficient balance'] += 1
        elif 'does not have market symbol' in error_str:
            error_types['Invalid symbol'] += 1
        elif 'Order value exceeded lower limit' in error_str:
            error_types['Order too small'] += 1
        elif 'amount.*must be greater' in error_str:
            error_types['Amount too small'] += 1
        elif 'retCode' in error_str:
            error_types['Bybit API error'] += 1
        else:
            error_types['Other'] += 1
    
    print("Error breakdown:")
    for err_type, count in error_types.most_common():
        print(f"  {err_type}: {count}")
    
    print()
    print("Recent errors:")
    for i, error in enumerate(errors[-10:], 1):
        error_str = str(error)[:150]
        print(f"  {i}. {error_str}")
else:
    print("No execution errors found in expected format")

print()

# Check if run_execution_loop is actually being called
print("Checking if run_execution_loop is called...")
print()

if 'run_execution_loop' in log.lower():
    print("[OK] run_execution_loop mentioned in log")
    # Find the lines
    lines = [l for l in log.split('\n') if 'run_execution_loop' in l.lower()]
    print(f"   Found {len(lines)} mentions")
    for line in lines[-5:]:
        print(f"   {line[:100]}")
else:
    print("[X] run_execution_loop NOT mentioned in log")
    print("   → Method exists but may not be called!")

