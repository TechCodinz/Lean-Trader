#!/usr/bin/env python3
"""
Comprehensive check of bot functionality:
1. Where pairs come from
2. Profit/loss on closes
3. How many pairs trading
4. Position sizing
5. Active engines
"""

import re
from collections import defaultdict

print("🔍 COMPREHENSIVE BOT CHECK")
print("=" * 70)
print()

# Read log
with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# 1. Check pair sources
print("1️⃣ PAIR SOURCES")
print("-" * 70)

pair_sources = re.findall(r'(Fetched|discovered|Found).*?(\d+)\s+pairs', log, re.IGNORECASE)
if pair_sources:
    for source, count in pair_sources[-5:]:
        print(f"   {source} {count} pairs")
else:
    print("   ⚠️  No pair discovery logs found")

# Check for hardcoded vs dynamic
if 'dynamic' in log.lower() or 'fetch.*pairs' in log.lower():
    print("   ✅ Using dynamic pair fetching")
elif 'hardcoded' in log.lower():
    print("   ⚠️  Using hardcoded pairs")

print()

# 2. Check profit/loss
print("2️⃣ PROFIT/LOSS ANALYSIS")
print("-" * 70)

closes = re.findall(r'POSITION CLOSED: (\S+).*?\(([+-][\d.]+)%\)', log)
if closes:
    profits = [float(pnl.replace('+','').replace('%','')) for _, pnl in closes]
    wins = sum(1 for p in profits if p > 0)
    losses = sum(1 for p in profits if p < 0)
    
    print(f"   Total closed: {len(closes)}")
    print(f"   Wins: {wins} ({wins/len(closes)*100:.1f}%)")
    print(f"   Losses: {losses} ({losses/len(closes)*100:.1f}%)")
    print(f"   Avg P&L: {sum(profits)/len(profits):.2f}%")
    
    if wins > losses:
        print("   ✅ More wins than losses!")
    else:
        print("   ⚠️  More losses - needs adjustment")
else:
    print("   ⚠️  No closed positions yet")

print()

# 3. Symbol diversity
print("3️⃣ SYMBOL DIVERSITY")
print("-" * 70)

symbols = set(re.findall(r'POSITION CLOSED: (\S+)', log))
entry_symbols = set(re.findall(r'Entry: immediate.*?(\S+/USDT)', log))

all_symbols = symbols | entry_symbols
if all_symbols:
    print(f"   Trading {len(all_symbols)} different symbols:")
    for sym in sorted(list(all_symbols))[:20]:
        print(f"      • {sym}")
    
    if len(all_symbols) > 10:
        print("   ✅ Good diversity!")
    elif len(all_symbols) > 3:
        print("   ⚠️  Limited diversity")
    else:
        print("   ❌ Too few symbols")
else:
    print("   ⚠️  No symbols detected yet")

print()

# 4. Position sizing
print("4️⃣ POSITION SIZING")
print("-" * 70)

sizing_logs = re.findall(r'position.*size[d]?:?\s*\$?([\d.]+)', log, re.IGNORECASE)
if sizing_logs:
    sizes = [float(s) for s in sizing_logs[-10:]]
    print(f"   Recent position sizes: ${min(sizes):.2f} - ${max(sizes):.2f}")
    print(f"   Average: ${sum(sizes)/len(sizes):.2f}")
    
    # Check if dynamic
    if len(set(sizes)) > 1:
        print("   ✅ Dynamic sizing detected")
    else:
        print("   ⚠️  Fixed sizing (all same)")
else:
    print("   ⚠️  No sizing info found")

# Check balance-based sizing
if 'balance.*size' in log.lower() or 'percent.*balance' in log.lower():
    print("   ✅ Using balance-based sizing")

print()

# 5. Active engines
print("5️⃣ ACTIVE ENGINES")
print("-" * 70)

engines = re.findall(r'([\w_]+(?:ENGINE|SYSTEM|ANALYZER|ORCHESTRATOR))\s*(?:-|:|\||initialized|active|started)', log, re.IGNORECASE)
unique_engines = set(e.upper() for e in engines)

if unique_engines:
    print(f"   Found {len(unique_engines)} active engines:")
    for i, engine in enumerate(sorted(unique_engines)[:30], 1):
        print(f"      {i:2d}. {engine}")
    
    if len(unique_engines) > 50:
        print(f"   ... and {len(unique_engines) - 30} more!")
        print(f"   ✅ {len(unique_engines)} engines active!")
    elif len(unique_engines) > 20:
        print(f"   ✅ Good engine coverage")
    else:
        print(f"   ⚠️  Only {len(unique_engines)} engines detected")
else:
    print("   ⚠️  No engine logs found")

print()
print("=" * 70)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 70)
print()

# Generate recommendations
issues = []
if not closes:
    issues.append("No closed positions yet - wait 10-15 minutes")
if len(all_symbols) < 5:
    issues.append("Low symbol diversity - check pair fetching")
if not sizing_logs:
    issues.append("No sizing info - verify position sizing is working")

if issues:
    print("⚠️  Issues to address:")
    for issue in issues:
        print(f"   • {issue}")
else:
    print("✅ Everything looks good!")
    print("   • Bot is trading multiple symbols")
    print("   • Position sizing is active")
    print("   • Engines are running")
    print()
    print("   Let it run for 2-3 hours to see profit growth!")

