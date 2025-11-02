#!/bin/bash
# Find out what REALLY happened to cause $24 → $0.47 loss

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        🔍 INVESTIGATING THE $24 LOSS                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

cd ~/apex_bot

echo "1️⃣ WAS MONITORING LOOP EVER STARTED?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -a "Position monitoring started\|run_monitoring_loop" apex_bot.log | head -5
if [ $? -ne 0 ]; then
    echo "❌ NO MONITORING LOOP FOUND - This is the problem!"
else
    echo "✅ Monitoring loop was started"
fi
echo ""

echo "2️⃣ WERE POSITIONS EVER MONITORED?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -a "MONITORING:" apex_bot.log | head -10
if [ $? -ne 0 ]; then
    echo "❌ NO POSITION MONITORING FOUND"
    echo "   Positions were opened but NEVER checked!"
else
    echo "✅ Positions were monitored"
fi
echo ""

echo "3️⃣ WERE POSITIONS CLOSED PROPERLY?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -a "CLOSED:\|CLOSING:\|Take profit\|Stop loss\|TAKE_PROFIT\|STOP_LOSS" apex_bot.log | tail -20
if [ $? -ne 0 ]; then
    echo "❌ NO PROPER CLOSES FOUND"
    echo "   Positions might have been auto-liquidated or manually closed"
else
    echo "✅ Positions were closed by bot"
fi
echo ""

echo "4️⃣ WHAT WAS THE P&L?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -a "P&L:\|profit.*\$\|loss.*\$\|Profit:" apex_bot.log | tail -20
echo ""

echo "5️⃣ BALANCE HISTORY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -a "balance.*\$\|Balance.*\$" apex_bot.log | grep -E "[0-9]+\.[0-9]+" | tail -20
echo ""

echo "6️⃣ ALL SUCCESSFUL ORDER EXECUTIONS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -a "ORDER EXECUTED\|order.*success\|✅.*order" apex_bot.log | tail -10
if [ $? -ne 0 ]; then
    echo "❌ NO SUCCESSFUL ORDERS FOUND IN RECENT LOGS"
else
    echo "(Successful orders shown above)"
fi
echo ""

echo "7️⃣ EXECUTION ORCHESTRATOR STATUS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -a "EXECUTION LOOP STARTED\|Profit System.*ACTIVE" apex_bot.log | head -5
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    🎯 DIAGNOSIS                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Based on the output above:"
echo ""
echo "If #1 shows ❌ → Monitoring loop never started"
echo "              → Positions opened but never managed"
echo "              → Likely hit exchange auto-stops or expired"
echo ""
echo "If #2 shows ❌ → Positions not being checked"
echo "              → Profit-taking system not working"
echo ""
echo "If #3 shows ❌ → Bot didn't close positions"
echo "              → Exchange might have closed them"
echo "              → Or user closed manually"
echo ""
echo "If balance went $24 → $0.47:"
echo "   → $23.53 lost (96% drawdown)"
echo "   → Either many small losses or few large losses"
echo "   → Need to see P&L history from #4"
echo ""
