#!/usr/bin/env python3
"""
Find WHERE signals are actually generated and WHERE ETH keeps coming from
"""

import re

print("🔍 Searching for signal generation loops...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find all while/for loops that might generate signals
loop_count = 0
eth_mentions = []

for i, line in enumerate(lines, 1):
    # Find main loops
    if re.search(r'^\s*(while|for)\s+', line) and 'symbol' in line.lower():
        loop_count += 1
        print(f"Loop {loop_count} at line {i}:")
        # Show context
        start = max(0, i-3)
        end = min(len(lines), i+10)
        for j in range(start, end):
            marker = ">>>" if j == i-1 else "   "
            print(f"{marker} {j+1:4d}: {lines[j].rstrip()}")
        print()
    
    # Find ETH/USDT mentions
    if "'ETH/USDT'" in line or '"ETH/USDT"' in line:
        eth_mentions.append((i, line.strip()))

print("=" * 60)
print(f"[OK] Found {loop_count} potential signal loops")
print()

if eth_mentions:
    print(f"  Found {len(eth_mentions)} ETH/USDT references:")
    for line_num, line_content in eth_mentions[:15]:
        print(f"   Line {line_num}: {line_content[:80]}")
print()

# Find where execute() is called
print("🔍 Searching for execute() calls...")
print()

execute_calls = []
for i, line in enumerate(lines, 1):
    if '.execute(' in line and not line.strip().startswith('#'):
        execute_calls.append((i, line.strip()))

if execute_calls:
    print(f"[OK] Found {len(execute_calls)} execute() calls:")
    for line_num, line_content in execute_calls[:10]:
        print(f"   Line {line_num}: {line_content[:80]}")
else:
    print("[X] No execute() calls found!")

print()
print("=" * 60)
print()

# The key: Find where symbols are iterated
print("🔍 Finding symbol iteration logic...")
print()

symbol_loops = []
for i, line in enumerate(lines, 1):
    if re.search(r'for.*symbol.*in', line, re.IGNORECASE):
        symbol_loops.append(i)
        print(f"[OK] Symbol loop at line {i}:")
        # Show context
        start = max(0, i-5)
        end = min(len(lines), i+15)
        for j in range(start, end):
            marker = ">>>" if j == i-1 else "   "
            print(f"{marker} {j+1:4d}: {lines[j].rstrip()}")
        print()

if not symbol_loops:
    print("  No 'for symbol in' loops found!")
    print("   Looking for alternative patterns...")
    for i, line in enumerate(lines, 1):
        if 'symbols' in line.lower() and ('for' in line or 'in' in line):
            print(f"   Line {i}: {line.strip()[:80]}")

print()
print("💡 KEY FINDINGS:")
print("   1. Check the loops above - that's where symbols are selected")
print("   2. Look for where ETH/USDT is hardcoded")
print("   3. Find where blacklist should be applied")

