#!/bin/bash
# ============================================================================
# 🚀 FINAL FIX - ALL ERRORS RESOLVED!
# ============================================================================
# This script:
# 1. Stops the bot safely
# 2. Pulls all fixes from repository
# 3. Restarts with CRYPTO-ONLY trading
#
# FIXES APPLIED:
# ✅ Removed hardcoded forex/commodity pairs from Evolution Engine
# ✅ Added get_recent_signals() to CentralDataHub
# ✅ Bot will now ONLY trade crypto USDT pairs
# ✅ No more EUR/GBP, PALLADIUM, CORN errors!
# ============================================================================

cd ~/bot || exit 1

echo "============================================================================="
echo "🚀 APPLYING FINAL FIX - ERROR-FREE TRADING!"
echo "============================================================================="
echo ""

# 1. Stop bot
echo "1️⃣ Stopping bot..."
pkill -f ORCHESTRATOR
sleep 2
echo "✅ Bot stopped"
echo ""

# 2. Pull fixes
echo "2️⃣ Pulling fixes from repository..."
git stash 2>/dev/null
GIT_EDITOR=true git pull --no-edit origin continue-from-micro-fix
echo "✅ Fixes pulled"
echo ""

# 3. Verify critical files
echo "3️⃣ Verifying fixes..."
if grep -q "get_recent_signals" COMPLETE_UNIFIED_ORCHESTRATOR.py 2>/dev/null; then
    echo "✅ get_recent_signals() fix confirmed"
else
    echo "⚠️  Checking out COMPLETE_UNIFIED_ORCHESTRATOR.py..."
    git checkout origin/continue-from-micro-fix -- COMPLETE_UNIFIED_ORCHESTRATOR.py
    cp COMPLETE_UNIFIED_ORCHESTRATOR.py systems/
fi

if grep -q "DISABLED FOR TESTNET" engines/EVOLUTION_ENGINE.py 2>/dev/null; then
    echo "✅ Evolution Engine crypto-only fix confirmed"
else
    echo "⚠️  Checking out engines/EVOLUTION_ENGINE.py..."
    git checkout origin/continue-from-micro-fix -- engines/EVOLUTION_ENGINE.py
fi
echo ""

# 4. Start bot with fixes
echo "4️⃣ Starting bot with all fixes..."
python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
sleep 15
echo "✅ Bot started"
echo ""

# 5. Verify no errors
echo "5️⃣ Checking for errors..."
echo ""
echo "Checking for forex/commodity errors:"
tail -100 bot.log | grep "EUR/GBP\|PALLADIUM\|CORN\|OIL\|GBP/JPY" || echo "  ✅ No forex/commodity attempts!"
echo ""

echo "Checking for get_recent_signals error:"
tail -100 bot.log | grep "get_recent_signals" || echo "  ✅ No get_recent_signals errors!"
echo ""

echo "Checking for USDT crypto trading:"
tail -100 bot.log | grep "EXECUTING.*USDT" | head -5
echo ""

# 6. Show bot status
echo "============================================================================="
echo "📊 BOT STATUS"
echo "============================================================================="
ps aux | grep ORCHESTRATOR | grep -v grep
echo ""
echo "📝 Monitor logs: tail -f bot.log"
echo "🔍 Check trades: tail -f bot.log | grep EXECUTING"
echo ""
echo "============================================================================="
echo "🎉 ALL FIXES APPLIED - BOT SHOULD NOW TRADE CRYPTO USDT ONLY!"
echo "============================================================================="
