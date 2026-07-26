#!/usr/bin/env python3
"""
Trace where signals come from and why only BTC/ETH are trading
"""

import re

print("🔍 Step 1: Find where executor gets signals...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    orchestrator = f.read()

# Find signal generation
print("Looking for signal generation in main orchestrator...")

patterns_to_find = [
    (r'def.*generate.*signal', 'Signal generation method'),
    (r'collective.*consensus', 'Collective consensus usage'),
    (r'get_trading_signals', 'Get trading signals'),
    (r'analyze.*symbols?', 'Symbol analysis'),
    (r'fetch.*pairs', 'Fetch trading pairs'),
    (r'\.execute\(', 'Execute method calls'),
]

for pattern, description in patterns_to_find:
    matches = re.findall(f'.*{pattern}.*', orchestrator, re.IGNORECASE)
    if matches:
        print(f"[OK] {description}:")
        for match in matches[:3]:
            print(f"   {match.strip()}")
    else:
        print(f"[X] {description}: NOT FOUND")
    print()

print("=" * 60)
print()

# Check EXECUTION_ORCHESTRATOR
print("🔍 Step 2: Check EXECUTION_ORCHESTRATOR signal handling...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    exec_orch = f.read()

# Find where it gets symbols
if 'fetch_markets' in exec_orch or 'get_markets' in exec_orch:
    print("[OK] Found market fetching")
    # Extract the section
    for line in exec_orch.split('\n'):
        if 'fetch_markets' in line or 'get_markets' in line:
            print(f"   {line.strip()}")
else:
    print("[X] No market fetching found")

print()

# Check for symbol filtering
print("🔍 Step 3: Check for symbol filtering...")
print()

filters = [
    'min_confidence',
    'min_agreement',
    'volume',
    'liquidity',
    'max_positions',
    'max_trades',
]

for filter_name in filters:
    if filter_name in exec_orch:
        # Find the value
        pattern = f'{filter_name}.*=.*'
        matches = re.findall(pattern, exec_orch, re.IGNORECASE)
        if matches:
            print(f"[OK] {filter_name}:")
            for match in matches[:3]:
                print(f"   {match.strip()}")
    else:
        print(f"[X] {filter_name}: not found")
print()

print("=" * 60)
print()

# Check COLLECTIVE_CONSENSUS_ENGINE
print("🔍 Step 4: Check COLLECTIVE_CONSENSUS_ENGINE filtering...")
print()

try:
    with open('COLLECTIVE_CONSENSUS_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
        consensus = f.read()
    
    # Find min thresholds
    thresholds = re.findall(r'(min_\w+)\s*=\s*([\d.]+)', consensus)
    if thresholds:
        print("[OK] Found thresholds in consensus engine:")
        for name, value in thresholds[:10]:
            print(f"   {name} = {value}")
    else:
        print("[X] No thresholds found")
    
    print()
    
    # Find symbol selection
    if 'select_symbols' in consensus or 'get_symbols' in consensus:
        print("[OK] Found symbol selection logic")
    else:
        print("  No explicit symbol selection found")
    
except FileNotFoundError:
    print("[X] COLLECTIVE_CONSENSUS_ENGINE.py not found")

print()
print("=" * 60)
print()

# The smoking gun: Check what symbols are being passed to executor
print("🔍 Step 5: Find the ACTUAL symbol source...")
print()

# Check if there's a hardcoded symbol list
for content, filename in [(orchestrator, 'ORCHESTRATOR'), (exec_orch, 'EXECUTION_ORCHESTRATOR')]:
    if "['BTC" in content or '["BTC' in content or "('BTC" in content:
        print(f"  FOUND HARDCODED SYMBOLS in {filename}!")
        # Find the line
        for i, line in enumerate(content.split('\n')):
            if "'BTC" in line or '"BTC' in line:
                print(f"   Line {i+1}: {line.strip()}")
                if i < 5:  # Only show first 5
                    break
        print()

# Check for symbol whitelist
if 'whitelist' in orchestrator.lower() or 'allowed_symbols' in orchestrator.lower():
    print("  FOUND SYMBOL WHITELIST/RESTRICTION!")
    for line in orchestrator.split('\n'):
        if 'whitelist' in line.lower() or 'allowed_symbols' in line.lower():
            print(f"   {line.strip()}")
    print()

print()
print("=" * 60)
print()
print("💡 DIAGNOSIS COMPLETE!")
print()
print("Next: Check the output above to find:")
print("  1. Where symbols are hardcoded to just BTC/ETH")
print("  2. If min_confidence is too high (blocking trades)")
print("  3. If there's a symbol whitelist limiting pairs")
print("  4. If collective consensus is filtering too aggressively")

