#!/bin/bash
cd ~/apex_bot

echo "=========================================="
echo "🧪 STARTING BOT IN TESTNET MODE"
echo "=========================================="
echo ""

# Stop any running bot
echo "1️⃣ Stopping any running bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3
echo "   ✅ Stopped"
echo ""

# Check .env
echo "2️⃣ Verifying .env configuration..."
if [ ! -f .env ]; then
    echo "❌ No .env file found!"
    echo ""
    echo "Create .env with testnet keys:"
    echo "nano .env"
    echo ""
    echo "Add:"
    echo "BYBIT_TESTNET_API_KEY=your_key"
    echo "BYBIT_TESTNET_SECRET=your_secret"
    echo "GATEIO_API_KEY=your_key"
    echo "GATEIO_SECRET=your_secret"
    echo "TRADING_MODE=testnet"
    exit 1
fi

# Check for testnet keys
if ! grep -q "BYBIT_TESTNET" .env; then
    echo "⚠️  No testnet keys found in .env"
    echo "   Bot will use live keys if present"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Testnet keys found"
fi
echo ""

# Clear log
echo "3️⃣ Clearing log..."
> apex.log
echo "   ✅ Cleared"
echo ""

# Start bot
echo "4️⃣ Starting bot with ALL PAIRS (testnet mode)..."
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode testnet > apex.log 2>&1 &
BOT_PID=$!
echo "   ✅ Started (PID: $BOT_PID)"
echo ""

# Wait for initialization
echo "5️⃣ Waiting 40 seconds for initialization..."
sleep 40
echo ""

echo "=========================================="
echo "📊 TESTNET STATUS"
echo "=========================================="
echo ""

echo "🌍 Dynamic Pairs Loaded:"
tail -200 apex.log | grep -E "🌍|Fetched.*pairs|Loaded.*pairs|dynamic" | head -10
echo ""

echo "🧪 Testnet Verification:"
tail -200 apex.log | grep -iE "testnet|test mode|sandbox|demo" | head -5
echo ""

echo "💰 Balance (should be testnet balance):"
tail -100 apex.log | grep -E "Balance.*\$|Starting.*\$" | head -5
echo ""

echo "⚡ Recent Activity:"
tail -100 apex.log | grep -E "EXECUTING|Signal|Decision" | tail -10
echo ""

echo "❌ Errors:"
tail -50 apex.log | grep -i "error" | tail -5
echo ""

echo "=========================================="
echo "✅ TESTNET BOT RUNNING"
echo "=========================================="
echo ""
echo "📊 Monitor: tail -f apex.log | grep -E '⚡|💰|🌍|💎'"
echo "🛑 Stop: pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR"
echo ""
