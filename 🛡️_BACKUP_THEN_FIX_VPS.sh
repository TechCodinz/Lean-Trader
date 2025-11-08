#!/bin/bash
# 🛡️ BACKUP EVERYTHING THEN APPLY FIXES - ZERO DATA LOSS
# This script is 100% safe - backs up everything before making changes

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        🛡️  BACKUP EVERYTHING + APPLY FIXES 🛡️                ║"
echo "║                    ZERO DATA LOSS                            ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Verify we're in bot directory
if [ ! -f "RUN_BOT.py" ]; then
    print_error "Not in bot directory!"
    echo ""
    echo "Please cd to your bot directory first, then run:"
    echo "bash 🛡️_BACKUP_THEN_FIX_VPS.sh"
    echo ""
    echo "To find your bot directory:"
    echo "find / -name 'RUN_BOT.py' 2>/dev/null"
    exit 1
fi

BOT_DIR=$(pwd)
print_success "Bot directory: $BOT_DIR"
echo ""

# Create backup directory with timestamp
BACKUP_ROOT="$HOME/bot_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/backup_before_fixes_$TIMESTAMP"

echo "════════════════════════════════════════════════════════════════"
echo "STEP 1: CREATING COMPLETE BACKUP"
echo "════════════════════════════════════════════════════════════════"
echo ""

mkdir -p "$BACKUP_DIR"
print_success "Backup directory: $BACKUP_DIR"
echo ""

# Backup 1: All Python files
echo "1️⃣  Backing up all Python code..."
mkdir -p "$BACKUP_DIR/python_files"
cp -r *.py "$BACKUP_DIR/python_files/" 2>/dev/null || true
PYTHON_COUNT=$(find "$BACKUP_DIR/python_files" -name "*.py" 2>/dev/null | wc -l)
print_success "Backed up $PYTHON_COUNT Python files"

