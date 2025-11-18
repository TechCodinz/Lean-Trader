#!/bin/bash
# ============================================================================
# 🔍 VPS COMPLETE AUDIT - Check Everything On VPS
# ============================================================================
# This script audits the ENTIRE VPS system to find what's failing/dormant

echo "════════════════════════════════════════════════════════════════════════"
echo "🔍 VPS COMPLETE AUDIT - Starting Comprehensive System Check"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# 1. SYSTEM INFORMATION
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "📊 SYSTEM INFORMATION"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

echo "🖥️  Hostname: $(hostname)"
echo "📅 Date/Time: $(date)"
echo "⏰ Uptime: $(uptime -p)"
echo "💾 Disk Usage: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
echo "🧠 Memory: $(free -h | awk 'NR==2 {print $3 "/" $2 " used"}')"
echo "🔧 CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

# ============================================================================
# 2. CHECK IF BOT IS RUNNING
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "🤖 BOT PROCESS STATUS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

BOT_PROCESSES=$(ps aux | grep -E "python.*ORCHESTRATOR|python.*bot|python.*trading" | grep -v grep)

if [ -z "$BOT_PROCESSES" ]; then
    echo -e "${RED}❌ NO BOT PROCESSES RUNNING${NC}"
    echo "   The trading bot is not active!"
else
    echo -e "${GREEN}✅ BOT PROCESSES FOUND:${NC}"
    echo "$BOT_PROCESSES" | while read line; do
        echo "   • $line"
    done
fi
echo ""

# ============================================================================
# 3. CHECK PYTHON VERSION & DEPENDENCIES
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "🐍 PYTHON ENVIRONMENT"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

echo "Python Version: $(python3 --version 2>&1)"
echo ""

echo "Checking Critical Dependencies:"
for pkg in numpy pandas scipy scikit-learn ccxt aiohttp requests; do
    if python3 -c "import $pkg" 2>/dev/null; then
        VERSION=$(python3 -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "unknown")
        echo -e "  ${GREEN}✅${NC} $pkg ($VERSION)"
    else
        echo -e "  ${RED}❌${NC} $pkg - NOT INSTALLED"
    fi
done
echo ""

# ============================================================================
# 4. CHECK GIT STATUS
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "📦 GIT REPOSITORY STATUS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

if [ -d ".git" ]; then
    echo "Current Branch: $(git branch --show-current)"
    echo "Latest Commit: $(git log -1 --oneline)"
    echo "Status: $(git status --short | wc -l) uncommitted changes"
    echo ""
    
    # Check if behind remote
    git fetch origin 2>/dev/null
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u} 2>/dev/null)
    
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo -e "${GREEN}✅ Up to date with remote${NC}"
    else
        echo -e "${YELLOW}⚠️  Local is behind remote - run 'git pull'${NC}"
    fi
else
    echo -e "${RED}❌ Not a git repository${NC}"
fi
echo ""

# ============================================================================
# 5. CHECK CRITICAL FILES EXIST
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "📁 CRITICAL FILES CHECK"
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
        echo -e "  ${GREEN}✅${NC} $file ($SIZE)"
    else
        echo -e "  ${RED}❌${NC} $file - MISSING"
    fi
done
echo ""

# ============================================================================
# 6. CHECK .ENV CONFIGURATION
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "🔐 ENVIRONMENT CONFIGURATION"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    
    # Check for placeholder values (security conscious - don't show actual keys)
    if grep -q "your_.*_here" .env 2>/dev/null; then
        echo -e "${RED}⚠️  WARNING: .env contains placeholder values!${NC}"
        echo "   Keys still using 'your_*_here' need to be configured"
    else
        echo -e "${GREEN}✅ .env appears to be configured${NC}"
    fi
    
    # Check critical keys exist (without showing values)
    echo ""
    echo "Critical keys status:"
    for key in GATE_API_KEY GATE_SECRET TELEGRAM_BOT_TOKEN; do
        if grep -q "^${key}=" .env 2>/dev/null; then
            echo -e "  ${GREEN}✅${NC} $key is set"
        else
            echo -e "  ${RED}❌${NC} $key is missing"
        fi
    done
