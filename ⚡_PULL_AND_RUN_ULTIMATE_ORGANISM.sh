#!/bin/bash
#
# ⚡ PULL AND RUN ULTIMATE ORGANISM ⚡
#
# This script:
# 1. Pulls the complete autonomous organism
# 2. Stops old version
# 3. Starts new version with full intelligence
# 4. Shows you it discovering everything!
#

set -e

echo "================================================================================"
echo "⚡ ACTIVATING ULTIMATE AUTONOMOUS ORGANISM"
echo "================================================================================"
echo ""

# Check we're in apex_bot directory
if [ ! -f "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py" ]; then
    echo "❌ ERROR: Run this from ~/apex_bot directory"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo "🔍 Branch: $(git branch --show-current)"
echo ""

# Step 1: Pull latest
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 PULLING ULTIMATE ORGANISM..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

git stash
git pull origin continue-from-micro-fix

echo ""
echo "✅ Latest organism pulled!"
echo ""

# Step 2: Stop old bot
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 STOPPING OLD VERSION..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "No bot running"

echo ""
echo "✅ Old version stopped"
echo ""

# Step 3: Start new organism
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 STARTING ULTIMATE ORGANISM..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Activate venv
source apex_venv/bin/activate

# Start organism in background
nohup python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > ultimate_organism.log 2>&1 &
ORGANISM_PID=$!

echo "✅ Ultimate organism started! (PID: $ORGANISM_PID)"
echo ""

# Step 4: Show discovery process
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 WATCHING DISCOVERY PROCESS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Watch it discover ALL pairs, analyze ALL opportunities, and start training!"
echo ""
echo "Press Ctrl+C to stop watching (organism will keep running in background)"
echo ""

sleep 5

# Show live discovery
tail -f ultimate_organism.log | grep -E "Discover|Found|TESTNET|LIVE|Trade|Profit|Exchange|Mastery|pairs|MODE" --line-buffered &
TAIL_PID=$!

# Show bot status every 30 seconds
while true; do
    sleep 30
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "📊 ORGANISM STATUS ($(date '+%H:%M:%S'))"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    ps aux | grep COMPLETE_ULTIMATE_ORCHESTRATOR | grep -v grep || echo "⚠️  Organism not running!"
    echo ""
done

# If Ctrl+C pressed, cleanup
trap "kill $TAIL_PID 2>/dev/null; echo ''; echo '✅ Organism running in background!'; echo 'Check logs: tail -f ultimate_organism.log'; exit 0" INT

wait
