#!/bin/bash
##############################################################################
# ⚡ FIX GIT MERGE AND DEPLOY
# Handles merge conflicts and deploys complete system
##############################################################################

echo "⚡ Fixing Git merge and deploying complete system..."

# 1. Kill any stopped jobs
echo "1️⃣ Killing stopped jobs..."
jobs -l
kill %1 %2 %3 %4 2>/dev/null
echo "✅ Cleared stopped jobs"

# 2. Abort current merge
echo ""
echo "2️⃣ Aborting current merge..."
git merge --abort 2>/dev/null
echo "✅ Merge aborted"

# 3. Stash local changes
echo ""
echo "3️⃣ Stashing local changes..."
git stash
echo "✅ Local changes stashed"

# 4. Force pull with rebase
echo ""
echo "4️⃣ Pulling with rebase..."
git pull --rebase origin continue-from-micro-fix
if [ $? -eq 0 ]; then
    echo "✅ Pull successful!"
else
    echo "❌ Pull failed! Trying hard reset..."
    git fetch origin continue-from-micro-fix
    git reset --hard origin/continue-from-micro-fix
    echo "✅ Hard reset complete"
fi

# 5. Stop old bot
echo ""
echo "5️⃣ Stopping old bot..."
pkill -f RUN_BOT
sleep 2
echo "✅ Bot stopped"

# 6. Start new bot
echo ""
echo "6️⃣ Starting bot with COMPLETE SYSTEM..."
nohup python3 RUN_BOT.py > apex.log 2>&1 &
BOT_PID=$!
echo "✅ Bot started (PID: $BOT_PID)"

# 7. Wait for initialization
echo ""
echo "7️⃣ Waiting 60 seconds for full initialization..."
sleep 60

# 8. Check if running
echo ""
echo "8️⃣ Checking bot status..."
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is RUNNING!"
else
    echo "❌ Bot died - checking logs..."
    tail -50 apex.log
    exit 1
fi

# 9. Check for router
echo ""
echo "9️⃣ Checking INTELLIGENT ROUTER..."
if grep -q "INTELLIGENT EXCHANGE ROUTER" apex.log; then
    echo "✅ ROUTER ACTIVE!"
    grep "INTELLIGENT.*ROUTER\|Discover\|pairs" apex.log | tail -10
else
    echo "⚠️ Router not found (may not be wired in yet)"
fi

# 10. Check for trades
echo ""
echo "🔟 Checking for trade activity..."
if grep -q "TESTNET" apex.log; then
    echo "✅ TESTNET active!"
fi

if grep -q "EXECUTED" apex.log; then
    echo "✅ TRADES executing!"
    grep "EXECUTED" apex.log | tail -3
else
    echo "⏳ No trades yet (waiting for signals)"
fi

echo ""
echo "✅ ═══════════════════════════════════════════════════════"
echo ""
echo "   DEPLOYMENT COMPLETE!"
echo ""
echo "════════════════════════════════════════════════════════="
echo ""
echo "🔍 MONITOR:"
echo ""
echo "# Watch router"
echo "tail -f apex.log | grep -E '🧠|ROUTER|Routed'"
echo ""
echo "# Watch trades"
echo "tail -f apex.log | grep -E 'EXECUTED|Order ID'"
echo ""
echo "# Watch profits"
echo "tail -f apex.log | grep -E 'P&L|Profit'"
echo ""
echo "════════════════════════════════════════════════════════="
