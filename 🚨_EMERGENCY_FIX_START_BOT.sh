#!/bin/bash

################################################################################
# 🚨 EMERGENCY FIX - START BOT WITH ALL FIXES
################################################################################

echo "================================================================================"
echo "🚨 EMERGENCY FIX - STARTING BOT WITH ALL CRITICAL FIXES!"
echo "================================================================================"
echo ""

cd ~/bot || cd ~/apex_bot || { echo "❌ Bot directory not found!"; exit 1; }

# Stop any running bot
echo "⏸️  Stopping any running bot..."
pkill -f ORCHESTRATOR
sleep 3

# Pull latest (force if needed)
echo "📥 Pulling latest code with fixes..."
git fetch origin continue-from-micro-fix
git reset --hard origin/continue-from-micro-fix

if [ $? -ne 0 ]; then
    echo "⚠️  Git pull failed, but continuing..."
fi

# Find virtual environment
echo "🔍 Finding virtual environment..."
VENV_PATH=""

if [ -d "apex_venv/bin" ]; then
    VENV_PATH="apex_venv/bin/activate"
elif [ -d "venv/bin" ]; then
    VENV_PATH="venv/bin/activate"
elif [ -d "../apex_venv/bin" ]; then
    VENV_PATH="../apex_venv/bin/activate"
elif [ -d "~/.venv/bin" ]; then
    VENV_PATH="~/.venv/bin/activate"
fi

if [ -z "$VENV_PATH" ]; then
    echo "⚠️  No virtual environment found, running with system Python"
else
    echo "✅ Found venv: $VENV_PATH"
    source "$VENV_PATH"
fi

# Check Python
PYTHON_CMD=$(which python3 2>/dev/null || which python 2>/dev/null)
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python not found!"
    exit 1
fi

echo "✅ Using Python: $PYTHON_CMD"
echo ""

# Check if main orchestrator exists
if [ ! -f "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py" ]; then
    echo "❌ systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py not found!"
    echo ""
    echo "Files in systems/:"
    ls -la systems/*.py 2>/dev/null | head -10
    exit 1
fi

echo "✅ Orchestrator found"
echo ""

# Start bot with better error handling
echo "================================================================================"
echo "🚀 STARTING BOT"
echo "================================================================================"
echo ""

# Start in background
nohup $PYTHON_CMD systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!

echo "🚀 Bot started with PID: $BOT_PID"
echo "⏳ Waiting 15 seconds for startup..."
sleep 15

echo ""
echo "================================================================================"
echo "✅ VERIFICATION"
echo "================================================================================"
echo ""

# Check if still running
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ BOT IS RUNNING (PID: $BOT_PID)"
    echo ""
    
    # Show recent logs
    echo "📊 Recent logs:"
    echo "----------------------------------------"
    tail -30 bot.log | head -25
    echo "----------------------------------------"
    echo ""
    
    # Check for critical errors
    CRITICAL=$(tail -50 bot.log | grep -c "CRITICAL\|FATAL\|create_market_buy_order.*has no attribute")
    
    if [ $CRITICAL -gt 0 ]; then
        echo "❌ CRITICAL ERRORS DETECTED:"
        tail -50 bot.log | grep "CRITICAL\|FATAL\|create_market_buy_order.*has no attribute" | tail -5
        echo ""
        echo "⚠️  Bot is running but has critical errors!"
    else
        echo "✅ No critical errors detected!"
    fi
    
    # Check for router errors specifically
    ROUTER_ERROR=$(tail -50 bot.log | grep -c "ExchangeRouter.*has no attribute.*fetch_balance\|create_market")
    
    if [ $ROUTER_ERROR -gt 0 ]; then
        echo ""
        echo "❌ ROUTER ERROR STILL PRESENT!"
        echo "   The router.py file may not be updated on VPS"
        echo ""
        echo "   Quick fix: Try running this on VPS:"
        echo "   cd ~/bot && git pull origin continue-from-micro-fix && pkill -f ORCHESTRATOR && nohup python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &"
    fi
    
else
    echo "❌ BOT CRASHED ON STARTUP!"
    echo ""
    echo "Last 40 log lines:"
    echo "----------------------------------------"
    tail -40 bot.log
    echo "----------------------------------------"
    exit 1
fi

echo ""
echo "================================================================================"
echo "📝 MONITORING"
echo "================================================================================"
echo ""
echo "Watch logs:  tail -f bot.log"
echo "Check status: ps aux | grep ORCHESTRATOR"
echo "Stop bot:    pkill -f ORCHESTRATOR"
echo ""
echo "================================================================================"
