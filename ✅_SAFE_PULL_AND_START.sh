#!/bin/bash

################################################################################
# ✅ SAFE PULL AND START - NO DESTRUCTIVE COMMANDS!
################################################################################

echo "================================================================================"
echo "✅ SAFE PULL AND START BOT"
echo "================================================================================"
echo ""

cd ~/bot || cd ~/apex_bot || { echo "❌ Bot directory not found!"; exit 1; }

# Stop bot
echo "⏸️  Stopping bot..."
pkill -f ORCHESTRATOR
sleep 3

# Fix any incomplete git operations (safe)
echo "🔧 Fixing git state (safe)..."
git merge --abort 2>/dev/null
git rebase --abort 2>/dev/null
rm -f .git/index.lock .git/HEAD.lock 2>/dev/null

# Stash local changes (preserves venv!)
echo "💾 Stashing local changes..."
git stash

# Pull latest
echo "📥 Pulling latest code..."
git pull origin continue-from-micro-fix

if [ $? -ne 0 ]; then
    echo "⚠️  Pull had conflicts, trying merge..."
    git pull --no-rebase origin continue-from-micro-fix
fi

echo "✅ Code updated!"
echo ""

# Check files
echo "🔍 Checking for critical files..."
for file in BOOTSTRAP_PROFIT_TRACKER.py ULTRA_GOLDMINE_FEATURES.py ULTRASONIC_INTEGRATION_COMPLETE.py DIVINE_INTELLIGENCE_FEATURES.py SUPREME_CONSCIOUSNESS_CORE.py; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
    fi
done

echo ""
echo "================================================================================"
echo "🚀 STARTING BOT"
echo "================================================================================"
echo ""

python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!

echo "⏳ Waiting 10 seconds..."
sleep 10

if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ BOT IS RUNNING!"
    echo ""
    echo "📊 Checking for module errors..."
    tail -50 bot.log | grep "No module named" | head -5 || echo "✅ No module errors!"
    echo ""
    echo "📝 Monitor: tail -f bot.log"
else
    echo "❌ Bot crashed!"
    echo ""
    tail -30 bot.log
fi

echo "================================================================================"
