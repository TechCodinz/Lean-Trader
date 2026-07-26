#!/usr/bin/env python3
"""
Comprehensive analysis of why balance dropped from $50 to $1.77
"""

import re
from collections import defaultdict

print("🔍 COMPREHENSIVE BALANCE DROP ANALYSIS")
print("=" * 80)
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# 1. Balance progression
print("1️⃣ BALANCE HISTORY")
print("-" * 80)

balances = re.findall(r'Balance: \$([\d.]+) free', log)

if balances:
    balance_vals = [float(b) for b in balances]
    print(f"  First recorded: ${balance_vals[0]:.2f}")
    print(f"  Highest: ${max(balance_vals):.2f}")
    print(f"  Lowest: ${min(balance_vals):.2f}")
    print(f"  Latest: ${balance_vals[-1]:.2f}")
    print(f"  Total change in this log: ${balance_vals[-1] - balance_vals[0]:.2f}")
    print()
    
    # Show key milestones
    print("  Balance milestones:")
    checkpoints = [0, len(balance_vals)//4, len(balance_vals)//2, 3*len(balance_vals)//4, -1]
    for i in checkpoints:
        print(f"    Sample {i if i >= 0 else len(balance_vals)+i}: ${balance_vals[i]:.2f}")
else:
    print("  ⚠️  No balance data found")

print()

# 2. ALL CLOSED POSITIONS with P&L
print("2️⃣ CLOSED POSITIONS P&L")
print("-" * 80)

closes = re.findall(
    r'POSITION CLOSED: (\S+).*?Entry: \$([\d.]+).*?Exit: \$([\d.]+).*?P&L: \$([\d.-]+).*?\(([+-][\d.]+)%\)',
    log
)

if closes:
    print(f"  Total closed: {len(closes)}")
    
    total_pnl = 0
    by_symbol = defaultdict(lambda: {'count': 0, 'pnl': 0, 'wins': 0, 'losses': 0})
    
    for symbol, entry, exit_p, pnl_dollar, pnl_pct in closes:
        pnl_val = float(pnl_dollar)
        pnl_pct_val = float(pnl_pct)
        
        total_pnl += pnl_val
        by_symbol[symbol]['count'] += 1
        by_symbol[symbol]['pnl'] += pnl_val
        
        if pnl_pct_val > 0:
            by_symbol[symbol]['wins'] += 1
        else:
            by_symbol[symbol]['losses'] += 1
    
    print(f"  Total P&L: ${total_pnl:.2f}")
    print()
    
    # By symbol breakdown
    print("  By symbol:")
    for symbol, stats in sorted(by_symbol.items(), key=lambda x: x[1]['pnl']):
        win_rate = stats['wins'] / stats['count'] * 100 if stats['count'] > 0 else 0
        print(f"    {symbol:12s}: {stats['count']:3d} trades, ${stats['pnl']:>8.2f}, {win_rate:.0f}% wins")
    
    print()
    
    # Show worst losses
    print("  10 WORST LOSSES:")
    sorted_closes = sorted(closes, key=lambda x: float(x[4]))
    for symbol, entry, exit_p, pnl, pct in sorted_closes[:10]:
        print(f"    ❌ {symbol:10s}: ${entry} → ${exit_p} = {pct}% (${pnl})")
    
    print()
    
    if abs(total_pnl) < 0.01:
        print("  ⚠️  WARNING: Total P&L is $0.00!")
        print("      This means trades are executing with $0 position size!")
        print("      OR P&L is not being captured properly!")
else:
    print("  ⚠️  No closed positions found in this log")

print()

# 3. OPEN POSITIONS
print("3️⃣ OPEN POSITIONS (consuming capital)")
print("-" * 80)

# Find currently open positions
open_positions = re.findall(r'Entry: immediate.*?(\S+/USDT)', log)

if open_positions:
    open_by_symbol = defaultdict(int)
    for symbol in open_positions:
        open_by_symbol[symbol] += 1
    
    print(f"  Total open: {len(open_positions)}")
    print()
    print("  By symbol:")
    for symbol, count in sorted(open_by_symbol.items(), key=lambda x: -x[1]):
        print(f"    {symbol:12s}: {count} positions")
else:
    print("  ⚠️  No open positions found")

print()

# 4. POSITION SIZES
print("4️⃣ POSITION SIZES")
print("-" * 80)

# Check for position size logs
size_logs = re.findall(r'Position size: \$([\d.]+)', log)

if size_logs:
    sizes = [float(s) for s in size_logs]
    print(f"  Total trades executed: {len(sizes)}")
    print(f"  Avg position size: ${sum(sizes)/len(sizes):.2f}")
    print(f"  Min: ${min(sizes):.2f}")
    print(f"  Max: ${max(sizes):.2f}")
    print()
    
    # Check if any are suspiciously small
    zero_sizes = sum(1 for s in sizes if s < 1)
    if zero_sizes > 0:
        print(f"  ⚠️  {zero_sizes} trades with size < $1 (essentially $0)!")
        print("      This explains why P&L shows $0.00!")
else:
    print("  ⚠️  No position size logs found")
    print("      Position sizing might not be working!")

print()

# 5. ROOT CAUSE SUMMARY
print("=" * 80)
print("ROOT CAUSE DIAGNOSIS")
print("=" * 80)
print()

if closes and abs(total_pnl) < 0.01 and balances and abs(balance_vals[-1] - balance_vals[0]) > 10:
    print("❌ CRITICAL BUG IDENTIFIED:")
    print()
    print("  • Balance dropped significantly (real trades on exchange)")
    print("  • But P&L in logs shows $0.00 (not capturing real money)")
    print()
    print("  This means:")
    print("    1. Trades ARE executing on Bybit testnet")
    print("    2. Real money IS being won/lost")
    print("    3. But position size calculation shows $0 in logs")
    print("    4. Actual position sizes on exchange are different!")
    print()
    print("  CAUSE: Position sizing code is NOT working")
    print("         Trades execute with fallback/default sizes")
    print("         But logs show $0 because calculation fails")
    print()
elif not closes:
    print("⚠️  No closed positions in current log")
    print("   Need to check if bot is actually trading")
else:
    print("✅ Logs show real P&L, can diagnose from data")

