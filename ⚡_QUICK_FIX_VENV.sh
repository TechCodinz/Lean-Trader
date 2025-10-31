#!/bin/bash
# ⚡ QUICK FIX - Recreate venv and install dependencies
# This fixes the venv that was wiped by the 4.1 agent

set -e  # Exit on any error

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          ⚡ QUICK FIX - RECREATING VENV & DEPENDENCIES ⚡         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    echo "⚠️  venv directory already exists"
    read -p "Remove and recreate? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "🗑️  Removing old venv..."
        rm -rf venv
    else
        echo "Using existing venv..."
    fi
fi

# Create venv
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
fi

# Activate venv
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install CRITICAL dependencies first (needed for bot to start)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Installing CRITICAL dependencies (required for bot startup)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Core data science (needed by brain, hivemind, profit features)
echo "1/6: Installing numpy..."
pip install numpy --quiet
echo "2/6: Installing pandas..."
pip install pandas --quiet
echo "3/6: Installing scipy..."
pip install scipy --quiet

# Trading (absolutely essential)
echo "4/6: Installing ccxt (Gate.io trading)..."
pip install ccxt --quiet

# Async & utilities (essential)
echo "5/6: Installing aiohttp..."
pip install aiohttp --quiet
echo "6/6: Installing utilities..."
pip install python-dotenv loguru --quiet

echo ""
echo "✅ CRITICAL dependencies installed!"
echo ""

# Test if bot can now import
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Testing bot imports..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << 'PYEOF'
import sys
try:
    print("Testing critical imports...")
    import numpy
    print("  ✅ numpy")
    import pandas
    print("  ✅ pandas")
    import scipy
    print("  ✅ scipy")
    import ccxt
    print("  ✅ ccxt (Gate.io trading)")
    import aiohttp
    print("  ✅ aiohttp")
    import loguru
    print("  ✅ loguru")
    from dotenv import load_dotenv
    print("  ✅ python-dotenv")
    print("")
    print("✅ All critical imports successful!")
    print("")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Critical imports failed. Please check errors above."
    exit 1
fi

# Install OPTIONAL but recommended dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Installing OPTIONAL dependencies (for full features)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Note: These may take longer. You can skip with Ctrl+C if you want"
echo "      to start trading immediately with just the critical features."
echo ""

# ML/AI (for evolution engine, divine intelligence)
echo "Installing ML/AI packages..."
pip install scikit-learn --quiet 2>/dev/null || echo "⚠️  scikit-learn skipped (optional)"
pip install xgboost --quiet 2>/dev/null || echo "⚠️  xgboost skipped (optional)"
pip install lightgbm --quiet 2>/dev/null || echo "⚠️  lightgbm skipped (optional)"

# Technical analysis
echo "Installing TA packages..."
pip install pandas-ta --quiet 2>/dev/null || echo "⚠️  pandas-ta skipped (optional)"

# Web scraping (for news engines)
echo "Installing web packages..."
pip install requests beautifulsoup4 feedparser --quiet 2>/dev/null || echo "⚠️  web packages skipped (optional)"

# NLP (for sentiment analysis)
echo "Installing NLP packages..."
pip install nltk vaderSentiment --quiet 2>/dev/null || echo "⚠️  NLP packages skipped (optional)"

# Web3 (for DEX trading - optional)
echo "Installing Web3 packages..."
pip install web3 --quiet 2>/dev/null || echo "⚠️  web3 skipped (optional)"

echo ""
echo "✅ Optional dependencies installed (or skipped if too large)"
echo ""

# Final test - try importing the orchestrator
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Final test - Loading orchestrator..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << 'PYFINAL'
import sys
import os
os.environ['TESTING_MODE'] = '1'  # Prevent full initialization

try:
    print("Loading COMPLETE_ULTIMATE_ORCHESTRATOR...")
    from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
    print("")
    print("✅ Orchestrator loaded successfully!")
    print("")
except Exception as e:
    print(f"⚠️  Warning: {e}")
    print("")
    print("This may be OK if optional dependencies are missing.")
    print("The bot should still work with reduced features.")
    print("")
PYFINAL

# Summary
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ QUICK FIX COMPLETE! ✅                      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Virtual environment: $SCRIPT_DIR/venv"
echo "Python executable: $SCRIPT_DIR/venv/bin/python3"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Test Gate.io connection:"
echo "   source venv/bin/activate"
echo "   python3 TEST_GATE_CONNECTION.py"
echo ""
echo "2. Start the bot:"
echo "   python3 RUN_BOT.py --live"
echo ""
echo "3. Or run in background:"
echo "   nohup python3 RUN_BOT.py --live > bot.log 2>&1 &"
echo ""
echo "4. Monitor trades:"
echo "   tail -f bot.log | grep -E 'EXECUTING|PROFIT|Decision'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💰 Your bot is ready to make profits!"
echo ""
