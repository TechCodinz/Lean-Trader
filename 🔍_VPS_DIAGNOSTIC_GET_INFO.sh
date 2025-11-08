#!/bin/bash
# 🔍 VPS DIAGNOSTIC - GET ALL INFO
# Run this on your VPS to get all the information needed

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🔍 VPS DIAGNOSTIC - COLLECTING ALL INFO"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_section() { echo -e "${BLUE}━━━ $1 ━━━${NC}"; }
print_info() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 1. FIND BOT DIRECTORY
print_section "1. BOT DIRECTORY"
echo ""
echo "Searching for RUN_BOT.py..."
BOT_LOCATIONS=$(find / -name "RUN_BOT.py" 2>/dev/null | head -5)

if [ -z "$BOT_LOCATIONS" ]; then
    echo "❌ RUN_BOT.py not found"
    echo "Searching for other bot files..."
    find / -name "COMPLETE_ULTIMATE_ORCHESTRATOR.py" 2>/dev/null | head -5
else
    echo "$BOT_LOCATIONS"
    BOT_DIR=$(echo "$BOT_LOCATIONS" | head -1 | xargs dirname)
    print_info "Main bot directory: $BOT_DIR"
fi
echo ""

# If we found the bot, get more info
if [ -n "$BOT_DIR" ] && [ -d "$BOT_DIR" ]; then
    cd "$BOT_DIR"
    
    # 2. GIT STATUS
    print_section "2. GIT STATUS"
    echo ""
    
    if [ -d ".git" ]; then
        echo "Current branch:"
        git branch --show-current 2>/dev/null || echo "  (detached)"
        
        echo ""
        echo "Last commit:"
        git log -1 --oneline 2>/dev/null || echo "  (no commits)"
        
        echo ""
        echo "Git remote:"
        git remote -v 2>/dev/null | head -2 || echo "  (no remote)"
        
        echo ""
        echo "Uncommitted changes:"
        git status --short 2>/dev/null | head -10 || echo "  (none)"
        
        echo ""
        echo "Available branches (local):"
        git branch 2>/dev/null | head -10
        
        echo ""
        echo "Available branches (remote):"
        git branch -r 2>/dev/null | grep -E "main|master|cursor|production|deploy" | head -10
    else
        print_warning "Not a git repository"
    fi
    echo ""
    
    # 3. PYTHON ENVIRONMENT
    print_section "3. PYTHON ENVIRONMENT"
    echo ""
    
    echo "Python version:"
    python3 --version 2>/dev/null || echo "  (python3 not found)"
    
    echo ""
    echo "Virtual environment:"
    if [ -d "venv" ]; then
        print_info "venv/ directory exists"
        if [ -f "venv/bin/python" ]; then
            echo "  Python: $(venv/bin/python --version 2>/dev/null)"
        fi
    elif [ -d "apex_venv" ]; then
        print_info "apex_venv/ directory exists"
        if [ -f "apex_venv/bin/python" ]; then
            echo "  Python: $(apex_venv/bin/python --version 2>/dev/null)"
        fi
    else
        print_warning "No virtual environment found"
    fi
    
    echo ""
    echo "Key Python packages:"
    if [ -f "venv/bin/pip" ]; then
        venv/bin/pip list 2>/dev/null | grep -E "ccxt|numpy|pandas|tensorflow" || echo "  (checking...)"
    elif [ -f "apex_venv/bin/pip" ]; then
        apex_venv/bin/pip list 2>/dev/null | grep -E "ccxt|numpy|pandas|tensorflow" || echo "  (checking...)"
    else
        python3 -m pip list 2>/dev/null | grep -E "ccxt|numpy|pandas|tensorflow" || echo "  (using system Python)"
    fi
    echo ""
    
    # 4. EVOLUTION DATABASES
    print_section "4. EVOLUTION DATA (YOUR 19K+ CYCLES)"
    echo ""
    
    echo "Evolution databases found:"
    find . -maxdepth 2 -name "*.db" -type f 2>/dev/null | while read dbfile; do
        SIZE=$(du -h "$dbfile" 2>/dev/null | cut -f1)
        MODIFIED=$(stat -c '%y' "$dbfile" 2>/dev/null | cut -d' ' -f1 || stat -f '%Sm' -t '%Y-%m-%d' "$dbfile" 2>/dev/null)
        echo "  📊 $dbfile"
        echo "     Size: $SIZE | Modified: $MODIFIED"
    done
    
    TOTAL_DB_SIZE=$(du -sh *.db 2>/dev/null | tail -1 | cut -f1 || echo "0")
    echo ""
    print_info "Total database size: $TOTAL_DB_SIZE"
    echo ""
    
    # 5. RUNNING PROCESSES
    print_section "5. RUNNING PROCESSES"
    echo ""
    
    echo "Bot processes:"
    ps aux | grep -E "RUN_BOT|python.*bot|ORCHESTRATOR" | grep -v grep || echo "  (no bot processes running)"
    echo ""
    
    BOT_PID=$(pgrep -f "RUN_BOT.py" 2>/dev/null || pgrep -f "python.*RUN_BOT" 2>/dev/null)
    if [ -n "$BOT_PID" ]; then
        print_info "Bot is RUNNING (PID: $BOT_PID)"
        echo ""
        echo "Bot uptime:"
        ps -p $BOT_PID -o etime= 2>/dev/null || echo "  (unknown)"
    else
        print_warning "Bot is NOT running"
    fi
    echo ""
    
    # 6. LOG FILES
    print_section "6. LOG FILES"
    echo ""
    
    echo "Recent log files:"
    ls -lht *.log 2>/dev/null | head -5 || echo "  (no log files found)"
    
    echo ""
    if [ -f "bot.log" ]; then
        LOG_SIZE=$(du -h bot.log 2>/dev/null | cut -f1)
        print_info "bot.log size: $LOG_SIZE"
        
        echo ""
        echo "Last 5 lines of bot.log:"
        tail -5 bot.log 2>/dev/null | sed 's/^/  /'
    fi
    echo ""
    
    # 7. DISK SPACE
    print_section "7. DISK SPACE"
    echo ""
    
    echo "Disk usage for bot directory:"
    du -sh "$BOT_DIR" 2>/dev/null
    
    echo ""
    echo "Available disk space:"
    df -h "$BOT_DIR" 2>/dev/null | tail -1 | awk '{print "  Total: "$2" | Used: "$3" | Available: "$4" | Use%: "$5}'
    echo ""
    
    # 8. CONFIG FILES
    print_section "8. CONFIG FILES"
    echo ""
    
    echo "Config files found:"
    ls -lh .env 2>/dev/null && echo "  ✅ .env exists" || echo "  ⚠️  .env not found"
    ls -lh config*.py 2>/dev/null | head -3
    ls -lh *.json 2>/dev/null | head -3
    ls -lh requirements.txt 2>/dev/null && echo "  ✅ requirements.txt exists" || echo "  ⚠️  requirements.txt not found"
    echo ""
    
    # 9. KEY FILES CHECK
    print_section "9. KEY FILES CHECK"
    echo ""
    
    echo "Checking for critical files:"
    [ -f "RUN_BOT.py" ] && print_info "RUN_BOT.py exists" || echo "❌ RUN_BOT.py missing"
    [ -f "COMPLETE_ULTIMATE_ORCHESTRATOR.py" ] && print_info "COMPLETE_ULTIMATE_ORCHESTRATOR.py exists" || echo "⚠️  COMPLETE_ULTIMATE_ORCHESTRATOR.py missing"
    [ -f "PROFESSIONAL_RISK_MANAGEMENT.py" ] && print_info "PROFESSIONAL_RISK_MANAGEMENT.py exists" || echo "⚠️  PROFESSIONAL_RISK_MANAGEMENT.py missing"
    [ -f "EVOLUTION_ENGINE.py" ] && print_info "EVOLUTION_ENGINE.py exists" || echo "⚠️  EVOLUTION_ENGINE.py missing"
    [ -f "CIRCUIT_BREAKER_SYSTEM.py" ] && print_info "CIRCUIT_BREAKER_SYSTEM.py exists" || echo "⚠️  CIRCUIT_BREAKER_SYSTEM.py missing"
    echo ""
    
    # 10. BACKUP CHECK
    print_section "10. EXISTING BACKUPS"
    echo ""
    
    if [ -d "$HOME/bot_backups" ]; then
        print_info "Backup directory exists: $HOME/bot_backups"
        echo ""
        echo "Recent backups:"
        ls -lht "$HOME/bot_backups" 2>/dev/null | head -6 || echo "  (no backups found)"
    else
        print_warning "No backup directory found at $HOME/bot_backups"
    fi
    echo ""
    
