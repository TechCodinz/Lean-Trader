#!/usr/bin/env python3
"""
Find exactly where the money went - $19 to $8
"""

import re
from collections import defaultdict

print("🔍 Analyzing ALL trades to find where $19 → $8...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# Find all balance mentions
balances = re.findall(r'Balance[:\s]*\$?([\d.]+)', log, re.IGNORECASE)
if balances:
    balance_vals = [float(b) for b in balances if b.replace('.', '').isdigit()]
    if balance_vals:
        print(f"Balance history:")
        print(f"  Started: ${balance_vals[0]:.2f}")
        print(f"  Highest: ${max(balance_vals):.2f}")
        print(f"  Current: ${balance_vals[-1]:.2f}")
        print(f"  Total loss: ${balance_vals[0] - balance_vals[-1]:.2f}")
        print()

# Find all closed positions
closes = re.findall(
    r'POSITION CLOSED[:\s]+(\S+).*?Entry[:\s]*\$?([\d.]+).*?Exit[:\s]*\$?([\d.]+).*?P&L[:\s]*\$?([\d.-]+).*?\(([+-][\d.]+)%\)',
    log,
    re.IGNORECASE | re.DOTALL
)

if closes:
    print(f"=" * 80)
    print(f"ALL CLOSED TRADES ({len(closes)} total)")
    print(f"=" * 80)
    print()
    
    total_pnl = 0
    wins = 0
    losses = 0
    loss_by_symbol = defaultdict(float)
    
    for symbol, entry, exit_p, pnl_dollar, pnl_pct in closes:
        try:
            pnl_val = float(pnl_dollar.replace('$', '').replace(',', ''))
            pnl_pct_val = float(pnl_pct.replace('%', '').replace('+', ''))
            total_pnl += pnl_val
            
            if pnl_pct_val > 0:
                wins += 1
                emoji = "[OK]"
            else:
                losses += 1
                emoji = "[X]"
                loss_by_symbol[symbol] += abs(pnl_val)
            
            print(f"{emoji} {symbol:12s} | Entry ${entry:>10s} | Exit ${exit_p:>10s} | P&L ${pnl_dollar:>8s} ({pnl_pct:>6s}%)")
        except:
            pass
    
    print()
    print(f"=" * 80)
    print(f"SUMMARY")
    print(f"=" * 80)
    print()
    print(f"Total trades: {len(closes)}")
    print(f"Wins: {wins} ({wins/len(closes)*100:.1f}%)")
    print(f"Losses: {losses} ({losses/len(closes)*100:.1f}%)")
    print(f"Total P&L: ${total_pnl:.2f}")
    print()
    
    if loss_by_symbol:
        print("Top losing symbols:")
        for symbol, loss in sorted(loss_by_symbol.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {symbol}: ${loss:.2f}")
    print()
    
    if total_pnl == 0:
        print("[X] CRITICAL ISSUE: Total P&L is $0.00!")
        print("   → Trades are executing but P&L not being calculated correctly")
        print("   → OR trades are closing but not recording P&L")
    elif total_pnl < 0:
        print(f"[X] CRITICAL: Total loss of ${abs(total_pnl):.2f}")
        print(f"   → {losses} losing trades vs {wins} winning trades")
else:
    print("  No closed positions found in log")
    print("   → Check if positions are being opened but not closed")
    print("   → OR if close logging is missing")

print()

# Find all trade executions
executions = re.findall(r'Trade executed.*?(\S+/USDT)', log, re.IGNORECASE)
if executions:
    print(f"Trade executions: {len(executions)}")
    symbol_counts = defaultdict(int)
    for sym in executions:
        symbol_counts[sym] += 1
    print("Most traded symbols:")
    for sym, count in sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {sym}: {count} trades")

print()

# Find position sizes
position_sizes = re.findall(r'Position size[:\s]*\$?([\d.]+)', log, re.IGNORECASE)
if position_sizes:
    sizes = [float(s) for s in position_sizes if s.replace('.', '').isdigit()]
    if sizes:
        print(f"Position sizes:")
        print(f"  Min: ${min(sizes):.2f}")
        print(f"  Max: ${max(sizes):.2f}")
        print(f"  Avg: ${sum(sizes)/len(sizes):.2f}")
        print(f"  Total: ${sum(sizes):.2f}")
        print()
        if min(sizes) < 5.0:
            print("[X] CRITICAL: Some positions are below $5 minimum!")
            print(f"   → Minimum position: ${min(sizes):.2f}")

print()

# Find errors
errors = re.findall(r'(ERROR|Error|Exception|Failed).*?(\S+/USDT)?', log, re.IGNORECASE)
if errors:
    print(f"Errors found: {len(errors)}")
    error_symbols = defaultdict(int)
    for err, sym in errors:
        if sym:
            error_symbols[sym] += 1
    if error_symbols:
        print("Symbols with errors:")
        for sym, count in sorted(error_symbols.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {sym}: {count} errors")

