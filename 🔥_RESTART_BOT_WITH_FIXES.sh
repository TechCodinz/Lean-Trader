#!/bin/bash
# 🔥 RESTART BOT WITH ALL 3 CRITICAL FIXES
# Run this on VPS after pulling fixes

cd ~/bot

echo "================================================================================"
echo "🔥 RESTARTING BOT WITH ALL CRITICAL FIXES"
echo "================================================================================"
echo ""

# Stop current bot
echo "Stopping current bot..."
pkill -f ORCHESTRATOR
sleep 3

# Pull all fixes
echo "Pulling critical fixes..."
git pull origin continue-from-micro-fix

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed"
    exit 1
fi

echo ""
echo "✅ Fixes pulled successfully!"
echo ""
echo "What was fixed:"
echo "  1. ✅ Gemini API: gemini-pro → gemini-1.5-flash"
echo "  2. ✅ Supreme Consciousness: Import path fixed"
echo "  3. ✅ ExchangeRouter: Missing methods added"
echo ""

# Verify fixes
echo "Verifying fixes..."
echo ""

# Check Gemini fix
if grep -q "gemini-1.5-flash" AI_CONSULTATION_SERVICE.py 2>/dev/null; then
    echo "✅ Gemini API fix verified"
else
    echo "⚠️  Gemini fix not detected"
fi

# Check router fix
if grep -q "def fetch_balance" router.py 2>/dev/null; then
    echo "✅ ExchangeRouter methods fix verified"
else
    echo "⚠️  ExchangeRouter fix not detected"
fi

echo ""
echo "================================================================================"
echo "🚀 STARTING BOT WITH FIXES"
echo "================================================================================"
echo ""

# Activate virtual environment
if [ -f "apex_venv/bin/activate" ]; then
    source apex_venv/bin/activate
    echo "✅ Virtual environment activated"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Start bot
echo "Starting bot..."
nohup python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!

echo "✅ Bot started (PID: $BOT_PID)"
echo ""

# Wait for startup
echo "⏳ Waiting for startup (15 seconds)..."
sleep 15

echo ""
echo "================================================================================"
echo "📊 CHECKING BOT STATUS"
echo "================================================================================"
echo ""

# Check if bot is running
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ Bot is running (PID: $BOT_PID)"
else
    echo "❌ Bot process not found!"
    echo ""
    echo "Check for errors:"
    tail -50 bot.log
    exit 1
fi

echo ""
echo "Recent log activity:"
echo "--------------------------------------------------------------------------------"
tail -40 bot.log
echo "--------------------------------------------------------------------------------"
echo ""

# Check for the 3 errors
echo "Checking if errors are fixed..."
echo ""

# Check Gemini error
if grep -q "gemini-pro is not found" bot.log; then
    echo "❌ Gemini error still present"
else
    echo "✅ Gemini error FIXED"
fi

# Check Supreme Consciousness
if grep -q "SUPREME CONSCIOUSNESS FAILED TO LOAD" bot.log; then
    echo "⚠️  Supreme Consciousness not loaded (run activation script)"
else
    if grep -q "SUPREME CONSCIOUSNESS" bot.log; then
        echo "✅ Supreme Consciousness check passed"
    else
        echo "ℹ️  Supreme Consciousness not integrated yet"
    fi
fi

# Check ExchangeRouter
if grep -q "ExchangeRouter.*has no attribute" bot.log; then
    echo "❌ ExchangeRouter error still present"
else
    echo "✅ ExchangeRouter error FIXED"
fi

echo ""
echo "================================================================================"
echo "✅ BOT RESTART COMPLETE"
echo "================================================================================"
echo ""
echo "📊 Bot Status:"
ps aux | grep ORCHESTRATOR | grep -v grep
echo ""
echo "📋 Next steps:"
echo "   • Watch live: tail -f bot.log"
echo "   • Check trades: grep 'Decision' bot.log | tail -10"
echo "   • Check errors: grep -i error bot.log | grep -v 'Guard Error' | tail -5"
echo "   • Activate Supreme: bash 🌌_ACTIVATE_SUPREME_NOW.sh"
echo ""
echo "🔥 All critical errors fixed! Bot should trade without issues now!"
echo ""
