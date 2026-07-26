#!/usr/bin/env python3
"""
Find why BTC works but ETH doesn't - they should use same code!
"""

import re

print("🔍 Finding the real difference between BTC and ETH...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Get recent BTC and ETH trades
print("1️⃣ COMPARING BTC vs ETH TRADES")
print("=" * 70)
print()

btc_closes = re.findall(r'POSITION CLOSED: BTC/USDT \| Entry: \$([\d.]+) \| Exit: \$([\d.]+) \| P&L: \$\S+ \(([+-][\d.]+)%\)', log)
eth_closes = re.findall(r'POSITION CLOSED: ETH/USDT \| Entry: \$([\d.]+) \| Exit: \$([\d.]+) \| P&L: \$\S+ \(([+-][\d.]+)%\)', log)

print("BTC closes:")
for entry, exit_p, pnl in btc_closes[-3:]:
    direction = "UP" if float(exit_p) > float(entry) else "DOWN"
    pnl_sign = "PROFIT" if float(pnl) > 0 else "LOSS"
    match = "[OK] CORRECT" if (direction == "UP" and pnl_sign == "PROFIT") or (direction == "DOWN" and pnl_sign == "LOSS") else "[X] WRONG"
    print(f"  Entry ${entry} → Exit ${exit_p} ({direction}) = {pnl}% ({pnl_sign}) {match}")

print()
print("ETH closes:")
for entry, exit_p, pnl in eth_closes[-3:]:
    direction = "UP" if float(exit_p) > float(entry) else "DOWN"
    pnl_sign = "PROFIT" if float(pnl) > 0 else "LOSS"
    match = "[OK] CORRECT" if (direction == "UP" and pnl_sign == "PROFIT") or (direction == "DOWN" and pnl_sign == "LOSS") else "[X] WRONG"
    print(f"  Entry ${entry} → Exit ${exit_p} ({direction}) = {pnl}% ({pnl_sign}) {match}")

print()
print("=" * 70)
print("2️⃣ FINDING WHERE ENTRY PRICES ARE STORED")
print("=" * 70)
print()

# Check if there's a pattern - maybe ETH entries are stored differently
btc_entries = re.findall(r'BTC/USDT.*?Entry: immediate @ \$([\d.]+)', log)
eth_entries = re.findall(r'ETH/USDT.*?Entry: immediate @ \$([\d.]+)', log)

print(f"BTC entries logged: {len(btc_entries)}")
if btc_entries:
    print(f"  Sample: ${btc_entries[-1]}")

print(f"ETH entries logged: {len(eth_entries)}")
if eth_entries:
    print(f"  Sample: ${eth_entries[-1]}")

print()

# Check for any special handling of ETH
print("=" * 70)
print("3️⃣ CHECKING FOR SPECIAL ETH HANDLING IN CODE")
print("=" * 70)
print()

files_to_check = [
    'INTELLIGENT_EXECUTION_ENGINE.py',
    'EXECUTION_ORCHESTRATOR.py',
    'PROFIT_MONITORING_SYSTEM.py'
]

for filename in files_to_check:
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Check for ETH-specific code
        if 'ETH' in content:
            eth_mentions = len(re.findall(r'\bETH\b', content))
            print(f"{filename}: {eth_mentions} ETH mentions")
            
            # Find lines with ETH
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'ETH' in line and ('if' in line.lower() or 'symbol' in line.lower()):
                    print(f"  Line {i}: {line.strip()[:80]}")
    except:
        pass

print()
print("=" * 70)
print("4️⃣ HYPOTHESIS")
print("=" * 70)
print()

# Analyze the pattern
if btc_closes and eth_closes:
    btc_correct = all(
        (float(exit_p) > float(entry) and float(pnl) > 0) or
        (float(exit_p) < float(entry) and float(pnl) < 0)
        for entry, exit_p, pnl in btc_closes[-3:]
    )
    
    eth_correct = all(
        (float(exit_p) > float(entry) and float(pnl) > 0) or
        (float(exit_p) < float(entry) and float(pnl) < 0)
        for entry, exit_p, pnl in eth_closes[-3:]
    )
    
    if btc_correct and not eth_correct:
        print("[OK] BTC: P&L calculation is CORRECT")
        print("[X] ETH: P&L calculation is WRONG")
        print()
        print("LIKELY CAUSES:")
        print("1. ETH entry price stored incorrectly when position opens")
        print("2. ETH using different code path than BTC")
        print("3. ETH 'side' field is 'sell' but should be 'buy'")
        print()
        print("SOLUTION: Check where 'side' is determined for each symbol")

print()
print("=" * 70)
print("NEXT: Find where the code branches differently for ETH vs BTC")
print("=" * 70)

