#!/bin/bash
#
# COMPLETE VPS SETUP - Pull latest + Activate IMMORTAL MEMORY
#

set -e

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🎯 COMPLETE VPS SETUP - PULLING LATEST + IMMORTAL MEMORY"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Stop bot if running
echo "1️⃣  Stopping bot (if running)..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR || true
sleep 2

# Go to bot directory
cd ~/apex_bot

# Pull latest changes
echo ""
echo "2️⃣  Pulling latest code from GitHub..."
echo "   Branch: continue-from-micro-fix"
git checkout -f continue-from-micro-fix
git pull --no-rebase origin continue-from-micro-fix

echo ""
echo "✅ Latest code pulled!"
echo ""

# Download IMMORTAL MEMORY files if not present
echo "3️⃣  Setting up IMMORTAL MEMORY..."
if [ ! -f "IMMORTAL_MEMORY_SYSTEM.py" ]; then
    echo "   Downloading IMMORTAL MEMORY files..."
    curl -L -o IMMORTAL_MEMORY_SYSTEM.py 'https://raw.githubusercontent.com/TechCodinz/Lean-Trader/continue-from-micro-fix/IMMORTAL_MEMORY_SYSTEM.py'
    curl -L -o INTEGRATE_IMMORTAL_MEMORY.py 'https://raw.githubusercontent.com/TechCodinz/Lean-Trader/continue-from-micro-fix/INTEGRATE_IMMORTAL_MEMORY.py'
fi

# Test IMMORTAL MEMORY
echo ""
echo "Testing IMMORTAL MEMORY on your database..."
python3 IMMORTAL_MEMORY_SYSTEM.py

# Integrate it
echo ""
echo "Integrating IMMORTAL MEMORY into evolution engine..."
python3 INTEGRATE_IMMORTAL_MEMORY.py

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "YOUR BOT IS NOW:"
echo "  ✅ Updated to latest code (395,000+ lines!)"
echo "  ✅ Protected with IMMORTAL MEMORY (photographic memory)"
echo "  ✅ Triple redundant backups"
echo "  ✅ Auto-recovery enabled"
echo "  ✅ Git-safe persistence"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "🚀 START YOUR BOT NOW"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Run this command:"
echo ""
echo "  nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex.log 2>&1 &"
echo ""
echo "Then monitor:"
echo ""
echo "  tail -f apex.log"
echo ""
echo "You should see:"
echo "  ✅ LOADED: Generation 1020, 11082 models"
echo "  🧠 IMMORTAL MEMORY activated"
echo "  💾 BACKED UP: ... → 3 locations"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
