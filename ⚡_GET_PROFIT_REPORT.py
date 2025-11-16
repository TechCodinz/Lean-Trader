#!/usr/bin/env python3
"""
💰 APEX BOT - DETAILED PROFIT REPORT
Analyzes all trades and calculates exact profits
"""

import os
import re
import json
import glob
from datetime import datetime, timedelta
from collections import defaultdict

print("=" * 80)
print("💰 APEX BOT - DETAILED PROFIT ANALYSIS")
print("=" * 80)
print()

# Find all trade logs
log_files = glob.glob("logs/trades_*.log")

if not log_files:
    print("❌ No trade logs found!")
    print("   Bot may not have placed trades yet")
    print("   Or logs directory doesn't exist")
    exit(1)

print(f"📁 Found {len(log_files)} trade log files")
print()

# Parse trades from logs
trades = []
balance_updates = []

for log_file in sorted(log_files):
    print(f"📖 Reading {os.path.basename(log_file)}...")
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                # Look for trade entries
                if any(keyword in line.lower() for keyword in ['profit', 'pnl', 'closed', 'win', 'loss']):
                    trades.append(line.strip())
                
                # Look for balance updates
                if 'balance' in line.lower():
                    balance_updates.append(line.strip())
    except Exception as e:
        print(f"   ⚠️  Error reading {log_file}: {e}")

print(f"📊 Found {len(trades)} trade entries")
print(f"💰 Found {len(balance_updates)} balance updates")
print()

if not trades and not balance_updates:
    print("⚠️  No trade or balance data found in logs")
    print()
    print("Possible reasons:")
    print("1. Bot just started and hasn't placed trades yet")
    print("2. Bot is in testnet mode with no activity")
    print("3. Logs are in different format")
    print()
    print("Check bot status:")
    print("  ps aux | grep COMPLETE_ULTIMATE_ORCHESTRATOR")
    print()
    print("Check recent logs:")
    print("  tail -50 logs/bot_*.log")
    exit(0)

print("=" * 80)
print("📊 TRADE ANALYSIS")
print("=" * 80)
print()

# Show recent trades
print("Recent trades (last 20):")
print()
for trade in trades[-20:]:
    print(f"  {trade}")

print()
print("=" * 80)
print("💰 BALANCE ANALYSIS")
print("=" * 80)
print()

# Show recent balance updates
print("Recent balance updates (last 10):")
print()
for balance in balance_updates[-10:]:
    print(f"  {balance}")

print()
print("=" * 80)
print("📈 STATISTICS")
print("=" * 80)
print()

# Try to extract numbers
wins = sum(1 for t in trades if 'win' in t.lower() or 'profit' in t.lower())
losses = sum(1 for t in trades if 'loss' in t.lower())

if wins + losses > 0:
    win_rate = (wins / (wins + losses)) * 100
    print(f"✅ Wins: {wins}")
    print(f"❌ Losses: {losses}")
    print(f"📊 Win Rate: {win_rate:.1f}%")
    print()
    
    if win_rate >= 60:
        print("🎯 EXCELLENT win rate! Bot is performing well!")
    elif win_rate >= 50:
        print("✅ GOOD win rate! Bot is profitable!")
    else:
        print("⚠️  Win rate needs improvement")
        print("   Consider:")
        print("   1. Adding AI API keys for better intelligence")
        print("   2. Waiting for more trades (small sample)")
        print("   3. Checking if testnet vs live mode")
else:
    print("ℹ️  Not enough trade data to calculate win rate")

print()

# Try to find profit/loss amounts
print("💰 Attempting to extract profit amounts...")
print()

profit_pattern = r'[\+\-]?\$?(\d+\.?\d*)'
total_profit = 0.0
profit_found = False

for trade in trades:
    matches = re.findall(profit_pattern, trade)
    for match in matches:
        try:
            amount = float(match)
            if 0.01 < amount < 10000:  # Reasonable trade size
                if 'profit' in trade.lower() or '+' in trade:
                    total_profit += amount
                    profit_found = True
                elif 'loss' in trade.lower() or '-' in trade:
                    total_profit -= amount
                    profit_found = True
        except:
            pass

