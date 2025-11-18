#!/bin/bash

################################################################################
# 🔥 PULL ALL MISSING ENGINES + RESTART BOT
################################################################################

echo "================================================================================"
echo "🔥 PULLING ALL ENGINES + RESTARTING BOT!"
echo "================================================================================"
echo ""

cd ~/bot || cd ~/apex_bot || { echo "❌ Bot directory not found!"; exit 1; }

# Stop bot
echo "⏸️  Stopping bot..."
pkill -f ORCHESTRATOR
sleep 3

# Pull with force (to get all files)
echo "📥 Pulling all files..."
git fetch --all
git reset --hard origin/continue-from-micro-fix

echo "✅ Files updated!"
echo ""

# Check for critical files
echo "🔍 Checking for critical engines..."
MISSING=""

if [ ! -f "BOOTSTRAP_PROFIT_TRACKER.py" ]; then
    echo "❌ BOOTSTRAP_PROFIT_TRACKER.py missing"
    MISSING="$MISSING bootstrap"
fi

if [ ! -f "ULTRA_GOLDMINE_FEATURES.py" ]; then
    echo "❌ ULTRA_GOLDMINE_FEATURES.py missing"
    MISSING="$MISSING goldmine"
fi

if [ ! -f "ULTRASONIC_INTEGRATION_COMPLETE.py" ]; then
    echo "❌ ULTRASONIC_INTEGRATION_COMPLETE.py missing"
    MISSING="$MISSING ultrasonic"
fi

if [ ! -f "DIVINE_INTELLIGENCE_FEATURES.py" ]; then
    echo "❌ DIVINE_INTELLIGENCE_FEATURES.py missing"
    MISSING="$MISSING divine"
fi

if [ ! -f "SUPREME_CONSCIOUSNESS_CORE.py" ]; then
    echo "❌ SUPREME_CONSCIOUSNESS_CORE.py missing"
    MISSING="$MISSING supreme"
fi

if [ -z "$MISSING" ]; then
    echo "✅ ALL ENGINE FILES PRESENT!"
else
    echo ""
    echo "⚠️  MISSING: $MISSING"
    echo "   These files are not in the repo yet"
    echo "   Bot will run with reduced features"
fi

echo ""
echo "================================================================================"
echo "🚀 STARTING BOT"
echo "================================================================================"
echo ""

# Start bot
python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!

echo "🚀 Bot started (PID: $BOT_PID)"
echo "⏳ Waiting 15 seconds..."
sleep 15

echo ""
echo "================================================================================"
echo "✅ VERIFICATION"
echo "================================================================================"
echo ""

if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ BOT IS RUNNING!"
    echo ""
    
    # Check for module errors
    echo "🔍 Checking for missing module errors..."
    ERRORS=$(tail -50 bot.log | grep -c "No module named")
    
    if [ $ERRORS -eq 0 ]; then
        echo "✅ NO MODULE ERRORS!"
    else
        echo "⚠️  Found $ERRORS module errors:"
        tail -50 bot.log | grep "No module named" | head -5
    fi
    
    echo ""
    echo "📊 Recent logs:"
    tail -20 bot.log | grep -E "Phase|Loaded|Initialized|✅" | head -10 || tail -15 bot.log
    
else
    echo "❌ BOT CRASHED!"
    echo ""
    tail -40 bot.log
    exit 1
fi

echo ""
echo "================================================================================"
echo "📝 Monitor: tail -f bot.log"
echo "================================================================================"
