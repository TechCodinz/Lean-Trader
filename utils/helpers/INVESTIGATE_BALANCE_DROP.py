#!/usr/bin/env python3
"""
URGENT INVESTIGATION: Balance drop from $780 to $130
1. Analyze what happened
2. Find losing patterns
3. Implement intelligent position sizing
"""

import re
from datetime import datetime
from collections import defaultdict

print("="*70)
print("🚨 BALANCE DROP INVESTIGATION")
print("="*70)
print()

try:
    with open('bot.log', 'r', errors='ignore') as f:
        logs = f.read()
    
    # ========================================
    # 1. BALANCE TIMELINE
    # ========================================
    print("1️⃣ BALANCE TIMELINE:")
    print("-" * 70)
    
    balance_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?Got exchange balance: \$([0-9.]+)'
    balances = re.findall(balance_pattern, logs)
    
    if balances:
        print(f"Found {len(balances)} balance checks")
        print()
        
        # Show key points
        if len(balances) >= 2:
            first_time, first_bal = balances[0]
            peak_bal = max(float(b[1]) for b in balances)
            peak_idx = [i for i, b in enumerate(balances) if float(b[1]) == peak_bal][0]
            peak_time = balances[peak_idx][0]
            last_time, last_bal = balances[-1]
            
            print(f"Start:   {first_time} → ${float(first_bal):.2f}")
            print(f"Peak:    {peak_time} → ${peak_bal:.2f}")
            print(f"Current: {last_time} → ${float(last_bal):.2f}")
            print()
            print(f"Peak to Current: -{((peak_bal - float(last_bal))/peak_bal*100):.1f}%")
            print()
        
        # Show last 10 balances
        print("Last 10 balance checks:")
        for time, bal in balances[-10:]:
            print(f"  {time} → ${float(bal):.2f}")
    
    print()
    
    # ========================================
    # 2. TRADES AFTER PEAK
    # ========================================
    print("2️⃣ TRADES AFTER PEAK (When did it crash?):")
    print("-" * 70)
    
    # Find trades around peak
    trade_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?POSITION CLOSED: ([A-Z/]+).*?\(([+-][0-9.]+)%\)'
    all_trades = re.findall(trade_pattern, logs)
    
    if all_trades and balances:
        # Find trades after peak
        peak_time_obj = datetime.strptime(peak_time, '%Y-%m-%d %H:%M:%S')
        
        trades_after_peak = []
        for trade in all_trades:
            trade_time = datetime.strptime(trade[0], '%Y-%m-%d %H:%M:%S')
            if trade_time > peak_time_obj:
                trades_after_peak.append(trade)
        
        print(f"Found {len(trades_after_peak)} trades after peak")
        print()
        
        # Analyze losses
        big_losses = [t for t in trades_after_peak if float(t[2]) < -5]
        
        if big_losses:
            print(f" FOUND {len(big_losses)} BIG LOSSES (>5%):")
            print()
            for time, symbol, pnl in big_losses[:10]:
                print(f"  {time} | {symbol:12s} | {pnl:>7s}%")
            
            # Calculate total loss
            total_loss = sum(float(t[2]) for t in big_losses)
            print()
            print(f"Total from big losses: {total_loss:.1f}%")
        
        print()
        
        # Recent trades
        print("Last 10 trades:")
        for time, symbol, pnl in all_trades[-10:]:
            emoji = "[OK]" if float(pnl) > 0 else "[X]"
            print(f"  {emoji} {time} | {symbol:12s} | {pnl:>7s}%")
    
    print()
    
    # ========================================
    # 3. POSITION SIZING ANALYSIS
    # ========================================
    print("3️⃣ POSITION SIZING ANALYSIS:")
    print("-" * 70)
    
    # Check current position size
    size_pattern = r'Position sizing: \$([0-9.]+)'
    sizes = re.findall(size_pattern, logs)
    
    if sizes:
        sizes_float = [float(s) for s in sizes]
        avg_size = sum(sizes_float) / len(sizes_float)
        max_size = max(sizes_float)
        current_size = sizes_float[-1]
        
        print(f"Average position: ${avg_size:.2f}")
        print(f"Max position:     ${max_size:.2f}")
        print(f"Current position: ${current_size:.2f}")
        print()
        
        # Check if position size is too large
        if balances:
            current_balance = float(balances[-1][1])
            position_pct = (current_size / current_balance * 100) if current_balance > 0 else 0
            
            print(f"Current balance:  ${current_balance:.2f}")
            print(f"Position % of balance: {position_pct:.1f}%")
            print()
            
            if position_pct > 20:
                print("🚨 PROBLEM: Position size TOO LARGE!")
                print(f"   Trading ${current_size:.2f} on ${current_balance:.2f} balance ({position_pct:.1f}%)")
                print("   Should be 5-10% max!")
            elif position_pct > 10:
                print(" WARNING: Position size aggressive")
                print("   Consider reducing to 5-10%")
            else:
                print("[OK] Position size looks reasonable")
    
    print()
    
    # ========================================
    # 4. WIN/LOSS ANALYSIS
    # ========================================
    print("4️⃣ WIN/LOSS ANALYSIS:")
    print("-" * 70)
    
    if all_trades:
        wins = [t for t in all_trades if float(t[2]) > 0]
        losses = [t for t in all_trades if float(t[2]) < 0]
        
        total_trades = len(all_trades)
        win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
        
        avg_win = sum(float(t[2]) for t in wins) / len(wins) if wins else 0
        avg_loss = sum(float(t[2]) for t in losses) / len(losses) if losses else 0
        
        print(f"Total trades: {total_trades}")
        print(f"Wins:         {len(wins)} ({win_rate:.1f}%)")
        print(f"Losses:       {len(losses)}")
        print()
        print(f"Average win:  +{avg_win:.2f}%")
        print(f"Average loss: {avg_loss:.2f}%")
        print()
        
        # Risk/Reward
        if avg_loss != 0:
            risk_reward = abs(avg_win / avg_loss)
            print(f"Risk/Reward:  {risk_reward:.2f}:1")
            print()
        
        # Find worst performers
        symbol_pnl = defaultdict(list)
        for trade in all_trades:
            symbol_pnl[trade[1]].append(float(trade[2]))
        
        print("Worst performing symbols:")
        symbol_avg = {sym: sum(pnls)/len(pnls) for sym, pnls in symbol_pnl.items()}
        worst = sorted(symbol_avg.items(), key=lambda x: x[1])[:5]
        
        for symbol, avg_pnl in worst:
            count = len(symbol_pnl[symbol])
            print(f"  {symbol:12s}: {avg_pnl:>6.2f}% avg ({count} trades)")
    
    print()
    
    # ========================================
    # DIAGNOSIS
    # ========================================
    print("="*70)
    print("💡 DIAGNOSIS")
    print("="*70)
    print()
    
    if balances and len(balances) >= 2:
        peak_bal = max(float(b[1]) for b in balances)
        current_bal = float(balances[-1][1])
        drop_pct = (peak_bal - current_bal) / peak_bal * 100
        
        print(f"Balance dropped: ${peak_bal:.2f} → ${current_bal:.2f} (-{drop_pct:.1f}%)")
        print()
        
        if drop_pct > 50:
            print("🚨 CRITICAL: Major drawdown!")
            print()
            print("Likely causes:")
            print("  1. Position size too large (risking too much per trade)")
            print("  2. No stop-loss protection")
            print("  3. Trading low-quality signals")
            print("  4. Not cutting losses early enough")
            print()
            print("URGENT FIXES NEEDED:")
            print("  ✓ Reduce position size to 5% of balance")
            print("  ✓ Tighter stop-losses")
            print("  ✓ Better signal filtering")
            print("  ✓ Compound intelligently")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)

