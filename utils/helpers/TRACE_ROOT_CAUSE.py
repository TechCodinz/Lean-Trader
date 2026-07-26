#!/usr/bin/env python3
"""
Find WHERE entry and exit are being swapped in position tracking
"""

import re

print("🔍 Finding the root cause of entry/exit swap...")
print()

# Check EXECUTION_ORCHESTRATOR - the close_position function
print("1️⃣ Checking EXECUTION_ORCHESTRATOR.py close_position...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Find close_position or monitor_positions
for i, line in enumerate(lines, 1):
    if 'def close_position' in line or 'def monitor_positions' in line:
        print(f"Found at line {i}: {line.strip()}")
        # Show next 100 lines
        for j in range(i, min(i+100, len(lines))):
            if 'entry_price' in lines[j] or 'exit_price' in lines[j]:
                print(f"  Line {j+1}: {lines[j]}")
        print()

# Check line 1327-1328 specifically (where we saw the bug before)
print("2️⃣ Checking lines 1325-1335 (where position dict is created)...")
print()

if len(lines) > 1335:
    for i in range(1324, 1335):
        print(f"  {i+1:4d}: {lines[i]}")
else:
    print("  File has fewer lines than expected")

print()

# Check if entry_price = 0 is still there
if "entry_price = 0" in content:
    print("3️⃣ Found 'entry_price = 0' placeholder - this is the issue!")
    print()
    
    # Find where it's used
    for i, line in enumerate(lines, 1):
        if 'entry_price = 0' in line:
            print(f"  Line {i}: {line}")
            print(f"  Context:")
            for j in range(max(0, i-5), min(len(lines), i+10)):
                marker = ">>> " if j == i-1 else "    "
                print(f"  {marker}{j+1:4d}: {lines[j]}")
            break

print()
print("4️⃣ Checking how position dict is created in INTELLIGENT_EXECUTION_ENGINE...")
print()

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8') as f:
        exec_content = f.read()
        exec_lines = exec_content.split('\n')
    
    # Find where trade record is created
    for i, line in enumerate(exec_lines, 1):
        if "'entry_price'" in line and ('actual_price' in line or 'current_price' in line):
            print(f"  Line {i}: {line.strip()}")
            
except FileNotFoundError:
    print("    INTELLIGENT_EXECUTION_ENGINE.py not found!")

print()
print("=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print()
print("The issue is likely:")
print("  1. entry_price = 0 as placeholder (line 1315)")
print("  2. Then position dict uses exit_price for entry")
print("  3. Or trade.get('entry_price') returns None/exit_price")
print()
print("Need to ensure:")
print("  [OK] Entry price stored correctly when position opens")
print("  [OK] Exit price is current market price when closing")
print("  [OK] No fallback that swaps them")

