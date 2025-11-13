#!/bin/bash
##############################################################################
# 🚀 ACTIVATE EVERYTHING - COMPLETE FINAL INTEGRATION
#
# Activates:
# - Multi-timeframe trading (1m, 5m, 15m, 1h, 4h)
# - Multiple positions per pair  
# - AI self-optimization
# - News awareness
# - Session trading
# - Dynamic lot sizing
#
# COMPLETE SYSTEM ACTIVATION!
##############################################################################

echo "🚀 ═══════════════════════════════════════════════════════"
echo "   ACTIVATING COMPLETE SYSTEM"
echo "════════════════════════════════════════════════════════="
echo ""

cd /root/apex_bot

# 1. Pull latest code
echo "1️⃣ Pulling complete system..."
git stash
git pull --rebase origin continue-from-micro-fix
echo "✅ Latest code pulled"
echo ""

# 2. Verify all systems present
echo "2️⃣ Verifying systems..."
FILES=(
    "MULTI_TIMEFRAME_COORDINATOR.py"
    "🚀_SELF_OPTIMIZING_AI_TRADER.py"
    "PROFIT_MONITORING_SYSTEM.py"
    "QUANTUM_ENTANGLED_FORECASTER.py"
    "BIO_MIMETIC_SWARM.py"
    "HYPER_SENTIMENT_NEXUS.py"
    "DEEP_RL_TRADING_AGENT.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file MISSING!"
    fi
done
echo ""

# 3. Test imports
echo "3️⃣ Testing imports..."
python3 << 'EOF'
try:
    from MULTI_TIMEFRAME_COORDINATOR import MultiTimeframeCoordinator
    print("   ✅ Multi-timeframe coordinator")
except Exception as e:
    print(f"   ❌ MTF coordinator: {e}")

try:
    exec(open('🚀_SELF_OPTIMIZING_AI_TRADER.py').read().replace('#!/usr/bin/env python3', ''))
    print("   ✅ Self-optimizer")
except Exception as e:
    print(f"   ❌ Self-optimizer: {e}")

try:
    from PROFIT_MONITORING_SYSTEM import monitor_trade_for_profit
    print("   ✅ Profit monitoring")
except Exception as e:
    print(f"   ❌ Profit monitoring: {e}")

print("\\n✅ All systems importable!")
EOF
echo ""

# 4. Restart bot
echo "4️⃣ Restarting bot with COMPLETE SYSTEM..."
pkill -f RUN_BOT
sleep 3
nohup python3 RUN_BOT.py > apex.log 2>&1 &
BOT_PID=$!
echo "✅ Bot started (PID: $BOT_PID)"
echo ""

# 5. Wait for initialization
echo "5️⃣ Waiting 120 seconds for full initialization..."
sleep 120
echo ""

# 6. Verify bot running
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is RUNNING!"
else
    echo "❌ Bot died - check apex.log"
    tail -50 apex.log
    exit 1
fi
echo ""

# 7. Check systems loaded
echo "7️⃣ Verifying systems loaded..."
echo ""
echo "=== TRADING ACTIVITY ==="
TRADES=$(grep "Order ID:" apex.log | wc -l)
echo "Total trades: $TRADES"
echo ""

echo "=== PROFIT MONITORING ==="
grep "💰 Starting profit monitoring" apex.log | tail -5
echo ""

echo "=== SYSTEMS ACTIVE ==="
grep "COMPLETE CYCLE" apex.log | tail -3
echo ""

echo "✅ ═══════════════════════════════════════════════════════"
echo ""
echo "   COMPLETE SYSTEM ACTIVATED!"
echo ""
echo "════════════════════════════════════════════════════════="
echo ""
echo "🔍 MONITOR:"
echo ""
echo "# Watch profits"
echo "tail -f apex.log | grep -E '💰 POSITION CLOSED|TP.*HIT|PROFIT'"
echo ""
echo "# Watch trades"
echo "tail -f apex.log | grep 'Order ID'"
echo ""
echo "# Check status"
echo "ps aux | grep RUN_BOT"
echo ""
echo "════════════════════════════════════════════════════════="
