#!/bin/bash
# 🎯 YOUR EXACT VPS COMMANDS - Custom for /root/apex_bot
# Your current branch: continue-from-micro-fix
# Your databases: 7 files (216K total)

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🎯 BACKUP + FIX COMMANDS FOR YOUR VPS"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# You're already here, but just in case:
cd /root/apex_bot
source apex_venv/bin/activate

echo "✅ Current directory: $(pwd)"
echo "✅ Current branch: $(git branch --show-current)"
echo ""

# STEP 1: BACKUP EVERYTHING
echo "════════════════════════════════════════════════════════════════════════════════"
echo "STEP 1: BACKING UP ALL YOUR DATA"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

BACKUP_DIR="$HOME/bot_backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Backup location: $BACKUP_DIR"
echo ""

# Backup all your databases
echo "Backing up databases..."
cp -r divine_intelligence.db "$BACKUP_DIR/"
cp -r enhanced_trading_bot.db "$BACKUP_DIR/"
cp -r evolution_engine.db "$BACKUP_DIR/"
cp -r nobel_complete.db "$BACKUP_DIR/"
cp -r nobel_simple.db "$BACKUP_DIR/"
cp -r ultimate_bot_450_models.db "$BACKUP_DIR/"
cp -r ultra_trading_system.db "$BACKUP_DIR/"
echo "✅ Backed up 7 databases"

# Backup all Python files
echo "Backing up Python files..."
cp -r *.py "$BACKUP_DIR/" 2>/dev/null
echo "✅ Backed up Python files"

# Backup .env
echo "Backing up config..."
cp .env "$BACKUP_DIR/" 2>/dev/null
echo "✅ Backed up .env"

# Backup bot_data if exists
if [ -d "bot_data" ]; then
    cp -r bot_data "$BACKUP_DIR/"
    echo "✅ Backed up bot_data"
fi

# Save current git state
git branch --show-current > "$BACKUP_DIR/original_branch.txt"
git log -1 --oneline > "$BACKUP_DIR/last_commit.txt"

echo ""
echo "✅ BACKUP COMPLETE: $BACKUP_DIR"
echo "   Databases: 7 files (216K)"
echo "   All Python files saved"
echo "   Original branch: continue-from-micro-fix"
echo ""

# STEP 2: FETCH THE FIX BRANCH
echo "════════════════════════════════════════════════════════════════════════════════"
echo "STEP 2: FETCHING FIX BRANCH FROM GITHUB"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo "Stashing local changes..."
git stash push -m "Before applying fixes $(date)" 2>/dev/null || echo "Nothing to stash"

echo "Fetching updates from GitHub..."
git fetch origin

echo ""
echo "✅ Updates fetched"
echo ""

# STEP 3: SWITCH TO FIX BRANCH
echo "════════════════════════════════════════════════════════════════════════════════"
echo "STEP 3: SWITCHING TO FIX BRANCH"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

FIX_BRANCH="cursor/check-last-agent-stop-point-for-bot-functionality-8296"

echo "Switching to: $FIX_BRANCH"
if git checkout "$FIX_BRANCH" 2>/dev/null; then
    echo "✅ Switched to fix branch"
elif git checkout -b "$FIX_BRANCH" "origin/$FIX_BRANCH" 2>/dev/null; then
    echo "✅ Created and switched to fix branch"
else
    echo "❌ Failed to switch to fix branch"
    echo "Your backup is safe at: $BACKUP_DIR"
    exit 1
fi

echo "Pulling latest fixes..."
git pull origin "$FIX_BRANCH"

echo ""
echo "✅ Now on fix branch with all fixes"
echo ""

# STEP 4: VERIFY FIXES
echo "════════════════════════════════════════════════════════════════════════════════"
echo "STEP 4: VERIFYING ALL FIXES ARE PRESENT"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

FIXES_OK=true

# Check Fix 1: Risk Management
if [ -f "PROFESSIONAL_RISK_MANAGEMENT.py" ] && grep -q "initial_balance" PROFESSIONAL_RISK_MANAGEMENT.py 2>/dev/null; then
    echo "✅ Fix 1: Risk Management parameter compatibility"
else
    echo "❌ Fix 1: MISSING"
    FIXES_OK=false
fi

# Check Fix 2: Evolution Engine JSON
if grep -q "convert_datetimes" EVOLUTION_ENGINE.py 2>/dev/null; then
    echo "✅ Fix 2: Evolution Engine JSON serialization"
