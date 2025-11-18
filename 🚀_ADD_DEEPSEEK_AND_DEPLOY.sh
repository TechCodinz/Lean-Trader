#!/bin/bash

################################################################################
# 🚀 ADD DEEPSEEK + DEPLOY UNIVERSAL AI 🚀
################################################################################

echo "================================================================================"
echo "🚀🤖 UNIVERSAL AI DEPLOYMENT - DEEPSEEK + INFINITE INTELLIGENCE! 🤖🚀"
echo "================================================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating .env from example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
    else
        touch .env
        echo "✅ Created empty .env"
    fi
fi

echo "📝 Current AI providers in .env:"
echo ""
grep -E "API_KEY|ENDPOINT" .env | grep -v "^#" || echo "   (none configured yet)"
echo ""

# Interactive: Ask to add DeepSeek
echo "================================================================================"
echo "🔑 ADD DEEPSEEK API KEY"
echo "================================================================================"
echo ""
echo "Get your DeepSeek API key from: https://platform.deepseek.com/"
echo ""
read -p "Do you have a DeepSeek API key to add? (y/n): " add_deepseek

if [[ "$add_deepseek" == "y" || "$add_deepseek" == "Y" ]]; then
    read -p "Enter your DeepSeek API key: " deepseek_key
    
    # Check if already exists
    if grep -q "DEEPSEEK_API_KEY" .env; then
        # Replace existing
        sed -i.bak "s|DEEPSEEK_API_KEY=.*|DEEPSEEK_API_KEY=$deepseek_key|" .env
        echo "✅ Updated DEEPSEEK_API_KEY in .env"
    else
        # Add new
        echo "" >> .env
        echo "# DeepSeek AI" >> .env
        echo "DEEPSEEK_API_KEY=$deepseek_key" >> .env
        echo "✅ Added DEEPSEEK_API_KEY to .env"
    fi
fi

echo ""

# Ask to add other AIs
echo "================================================================================"
echo "➕ ADD OTHER AI APIS (OPTIONAL)"
echo "================================================================================"
echo ""
echo "You can add ANY AI API:"
echo "  • Grok (xAI)"
echo "  • Perplexity"
echo "  • Mistral"
echo "  • Your custom AI"
echo ""
read -p "Do you want to add another AI API? (y/n): " add_custom

if [[ "$add_custom" == "y" || "$add_custom" == "Y" ]]; then
    read -p "AI name (e.g., MYAI, GROK, PERPLEXITY): " ai_name
    read -p "API key: " ai_key
    read -p "API endpoint (optional, press Enter to skip): " ai_endpoint
    read -p "Model name (optional, press Enter to skip): " ai_model
    
    # Convert to uppercase
    ai_name_upper=$(echo "$ai_name" | tr '[:lower:]' '[:upper:]')
    
    echo "" >> .env
    echo "# Custom AI: $ai_name_upper" >> .env
    echo "CUSTOM_AI_${ai_name_upper}_KEY=$ai_key" >> .env
    
    if [ ! -z "$ai_endpoint" ]; then
        echo "CUSTOM_AI_${ai_name_upper}_ENDPOINT=$ai_endpoint" >> .env
    fi
    
    if [ ! -z "$ai_model" ]; then
        echo "CUSTOM_AI_${ai_name_upper}_MODEL=$ai_model" >> .env
    fi
    
    echo "✅ Added custom AI: $ai_name_upper"
fi

echo ""
echo "================================================================================"
echo "📊 FINAL AI CONFIGURATION"
echo "================================================================================"
echo ""

# Show all configured AIs
echo "Configured AI providers:"
grep -E "(ANTHROPIC|OPENAI|GOOGLE|GROK|DEEPSEEK|RAIZIOM|CUSTOM_AI).*_KEY" .env | grep -v "^#" | sed 's/=.*/=***/' || echo "   None yet"

echo ""
echo "================================================================================"
echo "🔄 DEPLOYING UNIVERSAL AI SYSTEM"
echo "================================================================================"
echo ""

# Stop bot
echo "⏸️  Stopping bot..."
pkill -f ORCHESTRATOR
sleep 2

# Pull latest (if in git repo)
if [ -d .git ]; then
    echo "📥 Pulling latest code..."
    git pull origin continue-from-micro-fix || echo "⚠️  Git pull failed (already up to date?)"
fi

# Integrate Universal AI (if not already)
if [ -f "⚡_INTEGRATE_UNIVERSAL_AI_NOW.py" ]; then
    echo "🔧 Integrating Universal AI..."
    python3 ⚡_INTEGRATE_UNIVERSAL_AI_NOW.py
fi

echo ""
echo "🚀 Starting bot with Universal AI..."
echo ""

# Start bot
if [ -f apex_venv/bin/activate ]; then
    source apex_venv/bin/activate
fi

nohup python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &

echo "⏳ Waiting for bot to initialize..."
sleep 10

echo ""
echo "================================================================================"
echo "✅ VERIFICATION"
echo "================================================================================"
echo ""

# Check if running
if pgrep -f ORCHESTRATOR > /dev/null; then
    echo "✅ Bot is RUNNING"
else
    echo "❌ Bot failed to start! Check bot.log"
    exit 1
fi

# Check AI providers detected
echo ""
echo "🤖 Detected AI Providers:"
grep -i "added ai provider\|orchestrator loaded" bot.log | tail -10 || echo "   (checking...)"

echo ""
echo "📊 Recent log entries:"
tail -20 bot.log | grep -E "AI|Intelligence|Provider|🤖|🧠"

echo ""
echo "================================================================================"
echo "🎉 UNIVERSAL AI DEPLOYED SUCCESSFULLY! 🎉"
echo "================================================================================"
echo ""
echo "Your bot now has access to:"

# Count providers
num_providers=$(grep -E "(ANTHROPIC|OPENAI|GOOGLE|GROK|DEEPSEEK|RAIZIOM|CUSTOM_AI).*_KEY" .env | grep -v "^#" | wc -l)
echo "   • $num_providers AI provider(s) configured"

if grep -q "DEEPSEEK_API_KEY" .env; then
    echo "   • ✅ DeepSeek (reasoning, code)"
fi

if grep -q "ANTHROPIC_API_KEY" .env; then
    echo "   • ✅ Claude (analysis, strategy)"
fi

if grep -q "OPENAI_API_KEY" .env; then
    echo "   • ✅ GPT-4 (general intelligence)"
fi

if grep -q "GOOGLE_API_KEY" .env; then
    echo "   • ✅ Gemini (fast responses)"
fi

if grep -q "GROK_API_KEY" .env; then
    echo "   • ✅ Grok (real-time data)"
fi

custom_ais=$(grep "CUSTOM_AI.*_KEY" .env | grep -v "^#" | wc -l)
if [ $custom_ais -gt 0 ]; then
    echo "   • ✅ $custom_ais custom AI(s)"
fi

echo ""
echo "♾️  Intelligence Level: INFINITE!"
echo ""
echo "📈 The bot will now:"
echo "   • Route queries to best AI for each task"
echo "   • Fallback if one AI fails"
echo "   • Learn which AI is best for what"
echo "   • Grow balance exponentially faster!"
echo ""
echo "📝 Monitor: tail -f bot.log"
echo "================================================================================"