else
    echo -e "${RED}❌ .env file does NOT exist${NC}"
    if [ -f ".env.template" ]; then
        echo -e "${YELLOW}💡 Template available: cp .env.template .env${NC}"
    fi
fi
echo ""

# ============================================================================
# 7. CHECK LOG FILES
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "📝 LOG FILES STATUS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

LOG_FILES=(
    "unified_trading_system.log"
    "bot.log"
    "apex_bot.log"
    "trading.log"
)

for logfile in "${LOG_FILES[@]}"; do
    if [ -f "$logfile" ]; then
        SIZE=$(du -h "$logfile" | cut -f1)
        LINES=$(wc -l < "$logfile")
        LAST_MODIFIED=$(stat -c %y "$logfile" | cut -d'.' -f1)
        echo -e "${GREEN}✅${NC} $logfile"
        echo "   Size: $SIZE | Lines: $LINES | Last: $LAST_MODIFIED"
        
        # Check for recent activity (last 5 minutes)
        if [ $(find "$logfile" -mmin -5 2>/dev/null | wc -l) -gt 0 ]; then
            echo -e "   ${GREEN}📍 Active (modified in last 5 min)${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Inactive (no recent activity)${NC}"
        fi
    else
        echo -e "${RED}❌${NC} $logfile - not found"
    fi
done
echo ""

# ============================================================================
# 8. RUN PYTHON DIAGNOSTIC
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "🔬 PYTHON DIAGNOSTIC - Engine Status"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

if [ -f "COMPREHENSIVE_ENGINE_DIAGNOSTIC.py" ]; then
    echo "Running comprehensive engine diagnostic..."
    echo ""
    python3 COMPREHENSIVE_ENGINE_DIAGNOSTIC.py 2>&1 | tail -100
else
    echo -e "${YELLOW}⚠️  COMPREHENSIVE_ENGINE_DIAGNOSTIC.py not found${NC}"
    echo "   Creating minimal diagnostic..."
    
    python3 << 'PYEOF'
import sys
import importlib

print("Testing critical imports:")
engines = [
    ('ULTRA_GOLDMINE_FEATURES', 'GammaSqueezeDetector'),
    ('DIVINE_INTELLIGENCE_FEATURES', 'DivineIntelligenceManager'),
    ('critical_features_addon', 'TrailingStopManager'),
    ('EXECUTION_ORCHESTRATOR', 'ExecutionOrchestrator'),
]

working = 0
broken = 0

for module_name, class_name in engines:
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, class_name):
            print(f"  ✅ {module_name}.{class_name}")
            working += 1
        else:
            print(f"  ⚠️  {module_name}.{class_name} - class not found")
            broken += 1
    except Exception as e:
        print(f"  ❌ {module_name} - {str(e)[:50]}")
        broken += 1

print(f"\n📊 Results: {working}/{len(engines)} engines working")
PYEOF
fi
echo ""

# ============================================================================
# 9. CHECK FOR ERRORS IN LOGS
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "🚨 RECENT ERRORS IN LOGS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

for logfile in unified_trading_system.log bot.log apex_bot.log; do
    if [ -f "$logfile" ]; then
        ERROR_COUNT=$(grep -i "error\|exception\|failed\|critical" "$logfile" 2>/dev/null | tail -50 | wc -l)
        if [ $ERROR_COUNT -gt 0 ]; then
            echo -e "${RED}⚠️  Found $ERROR_COUNT recent errors in $logfile:${NC}"
            grep -i "error\|exception\|failed\|critical" "$logfile" | tail -10 | while read line; do
                echo "   $line"
            done
            echo ""
        fi
    fi
done