else
    print_warning "Could not determine bot directory automatically"
    echo ""
    echo "Please manually provide:"
    echo "  - Bot directory path"
    echo "  - Current location: $(pwd)"
fi

# 11. SYSTEM INFO
print_section "11. SYSTEM INFO"
echo ""

echo "OS:"
uname -a 2>/dev/null | sed 's/^/  /'

echo ""
echo "Memory:"
free -h 2>/dev/null | grep -E "Mem:|Swap:" | sed 's/^/  /' || echo "  (not available)"

echo ""
echo "User:"
whoami
echo ""

# SUMMARY
echo "════════════════════════════════════════════════════════════════════════════════"
echo "📋 DIAGNOSTIC SUMMARY"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

if [ -n "$BOT_DIR" ]; then
    echo "✅ Bot directory found: $BOT_DIR"
    
    if [ -d "$BOT_DIR/.git" ]; then
        CURRENT_BRANCH=$(cd "$BOT_DIR" && git branch --show-current 2>/dev/null)
        echo "✅ Git repository: Yes"
        echo "✅ Current branch: $CURRENT_BRANCH"
    fi
    
    if [ -n "$BOT_PID" ]; then
        echo "✅ Bot status: RUNNING (PID: $BOT_PID)"
    else
        echo "⚠️  Bot status: NOT RUNNING"
    fi
    
    if [ -d "$BOT_DIR/venv" ] || [ -d "$BOT_DIR/apex_venv" ]; then
        echo "✅ Virtual environment: Yes"
    fi
    
    DB_COUNT=$(find "$BOT_DIR" -maxdepth 2 -name "*.db" 2>/dev/null | wc -l)
    echo "✅ Database files: $DB_COUNT found"
else
    echo "❌ Bot directory: NOT FOUND"
    echo ""
    echo "Please manually locate your bot directory and cd into it,"
    echo "then run this script again from that directory."
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "🎯 NEXT STEPS"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Copy ALL the output above and send it back."
echo "Then I'll give you the EXACT commands for your VPS setup!"
echo ""
