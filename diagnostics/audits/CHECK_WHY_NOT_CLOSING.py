#!/usr/bin/env python3
"""
Check if positions are open and why they're not closing
"""

import re

print("🔍 Checking open positions and close logic...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Find all entries
entries = re.findall(r'Entry:.*?(\S+/USDT).*?at \$([\d.]+)', log)

if entries:
    print(f"✅ Found {len(entries)} trade entries")
    print()
    print("Recent entries:")
    for symbol, price in entries[-10:]:
        print(f"  {symbol} at ${price}")
else:
    print("⚠️  No trade entries found in log")

print()

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

print()
print("=" * 70)
print("CHECKING MONITORING ACTIVITY")
print("=" * 70)
print()

# Check if monitor_positions is being called
monitor_calls = re.findall(r'monitor.*position', log, re.IGNORECASE)
if monitor_calls:
    print(f"✅ Found {len(monitor_calls)} monitoring references")
else:
    print("❌ No monitoring activity in logs!")

# Check for P&L calculations
pnl_checks = re.findall(r'P&L.*?([\d.]+)%', log)
if pnl_checks:
    print(f"✅ Found {len(pnl_checks)} P&L calculations")
    print(f"   Recent P&L values: {pnl_checks[-10:]}")
else:
    print("❌ No P&L calculations found!")

# Check for close attempts
close_attempts = re.findall(r'clos.*position|taking profit|cutting loss', log, re.IGNORECASE)
if close_attempts:
    print(f"✅ Found {len(close_attempts)} close attempts")
else:
    print("❌ No close attempts found!")

print()
print("=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print()

if len(entries) > 0 and len(closes) == 0:
    print("❌ PROBLEM: Positions are OPEN but NOT closing!")
    print()
    print("Possible causes:")
    print("  1. monitor_positions() not checking P&L correctly")
    print("  2. Take profit/stop loss thresholds too high")
    print("  3. Position tracking broken (can't find open positions)")
    print("  4. Close logic not executing")
    print()
    print("NEXT: Check monitor_positions() method to see close thresholds")

