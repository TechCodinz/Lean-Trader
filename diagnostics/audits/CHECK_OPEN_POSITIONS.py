#!/usr/bin/env python3
"""
Check what positions are open and why they're not closing
"""

import re
from datetime import datetime

print("🔍 Checking open positions and close logic...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Find all entries
entries = re.findall(r'Entry: immediate.*?(\S+/USDT).*?at \$([\d.]+)', log)

if entries:
    print(f"✅ Found {len(entries)} trade entries")
    print()
    
    # Group by symbol
    from collections import defaultdict
    by_symbol = defaultdict(int)
    for symbol, price in entries:
        by_symbol[symbol] += 1
    
    print("Open positions by symbol:")
    for symbol, count in sorted(by_symbol.items(), key=lambda x: -x[1]):
        print(f"  {symbol}: {count} positions")
    
    print()
else:
    print("⚠️  No trade entries found")

# Find closes
closes = re.findall(r'POSITION CLOSED: (\S+).*?P&L: \$([\d.-]+).*?\(([+-][\d.]+)%\)', log)

if closes:
    print(f"✅ Found {len(closes)} closes")
    print()
    print("Recent closes:")
    for symbol, pnl, pct in closes[-5:]:
        print(f"  {symbol}: ${pnl} ({pct}%)")
else:
    print("❌ NO CLOSES FOUND!")
    print("   This explains why balance is locked in positions")

print()
print("=" * 70)
print("CHECKING PROFIT MONITORING")
print("=" * 70)
print()

# Check if profit monitoring is active
if 'Monitoring' in log or 'monitor' in log:
    print("✅ Profit monitoring logs present")
    
    # Check for profit checks
    profit_checks = re.findall(r'P&L.*?([\d.]+)%', log)
    if profit_checks:
        print(f"   Found {len(profit_checks)} P&L checks")
        print(f"   Recent P&L values: {profit_checks[-10:]}")
    else:
        print("   ⚠️  No P&L calculation logs")
else:
    print("❌ No profit monitoring logs!")

print()

# Check for take profit / stop loss triggers
if 'take.profit' in log.lower() or 'taking profit' in log.lower():
    print("✅ Take profit logic triggered")
else:
    print("❌ Take profit NOT triggering")

if 'stop.loss' in log.lower() or 'cutting loss' in log.lower():
    print("✅ Stop loss logic present")
else:
    print("❌ Stop loss NOT triggering")

print()
print("=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print()

if len(entries) > 0 and len(closes) == 0:
    print("❌ CRITICAL BUG IDENTIFIED:")
    print()
    print("  • Trades ARE opening")
    print("  • But trades are NOT closing")
    print()
    print("LIKELY CAUSES:")
    print("  1. Profit monitoring not running")
    print("  2. Take profit threshold too high")
    print("  3. Monitor loop not checking positions")
    print("  4. Position tracking broken")
    print()
    print("IMMEDIATE FIX NEEDED:")
    print("  → Check PROFIT_MONITORING_SYSTEM.py settings")
    print("  → Check if monitor_positions() is being called")
    print("  → Lower take profit threshold for quick exits")

