#!/bin/bash
# ============================================================================
# DEPLOY COMPLETE SENTIENT BEAST TO VPS
# All 40+ engines wired with REAL data fetching!
# ============================================================================

set -e  # Exit on error

echo "============================================================================"
echo "DEPLOYING COMPLETE SENTIENT TRADING BEAST"
echo "============================================================================"
echo ""
echo "🔧 Step 1: Pulling latest code..."
cd ~/bot
git fetch origin
git checkout -B micro-fix-local origin/micro-fix-local
echo "✅ Code updated!"
echo ""

echo "🔍 Step 2: Verifying dependencies..."
if python3 -c "import numpy, pandas, ccxt" 2>/dev/null; then
    echo "✅ All dependencies installed!"
else
    echo "❌ Missing dependencies - installing..."
    pip3 install numpy pandas ccxt scipy scikit-learn talib-binary
fi
echo ""

echo "🧪 Step 3: Testing orchestrator syntax..."
if python3 -m py_compile COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "✅ Syntax check PASSED!"
else
    echo "❌ Syntax check FAILED - DO NOT DEPLOY"
    exit 1
fi
echo ""

echo "🔍 Step 4: Counting engines..."
ENGINE_COUNT=$(python3 -c "
import re
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()
    async_tasks = re.findall(r'tasks\.append\(asyncio\.create_task\(', content)
    print(len(async_tasks))
")
echo "   Found $ENGINE_COUNT async engine loops!"
echo ""

echo "⚠️  Step 5: Backing up current bot..."
cp COMPLETE_ULTIMATE_ORCHESTRATOR.py COMPLETE_ULTIMATE_ORCHESTRATOR.py.backup_$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created!"
echo ""

echo "🛑 Step 6: Stopping old bot..."
pkill -9 -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "   (no bot running)"
sleep 3
echo "✅ Old bot stopped!"
echo ""

echo "🚀 Step 7: Starting COMPLETE SENTIENT BEAST..."
nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!
echo "✅ Bot started! PID: $BOT_PID"
echo ""

echo "⏳ Waiting 5 seconds for startup..."
sleep 5
echo ""

echo "📊 Step 8: Checking for errors..."
if tail -50 bot.log | grep -q "SyntaxError\|Traceback\|FATAL"; then
    echo "❌ ERRORS DETECTED:"
    tail -50 bot.log | grep -A 5 "Error\|Traceback" | head -20
    echo ""
    echo "⚠️  Bot may have issues - check bot.log"
else
    echo "✅ No critical errors detected!"
fi
echo ""

echo "👀 Showing last 30 lines (Ctrl+C to stop)..."
echo "============================================================================"
tail -f bot.log | grep --line-buffered -E "✅|❌|💎|🧠|🐝|ACTIVE|ERROR|BTC|ETH|SIGNAL"

# Keep monitoring
