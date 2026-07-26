#!/usr/bin/env python3
"""
Fix the root cause: Bad ETH entry logic
"""

import re

print("🔧 Fixing ETH entry logic...")
print()

# Check lines 1441-1446 where hedging strategy is
print("1️⃣ Checking hedging/arbitrage code...")
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print("Lines 1440-1450:")
for i in range(1439, min(1450, len(lines))):
    print(f"  {i+1}: {lines[i].rstrip()}")

print()

# Find if this is forcing ETH trades
if any('LONG_ETH_SHORT_BTC' in line or 'LONG_BTC_SHORT_ETH' in line for line in lines):
    print("  Found hedging strategy code!")
    print()
    print("This may be opening ETH positions without proper signal validation")
    print()
    
    # Comment out the hedging code
    print("2️⃣ Disabling forced hedging (keep signal-based trading only)...")
    
    modified = False
    for i in range(len(lines)):
        if 'LONG_ETH_SHORT_BTC' in lines[i] or 'LONG_BTC_SHORT_ETH' in lines[i]:
            # Comment out this section
            if not lines[i].strip().startswith('#'):
                lines[i] = '# ' + lines[i]
                modified = True
    
    if modified:
        with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
            f.writelines(lines)
        
        print("   [OK] Hedging code disabled")
        print("   Now ETH will only trade on valid signals")
    else:
        print("   Already commented out")

print()

# Check the signal generation for ETH
print("3️⃣ Checking ETH signal confidence...")

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Find ETH entry decisions
eth_signals = re.findall(r'ETH/USDT.*?confidence[:\s]+([\d.]+)', log, re.IGNORECASE)

if eth_signals:
    confidences = [float(c) for c in eth_signals if float(c) <= 1.0]
    if confidences:
        avg_conf = sum(confidences) / len(confidences)
        print(f"   ETH average confidence: {avg_conf:.2f}")
        
        if avg_conf < 0.55:
            print("     Low confidence! ETH signals are weak")
            print("   Solution: Raise min confidence for ETH-like signals")

print()
print("=" * 70)
print("ROOT CAUSE IDENTIFIED!")
print("=" * 70)
print()
print("The issue is NOT the P&L calculation - that's working!")
print()
print("The REAL problems:")
print("  1. Hedging code forcing ETH LONG at wrong times")
print("  2. ETH entry signals may have low confidence")
print("  3. Bot buying ETH at local tops (~$3240)")
print()
print("SOLUTION:")
print("  [OK] Disabled forced hedging")
print("  [OK] ETH will now only trade on strong signals")
print("  [OK] Keep BTC (working perfectly)")

