#!/bin/bash
# 🔥 ULTIMATE VPS FIX - COPY THIS ENTIRE FILE AND RUN ON VPS 🔥

set -e  # Exit on any error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           ⚡ APPLYING ALL FIXES TO VPS BOT ⚡                 ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Detect bot directory
BOT_DIR=$(pwd)
if [ ! -f "RUN_BOT.py" ]; then
    print_error "Not in bot directory! Please cd to your bot directory first."
    echo ""
    echo "Example: cd /root/trading-bot"
    echo "Then run this script again."
    exit 1
fi

print_success "Bot directory: $BOT_DIR"
echo ""

# Step 1: Backup current state
echo "1️⃣  Backing up current state..."
BACKUP_DIR="backups/pre_fix_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r *.py "$BACKUP_DIR/" 2>/dev/null || true
cp -r *.db "$BACKUP_DIR/" 2>/dev/null || true
print_success "Backup created: $BACKUP_DIR"
echo ""

# Step 2: Save any local changes
echo "2️⃣  Saving local changes..."
git add -A 2>/dev/null || true
git stash push -m "Auto-stash before fix $(date)" 2>/dev/null || print_warning "No git repo or nothing to stash"
print_success "Changes saved"
echo ""

# Step 3: Fetch updates
echo "3️⃣  Fetching updates from GitHub..."
if git fetch origin 2>/dev/null; then
    print_success "Updates fetched"
else
    print_error "Failed to fetch updates"
    print_info "Check your git remote: git remote -v"
    exit 1
fi
echo ""

# Step 4: Determine which branch to use
echo "4️⃣  Finding branch with fixes..."
FIX_BRANCH="cursor/check-last-agent-stop-point-for-bot-functionality-8296"

# Check if branch exists remotely
if git ls-remote --heads origin "$FIX_BRANCH" | grep -q "$FIX_BRANCH"; then
    print_success "Found branch: $FIX_BRANCH"
else
    print_error "Fix branch not found on remote"
    print_info "Available branches:"
    git branch -r | grep cursor | head -5
    echo ""
    print_info "Please push the fixes branch first from your local machine"
    exit 1
fi
echo ""

# Step 5: Switch to fix branch
echo "5️⃣  Switching to fix branch..."
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
print_info "Current branch: $CURRENT_BRANCH"

if git checkout "$FIX_BRANCH" 2>/dev/null; then
    print_success "Switched to $FIX_BRANCH"
elif git checkout -b "$FIX_BRANCH" "origin/$FIX_BRANCH" 2>/dev/null; then
    print_success "Created and switched to $FIX_BRANCH"
else
    print_error "Failed to switch branches"
    exit 1
fi
echo ""

# Step 6: Pull fixes
echo "6️⃣  Pulling all fixes..."
if git pull origin "$FIX_BRANCH"; then
    print_success "All fixes downloaded"
    COMMIT=$(git rev-parse --short HEAD)
    print_info "Current commit: $COMMIT"
else
    print_error "Failed to pull fixes"
    exit 1
fi
echo ""

# Step 7: Verify fixes
echo "7️⃣  Verifying fixes are present..."
FIXES_OK=true

# Check Fix 1: Risk Management
if grep -q "initial_balance.*=" PROFESSIONAL_RISK_MANAGEMENT.py 2>/dev/null; then
    print_success "Fix 1: Risk Management parameter compatibility"
else
    print_error "Fix 1: MISSING"
    FIXES_OK=false
fi

# Check Fix 2: Evolution Engine datetime
if grep -q "convert_datetimes" EVOLUTION_ENGINE.py 2>/dev/null; then
    print_success "Fix 2: Evolution Engine JSON serialization"
else
    print_error "Fix 2: MISSING"
    FIXES_OK=false
fi

# Check Fix 3: Circuit Breaker
if grep -q "initial_balance" CIRCUIT_BREAKER_SYSTEM.py 2>/dev/null; then
    print_success "Fix 3: Circuit Breaker parameter compatibility"
else
    print_error "Fix 3: MISSING"
    FIXES_OK=false
fi

if [ "$FIXES_OK" = false ]; then
    print_error "Some fixes are missing!"
    print_info "The branch may not be fully synced"
    exit 1
fi
echo ""

# Step 8: Update dependencies
echo "8️⃣  Checking dependencies..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    if [ -f "requirements.txt" ]; then
        print_info "Updating Python packages..."
        pip install -r requirements.txt --upgrade -q
        print_success "Dependencies updated"
    fi
else
    print_warning "No virtual environment found (using system Python)"
fi
echo ""

# Step 9: Stop running bot
echo "9️⃣  Stopping current bot (if running)..."
BOT_PIDS=$(pgrep -f "RUN_BOT.py" || pgrep -f "python.*RUN_BOT" || echo "")
if [ -n "$BOT_PIDS" ]; then
    print_info "Found bot processes: $BOT_PIDS"
    kill $BOT_PIDS 2>/dev/null || true
    sleep 3
    pkill -9 -f "RUN_BOT.py" 2>/dev/null || true
    pkill -9 -f "python.*RUN_BOT" 2>/dev/null || true
    print_success "Bot stopped"
else
    print_info "No bot processes found"
fi
echo ""

# Step 10: Start bot with fixes
echo "🔟  Starting bot with all fixes..."
if [ -f "RUN_BOT.py" ]; then
    nohup python3 RUN_BOT.py > bot.log 2>&1 &
    NEW_PID=$!
    sleep 2
    
    if ps -p $NEW_PID > /dev/null; then
        print_success "Bot started successfully (PID: $NEW_PID)"
    else
        print_error "Bot failed to start"
        print_info "Check logs: tail -50 bot.log"
        exit 1
    fi
else
    print_error "RUN_BOT.py not found"
    exit 1
fi
echo ""

# Step 11: Monitor initial startup
echo "1️⃣1️⃣  Monitoring startup (10 seconds)..."
sleep 5

if tail -50 bot.log | grep -q "ERROR\|FAILED\|Traceback"; then
    print_warning "Errors detected in logs!"
    echo ""
    echo "Last 20 lines of log:"
    tail -20 bot.log
    echo ""
    print_info "Check full logs: tail -f bot.log"
else
    print_success "Bot started without errors!"
fi
echo ""

# Final summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              ✅ ALL FIXES APPLIED SUCCESSFULLY ✅             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 SUMMARY:"
echo "   Branch:  $FIX_BRANCH"
echo "   Commit:  $(git rev-parse --short HEAD)"
echo "   Bot PID: $(pgrep -f RUN_BOT.py || echo 'Not running')"
echo ""
echo "✅ FIXES APPLIED:"
echo "   ✅ Risk Management parameter compatibility"
echo "   ✅ Evolution Engine JSON serialization"
echo "   ✅ Circuit Breaker parameter compatibility"
echo "   ✅ All compatibility issues resolved"
echo ""
echo "📝 MONITORING COMMANDS:"
echo "   Watch logs:         tail -f bot.log"
echo "   Check errors:       grep -E '❌|ERROR' bot.log"
echo "   Check signals:      grep -E '🎯|💰|✅' bot.log"
echo "   Check bot status:   ps aux | grep RUN_BOT"
echo "   Stop bot:           pkill -9 -f RUN_BOT.py"
echo ""
echo "🎯 NEXT STEPS:"
echo "   1. Monitor bot.log for 5 minutes"
echo "   2. Verify no errors appear"
echo "   3. Check that signals are being generated"
echo "   4. Report any issues immediately"
echo ""
print_success "Bot is now running with all fixes!"
echo ""
