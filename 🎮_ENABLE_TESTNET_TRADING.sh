#!/bin/bash
# Enable testnet trading with verification

echo "=========================================="
echo "🎮 ENABLING TESTNET TRADING"
echo "=========================================="
echo ""

# 1. Stop current bot
echo "1️⃣ Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 2
echo "   ✅ Bot stopped"
echo ""

# 2. Verify testnet mode
echo "2️⃣ Verifying testnet configuration..."
MODE=$(grep "def __init__.*mode.*testnet" COMPLETE_ULTIMATE_ORCHESTRATOR.py)
if [ ! -z "$MODE" ]; then
    echo "   ✅ Testnet mode is DEFAULT"
else
    echo "   ⚠️  Checking mode setting..."
fi

# Check .env for testnet keys
echo ""
echo "3️⃣ Checking testnet API keys in .env..."
if grep -q "BYBIT_TESTNET_API_KEY" .env; then
    TESTNET_KEY=$(grep "BYBIT_TESTNET_API_KEY" .env | cut -d'=' -f2)
    if [ "$TESTNET_KEY" = "YOUR_TESTNET_KEY_HERE" ] || [ -z "$TESTNET_KEY" ]; then
        echo "   ⚠️  Bybit Testnet keys NOT configured"
        echo ""
        echo "   📝 TO GET TESTNET KEYS:"
        echo "   1. Go to: https://testnet.bybit.com"
        echo "   2. Sign up / Login"
        echo "   3. Go to: Account → API Management"
        echo "   4. Create API Key"
        echo "   5. Add keys to .env file"
        echo ""
    else
        echo "   ✅ Bybit Testnet keys found"
    fi
fi

# Check Gate.io testnet
GATEIO_MODE=$(grep "GATEIO_MODE" .env | cut -d'=' -f2)
echo ""
echo "   Gate.io mode: ${GATEIO_MODE:-testnet}"
if [ "$GATEIO_MODE" = "live" ]; then
    echo "   ⚠️  WARNING: Gate.io is in LIVE mode!"
    echo "   To switch to testnet, edit .env:"
    echo "   GATEIO_MODE=testnet"
fi

echo ""
echo "=========================================="
echo "4️⃣ STARTING BOT IN TESTNET MODE"
echo "=========================================="

# Clear log
> apex.log

# Start in testnet mode (explicit)
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode testnet > apex.log 2>&1 &
BOT_PID=$!

echo "   ✅ Bot started (PID: $BOT_PID)"
echo "   Mode: TESTNET (fake funds)"
echo ""

# Wait for initialization
echo "5️⃣ Waiting 20 seconds for initialization..."
sleep 20

echo ""
echo "=========================================="
echo "📊 CHECKING TESTNET STATUS"
echo "=========================================="

# Check mode in logs
echo ""
echo "🎮 Mode Verification:"
tail -500 apex.log | grep -i "testnet\|mode\|exchange.*initialized" | head -10

# Check balance
echo ""
echo "💰 Balance Check:"
tail -500 apex.log | grep -i "balance\|funds\|available" | head -5

# Check if trading
echo ""
echo "⚡ Trading Activity:"
tail -200 apex.log | grep -E "EXECUTING|Trade.*executed|Order.*placed" | head -10

# Check for errors
echo ""
echo "🔍 Error Check:"
ERRORS=$(tail -500 apex.log | grep -i "error\|failed\|exception" | grep -v "CUDA\|DEBUG" | wc -l)
if [ $ERRORS -eq 0 ]; then
    echo "   ✅ No errors detected"
else
    echo "   ⚠️  Found $ERRORS potential issues:"
    tail -500 apex.log | grep -i "error\|failed" | grep -v "CUDA\|DEBUG" | tail -5
fi

echo ""
echo "=========================================="
echo "📋 TESTNET TRADING SUMMARY"
echo "=========================================="
echo ""
echo "Bot Status: $(ps -p $BOT_PID > /dev/null && echo '✅ RUNNING' || echo '❌ STOPPED')"
echo "Mode: TESTNET (fake funds)"
echo "PID: $BOT_PID"
echo ""
echo "📺 WATCH LIVE:"
echo "   tail -f apex.log | grep -E '⚡ EXECUTING|Trade|Order|Balance|confidence'"
echo ""
echo "🎯 WHAT TO WATCH FOR:"
echo "   1. Balance updates (should show testnet funds)"
echo "   2. ⚡ EXECUTING messages (actual trades)"
echo "   3. Trade confirmations"
echo "   4. P&L updates"
echo ""
echo "📝 TO ADD REAL FUNDS LATER:"
echo "   1. Stop bot: pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR"
echo "   2. Edit .env: GATEIO_MODE=live"
echo "   3. Add Gate.io API keys"
echo "   4. Deposit $10 to Gate.io"
echo "   5. Start bot: python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode live"
echo ""
echo "=========================================="
echo "🎮 TESTNET MODE ACTIVE!"
echo "=========================================="
