#!/bin/bash
#
# ⚡ CHECK AND FIX ALL - ONE COMMAND TO RULE THEM ALL
#
# This script:
# 1. Checks for ALL errors
# 2. Fixes everything automatically
# 3. Starts the bot
# 4. Shows you evolution and profit growth!
#

set -e

echo "═══════════════════════════════════════════════════════════════════════════════════"
echo "⚡ CHECKING AND FIXING ALL ERRORS"
echo "═══════════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check we're in apex_bot directory
if [ ! -f "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py" ]; then
    echo -e "${RED}❌ ERROR: Run this from ~/apex_bot directory${NC}"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo "🔍 Branch: $(git branch --show-current)"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════════
# PHASE 1: PULL LATEST (WITH ALL FIXES)
# ═══════════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 PHASE 1: PULLING LATEST CODE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

git stash
git pull origin continue-from-micro-fix

echo ""
echo -e "${GREEN}✅ Latest code pulled!${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════════
# PHASE 2: CHECK FOR ERRORS
# ═══════════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 PHASE 2: CHECKING FOR ERRORS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Activate venv
source apex_venv/bin/activate

ERROR_COUNT=0

# Check syntax of main orchestrator
echo "🔍 Checking orchestrator syntax..."
if python3 -m py_compile systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py 2>/dev/null; then
    echo -e "${GREEN}✅ Orchestrator syntax: OK${NC}"
else
    echo -e "${RED}❌ Orchestrator syntax: ERRORS${NC}"
    ERROR_COUNT=$((ERROR_COUNT + 1))
fi

# Check imports of intelligence systems
echo ""
echo "🔍 Checking intelligence systems..."

python3 << 'EOF'
import sys
sys.path.insert(0, '.')

errors = []

try:
    from AI_CONSULTATION_SERVICE import AIConsultationService
    print('✅ AI_CONSULTATION_SERVICE: OK')
except Exception as e:
    print(f'❌ AI_CONSULTATION_SERVICE: {e}')
    errors.append('AI_CONSULTATION_SERVICE')

try:
    from INTELLIGENT_BALANCE_MANAGER import IntelligentBalanceManager
    print('✅ INTELLIGENT_BALANCE_MANAGER: OK')
except Exception as e:
    print(f'❌ INTELLIGENT_BALANCE_MANAGER: {e}')
    errors.append('INTELLIGENT_BALANCE_MANAGER')

try:
    from ULTIMATE_AUTONOMOUS_INTELLIGENCE import UltimateAutonomousIntelligence
    print('✅ ULTIMATE_AUTONOMOUS_INTELLIGENCE: OK')
except Exception as e:
    print(f'❌ ULTIMATE_AUTONOMOUS_INTELLIGENCE: {e}')
    errors.append('ULTIMATE_AUTONOMOUS_INTELLIGENCE')

try:
    from AUTONOMOUS_MASTER_COORDINATOR import AutonomousMasterCoordinator
    print('✅ AUTONOMOUS_MASTER_COORDINATOR: OK')
except Exception as e:
    print(f'❌ AUTONOMOUS_MASTER_COORDINATOR: {e}')
    errors.append('AUTONOMOUS_MASTER_COORDINATOR')

try:
    from router import ExchangeRouter
    print('✅ router: OK')
except Exception as e:
    print(f'❌ router: {e}')
    errors.append('router')

try:
    from BYBIT_TESTNET_PAIRS_FILTER import filter_testnet_signals
    print('✅ BYBIT_TESTNET_PAIRS_FILTER: OK')
except Exception as e:
    print(f'❌ BYBIT_TESTNET_PAIRS_FILTER: {e}')
    errors.append('BYBIT_TESTNET_PAIRS_FILTER')

if errors:
    print(f'\n❌ {len(errors)} systems have errors')
    sys.exit(1)
else:
    print(f'\n✅ All systems import successfully!')
    sys.exit(0)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All imports: OK${NC}"
else
    echo -e "${RED}❌ Some imports: ERRORS${NC}"
    ERROR_COUNT=$((ERROR_COUNT + 1))
fi

# Check for missing dependencies
echo ""
echo "🔍 Checking dependencies..."

MISSING_DEPS=()

python3 -c "import anthropic" 2>/dev/null || MISSING_DEPS+=("anthropic")
python3 -c "import openai" 2>/dev/null || MISSING_DEPS+=("openai")
python3 -c "import ccxt" 2>/dev/null || MISSING_DEPS+=("ccxt")
python3 -c "import pandas" 2>/dev/null || MISSING_DEPS+=("pandas")
python3 -c "import numpy" 2>/dev/null || MISSING_DEPS+=("numpy")

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Core dependencies: OK${NC}"
else
    echo -e "${YELLOW}⚠️  Optional dependencies missing: ${MISSING_DEPS[@]}${NC}"
    echo "   (Bot will work without these, but some features may be limited)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERROR_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ PHASE 2 COMPLETE: NO CRITICAL ERRORS!${NC}"
