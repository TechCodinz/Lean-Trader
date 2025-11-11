#!/bin/bash

echo "=========================================="
echo "🧪 DEPLOYING BYBIT TESTNET TRADING"
echo "=========================================="
echo ""

cd ~/apex_bot

# Stop bot
echo "1️⃣ Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 2

# Pull testnet fix
echo ""
echo "2️⃣ Pulling testnet trading fix..."
git pull origin continue-from-micro-fix

# Clear logs
echo ""
echo "3️⃣ Clearing logs..."
> apex.log

# Verify testnet balance
echo ""
echo "4️⃣ Testing Bybit testnet connection..."
python3 << 'EOF'
import ccxt
import os

with open('.env', 'r') as f:
    lines = f.readlines()
    key = None
    secret = None
    for line in lines:
        if 'BYBIT_TESTNET_API_KEY=' in line and not line.startswith('#') and 'your_actual' not in line:
            key = line.split('=')[1].strip()
        if 'BYBIT_TESTNET_SECRET=' in line and not line.startswith('#'):
            secret = line.split('=')[1].strip()

bybit = ccxt.bybit({
    'apiKey': key,
    'secret': secret,
    'options': {'defaultType': 'spot'},
    'enableRateLimit': True
})
bybit.set_sandbox_mode(True)

try:
    balance = bybit.fetch_balance()
    usdt = balance['USDT']['free']
    print(f"✅ Testnet Balance: ${usdt:.2f} USDT")
    
    if usdt < 100:
        print("⚠️  Balance low! Get more from: https://testnet.bybit.com")
    else:
        print(f"✅ Ready to trade!")
except Exception as e:
    print(f"❌ Connection error: {e}")
EOF

# Start bot in testnet mode
echo ""
echo "5️⃣ Starting bot in TESTNET mode..."
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode testnet > apex.log 2>&1 &
BOT_PID=$!
echo "   ✅ Started (PID: $BOT_PID)"

# Wait for initialization
echo ""
echo "6️⃣ Waiting 60 seconds for initialization..."
sleep 60

# Verification
echo ""
echo "=========================================="
echo "📊 TESTNET VERIFICATION"
echo "=========================================="
echo ""

echo "🧪 Testnet Mode:"
grep "TESTNET mode\|Bybit TESTNET" apex.log | head -3

echo ""
echo "💰 Testnet Balance:"
grep "Testnet balance:\|balance.*TESTNET" apex.log | head -3

echo ""
echo "⚡ Recent Executions:"
tail -50 apex.log | grep "⚡ EXECUTING" | head -10

echo ""
echo "💎 Profitable Opportunities:"
tail -100 apex.log | grep -E "ARBITRAGE.*profit|MONEY PRINTER" | head -5

echo ""
echo "🧠 AI Collective:"
tail -100 apex.log | grep "🧠" | head -5

echo ""
echo "❌ Any Errors:"
tail -100 apex.log | grep -i "error" | grep -v "0 errors" | head -5 || echo "   ✅ No errors!"

echo ""
echo "=========================================="
echo "✅ TESTNET BOT RUNNING!"
echo "=========================================="
echo ""
echo "📊 Monitor trading:"
echo "   tail -f apex.log | grep -E '⚡ EXECUTING|Order ID|filled|Profit'"
echo ""
echo "💰 Watch profits:"
echo "   tail -f apex.log | grep -E 'Balance.*USDT|Profit.*\$|P&L'"
echo ""
echo "🧠 Watch AI debates:"
echo "   tail -f apex.log | grep -E '🧠.*Cycle|Starting AI debate'"
echo ""
echo "🛑 Stop bot:"
echo "   pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR"
echo ""
echo "🎯 Expected to see:"
echo "   - Testnet balance: \$8,000+"
echo "   - Real orders placed"
echo "   - Order IDs shown"
echo "   - Profits tracked"
echo "   - Balance growing"
echo ""
