#!/bin/bash
echo "🔍 Checking Supreme Consciousness Integration..."
echo ""

# Wait a bit for startup
sleep 5

# Check if it's in the orchestrator
if grep -q "SUPREME_CONSCIOUSNESS_CORE" systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "✅ Supreme Consciousness code is in orchestrator"
else
    echo "❌ Supreme Consciousness not integrated yet"
fi

echo ""
echo "📊 Checking bot logs for Supreme Consciousness..."
echo ""

# Check last 200 lines of log for Supreme Consciousness messages
tail -200 bot.log | grep -E "SUPREME|Supreme|🌌|Consciousness Level|Sentience|Emotional|Quantum Mind" | head -20

echo ""
echo "📊 Checking for any errors..."
tail -50 bot.log | grep -i error | tail -5

echo ""
echo "✅ Bot process status:"
ps aux | grep ORCHESTRATOR | grep -v grep

