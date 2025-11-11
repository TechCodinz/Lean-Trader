#!/bin/bash

echo "=========================================="
echo "🧠 DEPLOYING AI COLLECTIVE CONSCIOUSNESS"
echo "=========================================="
echo ""

# Stop running bot
echo "1️⃣ Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "   (no bot running)"
sleep 2

# Pull latest code
echo ""
echo "2️⃣ Pulling AI Collective code..."
git pull origin continue-from-micro-fix

# Install AI libraries
echo ""
echo "3️⃣ Installing AI libraries..."
echo "   (This may take 1-2 minutes)"
pip3 install anthropic openai google-generativeai 2>&1 | grep -E "Successfully|already|Requirement" || true

# Check .env
echo ""
echo "4️⃣ Checking .env configuration..."
echo ""
echo "📋 Current AI API keys:"
grep -E "ANTHROPIC_API_KEY|OPENAI_API_KEY|GROK_API_KEY|GOOGLE_API_KEY|RAIZIOM" .env 2>/dev/null | sed 's/=.*/=****HIDDEN****/' || echo "   (no AI keys found)"

echo ""
echo "⚠️  ADD AI API KEYS TO .ENV:"
echo ""
echo "# AI Collective Consciousness"
echo "ANTHROPIC_API_KEY=sk-ant-api03-your-key    # Claude (optional)"
echo "OPENAI_API_KEY=sk-your-key                 # GPT-4 (optional)"
echo "GROK_API_KEY=your-key                      # Grok (optional)"
echo "GOOGLE_API_KEY=your-key                    # Gemini (optional)"
echo "RAIZIOM_ENDPOINT=https://your-api.com      # Your AI (optional)"
echo "RAIZIOM_API_KEY=your-key                   # Your AI (optional)"
echo "AI_DAILY_BUDGET=10.0                       # Budget control"
echo ""
echo "📚 Get keys:"
echo "   Claude:  https://console.anthropic.com"
echo "   OpenAI:  https://platform.openai.com"
echo "   Gemini:  https://makersuite.google.com/app/apikey"
echo "   Grok:    https://x.ai (when available)"
echo ""

read -p "Press ENTER when keys are added (or skip if testing without AIs)..."

# Clear logs
echo ""
echo "5️⃣ Clearing logs..."
> apex.log
echo "   ✅ Cleared"

# Start bot
echo ""
echo "6️⃣ Starting bot with AI Collective..."
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode testnet > apex.log 2>&1 &
BOT_PID=$!
echo "   ✅ Started (PID: $BOT_PID)"

# Wait for initialization
echo ""
echo "7️⃣ Waiting 60 seconds for initialization..."
sleep 60

# Verification
echo ""
echo "=========================================="
echo "📊 VERIFICATION"
echo "=========================================="
echo ""

echo "🧠 AI Collective Status:"
grep -E "AI COLLECTIVE|PHASE 11|active AIs|Autonomy" apex.log | tail -10 || echo "   (still initializing)"

echo ""
echo "🔒 Security Status:"
grep -E "Security Layer|Rate limit|Budget" apex.log | tail -5 || echo "   (still initializing)"

echo ""
echo "🧠 AI Debates:"
grep -E "Starting AI debate|Round 1|Round 2|Round 3|AUTONOMOUS" apex.log | tail -10 || echo "   (no debates yet - AIs optional)"

echo ""
echo "❌ Errors:"
grep -i "error" apex.log | grep -v "0 errors" | tail -5 || echo "   ✅ No errors"

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "📊 Monitor AI debates:"
echo "   tail -f apex.log | grep -E '🧠|DEBATE|AUTONOMOUS|Autonomy'"
echo ""
echo "📈 Watch autonomy growth:"
echo "   tail -f apex.log | grep 'Autonomy Progress'"
echo ""
echo "🔒 Check security:"
echo "   tail -f apex.log | grep -E 'Security|Rate|Budget'"
echo ""
echo "💰 Watch trades:"
echo "   tail -f apex.log | grep -E '⚡ EXECUTING|BUY|SELL'"
echo ""
echo "🛑 Stop bot:"
echo "   pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR"
echo ""
echo "📚 Read guide:"
echo "   cat 🌟_AI_COLLECTIVE_COMPLETE.md"
echo ""
echo "NOTE: Bot works perfectly WITHOUT AI APIs!"
echo "      AIs are optional enhancement"
echo "      Fallback to learned wisdom if APIs fail"
echo ""
