#!/bin/bash

echo "================================================================================"
echo "🔍 APEX BOT VPS STATUS CHECK"
echo "================================================================================"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  RUNNING PROCESSES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep -E "python|ORCHESTRATOR|EVOLUTION|apex" | grep -v grep
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  GIT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Current Directory: $(pwd)"
echo "Current Branch:"
git branch --show-current 2>/dev/null || echo "  Not in a git repo"
echo ""
echo "Git Status:"
git status -s 2>/dev/null || echo "  Not in a git repo"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  RECENT LOG OUTPUT (Last 30 lines)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "apex.log" ]; then
    tail -30 apex.log
elif [ -f "nohup.out" ]; then
    tail -30 nohup.out
else
    echo "  No log file found (apex.log or nohup.out)"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  EVOLUTION DATABASE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "evolution_engine.db" ]; then
    echo "Database exists: evolution_engine.db"
    echo "Database size: $(du -h evolution_engine.db | cut -f1)"
    echo ""
    echo "Database contents:"
    sqlite3 evolution_engine.db "SELECT COUNT(*) as total_rows FROM model_evolution;" 2>/dev/null || echo "  Could not read database"
    sqlite3 evolution_engine.db "SELECT MAX(generation) as max_generation FROM model_evolution;" 2>/dev/null || echo "  Could not get generation"
else
    echo "  evolution_engine.db NOT FOUND!"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  RECENT ERRORS (Last 10)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "apex.log" ]; then
    grep -i "error\|exception\|failed\|traceback" apex.log | tail -10
elif [ -f "nohup.out" ]; then
    grep -i "error\|exception\|failed\|traceback" nohup.out | tail -10
else
    echo "  No log file to check"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  RECENT TRADES (Last 10)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "apex.log" ]; then
    grep -iE "trade|signal|executed|buy|sell|profit" apex.log | tail -10
elif [ -f "nohup.out" ]; then
    grep -iE "trade|signal|executed|buy|sell|profit" nohup.out | tail -10
else
    echo "  No log file to check"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  SYSTEM RESOURCES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h | grep -E "Filesystem|/$|/root"
echo ""
echo "CPU Load:"
uptime
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  INSTALLED OPTIMIZATIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checking for new optimization modules..."
for file in WEBSOCKET_DATA_FEED.py SMART_ORDER_MANAGER.py SMART_TRADE_FILTER.py SIGNAL_AGGREGATOR.py DYNAMIC_POSITION_SIZER.py; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (not installed)"
    fi
done
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  PYTHON PACKAGES (ccxt)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip3 list | grep ccxt
echo ""

echo "================================================================================"
echo "✅ STATUS CHECK COMPLETE"
echo "================================================================================"
echo ""
echo "📋 SUMMARY:"
echo "   Check the sections above to see:"
echo "   - What's currently running"
echo "   - Which branch you're on"
echo "   - Recent bot activity"
echo "   - Evolution data status"
echo "   - Any errors"
echo "   - Available optimizations"
echo ""
echo "💡 NEXT STEPS:"
echo "   1. Review the output above"
echo "   2. Make note of current state"
echo "   3. Decide if you want to pull new optimizations"
echo "   4. Or continue monitoring current setup"
echo ""
echo "================================================================================"
