#!/usr/bin/env python3
"""
Check why bot isn't trading with $19 balance and why BTC isn't closing
"""

import re

print("🔍 Checking trading issues...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Check balance logs
print("1️⃣ BALANCE CHECKS")
print("-" * 70)
balances = re.findall(r'balance.*?(\d+\.?\d*)', log, re.IGNORECASE)
if balances:
    print(f"   Found {len(balances)} balance references")
    print(f"   Recent: {balances[-5:]}")
else:
    print("   ⚠️  No balance logs")

print()

# Check for BTC position monitoring
print("2️⃣ BTC POSITION MONITORING")
print("-" * 70)
btc_refs = re.findall(r'BTC.*?position|BTC.*?monitor|BTC.*?P&L', log, re.IGNORECASE)
if btc_refs:
    print(f"   ✅ Found {len(btc_refs)} BTC references")
    print(f"   Recent: {btc_refs[-5:]}")
else:
    print("   ❌ No BTC monitoring found!")

print()

# Check for "Found exchange position" (our new code)
print("3️⃣ EXCHANGE POSITION FETCHING")
print("-" * 70)
exchange_pos = re.findall(r'Found exchange position', log, re.IGNORECASE)
if exchange_pos:
    print(f"   ✅ Found {len(exchange_pos)} exchange positions detected")
else:
    print("   ❌ Exchange position fetching not working!")

print()

# Check for execution attempts
print("4️⃣ EXECUTION ATTEMPTS")
print("-" * 70)
exec_attempts = re.findall(r'execute.*signal|executing|insufficient balance', log, re.IGNORECASE)
if exec_attempts:
    print(f"   Found {len(exec_attempts)} execution references")
    # Show recent
    for attempt in exec_attempts[-10:]:
        if 'insufficient' in attempt.lower():
            print(f"   ❌ {attempt[:80]}")
        else:
            print(f"   ✅ {attempt[:80]}")
else:
    print("   ⚠️  No execution attempts found")

print()

# Check for position closes
print("5️⃣ POSITION CLOSES")
print("-" * 70)
closes = re.findall(r'POSITION CLOSED|taking profit|stop loss', log, re.IGNORECASE)
if closes:
    print(f"   ✅ Found {len(closes)} close events")
    for close in closes[-5:]:
        print(f"   {close[:80]}")
else:
    print("   ❌ NO CLOSES!")

print()
print("=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print()

if len(exchange_pos) == 0:
    print("❌ PROBLEM: Exchange position fetching not working!")
    print("   BTC position exists but bot can't find it")
    print()
    print("   This means monitor_positions() isn't seeing the BTC position")
    print("   Need to check if fetch_positions() works for spot trading")

if len(closes) == 0 and len(btc_refs) > 0:
    print("❌ PROBLEM: BTC is being monitored but not closing!")
    print("   P&L might not be hitting thresholds")
    print("   Or close_position() is failing")

if len(exec_attempts) == 0:
    print("❌ PROBLEM: Bot not attempting to execute new trades!")
    print("   Despite $19 balance (enough for $4-$7.50 positions)")

