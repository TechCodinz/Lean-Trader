#!/bin/bash
# 🔍 COMPLETE VPS DIAGNOSTIC - See Everything on VPS
# Run this ON YOUR VPS to capture complete state

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║              🔍 COMPLETE VPS DIAGNOSTIC - FULL STATE CAPTURE                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Create output file
OUTPUT="vps_diagnostic_$(date +%Y%m%d_%H%M%S).txt"
echo "📝 Saving results to: $OUTPUT"
echo ""

{
echo "VPS DIAGNOSTIC REPORT"
echo "Generated: $(date)"
echo "Host: $(hostname)"
echo "="
echo ""

# ============================================================================
# 1. PROCESS STATUS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. RUNNING PROCESSES (Python bots)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
ps aux | grep python | grep -v grep
echo ""

# ============================================================================
# 2. DIRECTORY STRUCTURE
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. BOT DIRECTORY STRUCTURE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Find bot directories
BOT_DIRS=$(find ~ -maxdepth 3 -type d \( -name "bot" -o -name "*trading*" -o -name "Lean-Trader" \) 2>/dev/null)

if [ -z "$BOT_DIRS" ]; then
    echo "⚠️  No bot directories found in home"
    echo "Checking common locations..."
    ls -la ~/
else
    echo "Found bot directories:"
    echo "$BOT_DIRS"
    echo ""
    
    for dir in $BOT_DIRS; do
        echo "📁 Directory: $dir"
        ls -lh "$dir" | head -30
        echo ""
    done
fi

# ============================================================================
# 3. MAIN PYTHON FILES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. KEY PYTHON FILES (Orchestrators, Profit Systems, etc.)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for dir in $BOT_DIRS ~/bot ~/trading_bot ~/Lean-Trader; do
    if [ -d "$dir" ]; then
        echo "In $dir:"
        find "$dir" -maxdepth 1 -name "*ORCHESTRATOR*.py" -o -name "*PROFIT*.py" -o -name "RUN_BOT.py" -o -name "*COMPLETE*.py" 2>/dev/null | while read file; do
            echo "  ✅ $(basename $file) ($(stat -c%s $file 2>/dev/null || stat -f%z $file 2>/dev/null) bytes)"
        done
        echo ""
    fi
done

# ============================================================================
# 4. VENV STATUS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. VIRTUAL ENVIRONMENT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for dir in $BOT_DIRS ~/bot ~/trading_bot ~/Lean-Trader; do
    if [ -d "$dir" ]; then
        echo "Checking $dir:"
        if [ -d "$dir/venv" ]; then
            echo "  ✅ venv exists"
            if [ -f "$dir/venv/bin/python3" ]; then
                echo "  ✅ Python: $($dir/venv/bin/python3 --version 2>&1)"
                echo "  📦 Installed packages:"
                $dir/venv/bin/pip list 2>/dev/null | grep -E "ccxt|pandas|numpy|aiohttp|loguru" | head -10
            fi
        else
            echo "  ❌ No venv found"
        fi
        echo ""
    fi
done

# ============================================================================
# 5. GIT STATUS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. GIT REPOSITORY STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for dir in $BOT_DIRS ~/bot ~/trading_bot ~/Lean-Trader; do
    if [ -d "$dir/.git" ]; then
        echo "📂 Repository: $dir"
        cd "$dir"
        echo "  Branch: $(git branch --show-current 2>/dev/null)"
        echo "  Remote: $(git remote get-url origin 2>/dev/null)"
        echo "  Last commit: $(git log -1 --oneline 2>/dev/null)"
        echo "  Status:"
        git status --short 2>/dev/null | head -10
        echo ""
    fi
done

# ============================================================================
# 6. CONFIGURATION FILES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. CONFIGURATION FILES (.env, accounts.yml)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for dir in $BOT_DIRS ~/bot ~/trading_bot ~/Lean-Trader; do
    if [ -d "$dir" ]; then
        echo "In $dir:"
        if [ -f "$dir/.env" ]; then
            echo "  ✅ .env exists"
            echo "  Configuration (hiding sensitive data):"
            grep -E "GATE_API_KEY|ENABLE_LIVE|TRADING_MODE|BYBIT" "$dir/.env" 2>/dev/null | sed 's/=.*/=***HIDDEN***/'
        else
            echo "  ❌ No .env file"
        fi
        
        if [ -f "$dir/accounts.yml" ]; then
            echo "  ✅ accounts.yml exists"
        else
            echo "  ⚠️  No accounts.yml"
        fi
        echo ""
    fi
done

# ============================================================================
# 7. RECENT LOGS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. RECENT BOT ACTIVITY (Last 50 lines of logs)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for dir in $BOT_DIRS ~/bot ~/trading_bot ~/Lean-Trader; do
    if [ -d "$dir" ]; then
        # Check for various log files
        for log in bot.log trading.log *.log; do
            if [ -f "$dir/$log" ]; then
                echo "📋 Log: $dir/$log (last 50 lines)"
                tail -50 "$dir/$log" 2>/dev/null
                echo ""
            fi
        done
    fi
done

# ============================================================================
# 8. SYSTEM RESOURCES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. SYSTEM RESOURCES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Memory:"
free -h
echo ""
echo "Disk:"
df -h | grep -E "Filesystem|/$"
echo ""

# ============================================================================
# 9. FILE COUNTS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. FILE STATISTICS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for dir in $BOT_DIRS ~/bot ~/trading_bot ~/Lean-Trader; do
    if [ -d "$dir" ]; then
        echo "In $dir:"
        echo "  Python files: $(find "$dir" -name "*.py" 2>/dev/null | wc -l)"
        echo "  Shell scripts: $(find "$dir" -name "*.sh" 2>/dev/null | wc -l)"
        echo "  MD files: $(find "$dir" -name "*.md" 2>/dev/null | wc -l)"
        echo ""
    fi
done

# ============================================================================
# 10. RECENT FILE MODIFICATIONS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "10. RECENTLY MODIFIED FILES (Last 24 hours)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for dir in $BOT_DIRS ~/bot ~/trading_bot ~/Lean-Trader; do
    if [ -d "$dir" ]; then
        echo "In $dir:"
        find "$dir" -type f -mtime -1 -name "*.py" -o -name "*.sh" -o -name "*.md" 2>/dev/null | head -20
        echo ""
    fi
done

} | tee "$OUTPUT"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                           ✅ DIAGNOSTIC COMPLETE                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Full report saved to: $OUTPUT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. View the report:"
echo "   cat $OUTPUT"
echo ""
echo "2. Copy to your local machine:"
echo "   scp root@YOUR_VPS_IP:~/$OUTPUT ."
echo ""
echo "3. Or just paste the output when sharing with agent"
echo ""
echo "This report shows EVERYTHING on your VPS:"
echo "  ✅ What's running"
echo "  ✅ What files exist"
echo "  ✅ Git status & branch"
echo "  ✅ Configuration"
echo "  ✅ Recent activity"
echo "  ✅ venv status"
echo ""
