#!/usr/bin/env python3
"""
Live monitoring to show what's actually trading
"""

import re
from collections import defaultdict

print("📊 Analyzing bot activity...")
print()

try:
    with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
        log_content = f.read()
    
    # Extract entry prices
    entries = re.findall(r'Entry: immediate @ \$(\d+\.?\d*)', log_content)
    
    # Extract position closes with symbols
    closes = re.findall(r'POSITION CLOSED: (\S+) \| Entry: \$(\d+\.?\d*) \| Exit: \$(\d+\.?\d*) \| P&L: \$(\S+) \(([^)]+)\)', log_content)
    
    print("=" * 60)
    print("ENTRY ACTIVITY")
    print("=" * 60)
    print()
    
    if entries:
        print(f"Total entries: {len(entries)}")
        
        # Group by price ranges
        price_ranges = defaultdict(int)
        for price_str in entries:
            price = float(price_str)
            if price < 1:
                price_ranges["< $1"] += 1
            elif price < 10:
                price_ranges["$1-10"] += 1
            elif price < 100:
                price_ranges["$10-100"] += 1
            elif price < 1000:
                price_ranges["$100-1000"] += 1
            elif price < 10000:
                price_ranges["$1k-10k"] += 1
            else:
                price_ranges["> $10k"] += 1
        
        print("\nPrice range distribution:")
        for range_name, count in sorted(price_ranges.items()):
            print(f"  {range_name:15s}: {count:3d} entries")
        
        # Unique prices
        unique = set(entries)
        print(f"\nUnique price points: {len(unique)}")
        print("\nSample prices:")
        for price in sorted([float(p) for p in unique])[:20]:
            print(f"  ${price:,.4f}")
    else:
        print("  No entries found yet")
    
    print()
    print("=" * 60)
    print("CLOSED POSITIONS")
    print("=" * 60)
    print()
    
    if closes:
        print(f"Total closed: {len(closes)}")
        print()
        
        wins = 0
        losses = 0
        total_pnl = 0.0
        
        print("Recent closes:")
        for symbol, entry, exit_p, pnl, pct in closes[-15:]:
            pnl_val = float(pnl.replace('$', '').replace(',', ''))
            total_pnl += pnl_val
            
            if '+' in pct:
                wins += 1
                emoji = "[OK]"
            else:
                losses += 1
                emoji = "[X]"
            
            print(f"  {emoji} {symbol:15s} Entry: ${entry:>10s} | Exit: ${exit_p:>10s} | {pct:>8s}")
        
        print()
        print(f"Win rate: {wins}/{wins+losses} = {wins/(wins+losses)*100:.1f}%")
        print(f"Total P&L: ${total_pnl:.2f}")
    else:
        print("  No closed positions yet (trades still opening)")
    
    print()
    print("=" * 60)
    
except Exception as e:
    print(f"Error: {e}")

