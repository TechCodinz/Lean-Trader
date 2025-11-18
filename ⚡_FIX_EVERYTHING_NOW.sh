#!/bin/bash
# COMPLETE FIX - EVERY SINGLE FILE NEEDED

cd ~/apex_bot
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR

echo "Pulling ALL files from branch..."

# Pull EVERY file that has fixes
git fetch origin 2>&1
git checkout origin/continue-from-micro-fix -- \
    systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py \
    systems/COMPLETE_UNIFIED_ORCHESTRATOR.py \
    systems/ULTIMATE_ORCHESTRATOR.py \
    EXECUTION_ORCHESTRATOR.py \
    INTELLIGENT_EXECUTION_ENGINE.py \
    router.py \
    PROFIT_MONITORING_SYSTEM.py \
    DYNAMIC_MARKET_SCANNER.py \
    DYNAMIC_PAIR_DISCOVERY.py \
    TESTNET_TRAINER.py \
    SAFE_MICRO_GROWTH_ENGINE.py \
    critical_features_addon.py \
    ULTRA_GOLDMINE_FEATURES.py \
    DIVINE_INTELLIGENCE_FEATURES.py \
    AI_CONSULTATION_SERVICE.py \
    INTELLIGENT_BALANCE_MANAGER.py \
    ULTIMATE_AUTONOMOUS_INTELLIGENCE.py \
    AUTONOMOUS_MASTER_COORDINATOR.py 2>&1

echo "✅ All files pulled"

# Export ALL keys
export BYBIT_TESTNET=true
export ENABLE_LIVE=true
export ALLOW_LIVE=true
export LIVE_CONFIRM=YES
export API_KEY=N8BMgWdfisCtkvfZk8
export API_SECRET=BIu7c65FQnDsd6kBmctU7gK9bBbzY15vi8oe
export BYBIT_TESTNET_API_KEY=N8BMgWdfisCtkvfZk8
export BYBIT_TESTNET_API_SECRET=BIu7c65FQnDsd6kBmctU7gK9bBbzY15vi8oe
export MEXC_API_KEY=mx0vgl7ytNbnU44V5G
export MEXC_SECRET=68562da9963e4666a32a4a73cda61062
export GATE_API_KEY=eddc6317aa4f702302f69f875971fb03
export GATE_SECRET=af14b34a638f22b744cba0b7e13f5b88bb4622f3427d0999584a7a526493e8d8
export BINANCE_API_KEY=uxMw38StLFlWpqzi9OpFMMj4H7m3dWy8jnR2EAl2raL0n465jtxnlK9S2CYBflyf
export BINANCE_SECRET=k6dCSRQfCiNYHn3PjWtORNUKP69EvnbyAHmEIio9my8qRBHbzNHbXdWV2HilzRrO

echo "✅ All keys exported"

# Clear cache
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo "✅ Cache cleared"

# Start bot
source apex_venv/bin/activate
python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_COMPLETE_WORKING.log 2>&1 &

echo "✅ Bot started - waiting 40 seconds..."
sleep 40

echo ""
echo "════════════════════════════════════════════════════════════"
echo "WATCHING BOT:"
echo "════════════════════════════════════════════════════════════"

tail -f apex_COMPLETE_WORKING.log
