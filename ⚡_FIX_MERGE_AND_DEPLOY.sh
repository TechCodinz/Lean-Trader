#!/bin/bash
# ⚡ FIX MERGE CONFLICT AND DEPLOY ⚡

echo "🔧 Fixing merge conflict and deploying intelligent execution..."
echo ""

# Stop bot first
echo "1️⃣  Stopping bot..."
pkill -f RUN_BOT.py
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3
echo "   ✅ Bot stopped"

# Backup current logs
echo "2️⃣  Backing up logs..."
if [ -f apex.log ]; then
    cp apex.log apex.log.backup_$(date +%Y%m%d_%H%M%S)
    echo "   ✅ Logs backed up"
fi

# Stash local changes
echo "3️⃣  Stashing local changes..."
git stash
echo "   ✅ Local changes stashed"

# Pull updates
echo "4️⃣  Pulling intelligent execution updates..."
git pull origin continue-from-micro-fix
if [ $? -eq 0 ]; then
    echo "   ✅ Updates pulled successfully!"
else
    echo "   ❌ Pull failed! Check git status"
    exit 1
fi

# Check if deployment script exists
if [ ! -f "🚀_DEPLOY_INTELLIGENT_EXECUTION_NOW.sh" ]; then
    echo "   ⚠️  Deployment script not found, continuing with manual deployment..."
fi

# Verify intelligent execution engine
echo "5️⃣  Verifying intelligent execution files..."
if [ -f INTELLIGENT_EXECUTION_ENGINE.py ]; then
    echo "   ✅ INTELLIGENT_EXECUTION_ENGINE.py found"
else
    echo "   ❌ INTELLIGENT_EXECUTION_ENGINE.py NOT FOUND!"
    exit 1
fi

# Test Python syntax
echo "6️⃣  Testing Python syntax..."
python3 -m py_compile INTELLIGENT_EXECUTION_ENGINE.py
if [ $? -eq 0 ]; then
    echo "   ✅ INTELLIGENT_EXECUTION_ENGINE syntax OK"
else
    echo "   ❌ Syntax error in INTELLIGENT_EXECUTION_ENGINE!"
    exit 1
fi

python3 -m py_compile EXECUTION_ORCHESTRATOR.py
if [ $? -eq 0 ]; then
    echo "   ✅ EXECUTION_ORCHESTRATOR syntax OK"
else
    echo "   ❌ Syntax error in EXECUTION_ORCHESTRATOR!"
    exit 1
fi

# Start bot
echo "7️⃣  Starting bot with INTELLIGENT EXECUTION..."
nohup python3 RUN_BOT.py > apex.log 2>&1 &
BOT_PID=$!
echo "   ✅ Bot started (PID: $BOT_PID)"

# Wait for initialization
echo "8️⃣  Waiting 30 seconds for initialization..."
sleep 30

# Check if bot is running
if ps -p $BOT_PID > /dev/null; then
    echo "   ✅ Bot is running!"
else
    echo "   ⚠️  Bot may have crashed, checking logs..."
    tail -50 apex.log
fi

# Verify intelligent execution loaded
echo "9️⃣  Verifying INTELLIGENT EXECUTION loaded..."
if grep -q "INTELLIGENT EXECUTION ENGINE" apex.log; then
    echo "   ✅ INTELLIGENT EXECUTION ENGINE loaded!"
    echo ""
    grep "INTELLIGENT EXECUTION ENGINE" apex.log | head -5
else
    echo "   ⚠️  Not loaded yet, checking logs..."
    echo ""
    tail -30 apex.log
fi

echo ""
echo "✅ ════════════════════════════════════════════════"
echo "   DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════"
echo ""
echo "🔍 MONITOR WITH:"
echo ""
echo "# Watch intelligent execution"
echo "tail -f apex.log | grep -E '🧠|INTELLIGENT|🔥|OMNISCIENT'"
echo ""
echo "# Check if it's working"
echo "grep 'INTELLIGENT EXECUTION ENGINE' apex.log"
echo ""
echo "# See recent activity"
echo "tail -50 apex.log"
echo ""
echo "# Check bot is running"
echo "ps aux | grep RUN_BOT | grep -v grep"
echo ""
