#!/bin/bash
# ONE COMMAND TO FIX EVERYTHING

set -e

echo "🔧 FIXING APEX BOT - ONE COMMAND"
echo ""

cd ~/apex_bot

# Stop bot
echo "🛑 Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR || true
sleep 2

# Backup broken file
echo "💾 Backing up current file..."
cp COMPLETE_ULTIMATE_ORCHESTRATOR.py COMPLETE_ULTIMATE_ORCHESTRATOR.py.broken_backup

# Copy fixed files from workspace
echo "📥 Copying fixed files..."
cp /workspace/COMPLETE_ULTIMATE_ORCHESTRATOR.py .
cp /workspace/UNIVERSAL_PAIR_FETCHER.py .

# Verify syntax
echo "✅ Verifying syntax..."
python3 -m py_compile COMPLETE_ULTIMATE_ORCHESTRATOR.py
python3 -m py_compile UNIVERSAL_PAIR_FETCHER.py

# Restart bot
echo "🚀 Starting bot..."
nohup apex_venv/bin/python COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &

echo ""
echo "⏳ Waiting 30 seconds for initialization..."
sleep 30

echo ""
echo "📊 CHECKING RESULTS:"
echo ""
grep "Universal Pair Fetcher\|Fetched.*pairs" apex_bot.log || echo "⚠️  Not found yet - check logs manually"

echo ""
echo "✅ DONE! Check full logs with:"
echo "   tail -f apex_bot.log | grep -i universal"
