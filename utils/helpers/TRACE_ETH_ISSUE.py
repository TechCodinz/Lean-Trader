#!/usr/bin/env python3
"""
Trace where ETH trades come from and where entry/exit get swapped
"""

import re

print("🔍 Analyzing ETH trade flow in logs...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log_lines = f.readlines()

# Find all ETH-related lines
eth_entries = []
eth_closes = []

for i, line in enumerate(log_lines):
    if 'ETH' in line:
        if 'Entry: immediate @' in line:
            price_match = re.search(r'\$(\d+\.?\d*)', line)
            if price_match:
                eth_entries.append((i+1, price_match.group(1), line.strip()))
        
        elif 'POSITION CLOSED: ETH' in line:
            # Get the full close line
            close_match = re.search(r'Entry: \$(\d+\.?\d*) \| Exit: \$(\d+\.?\d*) \| P&L.*\(([^)]+)\)', line)
            if close_match:
                entry, exit_p, pnl_pct = close_match.groups()
                eth_closes.append((i+1, entry, exit_p, pnl_pct, line.strip()))

print("=" * 70)
print("ETH ENTRY PRICES")
print("=" * 70)
print()

if eth_entries:
    print(f"Found {len(eth_entries)} ETH entries:")
    for line_num, price, full_line in eth_entries[-10:]:
        print(f"  Line {line_num}: ${price}")
    
    # Calculate entry price range
    entry_prices = [float(p) for _, p, _ in eth_entries]
    print(f"\n  Entry range: ${min(entry_prices):.2f} - ${max(entry_prices):.2f}")
    print(f"  Average: ${sum(entry_prices)/len(entry_prices):.2f}")
else:
    print("  No ETH entries found")

print()
print("=" * 70)
print("ETH POSITION CLOSES")
print("=" * 70)
print()

if eth_closes:
    print(f"Found {len(eth_closes)} ETH closes:")
    print()
    for line_num, entry, exit_p, pnl_pct, full_line in eth_closes[-5:]:
        entry_f = float(entry)
        exit_f = float(exit_p)
        actual_pnl = ((exit_f - entry_f) / entry_f) * 100
        
        print(f"  Line {line_num}:")
        print(f"    Logged: Entry ${entry} | Exit ${exit_p} | {pnl_pct}")
        print(f"    Actual: ${entry} → ${exit_p} = {actual_pnl:+.2f}%")
        
        if actual_pnl > 0 and '-' in pnl_pct:
            print(f"    [X] SWAP BUG: Profitable but shows as loss!")
        elif actual_pnl < 0 and '+' in pnl_pct:
            print(f"    [X] SWAP BUG: Loss but shows as profit!")
        else:
            print(f"    [OK] CORRECT")
        print()
else:
    print("  No ETH closes found yet")

print()
print("=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print()

if eth_closes:
    swap_count = 0
    for _, entry, exit_p, pnl_pct, _ in eth_closes:
        entry_f = float(entry)
        exit_f = float(exit_p)
        actual_pnl = ((exit_f - entry_f) / entry_f) * 100
        
        if (actual_pnl > 0 and '-' in pnl_pct) or (actual_pnl < 0 and '+' in pnl_pct):
            swap_count += 1
    
    if swap_count > 0:
        print(f"  {swap_count}/{len(eth_closes)} ETH trades have swapped entry/exit")
        print()
        print("This is a LOGGING bug, not an ETH problem!")
        print()
        print("Root cause:")
        print("  When closing positions, the code assigns:")
        print("  • entry_price = current_price (EXIT price)")
        print("  • exit_price = stored_entry (ENTRY price)")
        print()
        print("Solution:")
        print("  Find the POSITION CLOSED logging in orchestrators")
        print("  Fix the variable assignment BEFORE logging")
    else:
        print("[OK] All ETH trades logged correctly!")
else:
    print("Waiting for ETH trades to close to analyze...")

print()
print("=" * 70)
print("NEXT STEPS")
print("=" * 70)
print()
print("1. Remove ETH from TOXIC_SYMBOLS (it's a good pair!)")
print("2. Fix entry/exit assignment in close_position")
print("3. Trade ALL pairs including ETH")

