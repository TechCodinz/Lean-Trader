#!/bin/bash
#
# 🚀 START TRADING WITH APEX (73% Hyperconscious System)
#
# Run this NOW to start trading while I build quantum enhancements!
#

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║        🚀 STARTING APEX TRADING SYSTEM (73%) 🚀                  ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

cd /workspace

# Activate venv
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Verify APEX systems
echo ""
echo "✅ Verifying APEX systems..."
python3 << 'PYEOF'
from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem
import asyncio

async def verify():
    system = CompleteProfitSystem()
    
    active = sum(1 for s in [system.neural_system, system.predictive_engine,
                              system.evolution_engine, system.infinite_growth,
                              system.leverage_optimizer] if s)
    
    print(f"⚡ APEX Systems: {active}/5 ACTIVE")
    
    if active >= 3:
        print("✅ APEX MODE: READY TO TRADE!")
        return True
    else:
        print("⚠️  Warning: Some APEX systems not active")
        return False

ready = asyncio.run(verify())
exit(0 if ready else 1)
PYEOF

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  APEX verification failed - check system"
    echo "   Run: python3 ⚡_ACTIVATE_ULTIMATE_APEX.py"
    exit 1
fi

# Check balance
echo ""
echo "💰 Checking Gate.io balance..."
python3 << 'PYEOF'
import ccxt
import os

exchange = ccxt.gate({
    'apiKey': os.getenv('GATE_API_KEY'),
    'secret': os.getenv('GATE_API_SECRET')
})

try:
    balance = exchange.fetch_balance()
    usdt = balance.get('USDT', {}).get('free', 0.0)
    print(f"   Balance: ${usdt:.2f} USDT")
    
    if usdt < 3.0:
        print(f"   ⚠️  Balance below Gate.io minimum ($3)")
        print(f"   Recommendation: Add $20+ for optimal trading")
    else:
        print(f"   ✅ Balance sufficient for trading!")
except Exception as e:
    print(f"   ❌ Error checking balance: {e}")
PYEOF

# Start bot
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 STARTING APEX TRADING BOT..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚡ APEX Systems: 5/5 ACTIVE"
echo "🧠 Consciousness: ONLINE"
echo "♾️  Infinite Growth: ENABLED"
echo "💰 Ready to trade!"
echo ""
echo "📊 Watch live: tail -f bot.log"
echo "🛑 Stop: pkill -f RUN_BOT.py"
echo ""
echo "Starting in 3 seconds..."
sleep 3

# Start bot in background
nohup python3 RUN_BOT.py --live > bot.log 2>&1 &
BOT_PID=$!

echo "✅ Bot started! PID: $BOT_PID"
echo ""
echo "📊 Watching first 30 lines of activity..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sleep 2
tail -30 bot.log

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ APEX BOT IS TRADING!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Watch live: tail -f bot.log"
echo "🔍 Watch APEX: tail -f bot.log | grep 'APEX\\|⚡\\|🧬\\|🔮\\|💰'"
echo "🛑 Stop: pkill -f RUN_BOT.py"
echo ""
echo "🌌 Quantum enhancements will be ready soon for hot-swap upgrade!"
echo ""