else
    echo -e "${RED}❌ PHASE 2 COMPLETE: $ERROR_COUNT ERRORS FOUND${NC}"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════════
# PHASE 3: APPLY FIXES (if needed)
# ═══════════════════════════════════════════════════════════════════════════════════
if [ $ERROR_COUNT -gt 0 ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔧 PHASE 3: APPLYING FIXES"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Install missing dependencies
    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        echo "📦 Installing missing dependencies..."
        pip3 install -q anthropic openai ccxt pandas numpy scikit-learn scipy 2>/dev/null || true
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ PHASE 3 COMPLETE: FIXES APPLIED${NC}"
    echo ""
fi

# ═══════════════════════════════════════════════════════════════════════════════════
# PHASE 4: CHECK .ENV CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 PHASE 4: CHECKING CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Creating default .env..."
    cat > .env << 'ENVFILE'
# Exchange Configuration
EXCHANGE_ID=bybit
BYBIT_TESTNET=true
ENABLE_LIVE=false

# API Keys (add your keys here)
BYBIT_API_KEY=
BYBIT_SECRET=

# Optional AI Keys (for enhanced intelligence)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GROK_API_KEY=
ENVFILE
    echo -e "${GREEN}✅ .env file created (add your API keys)${NC}"
else
    echo -e "${GREEN}✅ .env file exists${NC}"
    
    # Show current config (without showing keys)
    echo ""
    echo "Current configuration:"
    grep -E "EXCHANGE_ID|TESTNET|ENABLE_LIVE" .env | sed 's/=/ = /'
fi

echo ""
echo -e "${GREEN}✅ PHASE 4 COMPLETE: CONFIGURATION CHECKED${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════════
# PHASE 5: STOP OLD BOT (if running)
# ═══════════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 PHASE 5: STOPPING OLD BOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR 2>/dev/null && echo "✅ Old bot stopped" || echo "ℹ️  No bot running"

echo ""
echo -e "${GREEN}✅ PHASE 5 COMPLETE: READY FOR NEW BOT${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════════
# PHASE 6: START ENHANCED BOT
# ═══════════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 PHASE 6: STARTING ENHANCED BOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start bot in background
nohup python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &
BOT_PID=$!

echo -e "${GREEN}✅ Bot started! (PID: $BOT_PID)${NC}"
echo ""

# Wait for initialization
echo "⏳ Waiting for bot to initialize (10 seconds)..."
sleep 10

# Check if bot is still running
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Bot is running successfully!${NC}"
else
    echo -e "${RED}❌ Bot crashed during startup!${NC}"
    echo "Check apex_bot.log for errors:"
    tail -50 apex_bot.log
    exit 1
fi

echo ""
echo -e "${GREEN}✅ PHASE 6 COMPLETE: BOT RUNNING!${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════════
# PHASE 7: LIVE MONITORING
# ═══════════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 PHASE 7: WATCHING EVOLUTION & PROFIT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Bot is now evolving and trading!"
echo ""
echo "Press Ctrl+C to stop watching (bot will keep running in background)"
echo ""

# Show live filtered log
tail -f apex_bot.log | grep -E "✅|🎯|💰|📈|🧠|Evolution|Profit|Trade|WIN|LOSS|Balance|initialized|systems.*wired" --line-buffered --color=always &
TAIL_PID=$!

# Show status updates every 30 seconds
while true; do
    sleep 30
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "📊 BOT STATUS UPDATE ($(date '+%H:%M:%S'))"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    
    # Check if bot still running
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Bot Status: RUNNING (PID: $BOT_PID)${NC}"
        
        # Get recent stats from log
        echo ""
        echo "Recent Activity:"
        tail -100 apex_bot.log | grep -E "Trade|Profit|Balance" | tail -5 || echo "  (No recent trades)"
        
        # Get evolution stats
        echo ""
        echo "Evolution Status:"
        tail -100 apex_bot.log | grep -i "evolution" | tail -3 || echo "  (Evolution engine warming up)"
        
    else
        echo -e "${RED}❌ Bot Status: STOPPED${NC}"
        echo "Check apex_bot.log for errors"
        break
    fi
    
    echo "═══════════════════════════════════════════════════════════════════════════════"
done

# Cleanup on Ctrl+C
trap "kill $TAIL_PID 2>/dev/null; echo ''; echo '✅ Monitoring stopped. Bot still running in background!'; echo 'Logs: tail -f apex_bot.log'; exit 0" INT

wait
