#!/bin/bash
# 🎊 ONE-COMMAND FINAL FIX
# This applies the last fix needed for 100% working bot

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          🎊 APPLYING FINAL FIX TO APEX BOT              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Navigate to bot directory
cd ~/apex_bot
echo "📂 Working directory: $(pwd)"
echo ""

# Pull latest code
echo "📥 Pulling latest code from branch..."
git pull origin continue-from-micro-fix
echo "✅ Code updated!"
echo ""

# Run the fix script
echo "🔧 Applying _get_all_pairs fix..."
bash FINAL_FIX_GET_PAIRS.sh
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    ✅ ALL DONE!                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Your bot is now 100% operational!"
echo ""
echo "📊 Monitor trading:"
echo "   tail -f apex_bot.log | grep 'Decision:\\|ORDER EXECUTED\\|CLOSED'"
echo ""
echo "💰 Check balance:"
echo "   grep 'balance:' apex_bot.log | tail -1"
echo ""
echo "🎯 See unique pairs being traded:"
echo "   grep 'Decision:' apex_bot.log | tail -100 | grep -oE '[A-Z0-9]+/USDT' | sort -u"
echo ""
