#!/bin/bash
#
# 🚀 DEPLOY ALL PAIRS FIX
# Removes all hardcoded pairs, enables 1000+ pair trading
#

echo "=============================================="
echo "🔥 DEPLOYING ALL PAIRS FIX"
echo "=============================================="
echo ""

cd ~/apex_bot || exit 1

# 1. Stop bot
echo "1️⃣ Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3
echo "   ✅ Bot stopped"
echo ""

# 2. Pull latest fixes
echo "2️⃣ Pulling latest fixes..."
git pull origin continue-from-micro-fix
echo ""

# 3. Clear log
echo "3️⃣ Clearing old logs..."
> apex.log
echo "   ✅ Logs cleared"
echo ""

# 4. Start bot
echo "4️⃣ Starting bot with ALL PAIRS..."
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode live > apex.log 2>&1 &
BOT_PID=$!
echo "   ✅ Bot started (PID: $BOT_PID)"
echo ""

# 5. Wait for initialization
echo "5️⃣ Waiting 30 seconds for initialization..."
sleep 30
echo ""

# 6. Verify dynamic pairs
echo "=============================================="
echo "📊 VERIFICATION"
echo "=============================================="
echo ""

echo "🌍 Dynamic Pair Loading:"
tail -200 apex.log | grep -E "🌍|Loaded.*pairs|Fetched.*pairs|dynamic" | tail -10
echo ""

echo "💎 Enhanced Grower Status:"
tail -100 apex.log | grep -E "💎|Enhanced|Gate.io" | tail -5
echo ""

echo "⚡ Recent Executions:"
tail -50 apex.log | grep -E "EXECUTING" | tail -5
echo ""

echo "❌ Errors:"
tail -100 apex.log | grep -i "error" | tail -5
echo ""

echo "=============================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=============================================="
echo ""
echo "📊 Check how many pairs loaded:"
echo "   tail -100 apex.log | grep -E '🌍.*pairs|Loaded.*pairs'"
echo ""
echo "📈 Watch live trading:"
echo "   tail -f apex.log | grep -E '⚡|💰|🌍|💎'"
echo ""
echo "🔍 Verify no hardcoded pairs:"
echo "   tail -f apex.log | grep -vE 'BTC/USDT.*ETH/USDT.*SOL/USDT'"
echo ""
