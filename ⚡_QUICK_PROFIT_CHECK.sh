#!/bin/bash
#
# ⚡ QUICK PROFIT CHECK - See bot performance instantly
#

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "💰 QUICK PROFIT & EVOLUTION CHECK"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if bot is running
if pgrep -f "COMPLETE_ULTIMATE_ORCHESTRATOR" > /dev/null; then
    echo "✅ Bot Status: RUNNING"
else
    echo "❌ Bot Status: STOPPED"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 RECENT TRADES & PROFIT:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -1000 apex_bot.log | grep -E "Profit|WIN|LOSS|Trade.*executed|Balance.*updated" | tail -20 || echo "No trades yet"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧬 EVOLUTION STATUS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -1000 apex_bot.log | grep -i "evolution\|evolving\|evolved" | tail -10 || echo "Evolution warming up"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 INTELLIGENCE STATUS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -1000 apex_bot.log | grep -E "AI.*initialized|Balance.*Manager|Intelligence|Coordinator" | tail -10 || echo "Intelligence loading"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 PROFIT SUMMARY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Try to extract profit data
WINS=$(tail -1000 apex_bot.log | grep -c "WIN" 2>/dev/null || echo "0")
LOSSES=$(tail -1000 apex_bot.log | grep -c "LOSS" 2>/dev/null || echo "0")
TOTAL=$((WINS + LOSSES))

if [ $TOTAL -gt 0 ]; then
    WIN_RATE=$(echo "scale=1; $WINS * 100 / $TOTAL" | bc 2>/dev/null || echo "0")
    echo "  Total Trades: $TOTAL"
    echo "  Wins: $WINS ✅"
    echo "  Losses: $LOSSES ❌"
    echo "  Win Rate: ${WIN_RATE}%"
else
    echo "  No trades yet - Bot is analyzing markets"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Run again anytime: bash ⚡_QUICK_PROFIT_CHECK.sh"
echo "═══════════════════════════════════════════════════════════════════════════════"
