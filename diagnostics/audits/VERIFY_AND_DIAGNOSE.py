#!/usr/bin/env python3
"""
Verify spot checking is working and diagnose trading issues
"""

import re

print("🔍 Verifying fixes and diagnosing...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Check for spot position detection
print("1️⃣ SPOT POSITION DETECTION")
print("-" * 70)
spot_detections = re.findall(r'Found spot position.*?BTC', log, re.IGNORECASE)
if spot_detections:
    print(f"   ✅ Found {len(spot_detections)} BTC spot position detections!")
    for det in spot_detections[-3:]:
        print(f"   {det[:80]}")
else:
    print("   ❌ No BTC spot position detected yet")

print()

# Check for BTC monitoring
print("2️⃣ BTC MONITORING")
print("-" * 70)
btc_monitor = re.findall(r'BTC.*?monitor|Monitoring.*?BTC|BTC.*?P&L', log, re.IGNORECASE)
if btc_monitor:
    print(f"   ✅ Found {len(btc_monitor)} BTC monitoring references")
    for ref in btc_monitor[-5:]:
        print(f"   {ref[:80]}")
else:
    print("   ⚠️  No BTC monitoring logs yet")

print()

# Check for position closes
print("3️⃣ POSITION CLOSES")
print("-" * 70)
closes = re.findall(r'POSITION CLOSED.*?BTC|BTC.*?CLOSED', log, re.IGNORECASE)
if closes:
    print(f"   ✅ Found {len(closes)} BTC closes!")
    for close in closes[-3:]:
        print(f"   {close[:80]}")
else:
    print("   ❌ No BTC closes yet")

print()

# Check balance and execution
print("4️⃣ BALANCE & EXECUTION")
print("-" * 70)
balance_refs = re.findall(r'balance.*?(\d+\.?\d*)|Balance:.*?(\d+\.?\d*)', log, re.IGNORECASE)
if balance_refs:
    # Get actual numbers
    balances = []
    for match in balance_refs:
        for val in match:
            if val and val.replace('.', '').isdigit():
                try:
                    balances.append(float(val))
                except:
                    pass
    
    if balances:
        print(f"   Recent balances: {balances[-5:]}")
        if max(balances) >= 19:
            print(f"   ✅ Balance is sufficient (${max(balances):.2f})")
        else:
            print(f"   ⚠️  Balance might be low")

# Check execution attempts
exec_errors = re.findall(r'insufficient balance|Insufficient balance', log, re.IGNORECASE)
if exec_errors:
    print(f"   ❌ Found {len(exec_errors)} 'insufficient balance' errors")
    print("   This might be blocking trades despite having $19")

print()

# Check for new trade entries
print("5️⃣ NEW TRADE ENTRIES")
print("-" * 70)
entries = re.findall(r'Entry:.*?(\S+/USDT)|executing.*?(\S+/USDT)', log, re.IGNORECASE)
if entries:
    print(f"   ✅ Found {len(entries)} trade entries")
    symbols = set()
    for entry in entries:
        for sym in entry:
            if sym:
                symbols.add(sym)
    print(f"   Symbols: {', '.join(list(symbols)[:10])}")
else:
    print("   ❌ No new trade entries")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

if len(spot_detections) == 0:
    print("❌ PROBLEM: Spot position detection not working")
    print("   BTC position exists but not being detected")
    print("   Need to check if fetch_balance() is working")

if len(closes) == 0 and len(btc_monitor) > 0:
    print("❌ PROBLEM: BTC is monitored but not closing")
    print("   P&L might not be hitting thresholds")
    print("   Or close_position() is failing")

if len(entries) == 0 and len(exec_errors) == 0:
    print("❌ PROBLEM: Bot not attempting new trades")
    print("   Despite $19 balance (enough for $1.50-$2.85 positions)")
    print("   Check if signals are being filtered out")

