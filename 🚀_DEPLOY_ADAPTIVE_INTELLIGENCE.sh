#!/bin/bash
##############################################################################
# 🚀 DEPLOY ADAPTIVE INTELLIGENT TRADING SYSTEM
#
# Deploys the complete adaptive, AI-enhanced trading system:
# - Adaptive Exchange Intelligence (knows all pairs, balances, rules)
# - AI Consultation System (Claude, GPT-4, Gemini)
# - Enhanced Intelligent Execution (uses both systems)
#
# COPY/PASTE ON VPS:
# cd ~/apex_bot && bash 🚀_DEPLOY_ADAPTIVE_INTELLIGENCE.sh
##############################################################################

echo "🧠 ═════════════════════════════════════════════════════════"
echo "   DEPLOYING ADAPTIVE INTELLIGENT TRADING SYSTEM"
echo "═══════════════════════════════════════════════════════════"

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
echo "3️⃣ Pulling adaptive intelligence updates..."
git pull origin continue-from-micro-fix
if [ $? -eq 0 ]; then
    echo "✅ Updates pulled"
else
    echo "❌ Pull failed - check git status"
    exit 1
fi

# 4. Verify new files
echo ""
echo "4️⃣ Verifying adaptive intelligence files..."
if [ -f ADAPTIVE_EXCHANGE_INTELLIGENCE.py ]; then
    echo "✅ ADAPTIVE_EXCHANGE_INTELLIGENCE.py found"
else
    echo "❌ ADAPTIVE_EXCHANGE_INTELLIGENCE.py missing!"
    exit 1
fi

if [ -f AI_CONSULTATION_SYSTEM.py ]; then
    echo "✅ AI_CONSULTATION_SYSTEM.py found"
else
    echo "❌ AI_CONSULTATION_SYSTEM.py missing!"
    exit 1
fi

if [ -f INTELLIGENT_EXECUTION_ENGINE.py ]; then
    echo "✅ INTELLIGENT_EXECUTION_ENGINE.py found (enhanced)"
else
    echo "❌ INTELLIGENT_EXECUTION_ENGINE.py missing!"
    exit 1
fi

# 5. Install AI libraries
echo ""
echo "5️⃣ Installing AI libraries..."
source apex_venv/bin/activate
pip3 install --quiet anthropic openai google-generativeai
if [ $? -eq 0 ]; then
    echo "✅ AI libraries installed"
else
    echo "⚠️ AI library installation had issues (may already be installed)"
fi

# 6. Test Python syntax
echo ""
echo "6️⃣ Testing Python syntax..."
python3 -m py_compile ADAPTIVE_EXCHANGE_INTELLIGENCE.py
if [ $? -eq 0 ]; then
    echo "✅ ADAPTIVE_EXCHANGE_INTELLIGENCE syntax OK"
else
    echo "❌ ADAPTIVE_EXCHANGE_INTELLIGENCE syntax error!"
    exit 1
fi

python3 -m py_compile AI_CONSULTATION_SYSTEM.py
if [ $? -eq 0 ]; then
    echo "✅ AI_CONSULTATION_SYSTEM syntax OK"
else
    echo "❌ AI_CONSULTATION_SYSTEM syntax error!"
    exit 1
fi

python3 -m py_compile INTELLIGENT_EXECUTION_ENGINE.py
if [ $? -eq 0 ]; then
    echo "✅ INTELLIGENT_EXECUTION_ENGINE syntax OK"
else
    echo "❌ INTELLIGENT_EXECUTION_ENGINE syntax error!"
    exit 1
fi

# 7. Check .env for AI keys
echo ""
echo "7️⃣ Checking .env for AI API keys..."
has_anthropic=$(grep -c "ANTHROPIC_API_KEY=sk-ant" .env 2>/dev/null || echo "0")
has_openai=$(grep -c "OPENAI_API_KEY=sk-" .env 2>/dev/null || echo "0")
has_google=$(grep -c "GOOGLE_API_KEY=" .env 2>/dev/null || echo "0")

if [ "$has_anthropic" -gt 0 ]; then
    echo "✅ Anthropic API key configured"
else
    echo "⚠️ Anthropic API key not found in .env"
fi

if [ "$has_openai" -gt 0 ]; then
    echo "✅ OpenAI API key configured"
else
    echo "⚠️ OpenAI API key not found in .env"
fi

if [ "$has_google" -gt 0 ]; then
    echo "✅ Google API key configured"
else
    echo "⚠️ Google API key not found in .env"
fi

echo ""
echo "NOTE: AI keys are optional but recommended for full intelligence!"
echo "Without AI keys, bot will still work but won't consult AI APIs."

# 8. Start bot
echo ""
echo "8️⃣ Starting bot with ADAPTIVE INTELLIGENCE..."
nohup python3 RUN_BOT.py > apex.log 2>&1 &
BOT_PID=$!
echo "✅ Bot started (PID: $BOT_PID)"

# 9. Wait for initialization
echo ""
echo "9️⃣ Waiting 30 seconds for initialization..."
sleep 30

# 10. Verify bot running
echo ""
echo "🔟 Verifying bot status..."
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Bot is running!"
else
    echo "❌ Bot died - check apex.log"
    tail -50 apex.log
    exit 1
fi

# 11. Check for adaptive intelligence loaded
echo ""
echo "1️⃣1️⃣ Verifying ADAPTIVE INTELLIGENCE loaded..."
sleep 5
if grep -q "ADAPTIVE EXCHANGE INTELLIGENCE" apex.log; then
    echo "✅ ADAPTIVE EXCHANGE INTELLIGENCE loaded!"
    grep "ADAPTIVE EXCHANGE INTELLIGENCE" apex.log | tail -1
else
    echo "⚠️ ADAPTIVE EXCHANGE INTELLIGENCE not found in logs"
fi

if grep -q "AI CONSULTATION" apex.log; then
    echo "✅ AI CONSULTATION SYSTEM loaded!"
    grep "AI CONSULTATION" apex.log | tail -1
else
    echo "⚠️ AI CONSULTATION SYSTEM not found in logs"
fi

# Done!
echo ""
echo "✅ ════════════════════════════════════════════════════════"
echo ""
echo "   DEPLOYMENT COMPLETE!"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🔍 MONITOR WITH:"
echo ""
echo "# Watch adaptive intelligence"
echo "tail -f apex.log | grep -E '🧠|ADAPTIVE|AI CONSUL'"
echo ""
echo "# Watch exchange selection"
echo "tail -f apex.log | grep -E 'ADAPTIVE: Selected|Optimal exchange'"
echo ""
echo "# Watch AI consultations"
echo "tail -f apex.log | grep -E '🤖|Consulting AI|AI CONSENSUS'"
echo ""
echo "# Check bot is running"
echo "ps aux | grep RUN_BOT | grep -v grep"
echo ""
echo "# See recent activity"
echo "tail -50 apex.log"
echo ""
echo "════════════════════════════════════════════════════════════"
