#!/bin/bash
# 🔥 CRITICAL FIX: Activate UnifiedDecisionEngine

echo "═══════════════════════════════════════════════════════"
echo "🔥 DEPLOYING ENGINE SYNCHRONIZATION FIX"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "BEFORE:"
echo "  ✅ Scalper: 47 signals → signal_queue → 🗑️ NOWHERE"
echo "  ❌ DecisionEngine: NOT RUNNING"
echo "  ❌ ExecutionOrchestrator: STARVING (no decisions)"
echo "  ✅ REAL_PROFIT_BOT: Trading alone (only BTC/USDT)"
echo ""
echo "AFTER THIS FIX:"
echo "  ✅ Scalper: signals → DecisionEngine"
echo "  ✅ DecisionEngine: RUNNING → processes signals"
echo "  ✅ ExecutionOrchestrator: receives decisions → EXECUTES"
echo "  ✅ ALL pairs trade (not just BTC/USDT)!"
echo ""

cd /root/trading_bot
source venv/bin/activate

echo "📥 Pulling the fix..."
git fetch origin main
git reset --hard origin/main

echo "✅ Fix pulled"
echo ""

echo "🧹 Clearing cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Cache cleared"
echo ""

echo "🔄 Restarting bot..."
sudo systemctl restart trading-bot-testnet

echo "✅ Bot restarted"
echo ""

echo "⏳ Waiting 60s for startup..."
sleep 60

echo ""
echo "═══════════════════════════════════════════════════════"
echo "🔍 VERIFICATION"
echo "═══════════════════════════════════════════════════════"
echo ""

echo "1️⃣ Is DecisionEngine started?"
sudo journalctl -u trading-bot-testnet --since "2 min ago" | grep -E "Decision loop started|UnifiedDecisionEngine created" | tail -3

echo ""
echo "2️⃣ Is it making decisions? (Should see 🎯 Decision: messages)"
sudo journalctl -u trading-bot-testnet --since "2 min ago" | grep "🎯 Decision:" | tail -10

echo ""
echo "3️⃣ Is ExecutionOrchestrator executing? (Should see ⚡ EXECUTING:)"
sudo journalctl -u trading-bot-testnet --since "2 min ago" | grep "⚡ EXECUTING:" | tail -10

echo ""
echo "4️⃣ Which pairs are being traded?"
sudo journalctl -u trading-bot-testnet --since "2 min ago" | grep -E "TRADE EXECUTED|REAL PROFIT" | tail -15

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "🎯 Expected: You should now see:"
echo "   - Decisions being made for multiple pairs"
echo "   - ExecutionOrchestrator executing trades"
echo "   - Not just BTC/USDT, but ETH, SOL, etc."
echo ""
echo "Monitor live:"
echo "  sudo journalctl -u trading-bot-testnet -f | grep -E 'Decision:|EXECUTING:|TRADE EXECUTED'"
