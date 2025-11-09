#!/bin/bash

echo "================================================================================"
echo "🔍 CURRENT VPS TRADING LOGIC ANALYSIS"
echo "================================================================================"
echo ""
echo "This shows EXACTLY what's running on your VPS right now!"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  DATA SOURCES - Where is bot getting trading info?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📊 Checking CENTRAL_DATA_HUB.py (if exists):"
if [ -f "CENTRAL_DATA_HUB.py" ]; then
    echo "  ✅ File exists"
    echo ""
    echo "  Data fetching methods:"
    grep -n "def fetch\|def watch\|def get.*data\|fetch_ticker\|fetch_ohlcv\|watch_ticker" CENTRAL_DATA_HUB.py | head -20
    echo ""
    echo "  WebSocket usage:"
    grep -n "websocket\|ws\|watch_\|ccxt.pro" CENTRAL_DATA_HUB.py | head -10
    echo ""
    echo "  REST API usage:"
    grep -n "fetch_ticker\|fetch_ohlcv\|fetch_trades" CENTRAL_DATA_HUB.py | head -10
else
    echo "  ❌ CENTRAL_DATA_HUB.py not found"
fi

echo ""
echo "📊 Checking COMPLETE_ULTIMATE_ORCHESTRATOR.py:"
if [ -f "COMPLETE_ULTIMATE_ORCHESTRATOR.py" ]; then
    echo "  Data source initialization:"
    grep -n "data.*hub\|fetch.*ticker\|exchange.*fetch\|ccxt\|binance\|bybit" COMPLETE_ULTIMATE_ORCHESTRATOR.py | head -15
else
    echo "  ❌ COMPLETE_ULTIMATE_ORCHESTRATOR.py not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  TRADING MODE - Testnet or Live?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Checking mode configuration:"
grep -n "mode.*=.*testnet\|mode.*=.*live\|testnet.*True\|live.*True" *.py 2>/dev/null | head -10

echo ""
echo "Checking environment variables:"
grep -n "TRADING_MODE\|LIVE_TRADING" *.py 2>/dev/null | head -5

echo ""
echo "Current mode in orchestrator:"
grep -n "def __init__.*mode\|self.mode\|testnet\|sandbox" COMPLETE_ULTIMATE_ORCHESTRATOR.py 2>/dev/null | head -10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  ACTIVE ENGINES - What strategies are running?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Engine files present:"
ls -1 *ENGINE*.py 2>/dev/null | grep -v "__pycache__"

echo ""
echo "Engines initialized in orchestrator:"
grep -n "ENGINE\|engine.*=\|ScalpEngine\|TrendEngine\|MomentumEngine" COMPLETE_ULTIMATE_ORCHESTRATOR.py 2>/dev/null | head -20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  SIGNAL GENERATION - How are trade signals created?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Checking SMART_SCALPING_ENGINE.py (if exists):"
if [ -f "SMART_SCALPING_ENGINE.py" ]; then
    echo "  ✅ File exists"
    echo ""
    echo "  Signal generation methods:"
    grep -n "def generate.*signal\|def analyze\|def detect" SMART_SCALPING_ENGINE.py | head -15
    echo ""
    echo "  Confidence calculation:"
    grep -n "confidence\|probability" SMART_SCALPING_ENGINE.py | head -10
    echo ""
    echo "  Indicators used:"
    grep -n "RSI\|MACD\|EMA\|SMA\|Bollinger\|ATR\|volume" SMART_SCALPING_ENGINE.py | head -15
else
    echo "  ❌ SMART_SCALPING_ENGINE.py not found"
fi

echo ""
echo "Signal generation in other engines:"
grep -n "def.*signal\|generate.*signal" *ENGINE*.py 2>/dev/null | head -15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  TRADE FILTERING - What filters are applied?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Checking for filtering logic:"
grep -n "confidence.*threshold\|min.*confidence\|filter.*trade\|should.*trade" *.py 2>/dev/null | head -20

echo ""
echo "Checking for cooldown/rate limiting:"
grep -n "cooldown\|last.*trade\|rate.*limit\|time.*since" *.py 2>/dev/null | head -15

echo ""
echo "Checking for volatility checks:"
grep -n "volatility\|min.*vol\|market.*condition" *.py 2>/dev/null | head -15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  ORDER EXECUTION - Market or Limit orders?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Checking EXECUTION_ORCHESTRATOR.py (if exists):"
if [ -f "EXECUTION_ORCHESTRATOR.py" ]; then
    echo "  ✅ File exists"
    echo ""
    echo "  Order placement methods:"
    grep -n "create.*order\|place.*order\|execute.*trade" EXECUTION_ORCHESTRATOR.py | head -15
    echo ""
    echo "  Order types used:"
    grep -n "market\|limit\|order.*type" EXECUTION_ORCHESTRATOR.py | head -15
else
    echo "  ❌ EXECUTION_ORCHESTRATOR.py not found"
fi

echo ""
echo "Order execution in other files:"
grep -n "create.*order\|market.*order\|limit.*order" *.py 2>/dev/null | grep -v "#" | head -15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  POSITION SIZING - How much to trade?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Checking SMART_POSITION_SIZER.py (if exists):"
if [ -f "SMART_POSITION_SIZER.py" ]; then
    echo "  ✅ File exists"
    echo ""
    echo "  Position sizing logic:"
    grep -n "def calculate.*size\|def get.*position\|position.*size" SMART_POSITION_SIZER.py | head -10
    echo ""
    echo "  Risk management:"
    grep -n "risk\|stop.*loss\|take.*profit" SMART_POSITION_SIZER.py | head -15
