#!/bin/bash
# ============================================================================
# 🔍 CAPTURE VPS STATE - Run this on VPS, share output with me
# ============================================================================
# This script captures all diagnostic info safely (no sensitive data)
# You can then share the output for analysis

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="vps_state_${TIMESTAMP}.txt"

echo "════════════════════════════════════════════════════════════════════════"
echo "🔍 CAPTURING VPS STATE FOR ANALYSIS"
echo "════════════════════════════════════════════════════════════════════════"
echo "Output will be saved to: $OUTPUT_FILE"
echo ""

# Start capturing
{
echo "════════════════════════════════════════════════════════════════════════"
echo "VPS STATE CAPTURE - $(date)"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# 1. BASIC SYSTEM INFO
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "1. SYSTEM INFORMATION"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo "Uptime: $(uptime -p)"
echo "Kernel: $(uname -r)"
echo "OS: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2)"
echo ""

# ============================================================================
# 2. RESOURCE USAGE
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "2. RESOURCE USAGE"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
echo "Memory:"
free -h
echo ""
echo "Disk Usage:"
df -h | grep -E "Filesystem|/$|/home"
echo ""

# ============================================================================
# 3. PYTHON ENVIRONMENT
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "3. PYTHON ENVIRONMENT"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Python Version: $(python3 --version 2>&1)"
echo "Python Path: $(which python3)"
echo ""
echo "Checking Dependencies:"
for pkg in numpy pandas scipy scikit-learn ccxt aiohttp requests; do
    if python3 -c "import $pkg" 2>/dev/null; then
        VERSION=$(python3 -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "unknown")
        echo "  ✅ $pkg ($VERSION)"
    else
        echo "  ❌ $pkg - NOT INSTALLED"
    fi
done
echo ""

# ============================================================================
# 4. BOT PROCESSES
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "4. BOT PROCESSES"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
BOT_PROCS=$(ps aux | grep -E "python.*ORCHESTRATOR|python.*bot|python.*trading" | grep -v grep)
if [ -z "$BOT_PROCS" ]; then
    echo "❌ NO BOT PROCESSES RUNNING"
else
    echo "✅ BOT PROCESSES FOUND:"
    echo "$BOT_PROCS"
fi
echo ""

# ============================================================================
# 5. GIT STATUS
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "5. GIT REPOSITORY STATUS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
if [ -d ".git" ]; then
    echo "Current Branch: $(git branch --show-current)"
    echo "Latest Commit: $(git log -1 --oneline)"
    echo "Uncommitted Changes: $(git status --short | wc -l)"
    echo ""
    echo "Recent Commits:"
    git log --oneline -5
    echo ""
    
    # Check if behind remote
    git fetch origin 2>/dev/null
    LOCAL=$(git rev-parse @ 2>/dev/null)
    REMOTE=$(git rev-parse @{u} 2>/dev/null)
    
    if [ -z "$REMOTE" ]; then
        echo "⚠️  No remote tracking branch"
    elif [ "$LOCAL" = "$REMOTE" ]; then
        echo "✅ Up to date with remote"
    else
        echo "⚠️  Behind remote - need to pull"
        git log --oneline HEAD..@{u} 2>/dev/null | head -5
    fi
else
    echo "❌ Not a git repository"
fi
echo ""

# ============================================================================
# 6. CRITICAL FILES
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "6. CRITICAL FILES CHECK"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
CRITICAL_FILES=(
    "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py"
    "EXECUTION_ORCHESTRATOR.py"
    "INTELLIGENT_EXECUTION_ENGINE.py"
    "ULTRA_GOLDMINE_FEATURES.py"
    "DIVINE_INTELLIGENCE_FEATURES.py"
    "critical_features_addon.py"
    "ALL_ENGINES_ACTIVATED.py"
    "router.py"
    ".env"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(du -h "$file" | cut -f1)
        MODIFIED=$(stat -c %y "$file" 2>/dev/null | cut -d'.' -f1)
        echo "✅ $file ($SIZE) - Modified: $MODIFIED"
    else
        echo "❌ $file - MISSING"
    fi
done
echo ""

# ============================================================================
# 7. ENV FILE STATUS (NO SENSITIVE DATA)
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "7. ENVIRONMENT CONFIGURATION"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    SIZE=$(du -h .env | cut -f1)
    echo "   Size: $SIZE"
    
    # Check for placeholders (DON'T show actual keys!)
    if grep -q "your_.*_here" .env 2>/dev/null; then
        echo "   ⚠️  Contains placeholder values"
    else
        echo "   ✅ Appears to be configured"
    fi
    
    # Check key presence (NOT values!)
    echo ""
    echo "Key Status (presence only):"
    for key in GATE_API_KEY GATE_SECRET TELEGRAM_BOT_TOKEN GATE_TESTNET TRADING_MODE; do
        if grep -q "^${key}=" .env 2>/dev/null; then
            echo "  ✅ $key is set"
        else
            echo "  ❌ $key is missing"
        fi
    done
else
    echo "❌ .env file does NOT exist"
fi
echo ""

# ============================================================================
# 8. LOG FILES
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "8. LOG FILES"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Available log files:"
for logfile in *.log; do
    if [ -f "$logfile" ]; then
        SIZE=$(du -h "$logfile" | cut -f1)
        LINES=$(wc -l < "$logfile" 2>/dev/null || echo "0")
        AGE=$(($(date +%s) - $(stat -c %Y "$logfile" 2>/dev/null || echo "0")))
        echo "  $logfile - Size: $SIZE, Lines: $LINES, Age: ${AGE}s"
    fi
done
echo ""

# Most recent log activity
LATEST_LOG=$(ls -t *.log 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo "Last 30 lines from most recent log ($LATEST_LOG):"
    echo "────────────────────────────────────────────────────────────────────────"
    tail -30 "$LATEST_LOG" 2>/dev/null
    echo "────────────────────────────────────────────────────────────────────────"
fi
echo ""

# ============================================================================
# 9. ERROR ANALYSIS
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "9. RECENT ERRORS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
for logfile in *.log; do
    if [ -f "$logfile" ]; then
        ERROR_COUNT=$(grep -i "error\|exception\|failed\|critical" "$logfile" 2>/dev/null | wc -l)
        if [ $ERROR_COUNT -gt 0 ]; then
            echo "Found $ERROR_COUNT errors in $logfile (last 10):"
            grep -i "error\|exception\|failed\|critical" "$logfile" 2>/dev/null | tail -10
            echo ""
        fi
    fi
done

# ============================================================================
# 10. PYTHON IMPORT TEST
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "10. PYTHON IMPORT TEST"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
python3 << 'PYEOF'
import sys

# Test critical imports
tests = [
    ('ULTRA_GOLDMINE_FEATURES', 'GammaSqueezeDetector'),
    ('DIVINE_INTELLIGENCE_FEATURES', 'DivineIntelligenceManager'),
    ('critical_features_addon', 'TrailingStopManager'),
    ('EXECUTION_ORCHESTRATOR', 'ExecutionOrchestrator'),
    ('INTELLIGENT_EXECUTION_ENGINE', 'IntelligentExecutionEngine'),
]

print("Testing critical imports:")
working = 0
for module_name, class_name in tests:
    try:
        module = __import__(module_name)
        if hasattr(module, class_name):
            print(f"  ✅ {module_name}.{class_name}")
            working += 1
        else:
            print(f"  ⚠️  {module_name}.{class_name} - class not found")
    except Exception as e:
        print(f"  ❌ {module_name} - {str(e)[:60]}")

print(f"\n📊 {working}/{len(tests)} imports working")
PYEOF
echo ""

# ============================================================================
# 11. ENGINE ACTIVATION TEST
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "11. ENGINE ACTIVATION TEST"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
python3 << 'PYEOF'
import sys

try:
    import ALL_ENGINES_ACTIVATED as AE
    
    activated = [n for n in dir(AE) if n.endswith('_AVAILABLE') and getattr(AE, n)]
    failed = [n for n in dir(AE) if n.endswith('_AVAILABLE') and not getattr(AE, n)]
    
    print(f"✅ Engine activation module loaded")
    print(f"📊 {len(activated)}/{len(activated)+len(failed)} engines activated")
    print(f"   Success rate: {len(activated)/(len(activated)+len(failed))*100:.1f}%")
    print("")
    
    if activated:
        print("ACTIVE ENGINES (sample):")
        for eng in activated[:15]:
            print(f"  ✅ {eng.replace('_AVAILABLE', '')}")
        if len(activated) > 15:
            print(f"  ... and {len(activated) - 15} more")
    
    print("")
    
    if failed:
        print("FAILED TO ACTIVATE:")
        for eng in failed[:15]:
            print(f"  ❌ {eng.replace('_AVAILABLE', '')}")
        if len(failed) > 15:
            print(f"  ... and {len(failed) - 15} more")
    
except Exception as e:
    print(f"❌ Engine activation failed: {e}")
PYEOF
echo ""

# ============================================================================
# 12. NETWORK CONNECTIVITY
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "12. NETWORK CONNECTIVITY"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
for host in api.gate.io api.bybit.com api.binance.com; do
    if ping -c 1 -W 2 $host &>/dev/null; then
        echo "✅ $host - reachable"
    else
        echo "❌ $host - unreachable"
    fi
done
echo ""

# ============================================================================
# 13. DIRECTORY STRUCTURE
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "13. DIRECTORY STRUCTURE"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Top-level Python files:"
ls -lh *.py 2>/dev/null | head -20 | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Systems directory:"
ls -lh systems/*.py 2>/dev/null | head -10 | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "CAPTURE COMPLETE - $(date)"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "This file contains all diagnostic information needed for analysis."
echo "No sensitive data (API keys, passwords) has been captured."
echo ""
echo "Share this file for detailed analysis and recommendations."
echo "════════════════════════════════════════════════════════════════════════"

} | tee "$OUTPUT_FILE"

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "✅ CAPTURE COMPLETE!"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Output saved to: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "  1. Review the file: cat $OUTPUT_FILE"
echo "  2. Copy the entire output"
echo "  3. Share it for analysis"
echo ""
echo "No sensitive data has been captured - safe to share!"
echo "════════════════════════════════════════════════════════════════════════"
