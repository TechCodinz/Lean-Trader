#!/usr/bin/env python3
import re
from collections import defaultdict

def analyze_trades():
    try:
        with open('bot.log', 'r', errors='ignore') as f:  # Ignore binary errors
            logs = f.readlines()
    except:
        print("[X] Could not read log file")
        return
    
    trades = []
    symbols = defaultdict(int)
    
    for line in logs:
        if 'POSITION CLOSED' in line and 'Entry:' in line:
            match = re.search(r'POSITION CLOSED: (\S+) \| Entry: \$([0-9.]+) \| Exit: \$([0-9.]+) \| P&L: \$([0-9.]+) \(([+-][0-9.]+\.[0-9]+)%\)', line)
            if match:
                trades.append({
                    'symbol': match.group(1),
                    'entry': float(match.group(2)),
                    'exit': float(match.group(3)),
                    'pnl_pct': float(match.group(5))
                })
                symbols[match.group(1)] += 1
    
    print("="*70)
    print("📊 PROFIT ANALYSIS")
    print("="*70)
    print(f"\nTotal analyzed trades: {len(trades)}")
    
    if trades:
        profits = [t for t in trades if t['pnl_pct'] > 0]
        losses = [t for t in trades if t['pnl_pct'] < 0]
        
        print(f"\n[OK] Wins: {len(profits)} ({len(profits)/len(trades)*100:.1f}%)")
        print(f"[X] Losses: {len(losses)} ({len(losses)/len(trades)*100:.1f}%)")
        
        if profits:
            avg_win = sum(t['pnl_pct'] for t in profits) / len(profits)
            best_win = max(profits, key=lambda x: x['pnl_pct'])
            print(f"\n💚 Average Win: +{avg_win:.2f}%")
            print(f"🎯 Best Trade: {best_win['symbol']} +{best_win['pnl_pct']:.2f}%")
        
        if losses:
            avg_loss = sum(t['pnl_pct'] for t in losses) / len(losses)
            worst_loss = min(losses, key=lambda x: x['pnl_pct'])
            print(f"\n💔 Average Loss: {avg_loss:.2f}%")
            print(f"  Worst Trade: {worst_loss['symbol']} {worst_loss['pnl_pct']:.2f}%")
        
        # Most traded
        print("\n" + "="*70)
        print("🎯 MOST ACTIVE SYMBOLS (Top 10)")
        print("="*70)
        for symbol, count in sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:10]:
            sym_trades = [t for t in trades if t['symbol'] == symbol]
            sym_wins = len([t for t in sym_trades if t['pnl_pct'] > 0])
            sym_wr = sym_wins / count * 100 if count > 0 else 0
            print(f"{symbol:12} : {count:3} trades | Win rate: {sym_wr:5.1f}%")
        
        # Recommendations
        print("\n" + "="*70)
        print("💡 RECOMMENDATIONS")
        print("="*70)
        
        win_rate = len(profits) / len(trades) * 100
        
        if win_rate < 45:
            print("\n  Win rate below 45% - Actions:")
            print("   1. Increase confidence threshold")
            print("   2. Avoid BTC during high volatility")
            print("   3. Focus on alt coins with better win rate")
        elif win_rate >= 45 and win_rate < 55:
            print("\n[OK] Win rate OK (~50%) - Fine tune:")
            print("   1. Identify losing symbols and avoid them")
            print("   2. Increase position size on winning symbols")
            print("   3. Current performance is acceptable")
        else:
            print("\n🎉 Excellent win rate!")
            print("   Balance is growing - keep current settings")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    analyze_trades()