else
    echo "  ❌ SMART_POSITION_SIZER.py not found"
fi

echo ""
echo "Position sizing in other files:"
grep -n "position.*size\|calculate.*size\|risk.*per.*trade" *.py 2>/dev/null | head -15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  RISK MANAGEMENT - Stop loss, take profit?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Stop loss implementation:"
grep -n "stop.*loss\|stop_loss\|sl_price" *.py 2>/dev/null | head -15

echo ""
echo "Take profit implementation:"
grep -n "take.*profit\|take_profit\|tp_price\|target.*price" *.py 2>/dev/null | head -15

echo ""
echo "Emergency stop:"
grep -n "emergency.*stop\|max.*loss\|drawdown" *.py 2>/dev/null | head -10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  RECENT LOG ANALYSIS - What's actually happening?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Recent signals (last 10):"
if [ -f "apex.log" ]; then
    grep -i "signal.*confidence\|analyzing.*pair\|detected.*opportunity" apex.log | tail -10
else
    echo "  No apex.log found"
fi

echo ""
echo "Recent trades (last 10):"
if [ -f "apex.log" ]; then
    grep -i "executing.*trade\|placed.*order\|buy\|sell" apex.log | tail -10
else
    echo "  No apex.log found"
fi

echo ""
echo "Recent filters/rejections (last 10):"
if [ -f "apex.log" ]; then
    grep -i "filtered\|rejected\|skipped\|cooldown\|too.*low" apex.log | tail -10
else
    echo "  No apex.log found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔟  OPTIMIZATION STATUS - Are new modules present?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Checking for optimization modules:"
for file in WEBSOCKET_DATA_FEED.py SMART_ORDER_MANAGER.py SMART_TRADE_FILTER.py SIGNAL_AGGREGATOR.py DYNAMIC_POSITION_SIZER.py; do
    if [ -f "$file" ]; then
        echo "  ✅ $file (already on VPS)"
    else
        echo "  ❌ $file (not installed - will get from branch)"
    fi
done

echo ""
echo "Checking if optimizations are integrated:"
grep -n "WEBSOCKET_DATA_FEED\|SMART_ORDER_MANAGER\|SMART_TRADE_FILTER\|SIGNAL_AGGREGATOR\|DYNAMIC_POSITION_SIZER" COMPLETE_ULTIMATE_ORCHESTRATOR.py 2>/dev/null | head -10

if [ $? -ne 0 ]; then
    echo "  ❌ Optimizations NOT yet integrated into orchestrator"
else
    echo "  ✅ Optimizations appear to be integrated"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣1️⃣  CODE SAMPLES - Actual implementation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📄 How signals are generated (first match):"
grep -A 10 "def generate.*signal\|def analyze.*market\|def detect.*opportunity" SMART_SCALPING_ENGINE.py 2>/dev/null | head -15

echo ""
echo "📄 How orders are placed (first match):"
grep -A 10 "def.*execute.*trade\|def.*place.*order\|create_order" EXECUTION_ORCHESTRATOR.py 2>/dev/null | head -15

echo ""
echo "📄 How data is fetched (first match):"
grep -A 8 "def fetch.*ticker\|def get.*market.*data\|def fetch.*ohlcv" CENTRAL_DATA_HUB.py 2>/dev/null | head -12

echo ""
echo "================================================================================"
echo "✅ ANALYSIS COMPLETE"
echo "================================================================================"
echo ""
echo "📊 SUMMARY OF FINDINGS:"
echo ""

# Summary checks
echo "Data Source:"
if grep -q "websocket\|watch_ticker" *.py 2>/dev/null; then
    echo "  ✅ WebSocket detected"
else
    echo "  ⚠️  No WebSocket - using REST API (slower)"
fi

echo ""
echo "Order Type:"
if grep -q "limit.*order\|order.*limit" *.py 2>/dev/null; then
    echo "  ✅ Limit orders detected"
else
    echo "  ⚠️  Likely using market orders (higher fees)"
fi

echo ""
echo "Trade Filtering:"
if grep -q "confidence.*threshold\|min.*confidence.*0\.[8-9]" *.py 2>/dev/null; then
    echo "  ✅ Confidence filtering detected"
else
    echo "  ⚠️  No strong confidence filtering"
fi

echo ""
echo "Signal Aggregation:"
if grep -q "aggregate.*signal\|combine.*signal" *.py 2>/dev/null; then
    echo "  ✅ Signal aggregation detected"
else
    echo "  ⚠️  No signal aggregation (may over-trade)"
fi

echo ""
echo "Dynamic Position Sizing:"
if grep -q "kelly\|dynamic.*size\|confidence.*multiplier" *.py 2>/dev/null; then
    echo "  ✅ Dynamic sizing detected"
else
    echo "  ⚠️  Likely using fixed position sizes"
fi

echo ""
echo "================================================================================"
echo ""
echo "💡 NEXT STEPS:"
echo "   1. Copy/paste this entire output"
echo "   2. Share with the agent"
echo "   3. Agent will analyze what's ACTUALLY on your VPS"
echo "   4. Agent will tell you exactly what optimizations are needed"
echo ""
echo "================================================================================"
