#!/bin/bash
cd ~/apex_bot

echo "🔧 Fixing git conflicts..."
echo ""

# Remove lock
rm -f .git/index.lock

# Stash any local changes
echo "1. Stashing local changes..."
git stash
echo ""

# Pull new code
echo "2. Pulling new code..."
git pull origin continue-from-micro-fix
echo ""

# Stop bot
echo "3. Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3
echo "   ✅ Stopped"
echo ""

# Clear log
echo "4. Clearing log..."
> apex.log
echo ""

# Start with NEW code
echo "5. Starting with ALL PAIRS FIX..."
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode live > apex.log 2>&1 &
echo "   ✅ Started"
echo ""

# Wait
echo "6. Waiting 40 seconds..."
sleep 40
echo ""

echo "=========================================="
echo "📊 VERIFICATION"
echo "=========================================="
echo ""

echo "🌍 Dynamic Pairs (should see 100-1000+):"
tail -200 apex.log | grep -E "🌍|Fetched.*pairs|Loaded.*pairs|dynamic" | head -10
echo ""

echo "⚡ Recent Trades (should see varied pairs, not just BTC/ETH/SOL):"
tail -100 apex.log | grep "EXECUTING" | tail -10
echo ""

echo "💎 Enhanced Grower:"
tail -100 apex.log | grep "💎" | tail -5
echo ""

echo "❌ Errors:"
tail -50 apex.log | grep -i "error" | tail -3
echo ""

echo "=========================================="
echo "✅ DONE!"
echo "=========================================="
