#!/bin/bash
# ⚡ CHECK PROFIT STATUS - What's working, what's failing

echo "============================================================================"
echo "💰 PROFIT & PERFORMANCE CHECK"
echo "============================================================================"
echo ""

cd ~/bot

echo "1️⃣ CHECKING BOT STATUS..."
echo "----------------------------------------"
if ps aux | grep -q "[C]OMPLETE_ULTIMATE_ORCHESTRATOR"; then
    echo "✅ Bot is RUNNING"
    ps aux | grep "[C]OMPLETE_ULTIMATE_ORCHESTRATOR" | awk '{print "   PID:", $2, "| Uptime:", $10}'
else
    echo "❌ Bot is NOT running!"
    echo "   Start with: nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &"
fi
echo ""

echo "2️⃣ CHECKING ORDERS PLACED..."
echo "----------------------------------------"
ORDER_COUNT=$(grep -c "Order ID:" bot.log 2>/dev/null || echo "0")
echo "   Total orders placed: $ORDER_COUNT"
if [ "$ORDER_COUNT" -gt 0 ]; then
    echo "   ✅ Bot IS placing orders!"
    echo ""
    echo "   Last 5 orders:"
    grep "Order ID:" bot.log | tail -5
else
    echo "   ❌ No orders placed yet!"
fi
echo ""

echo "3️⃣ CHECKING PROFIT CLOSES..."
echo "----------------------------------------"
PROFIT_CLOSES=$(grep -c "FAST PROFIT HIT\|TP.*HIT\|PROFIT:" bot.log 2>/dev/null || echo "0")
echo "   Total profit closes: $PROFIT_CLOSES"
if [ "$PROFIT_CLOSES" -gt 0 ]; then
    echo "   ✅ Bot IS closing with profits!"
    echo ""
    echo "   Last 5 profit closes:"
    grep "FAST PROFIT HIT\|TP.*HIT.*+.*%" bot.log | tail -5
else
    echo "   ⚠️ No profit closes yet (may still be holding)"
fi
echo ""

echo "4️⃣ CHECKING BALANCE..."
echo "----------------------------------------"
LATEST_BALANCE=$(grep "Balance:" bot.log | tail -1)
if [ -n "$LATEST_BALANCE" ]; then
    echo "   $LATEST_BALANCE"
else
    echo "   ⚠️ No balance info found"
fi
echo ""

echo "5️⃣ CHECKING ACTIVE TRADES..."
echo "----------------------------------------"
ACTIVE_COUNT=$(grep "Active trades on" bot.log | tail -10 | wc -l)
echo "   Active trade sessions: $ACTIVE_COUNT"
if [ "$ACTIVE_COUNT" -gt 0 ]; then
    echo "   ✅ Bot has active trades!"
    echo ""
    echo "   Recent active trades:"
    grep "Active trades on" bot.log | tail -10
else
    echo "   ⚠️ No active trades found"
fi
echo ""

echo "6️⃣ CHECKING ERRORS..."
echo "----------------------------------------"
ERROR_COUNT=$(grep -c "ERROR\|Insufficient balance\|Failed to" bot.log 2>/dev/null || echo "0")
echo "   Total errors: $ERROR_COUNT"
if [ "$ERROR_COUNT" -gt 20 ]; then
    echo "   ⚠️ High error count! Recent errors:"
    grep "ERROR\|Insufficient balance\|Failed" bot.log | tail -10
elif [ "$ERROR_COUNT" -gt 0 ]; then
    echo "   ⚠️ Some errors found:"
    grep "ERROR\|Insufficient balance\|Failed" bot.log | tail -5
else
    echo "   ✅ No errors!"
fi
echo ""

echo "7️⃣ CHECKING COLLECTIVE SYSTEMS..."
echo "----------------------------------------"
echo "   Collective Consensus:"
if grep -q "COLLECTIVE CONSENSUS.*initialized" bot.log; then
    echo "      ✅ ACTIVE"
    CONSENSUS_APPROVALS=$(grep -c "Signal APPROVED" bot.log 2>/dev/null || echo "0")
    CONSENSUS_REJECTIONS=$(grep -c "Signal REJECTED" bot.log 2>/dev/null || echo "0")
    echo "      Approvals: $CONSENSUS_APPROVALS | Rejections: $CONSENSUS_REJECTIONS"
