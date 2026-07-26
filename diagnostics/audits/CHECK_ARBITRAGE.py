#!/usr/bin/env python3
"""
Check for triangular arbitrage capability and enable all pair trading
"""

import os
import glob

print("🔍 Scanning for arbitrage engines...")
print()

# Search for arbitrage-related files
arb_files = []
for pattern in ['*ARBITRAGE*.py', '*ARB*.py', '*TRIANGLE*.py']:
    arb_files.extend(glob.glob(pattern))

print("=" * 60)
print("ARBITRAGE ENGINE FILES")
print("=" * 60)
print()

if arb_files:
    print(f"Found {len(arb_files)} arbitrage-related files:")
    for f in arb_files:
        size = os.path.getsize(f)
        print(f"  ✅ {f} ({size:,} bytes)")
    print()
else:
    print("  ⚠️  No dedicated arbitrage files found")
    print()

# Check orchestrator for arbitrage mentions
print("=" * 60)
print("CHECKING ORCHESTRATOR FOR ARBITRAGE")
print("=" * 60)
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    orchestrator = f.read()

arb_keywords = [
    'arbitrage',
    'triangular',
    'cross_pair',
    'multi_leg',
    'three_way',
    'tri_arb'
]

found_arb = []
for keyword in arb_keywords:
    if keyword in orchestrator.lower():
        # Count occurrences
        count = orchestrator.lower().count(keyword)
        found_arb.append((keyword, count))

if found_arb:
    print("✅ Arbitrage features found:")
    for keyword, count in found_arb:
        print(f"   • {keyword}: {count} mentions")
    print()
else:
    print("⚠️  No arbitrage keywords found in orchestrator")
    print()

# Check for multi-pair coordination
print("=" * 60)
print("MULTI-PAIR COORDINATION")
print("=" * 60)
print()

multi_pair_indicators = [
    ('simultaneous.*position', 'Simultaneous positions'),
    ('cross.*symbol', 'Cross-symbol logic'),
    ('pair.*correlation', 'Pair correlation'),
    ('hedge', 'Hedging strategy'),
]

import re

for pattern, description in multi_pair_indicators:
    matches = re.findall(pattern, orchestrator, re.IGNORECASE)
    if matches:
        print(f"✅ {description}: Found")
    else:
        print(f"⚠️  {description}: Not found")

print()
print("=" * 60)
print("RECOMMENDATION")
print("=" * 60)
print()

if found_arb:
    print("✅ Bot HAS arbitrage capability!")
    print()
    print("This means it NEEDS multiple pairs active to:")
    print("  • Find arbitrage opportunities (BTC→ETH→USDT)")
    print("  • Execute multi-leg trades")
    print("  • Profit from price inefficiencies")
    print()
    print("Next steps:")
    print("  1. Remove ALL symbol blacklists")
    print("  2. Enable unlimited pair scanning")
    print("  3. Let arbitrage engine find opportunities")
else:
    print("⚠️  No explicit arbitrage found")
    print()
    print("But the bot can still benefit from multi-pair trading:")
    print("  • Diversification across symbols")
    print("  • Different market conditions")
    print("  • More opportunities")
    print()
    print("Next steps:")
    print("  1. Remove symbol blacklists")
    print("  2. Enable all pairs")
    print("  3. Let collective consensus find best trades")

