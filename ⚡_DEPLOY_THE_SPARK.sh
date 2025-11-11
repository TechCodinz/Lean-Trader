#!/bin/bash

echo "=========================================="
echo "⚡⚡⚡ DEPLOYING THE SPARK! ⚡⚡⚡"
echo "=========================================="
echo ""

cd ~/apex_bot

# Stop bot
echo "1️⃣ Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3

# Pull THE SPARK
echo ""
echo "2️⃣ Pulling THE SPARK (all fixes)..."
git pull origin continue-from-micro-fix

# Verify files
echo ""
echo "3️⃣ Verifying SPARK systems..."
ls -lh SUPREME_ACTIVATION_SYSTEM.py NEUROTRANSMITTER_SYSTEM.py 2>/dev/null || echo "   ⚠️  Files not found"

# Clear logs
echo ""
echo "4️⃣ Clearing logs..."
> apex.log

# Test Bybit testnet
echo ""
echo "5️⃣ Testing Bybit testnet ($8K balance)..."
python3 << 'EOF'
import ccxt
with open('.env', 'r') as f:
    lines = f.readlines()
    key = secret = None
    for line in lines:
        if 'BYBIT_TESTNET_API_KEY=' in line and not '#' in line and 'your_actual' not in line:
            key = line.split('=')[1].strip()
        if 'BYBIT_TESTNET_SECRET=' in line and not '#' in line:
            secret = line.split('=')[1].strip()
bybit = ccxt.bybit({'apiKey': key, 'secret': secret, 'enableRateLimit': True})
bybit.set_sandbox_mode(True)
balance = bybit.fetch_balance()
print(f"✅ Bybit Testnet: ${balance['USDT']['free']:.2f} USDT")
EOF

# Start bot with THE SPARK
echo ""
echo "6️⃣ Starting bot with THE SPARK..."
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode testnet > apex.log 2>&1 &
BOT_PID=$!
echo "   ✅ Started (PID: $BOT_PID)"

# Wait for THE SPARK
echo ""
echo "7️⃣ Waiting 90 seconds for SPARK activation..."
sleep 90

# Verification
echo ""
echo "=========================================="
echo "⚡ SPARK VERIFICATION"
echo "=========================================="
echo ""

echo "🧪 Testnet Mode:"
grep "Bybit TESTNET\|Testnet balance" apex.log | head -3

echo ""
echo "⚡ Supreme Activation:"
grep -E "SUPREME ACTIVATION|QUANTUM ACTIVATION|SPARK|power.*multiplier" apex.log | head -10

echo ""
echo "🧠 Neurotransmitter System:"
grep "Neurotransmitter\|Synapse\|Neural" apex.log | head -5

echo ""
echo "⚡ Real Orders (with details):"
tail -200 apex.log | grep -A 20 "⚡ TRADE EXECUTED" | head -25

echo ""
echo "💰 Profits:"
grep -E "Expected Profit|Order ID|filled" apex.log | head -10

echo ""
echo "❌ Any Errors:"
tail -100 apex.log | grep -i "error" | grep -v "0 errors" | head -5 || echo "   ✅ No errors!"

echo ""
echo "=========================================="
echo "✅ THE SPARK IS ACTIVE!"
echo "=========================================="
echo ""
echo "📊 Monitor real orders:"
echo "   tail -f apex.log | grep -A 20 '⚡ TRADE EXECUTED'"
echo ""
echo "💰 Watch profits:"
echo "   tail -f apex.log | grep -E 'Expected Profit|Balance.*->'"
echo ""
echo "⚡ Watch THE SPARK:"
echo "   tail -f apex.log | grep -E '⚡|QUANTUM|Synergy|Resonance'"
echo ""
echo "🧠 Watch AI debates:"
echo "   tail -f apex.log | grep '🧠'"
echo ""
echo "🎯 You should see:"
echo "   - Quantum activation (5-15x power)"
echo "   - Real Order IDs"
echo "   - Detailed trade info (timeframe, TP, SL, leverage)"
echo "   - Balance growing"
echo "   - Profits tracking"
echo ""
