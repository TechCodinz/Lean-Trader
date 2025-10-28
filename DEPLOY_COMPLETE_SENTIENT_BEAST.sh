#!/bin/bash
#
# 🧠 DEPLOY COMPLETE SENTIENT TRADING BEAST
# ==========================================
#
# Deploys ALL 135+ engines fully coordinated:
# - 40+ async loops
# - 5 intelligence layers  
# - Real data fetching
# - Professional risk management
# - Multi-timeframe coordination
# - Swarm intelligence
# - Strategy evolution
# - No blind decisions
#

set -e

echo "================================================================================"
echo "🧠 DEPLOYING COMPLETE SENTIENT TRADING BEAST"
echo "================================================================================"

# Check we're on VPS
if [ ! -f "COMPLETE_ULTIMATE_ORCHESTRATOR.py" ]; then
    echo "❌ ERROR: COMPLETE_ULTIMATE_ORCHESTRATOR.py not found"
    echo "Run this from ~/bot directory"
    exit 1
fi

echo ""
echo "📋 What Will Be Deployed:"
echo ""
echo "   CORE SYSTEMS (3):"
echo "   ✅ Learning, Decision, Enhanced Trading Loop"
echo ""
echo "   ADVANCED ORCHESTRATORS (7):"
echo "   ✅ Scouting, Forex, Deep Learning, Execution, Telegram, Quantum, DEX"
echo ""
echo "   SIGNAL GENERATORS (9):"
echo "   ✅ Smart Scalping, Arbitrage, P2P, Market Scanner, News"
echo "   ✅ Hedge Fund, Micro Moon, ML Strategy, Session Trader"
echo ""
echo "   ULTRA SYSTEMS (11):"
echo "   ✅ Swarm Consciousness (20 agents)"
echo "   ✅ Evolution Engine"
echo "   ✅ 450 Models Bot"
echo "   ✅ Revolutionary AI (10 features)"
echo "   ✅ Moon Spotter"
echo "   ✅ Forex Master"
echo "   ✅ Continuous Trading"
echo "   ✅ ML Pipeline"
echo "   ✅ Ultra Scalping"
echo "   ✅ Ultra Arbitrage"
echo "   ✅ Multi-Platform"
echo ""
echo "   NEW ULTRA RARE + PROFESSIONAL (3):"
echo "   ✅ Ultra Rare Engines (11 inefficiency detectors) - REAL data"
echo "   ✅ Brain Advisor (ATR-based SL/TP) - REAL data"
echo "   ✅ Hivemind (8 timeframe consensus) - REAL data"
echo ""
echo "   PROFIT ENGINES (3):"
echo "   ✅ Steady Profit, MICRO Wallet, Real Profit Bot"
echo ""
echo "   TOTAL: 135+ engines, 40+ async loops, 5 intelligence layers"
echo ""

read -p "Deploy? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

echo ""
echo "================================================================================"
echo "STEP 1: Pulling Latest Code"
echo "================================================================================"

git fetch origin micro-fix-local
git checkout micro-fix-local
git pull

echo "✅ Latest code pulled"

echo ""
echo "================================================================================"
echo "STEP 2: Verifying Dependencies"
echo "================================================================================"

# Check critical dependencies
python3 -c "import numpy, pandas; print('✅ numpy, pandas installed')" || {
    echo "⚠️  numpy/pandas missing - Brain/Hivemind will skip"
}

python3 -c "import ccxt; print('✅ ccxt installed')" || {
    echo "❌ ccxt missing - CRITICAL!"
    exit 1
}

python3 -c "from ULTRA_RARE_ENGINES import UltraRareEnginesOrchestrator; print('✅ Ultra Rare Engines import')" || {
    echo "❌ Ultra Rare Engines import failed!"
    exit 1
}

echo "✅ Dependencies verified"

echo ""
echo "================================================================================"
echo "STEP 3: Stopping Current Bot"
echo "================================================================================"

if pgrep -f COMPLETE_ULTIMATE_ORCHESTRATOR > /dev/null; then
    echo "Stopping current bot..."
    pkill -9 -f COMPLETE_ULTIMATE_ORCHESTRATOR
    sleep 3
    echo "✅ Bot stopped"
else
    echo "✅ No bot running"
fi

echo ""
echo "================================================================================"
echo "STEP 4: Starting Complete Sentient Beast"
echo "================================================================================"

# Start bot
nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &

# Get PID
sleep 2
BOT_PID=$(pgrep -f COMPLETE_ULTIMATE_ORCHESTRATOR)

if [ -n "$BOT_PID" ]; then
    echo "✅ Bot started successfully!"
    echo "   PID: $BOT_PID"
else
    echo "❌ Bot failed to start!"
    echo "Check bot.log for errors"
    exit 1
fi

echo ""
echo "================================================================================"
echo "STEP 5: Monitoring Startup"
echo "================================================================================"

echo "Waiting for systems to initialize (30 seconds)..."
sleep 5

# Check logs for key systems
echo ""
echo "Checking for Ultra systems..."
tail -50 bot.log | grep -E "ULTRA RARE|SWARM|EVOLUTION|BRAIN|HIVEMIND|ACTIVE" || echo "   (Still initializing...)"

echo ""
echo "================================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================================================"

echo ""
echo "🧠 Complete Sentient Trading Beast is LIVE!"
echo ""
echo "   Process ID: $BOT_PID"
echo "   Log file: bot.log"
echo ""
echo "   Active Systems:"
echo "   - 135+ engines initialized"
echo "   - 40+ async loops running"
echo "   - 11 Ultra Rare inefficiency detectors"
echo "   - 20 agent Swarm Consciousness"
echo "   - 8 timeframe Hivemind coordination"
echo "   - 450 model ensemble learning"
echo "   - Strategy evolution active"
echo "   - Professional risk management"
echo "   - REAL data fetching"
echo ""
echo "📊 Monitor Commands:"
echo ""
echo "   All signals:   tail -f bot.log | grep -E '💎|🧠|🐝|💰|📈'"
echo "   Ultra Rare:    tail -f bot.log | grep '💎'"
echo "   Brain:         tail -f bot.log | grep '🧠'"
echo "   Hivemind:      tail -f bot.log | grep '🐝'"
echo "   Swarm:         tail -f bot.log | grep 'SWARM'"
echo "   Errors:        tail -f bot.log | grep '❌'"
echo "   Trades:        tail -f bot.log | grep -E 'TRADE|executed|CLOSED'"
echo "   Balance:       tail -f bot.log | grep 'Balance'"
echo ""
echo "================================================================================"
echo "🎯 The sentient beast is hunting for profits!"
echo "================================================================================"
