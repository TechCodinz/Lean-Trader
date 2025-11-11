#!/bin/bash
cd ~/apex_bot

echo "1. Removing git lock..."
rm -f .git/index.lock
echo "   ✅ Lock removed"
echo ""

echo "2. Pulling ALL fixes..."
git pull origin continue-from-micro-fix
echo ""

echo "3. Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3
echo "   ✅ Stopped"
echo ""

echo "4. Clearing log..."
> apex.log
echo "   ✅ Cleared"
echo ""

echo "5. Starting bot with NEW CODE..."
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode live > apex.log 2>&1 &
echo "   ✅ Started (PID: $!)"
echo ""

echo "6. Waiting 35 seconds for full initialization..."
sleep 35
echo ""

echo "========================================"
echo "📊 CHECKING DYNAMIC PAIRS"
echo "========================================"
echo ""

echo "🌍 Pair Loading Messages:"
tail -200 apex.log | grep -E "🌍|Loaded.*pairs|Fetched.*pairs|dynamic" | head -15
echo ""

echo "⚠️  Old Hardcoded Pairs (should be EMPTY):"
tail -200 apex.log | grep -E "BTC/USDT.*ETH/USDT.*SOL/USDT.*BNB/USDT" | head -5
echo ""

echo "⚡ Recent Executions:"
tail -100 apex.log | grep "EXECUTING" | tail -10
echo ""

echo "💎 Enhanced Grower:"
tail -100 apex.log | grep -E "💎|Enhanced|Balance.*\$" | tail -5
echo ""

echo "❌ Any Errors:"
tail -100 apex.log | grep -i "error" | tail -5
echo ""

echo "========================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "========================================"