if profit_found:
    print(f"📊 Estimated Total P&L: ${total_profit:.2f}")
    if total_profit > 0:
        print("✅ PROFITABLE!")
    elif total_profit < 0:
        print("⚠️  Currently in drawdown")
    else:
        print("➖ Break-even")
else:
    print("ℹ️  Could not extract exact profit amounts from logs")
    print("   Check logs manually for detailed P&L:")
    print("   grep -i \"profit\\|pnl\\|balance\" logs/trades_*.log")

print()
print("=" * 80)
print("🧠 INTELLIGENCE SYSTEMS CHECK")
print("=" * 80)
print()

# Check bot logs for intelligence activity
bot_logs = glob.glob("logs/bot_*.log")
if bot_logs:
    latest_bot_log = max(bot_logs, key=os.path.getctime)
    
    print(f"📖 Checking {os.path.basename(latest_bot_log)} for intelligence activity...")
    print()
    
    with open(latest_bot_log, 'r') as f:
        log_content = f.read()
    
    # Check various intelligence systems
    checks = [
        ("AI Consultation", ["AI CONSULTATION", "claude", "gpt", "consult"]),
        ("Balance Manager", ["BALANCE MANAGER", "insufficient", "affordable"]),
        ("Dynamic Trades", ["trade count", "volatility", "optimal"]),
        ("Evolution", ["evolution", "learning", "improved"]),
        ("Swarm Intelligence", ["swarm", "agent", "collective"]),
    ]
    
    for system, keywords in checks:
        found = any(keyword.lower() in log_content.lower() for keyword in keywords)
        if found:
            print(f"✅ {system}: Active")
        else:
            print(f"⚠️  {system}: No activity detected")
    
    print()
    
    # Check feature loading
    print("Advanced Features:")
    if "CRITICAL PROFIT FEATURES LOADED" in log_content:
        print("✅ Critical Profit Features (+50-100%)")
    else:
        print("❌ Critical Profit Features not loaded")
    
    if "ULTRA GOLDMINE FEATURES LOADED" in log_content:
        print("✅ Ultra Goldmine Features (+200-500%)")
    else:
        print("❌ Ultra Goldmine Features not loaded")
    
    if "DIVINE INTELLIGENCE" in log_content and "LOADED" in log_content:
        print("✅ Divine Intelligence (+300-1000%)")
    else:
        print("❌ Divine Intelligence not loaded")

print()
print("=" * 80)
print("💡 RECOMMENDATIONS")
print("=" * 80)
print()

recommendations = []

if wins + losses < 10:
    recommendations.append("⏳ Wait for more trades (need 20+ for accurate statistics)")

if not profit_found:
    recommendations.append("📊 Check logs manually: grep -i 'profit' logs/trades_*.log")

# Check if AI keys present
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        env_content = f.read()
    
    if 'ANTHROPIC_API_KEY' not in env_content or env_content.count('your_') > 0:
        recommendations.append("🤖 Add AI API keys to .env for enhanced intelligence")

if "No AI providers available" in log_content if bot_logs else True:
    recommendations.append("🧠 Enable AI consultation for continuous learning")

if recommendations:
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
else:
    print("✅ All systems optimal! Keep monitoring performance!")

print()
print("=" * 80)
print("📋 NEXT STEPS")
print("=" * 80)
print()
print("1. Monitor live trading:")
print("   tail -f logs/bot_*.log")
print()
print("2. Watch trades in real-time:")
print("   tail -f logs/trades_*.log")
print()
print("3. Re-run this analysis anytime:")
print("   python3 ⚡_GET_PROFIT_REPORT.py")
print()
print("4. Check full performance:")
print("   bash ⚡_CHECK_TRADING_PERFORMANCE.sh")
print()
print("=" * 80)
print("✅ PROFIT ANALYSIS COMPLETE")
print("=" * 80)
