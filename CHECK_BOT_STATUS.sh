#!/bin/bash
# Quick bot status checker

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  🔍 BOT STATUS CHECK                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

cd ~/apex_bot

echo "📊 UNIQUE PAIRS BEING TRADED:"
grep -a "Decision:" apex_bot.log | tail -200 | grep -oE "[A-Z0-9]+/USDT" | sort -u | wc -l
echo ""

echo "💰 CURRENT BALANCE:"
grep -a "balance:" apex_bot.log | tail -3
echo ""

echo "📈 OPEN POSITIONS:"
grep -a "MONITORING\|positions open" apex_bot.log | tail -5
echo ""

echo "✅ SUCCESSFUL TRADES (last 10):"
grep -a "ORDER EXECUTED\|CLOSED.*profit" apex_bot.log | tail -10
echo ""

echo "❌ FAILED TRADES (last 10):"
grep -a "execution failed\|ERROR.*trade\|BALANCE_NOT_ENOUGH" apex_bot.log | tail -10
echo ""

echo "🎯 RECENT DECISIONS (last 20 unique pairs):"
grep -a "Decision:" apex_bot.log | tail -50 | grep -oE "Decision: [A-Z]+ [A-Z0-9]+/USDT" | tail -20
echo ""

echo "💸 P&L SUMMARY:"
grep -a "P&L\|profit\|loss" apex_bot.log | tail -10
echo ""

echo "🔄 BOT STATUS:"
ps aux | grep COMPLETE_ULTIMATE_ORCHESTRATOR | grep -v grep
echo ""
