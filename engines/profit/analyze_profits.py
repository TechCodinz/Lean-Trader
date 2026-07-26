#!/usr/bin/env python3
"""Detailed profit analysis from bot logs"""

import re
from datetime import datetime
from collections import defaultdict

def analyze_trades():
    """Extract and analyze all trades"""
    
    with open('bot.log', 'r') as f:
        logs = f.readlines()
    
    trades = []
    timeframes = defaultdict(int)
    symbols = defaultdict(int)
    
    for line in logs:
        # Find closed positions
        if 'POSITION CLOSED' in line:
            # Extract: symbol, entry, exit, P&L
            match = re.search(r'POSITION CLOSED: (\S+) \| Entry: \$([0-9.]+) \| Exit: \$([0-9.]+) \| P&L: \$([0-9.]+) \(([+-][0-9.]+\.[0-9]+)%\)', line)
            if match:
                symbol = match.group(1)
                entry = float(match.group(2))
                exit_price = float(match.group(3))
                pnl_dollar = float(match.group(4))
                pnl_pct = float(match.group(5))
                
                # Get timestamp
                timestamp = line.split(' - ')[0]
                
                trades.append({
                    'time': timestamp,
                    'symbol': symbol,
                    'entry': entry,
                    'exit': exit_price,
                    'pnl_pct': pnl_pct,
                    'pnl_dollar': pnl_dollar
                })
                
                symbols[symbol] += 1
        
        # Find timeframes
        if 'timeframe' in line.lower() and any(tf in line for tf in ['1m', '5m', '15m', '1h', '4h', '1d']):
            for tf in ['1m', '5m', '15m', '1h', '4h', '1d']:
                if tf in line:
                    timeframes[tf] += 1
    
    # Calculate stats
    print("="*60)
    print("📊 DETAILED TRADE ANALYSIS")
    print("="*60)
    print()
    
    if trades:
        print(f"Total trades closed: {len(trades)}")
        print()
        
        # Recent trades
        print("Last 10 Trades:")
        print("-" * 60)
        for i, trade in enumerate(trades[-10:], 1):
            status = "[OK] Profit" if trade['pnl_pct'] > 0 else "[X] Loss"
            print(f"{i}. {trade['time']} | {trade['symbol']}")
            print(f"   Entry: ${trade['entry']:.4f} → Exit: ${trade['exit']:.4f}")
            print(f"   {status}: {trade['pnl_pct']:+.2f}% (${trade['pnl_dollar']:.2f})")
            print()
        
        # P&L summary
        total_pnl = sum(t['pnl_dollar'] for t in trades)
        profits = [t for t in trades if t['pnl_pct'] > 0]
        losses = [t for t in trades if t['pnl_pct'] < 0]
        
        print("="*60)
        print("💰 P&L SUMMARY")
        print("="*60)
        print(f"Total P&L: ${total_pnl:.2f}")
        print(f"Winning trades: {len(profits)} ({len(profits)/len(trades)*100:.1f}%)")
        print(f"Losing trades: {len(losses)} ({len(losses)/len(trades)*100:.1f}%)")
        
        if profits:
            avg_profit = sum(t['pnl_pct'] for t in profits) / len(profits)
            print(f"Average profit: +{avg_profit:.2f}%")
        
        if losses:
            avg_loss = sum(t['pnl_pct'] for t in losses) / len(losses)
            print(f"Average loss: {avg_loss:.2f}%")
        
        print()
        
        # Most traded symbols
        print("="*60)
        print("🎯 MOST ACTIVE SYMBOLS")
        print("="*60)
        for symbol, count in sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{symbol}: {count} trades")
        print()
    
    else:
        print(" No closed trades found in logs")
        print()
    
    # Timeframe analysis
    if timeframes:
        print("="*60)
        print("⏱️  TIMEFRAME DISTRIBUTION")
        print("="*60)
        total_tf = sum(timeframes.values())
        for tf, count in sorted(timeframes.items(), key=lambda x: x[1], reverse=True):
            pct = count / total_tf * 100 if total_tf > 0 else 0
            print(f"{tf:>4}: {count:>3} trades ({pct:>5.1f}%)")
        print()
    
    # Recommendations
    print("="*60)
    print("💡 RECOMMENDATIONS")
    print("="*60)
    
    if trades:
        win_rate = len(profits) / len(trades) * 100 if trades else 0
        
        if win_rate < 50:
            print(" Win rate below 50% - Consider:")
            print("   • Higher confidence thresholds")
            print("   • Better entry timing")
            print("   • Review losing patterns")
        
        if total_pnl < 0:
            print(" Negative P&L - Consider:")
            print("   • Reducing position size")
            print("   • Tighter stop losses")
            print("   • Focus on higher timeframes")
        
        if len(trades) < 5:
            print("ℹ️ Limited data - Need more trades for analysis")
            print("   • Let bot run longer (6-12 hours)")
            print("   • Then reassess performance")
        
        if win_rate > 60 and total_pnl > 0:
            print("[OK] Good performance!")
            print("   • Win rate: {:.1f}%".format(win_rate))
            print("   • Profit: ${:.2f}".format(total_pnl))
            print("   • Can consider increasing position size")
    
    print("="*60)

if __name__ == '__main__':
    analyze_trades()
