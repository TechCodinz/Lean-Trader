#!/bin/bash
# ⚡ DEPLOY HYBRID AUTONOMOUS TRADING SYSTEM
# This deploys the complete fix for non-blocking AI + smart balance management

set -e  # Exit on error

echo "================================================"
echo "⚡ DEPLOYING HYBRID AUTONOMOUS SYSTEM"
echo "================================================"
echo ""

cd ~/bot

# 1. Check current status
echo "📊 Current bot status:"
ps aux | grep COMPLETE_ULTIMATE_ORCHESTRATOR | grep -v grep || echo "   Bot not running"
echo ""

# 2. Save any uncommitted changes
echo "💾 Saving current state..."
git stash
echo "   ✅ State saved"
echo ""

# 3. Pull latest fixes
echo "⬇️  Pulling critical fixes..."
git pull origin continue-from-micro-fix --no-edit
echo "   ✅ Fixes pulled"
echo ""

# 4. Stop old bot
echo "🛑 Stopping old bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "   No old bot running"
sleep 3
echo "   ✅ Old bot stopped"
echo ""

# 5. Start new bot
echo "🚀 Starting hybrid autonomous bot..."
nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!
echo "   ✅ Bot started (PID: $BOT_PID)"
echo ""

# 6. Wait for initialization
echo "⏳ Waiting for bot to initialize..."
sleep 5

# 7. Check if running
if ps -p $BOT_PID > /dev/null; then
    echo "   ✅ Bot is running!"
else
    echo "   ❌ Bot failed to start! Check bot.log"
    exit 1
fi
echo ""

# 8. Show recent logs
echo "📋 Recent logs:"
tail -20 bot.log
echo ""

# 9. Monitor commands
echo "================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================"
echo ""
echo "📊 MONITORING COMMANDS:"
echo ""
echo "# Watch live logs:"
echo "tail -f bot.log"
echo ""
echo "# Check active trades:"
echo "grep 'Active trades on' bot.log | tail -10"
echo ""
echo "# Check balance:"
echo "grep 'Balance:' bot.log | tail -5"
echo ""
echo "# Check profits:"
echo "grep -i 'profit\\|P&L' bot.log | tail -20"
echo ""
echo "# Check AI usage:"
echo "grep -i 'AI\\|consultation' bot.log | tail -10"
echo ""
echo "# Check orders placed:"
echo "grep 'Order ID:' bot.log | tail -10"
echo ""
echo "================================================"
echo "🎉 WHAT'S FIXED:"
echo "================================================"
echo ""
echo "1. ✅ NON-BLOCKING AI (2-second timeout)"
echo "   - AI enhances when available"
echo "   - Bot continues with engines when AI fails"
echo "   - No more waiting for 401/timeout errors"
echo ""
echo "2. ✅ SMART BALANCE MANAGEMENT"
echo "   - Checks free balance before orders"
echo "   - Accounts for open positions"
echo "   - Auto-reduces size if insufficient"
echo "   - Skips if less than \$5 available"
echo ""
echo "3. ✅ INTELLIGENT ROUTING"
echo "   - Routes pairs to correct exchanges"
echo "   - Gracefully skips unsupported pairs"
echo "   - MT5 integration for forex/TradFi"
echo ""
echo "================================================"
echo "🚀 BOT STATUS:"
echo "================================================"
echo ""

# Show current stats
ACTIVE_TRADES=$(grep -c "Active trades on" bot.log 2>/dev/null || echo "0")
ORDERS_PLACED=$(grep -c "Order ID:" bot.log 2>/dev/null || echo "0")
echo "   Active Trade Sessions: $ACTIVE_TRADES"
echo "   Orders Placed Today: $ORDERS_PLACED"
echo ""

LATEST_BALANCE=$(grep "Balance:" bot.log | tail -1)
if [ -n "$LATEST_BALANCE" ]; then
    echo "   $LATEST_BALANCE"
else
    echo "   Balance: Initializing..."
fi
echo ""

echo "================================================"
echo "⚡ HYBRID SYSTEM ACTIVE!"
echo "================================================"
echo ""
echo "The bot is now trading with:"
echo "   🤖 AI Collective (when available)"
echo "   🧠 205+ Ultra Engines (always active)"
echo "   💰 Smart balance management"
echo "   🎯 Intelligent routing"
echo "   ⚡ Fast execution (2s AI timeout)"
echo ""
echo "Monitor with: tail -f bot.log"
echo ""
