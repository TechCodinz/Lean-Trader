#!/bin/bash
cd ~/apex_bot

echo "=========================================="
echo "🧪 TESTNET VERIFICATION"
echo "=========================================="
echo ""

echo "1️⃣ Checking .env file..."
echo ""
if [ -f .env ]; then
    echo "📋 Current API Keys in .env:"
    echo ""
    
    # Check for testnet keys
    if grep -q "BYBIT_TESTNET" .env 2>/dev/null; then
        echo "✅ Bybit Testnet keys found"
        grep "BYBIT_TESTNET" .env | sed 's/=.*/=*****/g'
    else
        echo "❌ No BYBIT_TESTNET keys found"
        echo "   Add these to .env:"
        echo "   BYBIT_TESTNET_API_KEY=your_testnet_key"
        echo "   BYBIT_TESTNET_SECRET=your_testnet_secret"
    fi
    echo ""
    
    # Check for Gate.io keys
    if grep -q "GATEIO" .env 2>/dev/null; then
        echo "📊 Gate.io keys found"
        grep "GATEIO" .env | sed 's/=.*/=*****/g'
        echo "   ⚠️  Note: Gate.io doesn't have testnet, uses real API"
    fi
    echo ""
    
    # Check mode
    if grep -q "TRADING_MODE.*testnet" .env 2>/dev/null; then
        echo "✅ TRADING_MODE=testnet"
    else
        echo "⚠️  No TRADING_MODE set, defaulting to live"
        echo "   Add: TRADING_MODE=testnet"
    fi
else
    echo "❌ No .env file found!"
    echo ""
    echo "Create .env file:"
    echo "nano .env"
    echo ""
    echo "Add testnet keys:"
    echo "BYBIT_TESTNET_API_KEY=your_key_here"
    echo "BYBIT_TESTNET_SECRET=your_secret_here"
    echo "GATEIO_API_KEY=your_gateio_key"
    echo "GATEIO_SECRET=your_gateio_secret"
    echo "TRADING_MODE=testnet"
fi

echo ""
echo "=========================================="
echo "2️⃣ Checking bot logs for testnet usage..."
echo "=========================================="
echo ""

if [ -f apex.log ]; then
    echo "🔍 Exchange connections:"
    tail -200 apex.log | grep -iE "testnet|demo|sandbox|paper|test mode" | head -10
    echo ""
    
    echo "🔍 API endpoints:"
    tail -200 apex.log | grep -iE "api.*testnet|testnet.*api" | head -5
    echo ""
    
    echo "🔍 Recent trades (check if using testnet balance):"
    tail -100 apex.log | grep -E "Balance.*\$|EXECUTING" | head -10
else
    echo "⚠️  No apex.log file yet"
fi

echo ""
echo "=========================================="
echo "3️⃣ Get Testnet Keys"
echo "=========================================="
echo ""
echo "🔗 Bybit Testnet:"
echo "   https://testnet.bybit.com"
echo "   - Register account"
echo "   - Get free testnet USDT"
echo "   - Create API keys"
echo ""
echo "📊 Gate.io:"
echo "   https://www.gate.io"
echo "   - No testnet available"
echo "   - Start with small balance ($10-20)"
echo ""

echo "=========================================="
echo "✅ VERIFICATION COMPLETE"
echo "=========================================="
