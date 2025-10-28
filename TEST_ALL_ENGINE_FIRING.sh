#!/bin/bash
# Test ALL engines to see which are firing and which are dead

echo "🎯 TESTING ALL ENGINE FIRING"
echo "==========================================="
echo ""
echo "Running for 3 minutes to capture all activity..."
echo ""

# Start fresh log
> /tmp/engine_test.log

# Monitor for 3 minutes
timeout 180 tail -f ~/bot/bot.log >> /tmp/engine_test.log 2>&1 &
TAIL_PID=$!

sleep 180
kill $TAIL_PID 2>/dev/null

echo "✅ Captured 3 minutes of activity"
echo ""

# Analyze what's actually working
echo "📊 ENGINE ACTIVITY ANALYSIS:"
echo "==========================================="
echo ""

echo "1️⃣  SIGNAL GENERATORS:"
echo "   Smart Scalping:"
COUNT=$(grep -c "Scalper generated" /tmp/engine_test.log)
echo "      Signals: $COUNT cycles"
[ $COUNT -gt 0 ] && echo "      Status: ✅ FIRING" || echo "      Status: ❌ NOT FIRING"

echo "   Moon Spotter:"
COUNT=$(grep -c "Moon.*spotted\|MOON.*found\|micro.*moon" /tmp/engine_test.log)
echo "      Signals: $COUNT events"
[ $COUNT -gt 0 ] && echo "      Status: ✅ FIRING" || echo "      Status: ❌ NOT FIRING"

echo "   Arbitrage:"
COUNT=$(grep -c "Arbitrage.*found\|ARB.*opportunity" /tmp/engine_test.log)
echo "      Signals: $COUNT opportunities"
[ $COUNT -gt 0 ] && echo "      Status: ✅ FIRING" || echo "      Status: ❌ NOT FIRING"

echo "   News/Social:"
COUNT=$(grep -c "News/Social\|sentiment\|social.*signal" /tmp/engine_test.log)
echo "      Signals: $COUNT events"
[ $COUNT -gt 0 ] && echo "      Status: ✅ FIRING" || echo "      Status: ❌ NOT FIRING"

echo ""
echo "2️⃣  DATA HUB:"
COUNT=$(grep -c "Published.*signals to data hub" /tmp/engine_test.log)
echo "   Publications: $COUNT times"
[ $COUNT -gt 0 ] && echo "   Status: ✅ RECEIVING" || echo "   Status: ❌ NOT RECEIVING"

TOTAL=$(strings /tmp/engine_test.log | grep -o "Signals: [0-9]*" | tail -1 | awk '{print $2}')
echo "   Total Signals Stored: ${TOTAL:-0}"

echo ""
echo "3️⃣  PROFIT CONSUMERS:"
echo "   Steady Profit:"
COUNT=$(grep -c "STEADY PROFIT\|STEADY.*checking\|STEADY.*executing" /tmp/engine_test.log)
echo "      Activity: $COUNT events"
[ $COUNT -gt 0 ] && echo "      Status: ✅ ACTIVE" || echo "      Status: ❌ SILENT"

echo "   MICRO Wallet:"
COUNT=$(grep -c "MICRO.*checking\|MICRO.*TRADE\|MICRO ENTRY" /tmp/engine_test.log)
echo "      Activity: $COUNT events"
[ $COUNT -gt 0 ] && echo "      Status: ✅ ACTIVE" || echo "      Status: ❌ SILENT"

echo ""
echo "4️⃣  EXECUTION:"
COUNT=$(grep -c "Trade executed\|EXECUTED\|executed successfully" /tmp/engine_test.log)
echo "   Trades Executed: $COUNT"
[ $COUNT -gt 0 ] && echo "   Status: ✅ EXECUTING" || echo "   Status: ❌ NO EXECUTION"

COUNT=$(grep -c "CLOSING FULL POSITION\|Position closed\|TAKE_PROFIT\|STOP_LOSS" /tmp/engine_test.log)
echo "   Positions Closed: $COUNT"

echo ""
echo "5️⃣  ERRORS:"
ERRORS=$(grep -c "ERROR -" /tmp/engine_test.log)
echo "   Total Errors: $ERRORS"
if [ $ERRORS -gt 0 ]; then
    echo "   Top Errors:"
    grep "ERROR -" /tmp/engine_test.log | cut -d'-' -f5- | sort | uniq -c | sort -rn | head -5 | sed 's/^/      /'
fi

echo ""
echo "==========================================="
echo "📋 SUMMARY:"
echo ""

# Count active engines
ACTIVE=0
SILENT=0

[ $(grep -c "Scalper generated" /tmp/engine_test.log) -gt 0 ] && ((ACTIVE++)) || ((SILENT++))
[ $(grep -c "STEADY" /tmp/engine_test.log) -gt 0 ] && ((ACTIVE++)) || ((SILENT++))
[ $(grep -c "MICRO" /tmp/engine_test.log) -gt 0 ] && ((ACTIVE++)) || ((SILENT++))

echo "✅ Active Engines: $ACTIVE"
echo "❌ Silent Engines: $SILENT"
echo ""

if [ $ACTIVE -ge 2 ]; then
    echo "🎯 GOOD - Multiple engines firing!"
    echo "   Next: Verify profit is accumulating"
else
    echo "⚠️  PROBLEM - Too many silent engines!"
    echo "   Next: Check why engines aren't executing"
fi

echo ""
echo "Full log saved to: /tmp/engine_test.log"
echo ""
