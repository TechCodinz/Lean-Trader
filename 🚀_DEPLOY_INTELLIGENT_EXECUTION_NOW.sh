#!/bin/bash
# 🧠 DEPLOY INTELLIGENT EXECUTION SYSTEM
# This activates the FULL intelligence of your bot!

echo "🧠 ═══════════════════════════════════════════════════════"
echo "   DEPLOYING INTELLIGENT EXECUTION SYSTEM"
echo "   Uses ALL 116+ Engine Intelligence!"
echo "═══════════════════════════════════════════════════════"
echo ""

# Stop existing bot
echo "1️⃣  Stopping old bot..."
pkill -f RUN_BOT.py
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3

# Backup current apex.log
echo "2️⃣  Backing up logs..."
if [ -f apex.log ]; then
    cp apex.log apex.log.before_intelligent_$(date +%Y%m%d_%H%M%S)
    echo "   ✅ Log backed up"
fi

# Pull intelligent execution
echo "3️⃣  Pulling INTELLIGENT EXECUTION..."
git fetch origin continue-from-micro-fix
git pull origin continue-from-micro-fix

# Verify files exist
echo "4️⃣  Verifying intelligent execution files..."
if [ -f INTELLIGENT_EXECUTION_ENGINE.py ]; then
    echo "   ✅ INTELLIGENT_EXECUTION_ENGINE.py found"
else
    echo "   ❌ INTELLIGENT_EXECUTION_ENGINE.py NOT FOUND!"
    exit 1
fi

if grep -q "INTELLIGENT EXECUTION ENGINE" EXECUTION_ORCHESTRATOR.py; then
    echo "   ✅ EXECUTION_ORCHESTRATOR.py has intelligent execution wired"
else
    echo "   ❌ EXECUTION_ORCHESTRATOR.py not updated!"
    exit 1
fi

# Test syntax
echo "5️⃣  Testing Python syntax..."
python3 -m py_compile INTELLIGENT_EXECUTION_ENGINE.py
if [ $? -eq 0 ]; then
    echo "   ✅ INTELLIGENT_EXECUTION_ENGINE syntax OK"
else
    echo "   ❌ INTELLIGENT_EXECUTION_ENGINE syntax error!"
    exit 1
fi

python3 -m py_compile EXECUTION_ORCHESTRATOR.py
if [ $? -eq 0 ]; then
    echo "   ✅ EXECUTION_ORCHESTRATOR syntax OK"
else
    echo "   ❌ EXECUTION_ORCHESTRATOR syntax error!"
    exit 1
fi

# Start bot with intelligent execution
echo "6️⃣  Starting bot with INTELLIGENT EXECUTION..."
nohup python3 RUN_BOT.py > apex.log 2>&1 &
BOT_PID=$!
echo "   ✅ Bot started (PID: $BOT_PID)"

# Wait for initialization
echo "7️⃣  Waiting for initialization (30 seconds)..."
sleep 30

# Check if bot is running
if ps -p $BOT_PID > /dev/null; then
    echo "   ✅ Bot is running!"
else
    echo "   ❌ Bot crashed! Check apex.log"
    tail -50 apex.log
    exit 1
fi

# Verify intelligent execution loaded
echo "8️⃣  Verifying INTELLIGENT EXECUTION loaded..."
if grep -q "INTELLIGENT EXECUTION ENGINE loaded" apex.log; then
    echo "   ✅ INTELLIGENT EXECUTION ENGINE loaded!"
else
    echo "   ⚠️  Intelligent execution not loaded yet (may load later)"
fi

if grep -q "INTELLIGENT EXECUTION ENGINE initialized with TESTNET" apex.log; then
    echo "   ✅ INTELLIGENT ENGINE wired to TESTNET!"
else
    echo "   ⚠️  Testnet wiring not confirmed yet"
fi

# Show recent activity
echo ""
echo "9️⃣  Recent bot activity:"
echo "─────────────────────────────────────────────────────────"
tail -30 apex.log
echo "─────────────────────────────────────────────────────────"

echo ""
echo "✅ ═══════════════════════════════════════════════════════"
echo "   INTELLIGENT EXECUTION DEPLOYED!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🔍 MONITOR INTELLIGENCE:"
echo ""
echo "# Watch intelligent execution"
echo "tail -f apex.log | grep -E '🧠|INTELLIGENT'"
echo ""
echo "# See lot sizing decisions"
echo "tail -f apex.log | grep -A 5 'INTELLIGENT LOT SIZING'"
echo ""
echo "# See complete trade plans"
echo "tail -f apex.log | grep -A 10 'COMPLETE TRADE PLAN'"
echo ""
echo "# See multi-timeframe coordination"
echo "tail -f apex.log | grep 'Active TFs'"
echo ""
echo "# See session awareness"
echo "tail -f apex.log | grep -E 'Session:|london|ny|asian'"
echo ""
echo "🎯 WHAT TO EXPECT:"
echo ""
echo "OLD: Generic $10 orders"
echo "NEW: Dynamic $5-50 based on 6 intelligence factors!"
echo ""
echo "OLD: Single TP level"
echo "NEW: 3 TP levels with partial exits!"
echo ""
echo "OLD: Generic 0.5% stop"
echo "NEW: Volatility-based 2-10% stops!"
echo ""
echo "OLD: One trade per pair"
echo "NEW: Up to 5 trades (different timeframes) per pair!"
echo ""
echo "🚀 THE INTELLIGENCE IS FLOWING! 🧠✨"
echo ""
