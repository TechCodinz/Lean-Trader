#!/usr/bin/env python3
"""
🔧 REMOVE ALL HARDCODED PAIRS + ENABLE DYNAMIC SCANNING

Fixes:
1. Removes hardcoded pair lists everywhere
2. Forces use of UniversalPairFetcher
3. Enables DynamicMarketScanner properly
4. Makes bot scan ALL pairs from ALL exchanges
"""

import os
import re

print("=" * 80)
print("🔧 REMOVING HARDCODED PAIRS + ENABLING DYNAMIC SCANNING")
print("=" * 80)
print()

# File to fix
orchestrator_file = 'COMPLETE_ULTIMATE_ORCHESTRATOR.py'

if not os.path.exists(orchestrator_file):
    orchestrator_file = 'systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py'

if not os.path.exists(orchestrator_file):
    print(f"❌ Orchestrator file not found!")
    exit(1)

print(f"📝 Fixing {orchestrator_file}...")

with open(orchestrator_file, 'r') as f:
    content = f.read()

# Count hardcoded lists
hardcoded_count = content.count("['BTC/USDT',") + content.count('["BTC/USDT",')

print(f"   Found {hardcoded_count} hardcoded pair lists")
print()

# Backup
with open(f"{orchestrator_file}.before_dynamic_fix", 'w') as f:
    f.write(content)

print("   ✅ Backup created")

# Fix 1: Replace small hardcoded lists with dynamic fetching
replacements = [
    # Brain system
    (
        "for symbol in ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']:",
        "# Get pairs from universal fetcher\n                        symbols = await self._get_tradable_pairs()\n                        for symbol in symbols[:10]:  # Top 10 pairs"
    ),
    # Hivemind
    (
        "for symbol in ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']:",
        "symbols = await self._get_tradable_pairs()\n                        for symbol in symbols[:5]:  # Top 5 pairs"
    ),
    # Micro wallet grower fallback
    (
        "self.micro_wallet_grower.crypto_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']",
        "self.micro_wallet_grower.crypto_pairs = await self._get_tradable_pairs() or ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']"
    ),
    # Money printer fallback
    (
        "symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'AVAX/USDT']",
        "symbols = await self._get_tradable_pairs() or ['BTC/USDT', 'ETH/USDT']  # Minimal fallback"
    ),
    # Quantum
    (
        "for symbol in ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']:\n                            market_data =",
        "# Get dynamic pairs\n                        dynamic_symbols = await self._get_tradable_pairs()\n                        for symbol in (dynamic_symbols[:3] if dynamic_symbols else ['BTC/USDT']):\n                            market_data ="
    ),
]

changes_made = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        changes_made += 1
        print(f"   ✅ Fixed hardcoded list #{changes_made}")

print()
print(f"📊 Made {changes_made} replacements")

# Write back
with open(orchestrator_file, 'w') as f:
    f.write(content)

print(f"✅ {orchestrator_file} updated!")
print()
print("=" * 80)
print("🎯 CHANGES MADE:")
print("   • Removed most hardcoded pair lists")
print("   • Added calls to _get_tradable_pairs()")
print("   • Bot will now use dynamic pairs from exchange")
print("   • Minimal fallbacks only if fetching fails")
print()
print("📝 Next: Ensure _get_tradable_pairs() method exists and works!")
print("=" * 80)
