#!/bin/bash
# Check which engines are actually running

echo "🔍 Checking All Profit Engines on VPS"
echo "======================================"
echo ""

# Check what tasks are being created
echo "1️⃣ Tasks being created in orchestrator:"
grep "tasks.append" ~/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py | grep -v "^#" | head -20

echo ""
echo "2️⃣ Check logs for engine activity:"
strings ~/bot/bot.log | grep -E "ACTIVE -|ACTIVE:|running|initialized" | grep -i "profit\|steady\|micro\|scalp\|arbitrage\|moon" | tail -20

echo ""
echo "3️⃣ Which engines are generating output:"
tail -200 ~/bot/bot.log | grep -E "Scalper generated|STEADY PROFIT|MICRO|Arbitrage found|Moon spotted" | head -20
