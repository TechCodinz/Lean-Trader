#!/usr/bin/env python3
"""
Diagnose why bot isn't closing with profits
"""

import re
from collections import defaultdict

print("🔍 Analyzing why no profitable closes...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Find all position closes
closes = re.findall(r'POSITION CLOSED: (\S+) \| Entry: \$([\d.]+) \| Exit: \$([\d.]+) \| P&L: \$\S+ \(([+-][\d.]+)%\) \| Reason: (\w+)', log)

print("1️⃣ CLOSE ANALYSIS")
print("=" * 70)
print()

if closes:
    profits = []
    losses = []
    reasons = defaultdict(int)
    
    for symbol, entry, exit_p, pnl_pct, reason in closes:
        pnl = float(pnl_pct)
        reasons[reason] += 1
        
        if pnl > 0:
            profits.append((symbol, entry, exit_p, pnl_pct, reason))
        else:
            losses.append((symbol, entry, exit_p, pnl_pct, reason))
    
    print(f"Total closes: {len(closes)}")
    print(f"  Profits: {len(profits)} ({len(profits)/len(closes)*100:.1f}%)")
    print(f"  Losses: {len(losses)} ({len(losses)/len(closes)*100:.1f}%)")
    print()
    
    print("Close reasons:")
    for reason, count in reasons.items():
        print(f"  {reason}: {count}")
    print()
    
    if profits:
        print("[OK] Recent PROFITABLE closes:")
        for symbol, entry, exit_p, pnl, reason in profits[-10:]:
            print(f"  {symbol}: {entry} → {exit_p} = {pnl}% ({reason})")
    else:
        print("[X] NO PROFITABLE CLOSES!")
        print("   All closes are losses!")
    
    print()
    
    if losses:
        print("Recent LOSSES:")
        for symbol, entry, exit_p, pnl, reason in losses[-10:]:
            print(f"  {symbol}: {entry} → {exit_p} = {pnl}% ({reason})")
    
    print()
    
    # Analyze the issue
    print("=" * 70)
    print("🔍 ROOT CAUSE ANALYSIS")
    print("=" * 70)
    print()
    
    if len(profits) == 0:
        print("[X] CRITICAL: Zero profitable closes!")
        print()
        
        # Check if stop-loss is too tight
        stop_losses = [r for r in reasons if 'stop' in r.lower()]
        if stop_losses:
            print("Issue 1: Stop-loss too tight (-2%)?")
            print(f"  {reasons['stop_loss']} closes hit stop-loss")
            print("  Solution: Raise stop-loss from -2% to -5%")
            print()
        
        # Check if take-profit is too high
        take_profits = [r for r in reasons if 'profit' in r.lower()]
        if len(take_profits) == 0:
            print("Issue 2: Take-profit never triggering!")
            print("  Current: 1% target")
            print("  Solution: Lower to 0.5% for faster exits")
            print()
        
        # Check if positions held too long
        print("Issue 3: May be holding losing positions")
        print("  Need to check intelligent exit logic")
        print()
    
else:
    print("  No position closes found in log yet!")
    print("   Bot may still be opening positions...")

print()

# Check 2: Are there OPEN positions waiting?
print("2️⃣ OPEN POSITIONS")
print("=" * 70)
print()

entries = re.findall(r'Entry: immediate @ \$([\d.]+)', log)
if entries:
    print(f"Total entries: {len(entries)}")
    print(f"Total closes: {len(closes) if closes else 0}")
    print(f"Potentially open: {len(entries) - (len(closes) if closes else 0)}")
    print()
    
    if len(entries) > len(closes) * 2:
        print("  Many more entries than closes!")
        print("   Positions may not be closing fast enough")
else:
    print("  No entries found")

print()

# Check 3: Profit monitoring settings
print("3️⃣ PROFIT MONITORING SETTINGS")
print("=" * 70)
print()

try:
    with open('PROFIT_MONITORING_SYSTEM.py', 'r') as f:
        profit_sys = f.read()
    
    # Find take-profit settings
    take_profit = re.findall(r'take_profit.*?=.*?([\d.]+)', profit_sys)
    stop_loss = re.findall(r'stop_loss.*?=.*?([\d.]+)', profit_sys)
    
    if take_profit:
        print(f"Take-profit targets: {take_profit[:3]}")
    if stop_loss:
        print(f"Stop-loss levels: {stop_loss[:3]}")
    
    print()
    
    if take_profit and any(float(tp) > 0.005 for tp in take_profit):
        print("  Take-profit may be too high (>0.5%)")
        print("   Most crypto moves are small, need lower targets")
    
    if stop_loss and any(float(sl) < 0.03 for sl in stop_loss):
        print("  Stop-loss may be too tight (<3%)")
        print("   Hitting stop-loss before price can recover")
    
except FileNotFoundError:
    print("  PROFIT_MONITORING_SYSTEM.py not found")

print()
print("=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print()

if closes and len(profits) == 0:
    print("🔧 URGENT FIX NEEDED:")
    print()
    print("1. Lower take-profit: 1% → 0.3% (faster profit-taking)")
    print("2. Raise stop-loss: -2% → -3% (less premature stops)")
    print("3. Check intelligent exits are working")
    print()
    print("The bot is TOO CAUTIOUS - needs to take profits faster!")
else:
    print("Monitor for 30 more minutes, then re-check")