# ============================================================================
# 10. CHECK ACTIVE TRADING STATUS
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "💰 TRADING STATUS"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Check most recent log for trading activity
for logfile in unified_trading_system.log bot.log apex_bot.log; do
    if [ -f "$logfile" ]; then
        echo "Recent activity in $logfile:"
        
        # Check for trades
        TRADE_COUNT=$(grep -i "trade.*executed\|buy\|sell" "$logfile" 2>/dev/null | tail -20 | wc -l)
        if [ $TRADE_COUNT -gt 0 ]; then
            echo -e "  ${GREEN}✅ Found $TRADE_COUNT recent trade activities${NC}"
            grep -i "trade.*executed\|profit\|balance" "$logfile" | tail -5 | while read line; do
                echo "     $line"
            done
        else
            echo -e "  ${YELLOW}⚠️  No recent trades found${NC}"
        fi
        
        # Check for engine status
        ENGINE_COUNT=$(grep -i "engine.*active\|engine.*running\|initialized" "$logfile" 2>/dev/null | tail -20 | wc -l)
        if [ $ENGINE_COUNT -gt 0 ]; then
            echo -e "  ${GREEN}✅ Found $ENGINE_COUNT engine status messages${NC}"
        fi
        
        echo ""
    fi
done

# ============================================================================
# 11. NETWORK CONNECTIVITY
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "🌐 NETWORK CONNECTIVITY"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

echo "Testing connections to exchanges:"
for host in api.gate.io api.bybit.com api.binance.com; do
    if ping -c 1 -W 2 $host &>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $host - reachable"
    else
        echo -e "  ${RED}❌${NC} $host - unreachable"
    fi
done
echo ""

# ============================================================================
# 12. SYSTEM RESOURCE USAGE
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "📊 SYSTEM RESOURCE USAGE"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

echo "Top Python Processes:"
ps aux | grep python | grep -v grep | head -5 | awk '{printf "  CPU: %s%% | MEM: %s%% | %s\n", $3, $4, $11}' || echo "  No Python processes found"
echo ""

echo "Disk Space:"
df -h | grep -E "Filesystem|/$" | awk '{printf "  %s: %s used of %s (%s)\n", $6, $3, $2, $5}'
echo ""

echo "Memory Usage:"
free -h | awk 'NR==2{printf "  Used: %s / %s (%.0f%%)\n", $3, $2, ($3/$2)*100}'
echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo "════════════════════════════════════════════════════════════════════════"
echo "📊 AUDIT SUMMARY"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Count issues
ISSUES=0

# Check bot running
if [ -z "$BOT_PROCESSES" ]; then
    echo -e "${RED}❌ Bot not running${NC}"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}✅ Bot process active${NC}"
fi

# Check .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file missing${NC}"
    ISSUES=$((ISSUES + 1))
elif grep -q "your_.*_here" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  .env needs configuration${NC}"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}✅ .env configured${NC}"
fi

# Check dependencies
DEP_COUNT=$(python3 -c "import numpy, pandas, ccxt" 2>&1 | grep -c "No module" || echo 0)
if [ $DEP_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Missing dependencies${NC}"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Check critical files
if [ -f "ALL_ENGINES_ACTIVATED.py" ]; then
    echo -e "${GREEN}✅ Engine activation system present${NC}"
else
    echo -e "${YELLOW}⚠️  Engine activation system missing${NC}"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════"

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}🎉 AUDIT COMPLETE: NO CRITICAL ISSUES FOUND!${NC}"
    echo -e "${GREEN}   System appears to be operational${NC}"
else
    echo -e "${YELLOW}⚠️  AUDIT COMPLETE: $ISSUES ISSUE(S) FOUND${NC}"
    echo -e "${YELLOW}   Review the audit results above${NC}"
fi

echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "📝 For detailed engine diagnostic, run:"
echo "   python3 COMPREHENSIVE_ENGINE_DIAGNOSTIC.py"
echo ""
echo "🔧 To fix common issues automatically, run:"
echo "   bash AUTO_FIX_ALL_ISSUES.sh"
echo ""
echo "📖 For complete status report, read:"
echo "   cat FINAL_SYSTEM_STATUS_REPORT.md"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
