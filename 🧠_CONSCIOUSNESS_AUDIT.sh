#!/bin/bash
# 🧠 COMPREHENSIVE CONSCIOUSNESS SYSTEMS AUDIT
# Checks all AI/Learning/Consciousness components

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🧠 CONSCIOUSNESS & INTELLIGENCE SYSTEMS AUDIT 🧠           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if bot is running
echo "═══════════════════════════════════════════════════════"
echo "1️⃣  BOT STATUS"
echo "═══════════════════════════════════════════════════════"
ps aux | grep COMPLETE_ULTIMATE_ORCHESTRATOR | grep -v grep
echo ""

# Check all consciousness files exist
echo "═══════════════════════════════════════════════════════"
echo "2️⃣  CONSCIOUSNESS FILES CHECK"
echo "═══════════════════════════════════════════════════════"
files=(
    "WIRE_BRAIN_HIVEMIND.py"
    "SENTIENT_TRADING_BRAIN.py"
    "UNIVERSAL_CONSCIOUSNESS_INTEGRATION.py"
    "CONSCIOUSNESS_HARMONIZER.py"
    "COLLECTIVE_SWARM_INTELLIGENCE.py"
    "SENTIENT_INTEGRATION.py"
    "SENTIENT_TRADER_ULTIMATE.py"
    "SENTIENT_SCALPING_COORDINATOR.py"
    "EVOLUTION_ENGINE.py"
    "IMMORTAL_MEMORY_SYSTEM.py"
    "IBM_QUANTUM_ENGINE.py"
    "DIVINE_INTELLIGENCE_FEATURES.py"
    "REVOLUTIONARY_AI_FEATURES.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
    fi
done
echo ""

# Check what's imported in the orchestrator
echo "═══════════════════════════════════════════════════════"
echo "3️⃣  ORCHESTRATOR IMPORTS"
echo "═══════════════════════════════════════════════════════"
echo "Checking what consciousness systems are imported..."
grep -E "from (WIRE_BRAIN|SENTIENT|CONSCIOUSNESS|COLLECTIVE|EVOLUTION|IMMORTAL|QUANTUM|DIVINE|REVOLUTIONARY)" COMPLETE_ULTIMATE_ORCHESTRATOR.py | head -20
echo ""

# Check initialization in orchestrator
echo "═══════════════════════════════════════════════════════"
echo "4️⃣  ORCHESTRATOR INITIALIZATION"
echo "═══════════════════════════════════════════════════════"
echo "Checking what gets initialized..."
grep -E "self\.(brain|hive|consciousness|sentient|collective|evolution|immortal|quantum)" COMPLETE_ULTIMATE_ORCHESTRATOR.py | grep -v "^#" | head -20
echo ""

# Check apex.log for consciousness activity
echo "═══════════════════════════════════════════════════════"
echo "5️⃣  ACTIVE SYSTEMS IN LOGS (Last startup)"
echo "═══════════════════════════════════════════════════════"

echo ""
echo "🧠 BRAIN/HIVEMIND:"
grep -i "brain\|hivemind" apex.log | tail -3

echo ""
echo "🤖 SENTIENT SYSTEMS:"
grep -i "sentient" apex.log | tail -3

echo ""
echo "🌌 CONSCIOUSNESS:"
grep -i "consciousness\|harmonizer" apex.log | tail -3

echo ""
echo "🐝 COLLECTIVE SWARM:"
grep -i "swarm\|collective" apex.log | tail -3

echo ""
echo "🧬 EVOLUTION ENGINE:"
grep -i "evolution engine\|generation" apex.log | tail -3

echo ""
echo "💾 IMMORTAL MEMORY:"
grep -i "immortal\|memory system" apex.log | tail -3

echo ""
echo "⚛️ QUANTUM SYSTEMS:"
grep -i "quantum" apex.log | tail -3

echo ""
echo "✨ DIVINE/REVOLUTIONARY AI:"
grep -i "divine\|revolutionary" apex.log | tail -3

echo ""
echo "═══════════════════════════════════════════════════════"
echo "6️⃣  DATABASE STATUS"
echo "═══════════════════════════════════════════════════════"

if [ -f "evolution_engine.db" ]; then
    echo "✅ evolution_engine.db exists"
    sqlite3 evolution_engine.db "SELECT COUNT(*) FROM evolution_data;" 2>/dev/null | xargs -I {} echo "   📊 Evolution records: {}"
    sqlite3 evolution_engine.db "SELECT MAX(generation) FROM evolution_data;" 2>/dev/null | xargs -I {} echo "   🧬 Latest generation: {}"
else
    echo "❌ evolution_engine.db MISSING!"
fi

if [ -f "immortal_memory.db" ]; then
    echo "✅ immortal_memory.db exists"
else
    echo "⚠️  immortal_memory.db not found"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "7️⃣  RECENT CONSCIOUSNESS ACTIVITY"
echo "═══════════════════════════════════════════════════════"
echo "Last 10 consciousness-related log entries:"
grep -iE "brain|sentient|consciousness|swarm|evolution|immortal|quantum|divine|learn|adapt|aware" apex.log | tail -10

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ AUDIT COMPLETE"
echo "═══════════════════════════════════════════════════════"
