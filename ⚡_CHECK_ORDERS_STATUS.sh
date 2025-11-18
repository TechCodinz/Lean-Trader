#!/bin/bash
# Check what happened to the 8 orders

cd ~/bot

echo "============================================================================"
echo "🔍 CHECKING 8 ORDERS STATUS"
echo "============================================================================"
echo ""

echo "1️⃣ SHOW ALL 8 ORDER IDs:"
echo "----------------------------------------"
grep "Order ID:" bot.log
echo ""

echo "2️⃣ WHAT PAIRS WERE TRADED?"
echo "----------------------------------------"
grep "Order ID:" bot.log -B 5 | grep "EXECUTING\|symbol\|BUY\|SELL" | tail -20
echo ""

echo "3️⃣ DID ORDERS EXECUTE SUCCESSFULLY?"
echo "----------------------------------------"
grep "Order ID:" bot.log -A 10 | grep "success\|executed\|placed\|failed" | tail -20
echo ""

echo "4️⃣ ARE THEY BEING MONITORED?"
echo "----------------------------------------"
grep "Profit monitoring started\|Starting.*profit monitoring" bot.log | tail -10
echo ""

echo "5️⃣ DID ANY CLOSE ALREADY?"
echo "----------------------------------------"
grep "PROFIT HIT\|TP.*HIT\|closed\|exit" bot.log | tail -10
echo ""

echo "6️⃣ CHECK PAPER BROKER (if used):"
echo "----------------------------------------"
grep "PaperBroker\|paper.*order\|simulated" bot.log | tail -10
echo ""

echo "7️⃣ RECENT EXECUTION ATTEMPTS:"
echo "----------------------------------------"
tail -100 bot.log | grep "EXECUTING\|Order\|Balance\|open trades"
echo ""

echo "============================================================================"
echo "💡 RUN THIS:"
echo "============================================================================"
