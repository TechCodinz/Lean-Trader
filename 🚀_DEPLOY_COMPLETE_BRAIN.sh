#!/bin/bash
##############################################################################
# 🚀 DEPLOY COMPLETE BRAIN SYSTEM
#
# Deploys the FULL INTELLIGENCE:
# - Market Data Intelligence (live charts/trends)
# - Multi-AI Aggregator (collective AI intelligence)
# - TradingView Analytics (professional TA)
# - Self-Healing Orchestrator (autonomous health)
# - Divine Harmony Calibrator (perfect synchronicity)
#
# COPY/PASTE ON VPS:
# cd ~/apex_bot && bash 🚀_DEPLOY_COMPLETE_BRAIN.sh
##############################################################################

echo "🌟 ═══════════════════════════════════════════════════════════"
echo "      DEPLOYING COMPLETE BRAIN SYSTEM"
echo "═════════════════════════════════════════════════════════════"

# 1. Stop bot
echo ""
echo "1️⃣ Stopping bot..."
pkill -f RUN_BOT && echo "✅ Bot stopped" || echo "⚠️  Bot not running"

# 2. Backup logs
echo ""
echo "2️⃣ Backing up logs..."
if [ -f apex.log ]; then
    cp apex.log apex.log.backup.$(date +%s)
    echo "✅ Logs backed up"
fi

# 3. Pull updates
echo ""
echo "3️⃣ Pulling complete brain system..."
git pull origin continue-from-micro-fix
if [ $? -eq 0 ]; then
    echo "✅ Updates pulled"
else
    echo "❌ Pull failed - check git status"
    exit 1
fi

# 4. Verify brain system files
echo ""
echo "4️⃣ Verifying brain system files..."

FILES=(
    "MARKET_DATA_INTELLIGENCE.py"
    "MULTI_AI_AGGREGATOR.py"
    "TRADINGVIEW_ANALYTICS_ENGINE.py"
    "SELF_HEALING_ORCHESTRATOR.py"
    "DIVINE_HARMONY_CALIBRATOR.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file found"
    else
        echo "❌ $file missing!"
        exit 1
    fi
done

# 5. Install additional libraries
echo ""
echo "5️⃣ Installing additional libraries..."
source apex_venv/bin/activate
pip3 install --quiet tradingview-ta psutil
if [ $? -eq 0 ]; then
    echo "✅ Libraries installed (tradingview-ta, psutil)"
else
    echo "⚠️ Library installation had issues"
fi

# 6. Test Python syntax
echo ""
echo "6️⃣ Testing Python syntax..."
for file in "${FILES[@]}"; do
    python3 -m py_compile "$file"
    if [ $? -eq 0 ]; then
        echo "✅ $file syntax OK"
    else
        echo "❌ $file syntax error!"
        exit 1
    fi
done

# 7. Start bot
echo ""
echo "7️⃣ Starting bot with COMPLETE BRAIN..."
nohup python3 RUN_BOT.py > apex.log 2>&1 &
BOT_PID=$!
echo "✅ Bot started (PID: $BOT_PID)"

# 8. Wait for initialization
echo ""
echo "8️⃣ Waiting 40 seconds for full initialization..."
sleep 40

# 9. Verify bot running
echo ""
echo "9️⃣ Verifying bot status..."
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running!"
else
    echo "❌ Bot died - check apex.log"
    tail -50 apex.log
    exit 1
fi

# 10. Verify brain systems loaded
echo ""
echo "🔟 Verifying brain systems loaded..."

echo ""
echo "📊 Market Data Intelligence:"
if grep -q "MARKET DATA INTELLIGENCE" apex.log; then
    echo "   ✅ ACTIVE"
else
    echo "   ⚠️ Not found in logs"
fi

echo ""
echo "🤖 Multi-AI Aggregator:"
if grep -q "MULTI-AI AGGREGATOR" apex.log; then
    echo "   ✅ ACTIVE"
else
    echo "   ⚠️ Not found in logs"
fi

echo ""
echo "📈 TradingView Analytics:"
if grep -q "TRADINGVIEW ANALYTICS" apex.log; then
    echo "   ✅ ACTIVE"
else
    echo "   ⚠️ Not found in logs"
fi

echo ""
echo "🔧 Self-Healing Orchestrator:"
if grep -q "SELF-HEALING ORCHESTRATOR" apex.log; then
    echo "   ✅ ACTIVE"
else
    echo "   ⚠️ Not found in logs"
fi

echo ""
echo "🌟 Divine Harmony Calibrator:"
if grep -q "DIVINE HARMONY CALIBRATOR" apex.log; then
    echo "   ✅ ACTIVE"
else
    echo "   ⚠️ Not found in logs"
fi

# Done!
echo ""
echo "✅ ═══════════════════════════════════════════════════════════"
echo ""
echo "      DEPLOYMENT COMPLETE!"
echo ""
echo "════════════════════════════════════════════════════════════="
echo ""
echo "🔍 MONITOR WITH:"
echo ""
echo "# Watch market data gathering"
echo "tail -f apex.log | grep -E '📊|MARKET DATA'"
echo ""
echo "# Watch AI collective intelligence"
echo "tail -f apex.log | grep -E '🤖|COLLECTIVE|MULTI AI'"
echo ""
echo "# Watch TradingView analysis"
echo "tail -f apex.log | grep -E '📈|TRADINGVIEW'"
echo ""
echo "# Watch self-healing"
echo "tail -f apex.log | grep -E '🔧|HEALING|health'"
echo ""
echo "# Watch divine harmony"
echo "tail -f apex.log | grep -E '🌟|HARMONY|calibrat'"
echo ""
echo "# Check bot is running"
echo "ps aux | grep RUN_BOT | grep -v grep"
echo ""
echo "════════════════════════════════════════════════════════════="
