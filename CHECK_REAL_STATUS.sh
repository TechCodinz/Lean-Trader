#!/bin/bash
# Check what's ACTUALLY happening with the bot

echo "═══════════════════════════════════════════════════════"
echo "🔍 REAL-TIME BOT STATUS CHECK"
echo "═══════════════════════════════════════════════════════"
echo ""

echo "1️⃣ Bot service status:"
sudo systemctl status trading-bot-testnet | head -12
echo ""

echo "2️⃣ Last 2 minutes of activity:"
echo ""

echo "💰 SUCCESSFUL TRADES:"
sudo journalctl -u trading-bot-testnet --since "2 min ago" | grep -E "REAL PROFIT BUY|REAL PROFIT SELL|TRADE EXECUTED" | tail -20
echo ""

echo "📊 PROFIT UPDATES:"
sudo journalctl -u trading-bot-testnet --since "5 min ago" | grep -E "profit cycle|Profit:" | tail -10
echo ""

echo "❌ RECENT ERRORS (if any):"
sudo journalctl -u trading-bot-testnet --since "2 min ago" | grep -E "Insufficient balance|Trade execution failed" | tail -5
echo ""

echo "🧠 DECISION MAKING:"
sudo journalctl -u trading-bot-testnet --since "1 min ago" | grep -E "Decision:" | tail -10
echo ""

echo "📈 SIGNALS GENERATED:"
sudo journalctl -u trading-bot-testnet --since "1 min ago" | grep -E "Scalper generated|Published.*signals" | tail -10
echo ""

echo "═══════════════════════════════════════════════════════"
echo "💡 ANALYSIS"
echo "═══════════════════════════════════════════════════════"
echo ""

# Count recent successes vs failures
successes=$(sudo journalctl -u trading-bot-testnet --since "5 min ago" | grep -c "TRADE EXECUTED" || echo "0")
failures=$(sudo journalctl -u trading-bot-testnet --since "5 min ago" | grep -c "Insufficient balance" || echo "0")

echo "In last 5 minutes:"
echo "  ✅ Successful trades: $successes"
echo "  ❌ Failed attempts: $failures"
echo ""

if [ "$successes" -gt 0 ]; then
    echo "🎉 BOT IS TRADING! Some pairs work, some don't."
    echo "   This is normal - Bybit testnet doesn't support all pairs."
    echo ""
    echo "💰 Check profit growth:"
    echo "   sudo journalctl -u trading-bot-testnet -f | grep 'Profit:'"
else
    echo "⚠️  No successful trades yet. Keep monitoring."
fi
