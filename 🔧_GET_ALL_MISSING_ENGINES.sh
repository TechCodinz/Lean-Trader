#!/bin/bash

################################################################################
# 🔧 GET ALL MISSING ENGINE FILES TO VPS
################################################################################

echo "================================================================================"
echo "🔧 FETCHING ALL MISSING ENGINE FILES"
echo "================================================================================"
echo ""

cd ~/bot || cd ~/apex_bot || { echo "❌ Bot directory not found!"; exit 1; }

echo "📥 Fetching latest from GitHub..."
git fetch origin continue-from-micro-fix

echo ""
echo "📋 Checking out missing engine files..."

# List of all critical engine files
FILES=(
    "BOOTSTRAP_PROFIT_TRACKER.py"
    "ULTRA_GOLDMINE_FEATURES.py"
    "ULTRASONIC_INTEGRATION_COMPLETE.py"
    "ULTRASONIC_RARE_STRATEGIES.py"
    "DIVINE_INTELLIGENCE_FEATURES.py"
    "DIVINE_HARMONY_CALIBRATOR.py"
    "SUPREME_CONSCIOUSNESS_CORE.py"
    "SUPREME_ACTIVATION_SYSTEM.py"
    "UNIVERSAL_AI_ORCHESTRATOR.py"
    "mt5_forex_sync.py"
    "MT5_FOREX_ENGINE_INTEGRATION.py"
)

FOUND=0
MISSING=0

for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "📥 Checking out $file..."
        git checkout origin/continue-from-micro-fix -- "$file" 2>&1
        
        if [ -f "$file" ]; then
            SIZE=$(ls -lh "$file" | awk '{print $5}')
            echo "   ✅ Got it! ($SIZE)"
            FOUND=$((FOUND + 1))
        else
            echo "   ❌ Not in repo!"
            MISSING=$((MISSING + 1))
        fi
    else
        echo "✅ $file - already exists"
        FOUND=$((FOUND + 1))
    fi
done

echo ""
echo "================================================================================"
echo "📊 RESULTS"
echo "================================================================================"
echo "  Files found/checked out: $FOUND"
echo "  Files missing from repo: $MISSING"
echo ""

if [ $MISSING -gt 0 ]; then
    echo "⚠️  Some files are not in the GitHub repo yet"
    echo "   Bot will run with reduced features"
else
    echo "✅ ALL ENGINE FILES PRESENT!"
fi

echo "================================================================================"
