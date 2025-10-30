#!/bin/bash
# VPS Diagnostic - Run these commands on your VPS to see what's working

echo "==============================================================================="
echo "🔍 VPS BOT DIAGNOSTIC - Finding What's Actually Running"
echo "==============================================================================="
echo ""

echo "1️⃣ CHECK RUNNING PROCESSES:"
echo "==============================================================================="
ps aux | grep -E "python.*\.py" | grep -v grep
echo ""

echo "2️⃣ CHECK SCREEN SESSIONS:"
echo "==============================================================================="
screen -ls
echo ""

echo "3️⃣ CHECK RECENT BOT ACTIVITY (Last 50 lines):"
echo "==============================================================================="
if [ -f ~/trading_bot/bot.log ]; then
    tail -50 ~/trading_bot/bot.log
elif [ -f ~/bot.log ]; then
    tail -50 ~/bot.log
else
    echo "Looking for log files..."
    find ~ -name "bot.log" -o -name "*.log" | head -5
fi
echo ""

echo "4️⃣ CHECK BOT LOCATION:"
echo "==============================================================================="
if [ -d ~/trading_bot ]; then
    echo "✅ Found: ~/trading_bot"
    ls -la ~/trading_bot/*.py 2>/dev/null | head -20
elif [ -d ~/bot ]; then
    echo "✅ Found: ~/bot"
    ls -la ~/bot/*.py 2>/dev/null | head -20
else
    echo "Searching for bot directory..."
    find ~ -type d -name "*bot*" -o -name "*trading*" 2>/dev/null | head -10
fi
echo ""

echo "5️⃣ CHECK CURRENT BRANCH:"
echo "==============================================================================="
cd ~/trading_bot 2>/dev/null || cd ~/bot 2>/dev/null || cd ~
git branch 2>/dev/null || echo "Not a git repository"
git log --oneline -5 2>/dev/null || echo "No git history"
echo ""

echo "6️⃣ CHECK .ENV FILE:"
echo "==============================================================================="
if [ -f ~/trading_bot/.env ]; then
    echo "✅ Found .env file"
    grep -E "GATE_API|ENABLE_LIVE|TRADING_MODE" ~/trading_bot/.env 2>/dev/null
elif [ -f ~/.env ]; then
    echo "✅ Found .env file in home"
    grep -E "GATE_API|ENABLE_LIVE|TRADING_MODE" ~/.env 2>/dev/null
fi
echo ""

echo "7️⃣ CHECK GATE.IO BALANCE:"
echo "==============================================================================="
if [ -f ~/trading_bot/BALANCE_CHECKER.py ]; then
    python3 ~/trading_bot/BALANCE_CHECKER.py 2>/dev/null || echo "Balance checker failed"
else
    echo "No balance checker found - will need to check manually"
fi
echo ""

echo "8️⃣ FIND MAIN BOT FILE:"
echo "==============================================================================="
cd ~/trading_bot 2>/dev/null || cd ~/bot 2>/dev/null || cd ~
echo "Looking for main bot files..."
ls -lh *ORCHESTRATOR*.py *RUN*.py *PROFIT*.py 2>/dev/null | head -10
echo ""

echo "==============================================================================="
echo "✅ DIAGNOSTIC COMPLETE"
echo "==============================================================================="
echo ""
echo "📋 NEXT STEPS:"
echo "1. Copy the output above"
echo "2. Share with the agent"
echo "3. Agent will analyze your REAL running bot"
echo "4. Agent will create enhancements for YOUR specific setup"
echo "5. Agent will provide ONE command to deploy everything"
echo ""
echo "==============================================================================="
