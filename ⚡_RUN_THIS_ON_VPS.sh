#!/bin/bash
# ⚡ QUICK VPS DIAGNOSTIC - Copy this entire file to VPS and run
# This will show EVERYTHING you need to know

clear
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                     ⚡ QUICK VPS STATE REPORT ⚡                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Find bot directory
echo "🔍 Searching for bot directory..."
BOT_DIR=$(find ~ -maxdepth 2 -type d \( -name "bot" -o -name "*trading*" -o -name "Lean-Trader" \) 2>/dev/null | head -1)

if [ -z "$BOT_DIR" ]; then
    echo "⚠️  Bot directory not found. Checking home..."
    BOT_DIR="$HOME"
fi

echo "📁 Bot directory: $BOT_DIR"
echo ""

cd "$BOT_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  RUNNING PROCESSES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep python | grep -v grep
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  GIT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d ".git" ]; then
    echo "Branch: $(git branch --show-current 2>/dev/null)"
    echo "Remote: $(git remote get-url origin 2>/dev/null)"
    echo "Last commit:"
    git log -1 --oneline 2>/dev/null
else
    echo "⚠️  Not a git repository"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  KEY FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Main bot files:"
ls -lh *ORCHESTRATOR*.py *PROFIT*.py RUN_BOT.py 2>/dev/null | awk '{print "  ✅", $9, "("$5")"}'
echo ""
echo "Configuration:"
[ -f ".env" ] && echo "  ✅ .env ($(wc -l < .env) lines)" || echo "  ❌ .env missing"
[ -f "accounts.yml" ] && echo "  ✅ accounts.yml" || echo "  ⚠️  accounts.yml missing"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  VENV STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "venv" ]; then
    echo "✅ venv exists"
    if [ -f "venv/bin/python3" ]; then
        echo "Python: $(venv/bin/python3 --version)"
        echo ""
        echo "Critical packages:"
        venv/bin/pip list 2>/dev/null | grep -E "ccxt|pandas|numpy|aiohttp|loguru"
    fi
else
    echo "❌ venv directory missing"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  RECENT BOT ACTIVITY (Last 30 lines)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "bot.log" ]; then
    tail -30 bot.log
else
    echo "⚠️  No bot.log found"
    echo "Looking for other logs..."
    find . -maxdepth 1 -name "*.log" -exec echo "Found: {}" \;
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  FILE COUNTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Python files: $(find . -name "*.py" 2>/dev/null | wc -l)"
echo "Shell scripts: $(find . -name "*.sh" 2>/dev/null | wc -l)"
echo "Markdown docs: $(find . -name "*.md" 2>/dev/null | wc -l)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  API CONFIGURATION (Hidden for security)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f ".env" ]; then
    grep -E "GATE_API_KEY|ENABLE_LIVE|TRADING_MODE" .env 2>/dev/null | sed 's/=.*/=***/'
else
    echo "❌ No .env file"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                            ✅ REPORT COMPLETE                                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 COPY ALL OUTPUT ABOVE AND SHARE WITH AGENT"
echo ""
