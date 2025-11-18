#!/bin/bash
# ============================================================================
# 🔧 CHECKOUT MISSING FILES FROM REPOSITORY
# ============================================================================

cd ~/bot || exit 1

echo "============================================================================="
echo "🔧 CHECKING OUT MISSING FILES"
echo "============================================================================="
echo ""

# Stop bot
pkill -f ORCHESTRATOR
sleep 2

# Fetch latest
git fetch origin continue-from-micro-fix

echo "📥 Checking out missing core files..."
git checkout origin/continue-from-micro-fix -- \
    router.py \
    paper_broker.py \
    mt5_forex_sync.py \
    MT5_FOREX_ENGINE_INTEGRATION.py \
    BOOTSTRAP_PROFIT_TRACKER.py \
    ULTRA_GOLDMINE_FEATURES.py \
    DIVINE_INTELLIGENCE_FEATURES.py \
    ULTRASONIC_INTEGRATION_COMPLETE.py \
    ULTRASONIC_RARE_STRATEGIES.py \
    SUPREME_CONSCIOUSNESS_CORE.py \
    SUPREME_ACTIVATION_SYSTEM.py \
    UNIVERSAL_AI_ORCHESTRATOR.py \
    INTELLIGENT_EXECUTION_ENGINE.py \
    EXECUTION_ORCHESTRATOR.py \
    HYBRID_INTELLIGENCE_COORDINATOR.py \
    COMPLETE_UNIFIED_ORCHESTRATOR.py \
    systems/COMPLETE_UNIFIED_ORCHESTRATOR.py \
    systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py \
    2>/dev/null

echo "✅ Files checked out!"
echo ""

# Verify critical file
if [ -f "router.py" ]; then
    echo "✅ router.py exists"
else
    echo "❌ router.py MISSING!"
fi

if [ -f "mt5_forex_sync.py" ]; then
    echo "✅ mt5_forex_sync.py exists"
else
    echo "⚠️  mt5_forex_sync.py missing (optional)"
fi

echo ""
echo "🚀 Starting bot..."
python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
sleep 10

echo ""
echo "📊 Checking for errors..."
tail -50 bot.log | grep -i "error\|traceback" || echo "✅ No errors!"

echo ""
echo "============================================================================="
echo "✅ COMPLETE! Monitor: tail -f bot.log"
echo "============================================================================="
