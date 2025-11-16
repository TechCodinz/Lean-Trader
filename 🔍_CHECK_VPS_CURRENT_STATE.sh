#!/bin/bash
################################################################################
# 🔍 CHECK VPS CURRENT STATE - BEFORE PULLING ANYTHING!
# This shows exactly what's working NOW on your VPS
################################################################################

cd ~/apex_bot

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                     🔍 VPS CURRENT STATE DIAGNOSTIC                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📍 1. GIT STATUS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Current Branch:"
git branch --show-current
echo ""
echo "Last 5 Commits:"
git log --oneline -5
echo ""
echo "Working Tree Status:"
git status --short
echo ""
echo "Remote URL:"
git remote -v
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📦 2. PYTHON & VENV STATUS"
echo "═══════════════════════════════════════════════════════════════════════════════"
if [ -d "apex_venv" ]; then
    echo "✅ apex_venv exists"
    source apex_venv/bin/activate
    echo "Python version: $(python3 --version)"
    echo "Pip version: $(pip --version)"
    echo ""
    echo "Key packages installed:"
    pip list | grep -E "anthropic|openai|ccxt|python-telegram-bot|web3" || echo "No AI packages found"
else
    echo "❌ apex_venv NOT FOUND!"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🤖 3. AI CONSULTATION FILES CHECK"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Checking AI-related files:"
for file in "AI_CONSULTATION_SERVICE.py" "MULTI_AI_INTELLIGENCE_LAYER.py" "ULTIMATE_AUTONOMOUS_INTELLIGENCE.py"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists ($(wc -l < $file) lines)"
    else
        echo "❌ $file NOT FOUND"
    fi
done
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "⚙️  4. CONFIGURATION CHECK"
echo "═══════════════════════════════════════════════════════════════════════════════"
if [ -f "systems/.env" ]; then
    echo "✅ systems/.env exists"
    echo ""
    echo "AI API Keys configured:"
    grep -E "ANTHROPIC_API_KEY|OPENAI_API_KEY|GROK_API_KEY|RAIZIOM_API_KEY|CUSTOM_AI" systems/.env | sed 's/=.*/=***REDACTED***/'
    echo ""
    echo "AI Provider setting:"
    grep "AI_PROVIDER" systems/.env || echo "AI_PROVIDER not set (will use default)"
else
    echo "❌ systems/.env NOT FOUND!"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🔬 5. IMPORT TEST - Check What Works NOW"
echo "═══════════════════════════════════════════════════════════════════════════════"
if [ -d "apex_venv" ]; then
    source apex_venv/bin/activate
    
    echo "Testing imports..."
    python3 << 'PYEOF'
import sys
import os

print("Python Path:")
print(f"  {sys.executable}")
print()

print("Testing AI imports:")
print()

# Test Anthropic
try:
    import anthropic
    print("✅ anthropic installed (version: " + str(anthropic.__version__ if hasattr(anthropic, '__version__') else 'unknown') + ")")
except ImportError:
    print("❌ anthropic NOT installed")

# Test OpenAI
try:
    import openai
    print("✅ openai installed")
except ImportError:
    print("❌ openai NOT installed")

# Test requests
try:
    import requests
    print("✅ requests installed")
except ImportError:
    print("❌ requests NOT installed")

print()
print("Testing bot imports:")
print()

# Check if AI consultation exists and what it has
if os.path.exists('AI_CONSULTATION_SERVICE.py'):
    print("✅ AI_CONSULTATION_SERVICE.py exists")
    try:
        from AI_CONSULTATION_SERVICE import AIConsultationService
        print("   ✅ Can import AIConsultationService")
        
        # Check if it's old or new version
        import inspect
        sig = inspect.signature(AIConsultationService.__init__)
        params = list(sig.parameters.keys())
        if 'provider' in params:
            print("   ✅ NEW VERSION (multi-AI support)")
        elif 'api_key' in params:
            print("   ⚠️  OLD VERSION (Claude only)")
        else:
            print("   ❓ Unknown version")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
elif os.path.exists('MULTI_AI_INTELLIGENCE_LAYER.py'):
    print("✅ MULTI_AI_INTELLIGENCE_LAYER.py exists (alternative)")
else:
    print("❌ No AI consultation file found")

print()

# Check other intelligence files
for module in ['INTELLIGENT_BALANCE_MANAGER', 'ULTIMATE_AUTONOMOUS_INTELLIGENCE', 'AUTONOMOUS_MASTER_COORDINATOR']:
    if os.path.exists(f'{module}.py'):
        try:
            __import__(module)
            print(f"✅ {module}.py - import works")
        except Exception as e:
            print(f"⚠️  {module}.py - exists but import failed: {e}")
    else:
        print(f"❌ {module}.py - NOT FOUND")

PYEOF
else
    echo "⚠️ Cannot test imports - venv not found"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🤖 6. BOT PROCESS CHECK"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Python processes running:"
ps aux | grep -i "python.*bot\|python.*RUN_BOT\|python.*trading" | grep -v grep || echo "No bot processes found"
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 7. RECENT LOG CHECK"
echo "═══════════════════════════════════════════════════════════════════════════════"
if [ -f "logs/trading_bot.log" ]; then
    echo "Last 20 lines of bot log:"
    tail -20 logs/trading_bot.log
elif [ -f "bot.log" ]; then
    echo "Last 20 lines of bot log:"
    tail -20 bot.log
else
    echo "No log file found"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ 8. DIAGNOSTIC COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 SUMMARY:"
echo "  - Branch: $(git branch --show-current)"
echo "  - Venv: $([ -d apex_venv ] && echo 'EXISTS' || echo 'MISSING')"
echo "  - .env: $([ -f systems/.env ] && echo 'EXISTS' || echo 'MISSING')"
echo "  - AI Files: $(ls AI_*.py 2>/dev/null | wc -l) found"
echo ""
echo "🔍 Copy ALL output above and send to me!"
echo "   I'll analyze what's working and give you SAFE pull commands."
echo ""
