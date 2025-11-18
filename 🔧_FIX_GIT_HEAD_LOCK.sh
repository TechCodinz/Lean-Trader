#!/bin/bash

################################################################################
# 🔧 FIX GIT HEAD LOCK ERROR
################################################################################

echo "================================================================================"
echo "🔧 FIXING GIT HEAD LOCK ERROR"
echo "================================================================================"
echo ""

cd ~/bot || cd ~/apex_bot || { echo "❌ Bot directory not found!"; exit 1; }

# Stop bot first
echo "⏸️  Stopping bot..."
pkill -f ORCHESTRATOR
sleep 2

# Fix git state
echo "🔧 Fixing git state..."

# Abort any incomplete operations
git merge --abort 2>/dev/null
git rebase --abort 2>/dev/null
git cherry-pick --abort 2>/dev/null

# Remove lock files if they exist
if [ -f ".git/index.lock" ]; then
    echo "   Removing .git/index.lock"
    rm -f .git/index.lock
fi

if [ -f ".git/HEAD.lock" ]; then
    echo "   Removing .git/HEAD.lock"
    rm -f .git/HEAD.lock
fi

# Reset to clean state
echo "🔄 Resetting to clean state..."
git reset --hard HEAD 2>/dev/null

# Fetch latest
echo "📥 Fetching latest..."
git fetch origin continue-from-micro-fix

# Force update to match remote
echo "🔨 Force updating to remote..."
git reset --hard origin/continue-from-micro-fix

echo ""
echo "✅ Git state fixed!"
echo ""

# Verify
echo "================================================================================"
echo "✅ VERIFICATION"
echo "================================================================================"
echo ""

echo "Current branch: $(git branch --show-current)"
echo "Last commit: $(git log -1 --oneline)"
echo ""

# Check for critical files
echo "🔍 Checking for critical files..."
FILES_FOUND=0
FILES_MISSING=0

for file in BOOTSTRAP_PROFIT_TRACKER.py ULTRA_GOLDMINE_FEATURES.py ULTRASONIC_INTEGRATION_COMPLETE.py DIVINE_INTELLIGENCE_FEATURES.py SUPREME_CONSCIOUSNESS_CORE.py; do
    if [ -f "$file" ]; then
        echo "✅ $file"
        FILES_FOUND=$((FILES_FOUND + 1))
    else
        echo "❌ $file - MISSING"
        FILES_MISSING=$((FILES_MISSING + 1))
    fi
done

echo ""
echo "Files found: $FILES_FOUND"
echo "Files missing: $FILES_MISSING"

echo ""
echo "================================================================================"
echo "🚀 NEXT STEP"
echo "================================================================================"
echo ""

if [ $FILES_MISSING -eq 0 ]; then
    echo "✅ ALL FILES PRESENT! Starting bot..."
    python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
    echo "⏳ Waiting 10 seconds..."
    sleep 10
    echo ""
    echo "📊 Checking for errors..."
    tail -30 bot.log | grep -E "No module named|ERROR" | head -5 || echo "✅ No errors!"
    echo ""
    echo "📝 Monitor: tail -f bot.log"
else
    echo "⚠️  $FILES_MISSING files still missing!"
    echo ""
    echo "These files are not in the repo yet."
    echo "Checking git history..."
    echo ""
    git log --oneline --name-only -10 | grep -E "BOOTSTRAP|GOLDMINE|ULTRASONIC|DIVINE|SUPREME" | head -10 || echo "Not found in recent commits"
    echo ""
    echo "📝 Share this output so I can add the missing files!"
fi

echo "================================================================================"
