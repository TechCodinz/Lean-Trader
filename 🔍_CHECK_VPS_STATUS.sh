#!/bin/bash
# 🔍 VPS STATUS CHECK - Find out what's actually running
# Run this on your VPS to see current state

echo "═══════════════════════════════════════════════════════════════"
echo "🔍 VPS STATUS CHECK"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd ~/apex_bot

echo "1️⃣  CURRENT BRANCH & RECENT COMMITS:"
echo "───────────────────────────────────────────────────────────────"
git log --oneline -10
echo ""

echo "2️⃣  BOT RUNNING STATUS:"
echo "───────────────────────────────────────────────────────────────"
ps aux | grep -E "RUN_BOT|ORCHESTRATOR" | grep -v grep
if [ $? -eq 0 ]; then
    echo "✅ Bot IS running"
else
    echo "❌ Bot NOT running"
fi
echo ""

echo "3️⃣  MONITORING LOOP IN CODE (checking if fix exists):"
echo "───────────────────────────────────────────────────────────────"
if grep -q "monitor_positions_continuously" COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "✅ Monitoring loop code EXISTS in file"
    grep -n "def monitor_positions_continuously" COMPLETE_ULTIMATE_ORCHESTRATOR.py | head -1
else
    echo "❌ Monitoring loop code NOT FOUND - needs fix!"
fi
echo ""

echo "4️⃣  MONITORING LOOP ACTIVE IN LOGS:"
echo "───────────────────────────────────────────────────────────────"
if grep -q "POSITION MONITORING LOOP STARTED" apex.log; then
    echo "✅ Monitoring loop IS running:"
    grep "POSITION MONITORING LOOP STARTED" apex.log | tail -1
else
    echo "❌ Monitoring loop NOT started - critical issue!"
fi
echo ""

echo "5️⃣  ROUTER MODE:"
echo "───────────────────────────────────────────────────────────────"
if grep -q "Router initialized in" apex.log; then
    grep "Router initialized in" apex.log | tail -1
else
    echo "⚠️  Router mode not found in logs"
fi
echo ""

echo "6️⃣  ROUTER TESTNET FILTERING:"
echo "───────────────────────────────────────────────────────────────"
if grep -q "Testnet mode: Found on testnet" apex.log; then
    echo "✅ Router IS filtering for testnet:"
    grep "Testnet mode: Found on testnet" apex.log | tail -3
else
    echo "❌ No testnet filtering found - router may route to wrong exchanges"
fi
echo ""

echo "7️⃣  TRADES EXECUTED:"
echo "───────────────────────────────────────────────────────────────"
executed_count=$(grep -c "EXECUTED\|Order ID:" apex.log)
echo "Total trades: $executed_count"
if [ $executed_count -gt 0 ]; then
    echo "Recent trades:"
    grep -E "EXECUTED|Order ID:" apex.log | tail -5
else
    echo "❌ NO TRADES EXECUTED"
fi
echo ""

echo "8️⃣  POSITIONS CLOSED:"
echo "───────────────────────────────────────────────────────────────"
closed_count=$(grep -c "POSITION CLOSED\|Take profit\|Stop loss" apex.log)
echo "Total closures: $closed_count"
if [ $closed_count -gt 0 ]; then
    echo "Recent closures:"
    grep -E "POSITION CLOSED|Take profit|Stop loss" apex.log | tail -5
else
    echo "❌ NO POSITIONS CLOSED - monitoring loop issue!"
fi
echo ""

echo "9️⃣  GIT STATUS:"
echo "───────────────────────────────────────────────────────────────"
git status -sb
echo ""

echo "🔟 LATEST ACTIVITY (last 30 lines):"
echo "───────────────────────────────────────────────────────────────"
tail -30 apex.log
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "📊 SUMMARY:"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Summary checks
monitoring_in_code=0
monitoring_running=0
router_mode=0
trades_executed=0
positions_closed=0

if grep -q "monitor_positions_continuously" COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    monitoring_in_code=1
fi

if grep -q "POSITION MONITORING LOOP STARTED" apex.log; then
    monitoring_running=1
fi

if grep -q "Router initialized in.*TESTNET" apex.log; then
    router_mode=1
fi

if [ $(grep -c "EXECUTED\|Order ID:" apex.log) -gt 0 ]; then
    trades_executed=1
fi

if [ $(grep -c "POSITION CLOSED" apex.log) -gt 0 ]; then
    positions_closed=1
fi

echo "Monitoring loop in code: $([ $monitoring_in_code -eq 1 ] && echo '✅ YES' || echo '❌ NO')"
echo "Monitoring loop running: $([ $monitoring_running -eq 1 ] && echo '✅ YES' || echo '❌ NO')"
echo "Router in testnet mode: $([ $router_mode -eq 1 ] && echo '✅ YES' || echo '⚠️  UNKNOWN')"
echo "Trades executed: $([ $trades_executed -eq 1 ] && echo '✅ YES' || echo '❌ NO')"
echo "Positions closed: $([ $positions_closed -eq 1 ] && echo '✅ YES' || echo '❌ NO')"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "🎯 RECOMMENDATION:"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ $monitoring_in_code -eq 1 ] && [ $monitoring_running -eq 1 ] && [ $positions_closed -eq 1 ]; then
    echo "✅ ALL SYSTEMS WORKING! No fixes needed!"
    echo "   - Monitoring loop exists and is running"
    echo "   - Positions are closing"
    echo "   - Bot is operational"
elif [ $monitoring_in_code -eq 0 ]; then
    echo "🚨 NEED TO PULL FIXES:"
    echo "   - Monitoring loop code missing"
    echo "   - Pull from continue-from-micro-fix branch"
elif [ $monitoring_running -eq 0 ]; then
    echo "⚠️  NEED TO RESTART BOT:"
    echo "   - Code has monitoring loop"
    echo "   - But loop not started"
    echo "   - Restart bot to activate"
else
    echo "🔍 NEED MORE INVESTIGATION:"
    echo "   - Some systems working, others not"
    echo "   - Check logs for errors"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
