#!/bin/bash
# Auto-generated fix script

echo "🔧 FIXING TRADING BOT ISSUES..."
echo "================================"

# Install missing dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install numpy pandas scipy scikit-learn ccxt aiohttp requests 2>&1 | tail -5

# Create .env from template if missing
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env from template..."
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "✅ .env created - PLEASE EDIT IT with your API keys!"
    fi
fi

# Run diagnostic
echo ""
echo "🔍 Running diagnostic..."
python3 COMPREHENSIVE_ENGINE_DIAGNOSTIC.py

echo ""
echo "✅ Fixes applied!"
echo "   Next: Edit .env file with your API keys"
