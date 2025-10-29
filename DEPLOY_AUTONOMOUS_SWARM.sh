#!/bin/bash
# ============================================================================
# DEPLOY AUTONOMOUS SWARM - SELF-AWARE AUTO-ADJUSTING INTELLIGENCE
# ============================================================================

set -e

echo "============================================================================"
echo "🧠 DEPLOYING AUTONOMOUS SWARM INTELLIGENCE"
echo "============================================================================"
echo ""

cd ~/bot

echo "🔧 Step 1: Pulling autonomous swarm code..."
git fetch origin
git checkout micro-fix-local
git pull origin micro-fix-local
echo "✅ Autonomous swarm code loaded!"
echo ""

echo "🧪 Step 2: Verifying swarm intelligence..."
if [ -f "COLLECTIVE_SWARM_INTELLIGENCE.py" ]; then
    echo "✅ Collective Swarm Intelligence found"
    python3 -m py_compile COLLECTIVE_SWARM_INTELLIGENCE.py
    echo "✅ Swarm intelligence compiles"
else
    echo "❌ COLLECTIVE_SWARM_INTELLIGENCE.py not found!"
    exit 1
fi
echo ""

echo "🔍 Step 3: Verifying orchestrator integration..."
if grep -q "CollectiveSwarmIntelligence" COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "✅ Swarm integrated into orchestrator"
else
    echo "⚠️  Swarm not yet integrated (will work passively)"
fi
echo ""

echo "🛑 Step 4: Stopping old bot..."
pkill -9 -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "   (no bot running)"
sleep 3
echo "✅ Old bot stopped!"
echo ""

echo "🚀 Step 5: Starting AUTONOMOUS SWARM..."
nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!
echo "✅ Swarm started! PID: $BOT_PID"
echo ""

echo "⏳ Waiting 10 seconds for swarm to activate..."
sleep 10
echo ""

echo "🧠 Step 6: Checking swarm intelligence..."
echo ""

# Check for swarm activation
if tail -200 bot.log | grep -q "Collective Swarm Intelligence"; then
    echo "✅ SWARM INTELLIGENCE: ACTIVE"
else
    echo "⚠️  Swarm intelligence initializing..."
fi

# Check for engines
ENGINES_ACTIVE=$(tail -300 bot.log | grep -c "ACTIVE" || echo "0")
echo "✅ Engines Active: $ENGINES_ACTIVE"

# Check for trading
if tail -200 bot.log | grep -q "💎 MICRO TRADE"; then
    echo "✅ Swarm is trading"
    tail -200 bot.log | grep "💎 MICRO TRADE" | tail -3
else
    echo "⏳ Swarm warming up..."
fi
echo ""

echo "============================================================================"
echo "🎉 AUTONOMOUS SWARM DEPLOYED"
echo "============================================================================"
echo ""
echo "SWARM FEATURES:"
echo "  ✅ Self-aware - All engines know each other's state"
echo "  ✅ Auto-adjusting - Changes strategy based on performance"
echo "  ✅ Liquidation prevention - Stops at 20% drawdown"
echo "  ✅ Opportunity maximization - Catches ALL opportunities"
echo "  ✅ Resource sharing - All engines share collective intelligence"
echo ""
echo "SWARM MODES:"
echo "  Recovery: Down >20% → Ultra conservative (85% conf, 5% pos)"
echo "  Conservative: Up >50% → Protect profits (75% conf, 8% pos)"
echo "  Aggressive: Up >10% → Growth mode (65% conf, 12% pos)"
echo "  Balanced: Normal → (70% conf, 10% pos)"
echo ""
echo "Monitoring swarm activity (Ctrl+C to stop)..."
echo ""

# Monitor swarm
tail -f bot.log | grep --line-buffered -E "🧠|🐝|💎|SWARM|TRADE|Mode|consensus" | grep -v "Found.*pairs"