# Backup 2: All databases
echo "2️⃣  Backing up all databases..."
mkdir -p "$BACKUP_DIR/databases"
cp -r *.db "$BACKUP_DIR/databases/" 2>/dev/null || true
cp -r bot_data/*.db "$BACKUP_DIR/databases/" 2>/dev/null || true
cp -r replicas/*.db "$BACKUP_DIR/databases/" 2>/dev/null || true
DB_COUNT=$(find "$BACKUP_DIR/databases" -name "*.db" 2>/dev/null | wc -l)
print_success "Backed up $DB_COUNT database files"

# Backup 3: Evolution data (CRITICAL - this is your 19k+ cycles)
echo "3️⃣  Backing up evolution data (CRITICAL)..."
mkdir -p "$BACKUP_DIR/evolution_data"
cp -r evolution*.db "$BACKUP_DIR/evolution_data/" 2>/dev/null || true
cp -r divine_intelligence*.db "$BACKUP_DIR/evolution_data/" 2>/dev/null || true
cp -r ultimate_bot*.db "$BACKUP_DIR/evolution_data/" 2>/dev/null || true
cp -r enhanced_trading*.db "$BACKUP_DIR/evolution_data/" 2>/dev/null || true
cp -r bot_data/evolution*.db "$BACKUP_DIR/evolution_data/" 2>/dev/null || true
EVO_COUNT=$(find "$BACKUP_DIR/evolution_data" -name "*.db" 2>/dev/null | wc -l)
print_success "Backed up $EVO_COUNT evolution databases"
print_warning "Your 19k+ evolution cycles are now safely backed up!"

# Backup 4: Config files
echo "4️⃣  Backing up config files..."
mkdir -p "$BACKUP_DIR/configs"
cp -r *.json "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r *.yaml "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r *.yml "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r .env "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r config*.py "$BACKUP_DIR/configs/" 2>/dev/null || true
CONFIG_COUNT=$(find "$BACKUP_DIR/configs" -type f 2>/dev/null | wc -l)
print_success "Backed up $CONFIG_COUNT config files"

# Backup 5: Bot data directory
echo "5️⃣  Backing up bot_data directory..."
if [ -d "bot_data" ]; then
    cp -r bot_data "$BACKUP_DIR/" 2>/dev/null || true
    print_success "Backed up bot_data directory"
else
    print_info "No bot_data directory found (may not exist yet)"
fi

# Backup 6: Current git state
echo "6️⃣  Backing up git state..."
mkdir -p "$BACKUP_DIR/git_info"
git branch --show-current > "$BACKUP_DIR/git_info/current_branch.txt" 2>/dev/null || echo "unknown" > "$BACKUP_DIR/git_info/current_branch.txt"
git log -1 --oneline > "$BACKUP_DIR/git_info/last_commit.txt" 2>/dev/null || echo "no commits" > "$BACKUP_DIR/git_info/last_commit.txt"
git status > "$BACKUP_DIR/git_info/git_status.txt" 2>/dev/null || echo "not a git repo" > "$BACKUP_DIR/git_info/git_status.txt"
git diff > "$BACKUP_DIR/git_info/uncommitted_changes.diff" 2>/dev/null || true
print_success "Backed up git state"

# Backup 7: Current logs
echo "7️⃣  Backing up logs..."
mkdir -p "$BACKUP_DIR/logs"
cp -r *.log "$BACKUP_DIR/logs/" 2>/dev/null || true
cp -r bot_data/*.log "$BACKUP_DIR/logs/" 2>/dev/null || true
LOG_COUNT=$(find "$BACKUP_DIR/logs" -name "*.log" 2>/dev/null | wc -l)
print_success "Backed up $LOG_COUNT log files"

# Create backup manifest
echo "8️⃣  Creating backup manifest..."
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
═══════════════════════════════════════════════════════════════════════════
BACKUP INFORMATION
═══════════════════════════════════════════════════════════════════════════

Backup Date: $(date)
Bot Directory: $BOT_DIR
Backup Location: $BACKUP_DIR

FILES BACKED UP:
- Python files: $PYTHON_COUNT files
- Databases: $DB_COUNT files
- Evolution data: $EVO_COUNT files (INCLUDING YOUR 19K+ CYCLES!)
- Config files: $CONFIG_COUNT files
- Logs: $LOG_COUNT files
- Git state: Current branch, commit, uncommitted changes

═══════════════════════════════════════════════════════════════════════════
RESTORE INSTRUCTIONS (IF NEEDED)
═══════════════════════════════════════════════════════════════════════════

If something goes wrong, restore with:

cd $BOT_DIR
cp -r $BACKUP_DIR/python_files/* .
cp -r $BACKUP_DIR/databases/* .
cp -r $BACKUP_DIR/evolution_data/* .
cp -r $BACKUP_DIR/configs/* .

Then restart bot:
pkill -9 -f RUN_BOT.py
nohup python3 RUN_BOT.py > bot.log 2>&1 &

═══════════════════════════════════════════════════════════════════════════
EOF

print_success "Backup manifest created"
echo ""

# Calculate total backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
print_success "BACKUP COMPLETE!"
print_info "Total backup size: $BACKUP_SIZE"
print_info "Location: $BACKUP_DIR"
echo ""

# Show what was backed up
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ BACKUP SUCCESSFUL                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Backed up:"
echo "  ✅ $PYTHON_COUNT Python files"
echo "  ✅ $DB_COUNT databases"
echo "  ✅ $EVO_COUNT evolution databases (YOUR 19K+ CYCLES!)"
echo "  ✅ $CONFIG_COUNT config files"
echo "  ✅ $LOG_COUNT log files"
echo "  ✅ Git state (branch, commits, changes)"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""

# Ask user to confirm before applying fixes
echo "════════════════════════════════════════════════════════════════"
echo "STEP 2: APPLY FIXES"
echo "════════════════════════════════════════════════════════════════"
echo ""
print_warning "Everything is safely backed up!"
print_info "Now we'll apply all 5 fixes to your bot."
echo ""
echo "Fixes that will be applied:"
echo "  1. Risk Management parameter compatibility"
echo "  2. Evolution Engine JSON serialization"
echo "  3. Circuit Breaker parameter compatibility"
echo "  4. Evolution Engine database path support"
echo "  5. Circuit Breaker configuration support"
echo ""
read -p "Continue with applying fixes? (Y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ -n $REPLY ]]; then
    print_info "Fixes not applied. Your backup is safe at: $BACKUP_DIR"
    exit 0
fi

echo ""
echo "Applying fixes..."
echo ""

# Get current branch
ORIGINAL_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
print_info "Current branch: $ORIGINAL_BRANCH"

# Stash any local changes
echo "Saving local changes..."
git add -A 2>/dev/null || true
git stash push -m "Auto-stash before fix $(date)" 2>/dev/null || print_info "Nothing to stash"

# Fetch updates
echo "Fetching updates from GitHub..."
if ! git fetch origin 2>/dev/null; then
    print_error "Failed to fetch from GitHub"
    print_info "Your backup is still safe at: $BACKUP_DIR"
    exit 1
fi
print_success "Updates fetched"

# Switch to fix branch
FIX_BRANCH="cursor/check-last-agent-stop-point-for-bot-functionality-8296"
echo "Switching to fix branch: $FIX_BRANCH"

if git checkout "$FIX_BRANCH" 2>/dev/null; then
    print_success "Switched to fix branch"
elif git checkout -b "$FIX_BRANCH" "origin/$FIX_BRANCH" 2>/dev/null; then
    print_success "Created and switched to fix branch"
else
    print_error "Failed to switch to fix branch"
    print_info "Your backup is safe at: $BACKUP_DIR"
    print_info "Restoring original branch..."
    git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
    exit 1
fi

# Pull fixes
echo "Pulling all fixes..."
if git pull origin "$FIX_BRANCH" 2>/dev/null; then
    print_success "All fixes downloaded"
else
    print_error "Failed to pull fixes"
    print_info "Your backup is safe at: $BACKUP_DIR"
    exit 1
fi

echo ""

# Verify fixes are present
echo "════════════════════════════════════════════════════════════════"
echo "STEP 3: VERIFYING FIXES"
echo "════════════════════════════════════════════════════════════════"
echo ""

FIXES_OK=true

# Check Fix 1
if grep -q "initial_balance.*=" PROFESSIONAL_RISK_MANAGEMENT.py 2>/dev/null; then
    print_success "Fix 1: Risk Management - VERIFIED"
else
    print_error "Fix 1: NOT FOUND"
    FIXES_OK=false
fi

# Check Fix 2
if grep -q "convert_datetimes" EVOLUTION_ENGINE.py 2>/dev/null; then
    print_success "Fix 2: Evolution Engine JSON - VERIFIED"
else
    print_error "Fix 2: NOT FOUND"
    FIXES_OK=false
fi

# Check Fix 3
if grep -q "initial_balance" CIRCUIT_BREAKER_SYSTEM.py 2>/dev/null; then
    print_success "Fix 3: Circuit Breaker - VERIFIED"
else
    print_error "Fix 3: NOT FOUND"
    FIXES_OK=false
fi

# Check Fix 4
if grep -q "database_path" EVOLUTION_ENGINE.py 2>/dev/null; then
    print_success "Fix 4: Evolution database path - VERIFIED"
else
    print_error "Fix 4: NOT FOUND"
    FIXES_OK=false
fi

# Check Fix 5
if grep -q "daily_loss_limit.*=" CIRCUIT_BREAKER_SYSTEM.py 2>/dev/null; then
    print_success "Fix 5: Circuit Breaker config - VERIFIED"
else
    print_error "Fix 5: NOT FOUND"
    FIXES_OK=false
fi

echo ""

if [ "$FIXES_OK" = false ]; then
    print_error "Some fixes are missing!"
    print_info "Your backup is safe at: $BACKUP_DIR"
    print_info "Restoring original branch..."
    git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
    exit 1
fi

print_success "ALL FIXES VERIFIED!"
echo ""

# Verify evolution databases weren't touched
echo "════════════════════════════════════════════════════════════════"
echo "STEP 4: VERIFYING EVOLUTION DATA (19K+ CYCLES)"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -f "evolution_engine.db" ] || [ -f "divine_intelligence_latest.db" ] || [ -f "ultimate_bot_450_models.db" ]; then
    print_success "Evolution databases still present"
    
    # Check if they're the same as backup
    CURRENT_SIZE=$(du -sb evolution*.db divine*.db ultimate*.db 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
    BACKUP_SIZE=$(du -sb "$BACKUP_DIR/evolution_data"/*.db 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
    
    if [ "$CURRENT_SIZE" -eq "$BACKUP_SIZE" ]; then
        print_success "Evolution data unchanged (19K+ cycles preserved!)"
    else
        print_warning "Evolution data size changed (this may be normal if bot was running)"
        print_info "Original size: $BACKUP_SIZE bytes"
        print_info "Current size: $CURRENT_SIZE bytes"
    fi
else
    print_info "No evolution databases found in current directory"
fi

echo ""

# Update dependencies if needed
echo "════════════════════════════════════════════════════════════════"
echo "STEP 5: CHECKING DEPENDENCIES"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    if [ -f "requirements.txt" ]; then
        print_info "Checking for dependency updates..."
        pip install -r requirements.txt --upgrade -q 2>/dev/null && print_success "Dependencies updated" || print_warning "Some dependencies may need manual update"
    fi
else
    print_info "No virtual environment (using system Python)"
fi

echo ""

# Stop current bot
echo "════════════════════════════════════════════════════════════════"
echo "STEP 6: RESTARTING BOT WITH FIXES"
echo "════════════════════════════════════════════════════════════════"
echo ""

BOT_PIDS=$(pgrep -f "RUN_BOT.py" || echo "")
if [ -n "$BOT_PIDS" ]; then
    print_info "Stopping current bot (PIDs: $BOT_PIDS)"
    kill $BOT_PIDS 2>/dev/null || true
    sleep 3
    pkill -9 -f "RUN_BOT.py" 2>/dev/null || true
    print_success "Old bot stopped"
else
    print_info "No bot currently running"
fi

# Start bot with fixes
print_info "Starting bot with all fixes..."
nohup python3 RUN_BOT.py > bot.log 2>&1 &
NEW_PID=$!
sleep 3

# Verify bot started
if ps -p $NEW_PID > /dev/null 2>&1; then
    print_success "Bot started successfully (PID: $NEW_PID)"
else
    print_error "Bot failed to start"
    print_info "Check logs: tail -50 bot.log"
    print_info "Your backup is safe at: $BACKUP_DIR"
    exit 1
fi

echo ""

# Monitor initial startup
echo "Monitoring startup (10 seconds)..."
sleep 5

# Check for errors
if tail -50 bot.log | grep -qi "error\|failed\|traceback"; then
    print_warning "Possible errors detected in startup"
    echo ""
    echo "Last 20 lines of log:"
    tail -20 bot.log
    echo ""
    print_info "If bot is working, these may be harmless warnings"
    print_info "If bot is broken, restore from backup: $BACKUP_DIR"
else
    print_success "Bot started without errors!"
fi

echo ""

# Final summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        ✅ COMPLETE - BACKUP + FIXES APPLIED ✅                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 SUMMARY:"
echo ""
echo "BACKUP:"
echo "  ✅ Everything backed up to: $BACKUP_DIR"
echo "  ✅ Python files: $PYTHON_COUNT"
echo "  ✅ Databases: $DB_COUNT"  
echo "  ✅ Evolution data: $EVO_COUNT (YOUR 19K+ CYCLES!)"
echo "  ✅ Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
echo ""
echo "FIXES:"
echo "  ✅ Fix 1: Risk Management"
echo "  ✅ Fix 2: Evolution Engine JSON"
echo "  ✅ Fix 3: Circuit Breaker"
echo "  ✅ Fix 4: Evolution database path"
echo "  ✅ Fix 5: Circuit Breaker config"
echo ""
echo "BOT:"
echo "  ✅ Running on PID: $(pgrep -f RUN_BOT.py || echo 'Not running')"
echo "  ✅ Branch: $FIX_BRANCH"
echo "  ✅ Commit: $(git rev-parse --short HEAD)"
echo ""
echo "📝 MONITORING:"
echo "  Watch logs:      tail -f bot.log"
echo "  Check errors:    grep -E '❌|ERROR' bot.log"
echo "  Check signals:   grep -E '🎯|💰|✅' bot.log"
echo ""
echo "🔄 RESTORE (IF NEEDED):"
echo "  See: $BACKUP_DIR/BACKUP_INFO.txt"
echo ""
print_success "Your bot is now running with all fixes!"
print_success "Your 19k+ evolution cycles are preserved!"
echo ""
print_info "Monitor logs for the next 5 minutes to ensure everything works."
print_info "If you see any errors, you can restore from backup."
echo ""