else
    echo "      ⚠️ Not initialized"
fi

echo ""
echo "   Situational Awareness:"
if grep -q "SITUATIONAL AWARENESS initialized" bot.log; then
    echo "      ✅ ACTIVE"
    CURRENT_MODE=$(grep "Mode:" bot.log | tail -1)
    echo "      $CURRENT_MODE"
else
    echo "      ⚠️ Not initialized"
fi

echo ""
echo "   Enriched Signals:"
if grep -q "ENRICHED SIGNAL SYSTEM initialized" bot.log; then
    echo "      ✅ ACTIVE"
else
    echo "      ⚠️ Not initialized"
fi
echo ""

echo "8️⃣ CHECKING SIGNAL FLOW..."
echo "----------------------------------------"
SIGNALS_GENERATED=$(grep -c "Signal generated\|COLLECTIVE CONSENSUS" bot.log 2>/dev/null || echo "0")
echo "   Signals processed: $SIGNALS_GENERATED"
if [ "$SIGNALS_GENERATED" -gt 0 ]; then
    echo "   ✅ Signal flow active!"
else
    echo "   ⚠️ No signals yet"
fi
echo ""

echo "9️⃣ CHECKING PAIRS DISCOVERED..."
echo "----------------------------------------"
PAIRS_DISCOVERED=$(grep "Initial scan complete" bot.log | tail -1)
if [ -n "$PAIRS_DISCOVERED" ]; then
    echo "   $PAIRS_DISCOVERED"
    echo ""
    echo "   Per exchange:"
    grep "Found.*USDT pairs on" bot.log | tail -10
else
    echo "   ⚠️ Scanner hasn't completed yet"
fi
echo ""

echo "🔟 PROFIT SUMMARY..."
echo "----------------------------------------"
echo "   Total profit mentions:"
grep -i "profit" bot.log | grep -v "profit_system\|profit monitoring\|PROFIT_MONITORING" | tail -10
echo ""

echo "============================================================================"
echo "📊 DIAGNOSIS SUMMARY"
echo "============================================================================"
echo ""

# Overall status
if [ "$ORDER_COUNT" -gt 0 ]; then
    echo "✅ WORKING: Bot is placing orders"
else
    echo "❌ FAILING: No orders placed"
fi

if [ "$PROFIT_CLOSES" -gt 0 ]; then
    echo "✅ WORKING: Bot is closing with profits"
else
    echo "⚠️ PENDING: No profit closes yet (may be too early)"
fi

if [ "$ERROR_COUNT" -gt 50 ]; then
    echo "❌ FAILING: High error count ($ERROR_COUNT)"
elif [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️ WARNING: Some errors ($ERROR_COUNT)"
else
    echo "✅ WORKING: No errors"
fi

echo ""
echo "============================================================================"
echo "💡 RECOMMENDATIONS:"
echo "============================================================================"
echo ""

if [ "$ORDER_COUNT" -eq 0 ]; then
    echo "🔴 NO ORDERS PLACED:"
    echo "   - Check if signals are being generated"
    echo "   - Check if collective consensus is approving signals"
    echo "   - Check balance availability"
    echo "   Run: grep 'Signal.*APPROVED\|Signal.*REJECTED' bot.log | tail -20"
fi

if [ "$PROFIT_CLOSES" -eq 0 ] && [ "$ORDER_COUNT" -gt 0 ]; then
    echo "🟡 NO PROFIT CLOSES YET:"
    echo "   - Orders placed but not closed yet"
    echo "   - Check hold times (1m = 60s, 5m = 5min)"
    echo "   - Run: grep 'Max hold\|Held for' bot.log | tail -10"
fi

if [ "$ERROR_COUNT" -gt 20 ]; then
    echo "🔴 HIGH ERROR COUNT:"
    echo "   - Review recent errors"
    echo "   - Run: grep 'ERROR' bot.log | tail -20"
fi

echo ""
echo "============================================================================"