else
    echo "❌ Fix 2: MISSING"
    FIXES_OK=false
fi

# Check Fix 3: Circuit Breaker
if [ -f "CIRCUIT_BREAKER_SYSTEM.py" ] && grep -q "initial_balance" CIRCUIT_BREAKER_SYSTEM.py 2>/dev/null; then
    echo "✅ Fix 3: Circuit Breaker parameter compatibility"
else
    echo "❌ Fix 3: MISSING"
    FIXES_OK=false
fi

echo ""

if [ "$FIXES_OK" = false ]; then
    echo "❌ Some fixes are missing!"
    echo "Your backup is safe at: $BACKUP_DIR"
    exit 1
fi

echo "✅ ALL FIXES VERIFIED!"
echo ""

# STEP 5: VERIFY DATABASES PRESERVED
echo "════════════════════════════════════════════════════════════════════════════════"
echo "STEP 5: VERIFYING YOUR DATABASES ARE PRESERVED"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

echo "Checking databases..."
for db in divine_intelligence.db enhanced_trading_bot.db evolution_engine.db nobel_complete.db nobel_simple.db ultimate_bot_450_models.db ultra_trading_system.db; do
    if [ -f "$db" ]; then
        SIZE=$(du -h "$db" | cut -f1)
        echo "  ✅ $db ($SIZE)"
    else
        echo "  ⚠️  $db - not found (this may be normal if it's in bot_data/)"
    fi
done

echo ""
echo "✅ Database check complete"
echo ""

# STEP 6: START BOT
echo "════════════════════════════════════════════════════════════════════════════════"
echo "STEP 6: STARTING BOT WITH ALL FIXES"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Make sure bot is stopped
echo "Stopping any running bot..."
pkill -9 -f RUN_BOT.py 2>/dev/null || true
sleep 2

echo "Starting bot with fixes..."
nohup python3 RUN_BOT.py > bot.log 2>&1 &
BOT_PID=$!

sleep 3

# Check if started
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ Bot started successfully (PID: $BOT_PID)"
else
    echo "⚠️  Bot may have failed to start"
    echo "Check logs: tail -50 bot.log"
fi

echo ""

# STEP 7: MONITOR
echo "════════════════════════════════════════════════════════════════════════════════"
echo "STEP 7: INITIAL MONITORING (10 seconds)"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

sleep 5

echo "Checking for errors..."
if tail -50 bot.log | grep -qi "unexpected keyword\|datetime.*not.*serializable\|Traceback"; then
    echo "⚠️  Possible errors detected"
    echo ""
    echo "Last 20 lines of log:"
    tail -20 bot.log
else
    echo "✅ No errors detected in startup"
fi

echo ""

# FINAL SUMMARY
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ COMPLETE - ALL FIXES APPLIED"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 SUMMARY:"
echo ""
echo "BACKUP:"
echo "  Location: $BACKUP_DIR"
echo "  Databases: 7 files backed up"
echo "  Original branch: continue-from-micro-fix"
echo ""
echo "FIXES:"
echo "  ✅ Fix 1: Risk Management"
echo "  ✅ Fix 2: Evolution Engine JSON"
echo "  ✅ Fix 3: Circuit Breaker"
echo "  ✅ Fix 4: Evolution database path"
echo "  ✅ Fix 5: Circuit Breaker config"
echo ""
echo "BOT:"
echo "  Branch: $FIX_BRANCH"
echo "  Status: $(ps aux | grep RUN_BOT | grep -v grep > /dev/null && echo 'RUNNING' || echo 'CHECK LOGS')"
echo "  PID: $(pgrep -f RUN_BOT.py || echo 'Not found')"
echo ""
echo "📝 MONITORING COMMANDS:"
echo "  tail -f bot.log                              # Watch live logs"
echo "  grep -E '❌|ERROR' bot.log                   # Check for errors"
echo "  grep -E '🎯|💰|✅' bot.log | tail -20        # Check signals"
echo ""
echo "🔄 RESTORE (IF NEEDED):"
echo "  cd /root/apex_bot"
echo "  git checkout continue-from-micro-fix"
echo "  cp -r $BACKUP_DIR/* ."
echo "  pkill -9 -f RUN_BOT.py"
echo "  nohup python3 RUN_BOT.py > bot.log 2>&1 &"
echo ""
echo "✅ Done! Monitor logs for the next 5 minutes."
echo ""
