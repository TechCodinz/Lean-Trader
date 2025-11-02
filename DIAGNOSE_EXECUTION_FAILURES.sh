#!/bin/bash
# Diagnose why all trade executions are failing

echo "╔══════════════════════════════════════════════════════════╗"
echo "║           🔍 EXECUTION FAILURE DIAGNOSIS                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

cd ~/apex_bot

echo "💰 CURRENT BALANCE:"
grep -a "Gate.io balance:\|Binance balance:" apex_bot.log | tail -3
echo ""

echo "❌ DETAILED FAILURE REASONS (last 20):"
grep -aB2 -A2 "Trade execution failed" apex_bot.log | tail -80
echo ""

echo "🔧 EXECUTION ERRORS WITH CONTEXT (last 20):"
grep -a "ERROR.*EXECUTION\|ERROR.*order\|ERROR.*trade\|gate.*ERROR\|InvalidOrder\|InsufficientFunds\|BALANCE_NOT_ENOUGH\|too small\|minimum" apex_bot.log | tail -20
echo ""

echo "💸 RECENT EXECUTION ATTEMPTS:"
grep -a "EXECUTING:" apex_bot.log | tail -10
echo ""

echo "📊 POSITION SIZER LOGS:"
grep -a "Position size\|Sizing\|allocated\|risk" apex_bot.log | tail -15
echo ""

echo "🎯 EXCHANGE ROUTING:"
grep -a "Routing to\|exchange.*gateio\|exchange.*binance\|Using exchange" apex_bot.log | tail -10
echo ""

echo "⚠️ ALL ERROR TYPES (last 20):"
grep -a "ERROR" apex_bot.log | tail -20
echo ""
