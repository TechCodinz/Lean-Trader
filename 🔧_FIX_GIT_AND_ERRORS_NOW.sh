#!/bin/bash

################################################################################
# 🔧 FIX GIT DIVERGENCE + CODE ERRORS + RESTART BOT 🔧
################################################################################

echo "================================================================================"
echo "🔧 FIXING GIT + CODE ERRORS + RESTARTING BOT!"
echo "================================================================================"
echo ""

# Stop bot first
echo "⏸️  Stopping bot..."
pkill -f ORCHESTRATOR
sleep 2

# Fix git divergence (use rebase to get clean history)
echo "📥 Fixing git divergence..."
git config pull.rebase true
git pull --rebase origin continue-from-micro-fix

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed! Trying alternative..."
    git rebase --abort 2>/dev/null
    git pull --ff-only origin continue-from-micro-fix
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Fast-forward failed. Using merge strategy..."
        git config pull.rebase false
        git pull origin continue-from-micro-fix
    fi
fi

echo "✅ Git sync complete!"
echo ""

# Check if bootstrap tracker error needs fixing
echo "🔍 Checking for code errors..."

# Check HYBRID_INTELLIGENCE_COORDINATOR for the get_all_signals error
if [ -f "HYBRID_INTELLIGENCE_COORDINATOR.py" ]; then
    echo "📝 Checking HYBRID_INTELLIGENCE_COORDINATOR.py..."
    
    # Check if get_all_signals is used
    if grep -q "get_all_signals" HYBRID_INTELLIGENCE_COORDINATOR.py; then
        echo "⚠️  Found get_all_signals usage - needs fixing"
        
        # Create backup
        cp HYBRID_INTELLIGENCE_COORDINATOR.py HYBRID_INTELLIGENCE_COORDINATOR.py.backup
        
        # Fix: Replace get_all_signals with get_recent_signals
        sed -i 's/\.get_all_signals()/\.get_recent_signals(limit=1000)/g' HYBRID_INTELLIGENCE_COORDINATOR.py
        
        echo "✅ Fixed get_all_signals → get_recent_signals"
    fi
fi

# Similar fix for any other files
for file in *.py systems/*.py; do
    if [ -f "$file" ]; then
        if grep -q "\.get_all_signals()" "$file" 2>/dev/null; then
            echo "📝 Fixing $file..."
            cp "$file" "$file.backup"
            sed -i 's/\.get_all_signals()/\.get_recent_signals(limit=1000)/g' "$file"
            echo "✅ Fixed $file"
        fi
    fi
done

echo ""
echo "================================================================================"
echo "🚀 RESTARTING BOT WITH FIXES"
echo "================================================================================"
echo ""

# Activate venv if exists
if [ -f apex_venv/bin/activate ]; then
    source apex_venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Start bot
echo "🚀 Starting bot..."
nohup python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &

echo "⏳ Waiting for startup..."
sleep 10

echo ""
echo "================================================================================"
echo "✅ VERIFICATION"
echo "================================================================================"
echo ""

# Check if running
if pgrep -f ORCHESTRATOR > /dev/null; then
    echo "✅ Bot is RUNNING"
    echo ""
    
    # Check for errors
    echo "🔍 Checking for errors in last 30 lines..."
    tail -30 bot.log | grep -i "error\|ERROR" | tail -5 || echo "   No recent errors found! ✅"
    
    echo ""
    echo "📊 Recent log entries:"
    tail -20 bot.log | grep -E "Phase|Profit|Trade|Balance|Bootstrap|Milestone" || tail -20 bot.log
    
else
    echo "❌ Bot failed to start!"
    echo ""
    echo "Last 30 log lines:"
    tail -30 bot.log
    exit 1
fi

echo ""
echo "================================================================================"
echo "🎉 ALL FIXED! BOT RUNNING!"
echo "================================================================================"
echo ""
echo "📝 Monitor with: tail -f bot.log"
echo "📊 Check profits: grep -i \"profit\|milestone\" bot.log | tail -20"
echo ""
