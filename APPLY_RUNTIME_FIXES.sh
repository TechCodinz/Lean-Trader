#!/bin/bash
# ============================================================================
# APPLY RUNTIME FIXES TO VPS
# Fixes 3 errors discovered during live trading
# ============================================================================

set -e

echo "============================================================================"
echo "APPLYING 3 RUNTIME FIXES"
echo "============================================================================"
echo ""

cd ~/bot

echo "🔧 Step 1: Pulling fixed code..."
git fetch origin
git checkout micro-fix-local
git pull origin micro-fix-local
echo "✅ Code updated!"
echo ""

echo "🧪 Step 2: Verifying syntax..."
if python3 -m py_compile COMPLETE_ULTIMATE_ORCHESTRATOR.py MICRO_TRADING_BOT.py; then
    echo "✅ Syntax check PASSED!"
else
    echo "❌ Syntax check FAILED - STOP"
    exit 1
fi
echo ""

echo "🛑 Step 3: Stopping bot..."
pkill -9 -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "   (no bot running)"
sleep 3
echo "✅ Bot stopped!"
echo ""

echo "🚀 Step 4: Starting fixed bot..."
nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!
echo "✅ Bot started! PID: $BOT_PID"
echo ""

echo "⏳ Waiting 5 seconds..."
sleep 5
echo ""

echo "👀 Watching for fixes..."
echo "   Looking for these to DISAPPEAR:"
echo "   ❌ MICRO WALLET ERROR: 'MICRO_GATE_BOT' object has no attribute 'crypto_pairs'"
echo "   ❌ ML Strategy Publisher error: 'CentralDataHub' object has no attribute 'get_market_data'"
echo "   ❌ Session Publisher error: object str can't be used in 'await' expression"
echo ""
echo "============================================================================"
tail -f bot.log | grep --line-buffered -E "❌|✅|💎|🧠|🐝|MICRO|ERROR|SIGNAL"
