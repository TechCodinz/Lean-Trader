#!/usr/bin/env python3
"""
Quick script to check what's in the data hub
Shows signal diversity and pair distribution
"""

import sys
sys.path.insert(0, '/root/bot')

from ULTIMATE_ORCHESTRATOR import CentralDataHub

# Initialize data hub
hub = CentralDataHub()

# Get recent signals
signals = hub.get_signals(limit=200)

print(f"\n📊 DATA HUB ANALYSIS")
print(f"=" * 80)
print(f"Total signals in hub: {len(signals)}")

# Count unique symbols
symbols = [s.get('symbol') for s in signals if s.get('symbol')]
unique_symbols = list(set(symbols))

print(f"\n🎯 UNIQUE PAIRS: {len(unique_symbols)}")
print(f"Pairs: {', '.join(sorted(unique_symbols)[:20])}")
if len(unique_symbols) > 20:
    print(f"... and {len(unique_symbols) - 20} more")

# Count by strategy
strategies = {}
for s in signals:
    strat = s.get('strategy', s.get('source', 'unknown'))
    strategies[strat] = strategies.get(strat, 0) + 1

print(f"\n📈 SIGNALS BY STRATEGY:")
for strat, count in sorted(strategies.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"   {strat}: {count}")

# Count by side
sides = {}
for s in signals:
    side = s.get('side', 'unknown')
    sides[side] = sides.get(side, 0) + 1

print(f"\n🔄 SIGNALS BY SIDE:")
for side, count in sides.items():
    print(f"   {side}: {count}")

# Average confidence
confidences = [s.get('confidence', 0) for s in signals if s.get('confidence')]
if confidences:
    avg_conf = sum(confidences) / len(confidences)
    if avg_conf <= 1:
        avg_conf *= 100
    print(f"\n📊 AVERAGE CONFIDENCE: {avg_conf:.1f}%")

print(f"\n" + "=" * 80)
