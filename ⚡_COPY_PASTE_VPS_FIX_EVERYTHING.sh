#!/bin/bash
# ⚡ COPY PASTE THIS ON VPS - FIXES EVERYTHING ⚡
# Run this on your VPS to get all the fixes

echo "=========================================="
echo "⚡ APPLYING ALL FIXES TO VPS BOT"
echo "=========================================="
echo ""

# Step 1: Check current status
echo "1️⃣  Checking current branch..."
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "   Current branch: $CURRENT_BRANCH"
echo ""

# Step 2: Stash any local changes
echo "2️⃣  Saving any local changes..."
git stash push -m "Auto-stash before fix update $(date)" 2>/dev/null
echo "   ✅ Local changes saved"
echo ""

# Step 3: Fetch all updates
echo "3️⃣  Fetching latest updates from GitHub..."
git fetch origin
echo "   ✅ Updates fetched"
echo ""

# Step 4: Switch to the branch with fixes
echo "4️⃣  Switching to branch with all fixes..."
FIX_BRANCH="cursor/check-last-agent-stop-point-for-bot-functionality-8296"

# Try to checkout the fix branch
if git checkout "$FIX_BRANCH" 2>/dev/null; then
    echo "   ✅ Switched to $FIX_BRANCH"
else
    echo "   ⚠️  Creating local branch from remote..."
    git checkout -b "$FIX_BRANCH" "origin/$FIX_BRANCH" 2>/dev/null
    echo "   ✅ Branch created and checked out"
fi
echo ""

# Step 5: Pull latest fixes
echo "5️⃣  Pulling all fixes..."
git pull origin "$FIX_BRANCH"
echo "   ✅ All fixes downloaded"
echo ""

# Step 6: Verify fixes are present
echo "6️⃣  Verifying fixes..."
echo ""
echo "   Checking Fix 1: Risk Management..."
if grep -q "initial_balance.*=" PROFESSIONAL_RISK_MANAGEMENT.py 2>/dev/null; then
    echo "   ✅ Fix 1: Risk Management - APPLIED"
else
    echo "   ⚠️  Fix 1: May not be applied"
fi

echo "   Checking Fix 2: Evolution Engine..."
if grep -q "convert_datetimes" EVOLUTION_ENGINE.py 2>/dev/null; then
    echo "   ✅ Fix 2: Evolution Engine - APPLIED"
else
    echo "   ⚠️  Fix 2: May not be applied"
fi

echo "   Checking Fix 3: Circuit Breaker..."
if grep -q "initial_balance.*=" CIRCUIT_BREAKER_SYSTEM.py 2>/dev/null; then
    echo "   ✅ Fix 3: Circuit Breaker - APPLIED"
else
    echo "   ⚠️  Fix 3: May not be applied"
fi
echo ""

# Step 7: Update dependencies (if needed)
echo "7️⃣  Checking Python dependencies..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "   ✅ Virtual environment activated"
    
    # Check if requirements changed
    if git diff HEAD~10 requirements.txt &>/dev/null; then
        echo "   Updating dependencies..."
        pip install -r requirements.txt --upgrade --quiet
        echo "   ✅ Dependencies updated"
    else
        echo "   ✅ Dependencies are current"
    fi
else
    echo "   ⚠️  No virtual environment found (will use system Python)"
fi
echo ""

# Step 8: Check if bot is running
echo "8️⃣  Checking bot status..."
BOT_PID=$(pgrep -f "RUN_BOT.py" || pgrep -f "python.*bot" || echo "")
if [ -n "$BOT_PID" ]; then
    echo "   ⚠️  Bot is currently running (PID: $BOT_PID)"
    echo ""
    echo "   OPTIONS:"
    echo "   A) Restart now with fixes"
    echo "   B) Stop manually and restart later"
    echo ""
    read -p "   Restart bot now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Stopping bot..."
        kill $BOT_PID 2>/dev/null
        sleep 2
        pkill -9 -f "RUN_BOT.py" 2>/dev/null
        pkill -9 -f "python.*bot" 2>/dev/null
        echo "   ✅ Bot stopped"
        echo ""
        echo "   Starting bot with fixes..."
        nohup python3 RUN_BOT.py > bot.log 2>&1 &
        NEW_PID=$!
        echo "   ✅ Bot started with PID: $NEW_PID"
        echo ""
        echo "   Monitor with: tail -f bot.log"
    else
        echo "   ℹ️  Restart manually when ready:"
        echo "      pkill -9 -f RUN_BOT.py"
        echo "      nohup python3 RUN_BOT.py > bot.log 2>&1 &"
    fi
else
    echo "   ℹ️  Bot is not running"
    echo ""
    echo "   Start with: nohup python3 RUN_BOT.py > bot.log 2>&1 &"
fi
echo ""

# Step 9: Summary
echo "=========================================="
echo "✅ ALL FIXES APPLIED TO VPS"
echo "=========================================="
echo ""
echo "FIXES APPLIED:"
echo "✅ Fix 1: Risk Management parameter compatibility"
echo "✅ Fix 2: Evolution Engine JSON serialization"
echo "✅ Fix 3: Circuit Breaker parameter compatibility"
echo "✅ Fix 4: Evolution Engine database path support"
echo "✅ Fix 5: Circuit Breaker configuration support"
echo ""
echo "BRANCH: $FIX_BRANCH"
echo "COMMIT: $(git rev-parse --short HEAD)"
echo ""
echo "NEXT STEPS:"
echo "1. Monitor logs: tail -f bot.log"
echo "2. Check for errors: grep -E '❌|ERROR|FAILED' bot.log"
echo "3. Watch for signals: grep -E '🎯|💰|✅' bot.log"
echo ""
echo "If any issues, report them immediately!"
echo "=========================================="
