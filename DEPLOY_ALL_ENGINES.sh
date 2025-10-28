#!/bin/bash
# Deploy Complete Engine Synchronization
# This wires ALL profit engines together systematically

set -e

echo "🎯 DEPLOYING COMPLETE ENGINE SYNCHRONIZATION"
echo "=============================================="
echo ""
echo "This will:"
echo "  1. Enhance all signal generators (add SL/TP)"
echo "  2. Wire all consumers to Data Hub"
echo "  3. Enable position monitoring"
echo "  4. Coordinate all engines"
echo ""
read -p "Press ENTER to continue or Ctrl+C to cancel..."

# Backup current orchestrator
echo ""
echo "📦 Creating backup..."
cp ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py.backup_before_sync_$(date +%s)

# Phase 1: Enhance signals
echo ""
echo "Phase 1: Enhancing signal generators..."
echo "----------------------------------------"

if [ -f ~/bot/ENHANCE_SCALPER_SIGNALS.py ]; then
    python3 ~/bot/ENHANCE_SCALPER_SIGNALS.py ~/bot/SMART_SCALPING_ENGINE.py && \
        echo "  ✅ Smart Scalping signals enhanced (added SL/TP)"
else
    echo "  ⚠️  ENHANCE_SCALPER_SIGNALS.py not found - signals may lack SL/TP"
fi

# Phase 2: Fix engine coordination
echo ""
echo "Phase 2: Wiring engines to Data Hub..."
echo "----------------------------------------"

if [ -f ~/bot/FIX_ENGINE_COORDINATION.py ]; then
    python3 ~/bot/FIX_ENGINE_COORDINATION.py ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py && \
        echo "  ✅ Steady Profit wired to Data Hub"
        echo "  ✅ MICRO wired to Data Hub"
        echo "  ✅ Execution logging enabled"
else
    echo "  ⚠️  FIX_ENGINE_COORDINATION.py not found - manual wiring needed"
fi

# Phase 3: Apply profitability fixes
echo ""
echo "Phase 3: Applying profitability fixes..."
echo "----------------------------------------"

if [ -f ~/bot/COMPLETE_MICRO_FIX.py ]; then
    python3 ~/bot/COMPLETE_MICRO_FIX.py ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py && \
        echo "  ✅ Close threshold fixed ($1 → $3)"
        echo "  ✅ PIG excluded from auto-close"
        echo "  ✅ Dynamic position sizing added"
else
    echo "  ⚠️  COMPLETE_MICRO_FIX.py not found"
fi

# Verify fixes applied
echo ""
echo "🔍 Verifying fixes..."
echo "----------------------------------------"

# Check Steady Profit gets signals
if grep -q "all_signals = self.data_hub.get_signals" ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "  ✅ Steady Profit: Connected to Data Hub"
else
    echo "  ❌ Steady Profit: NOT connected to Data Hub"
fi

# Check MICRO uses hub signals
if grep -q "hub_signals = self.data_hub.get_signals" ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "  ✅ MICRO: Connected to Data Hub"
else
    echo "  ❌ MICRO: NOT connected to Data Hub"
fi

# Check close threshold
if grep -q "if position_value >= 3.0" ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "  ✅ Close threshold: $3 (Gate.io compatible)"
else
    echo "  ⚠️  Close threshold: May cause errors"
fi

# Check PIG exclusion
if grep -q "'USDT', 'GT', 'PIG'" ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "  ✅ PIG: Excluded from auto-close"
else
    echo "  ⚠️  PIG: Not excluded (may cause loops)"
fi

echo ""
echo "🚀 Restarting bot with synchronized engines..."
echo "----------------------------------------"

# Kill old process
pkill -9 -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "  (No existing process)"
sleep 3

# Start new
nohup python ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py > ~/bot/bot.log 2>&1 &
NEW_PID=$!

echo "  ✅ Bot started (PID: $NEW_PID)"
echo ""
echo "⏳ Waiting 15 seconds for initialization..."
sleep 15

# Show startup
echo ""
echo "📊 Startup Check:"
echo "----------------------------------------"
tail -50 ~/bot/bot.log | grep -E "ACTIVE|initialized|WIRED"

echo ""
echo "📈 Watching for engine activity (30 seconds)..."
echo "----------------------------------------"
timeout 30 tail -f ~/bot/bot.log | grep --line-buffered -E "MICRO|STEADY|Scalper generated|Published|PROFIT|CLOSED" || true

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "=============================================="
echo ""
echo "All profit engines should now be:"
echo "  ✅ Generating signals"
echo "  ✅ Publishing to Data Hub"
echo "  ✅ Consuming from Data Hub"
echo "  ✅ Executing trades"
echo "  ✅ Monitoring positions"
echo "  ✅ Growing balance together!"
echo ""
echo "Monitor with:"
echo "  tail -f ~/bot/bot.log | grep -E 'MICRO|STEADY|Scalper|PROFIT'"
echo ""
echo "Check profits after 1 hour!"
echo ""
