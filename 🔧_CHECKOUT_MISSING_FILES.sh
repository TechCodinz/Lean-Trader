#!/bin/bash

################################################################################
# 🔧 CHECKOUT MISSING FILES FROM GIT
################################################################################

echo "================================================================================"
echo "🔧 CHECKING OUT MISSING FILES FROM GIT"
echo "================================================================================"
echo ""

cd ~/bot || cd ~/apex_bot || { echo "❌ Bot directory not found!"; exit 1; }

# List of missing files
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
)

echo "📊 Checking which files are missing..."
echo ""

MISSING_COUNT=0
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ $file - MISSING"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    else
        echo "✅ $file - EXISTS"
    fi
done

if [ $MISSING_COUNT -eq 0 ]; then
    echo ""
    echo "✅ ALL FILES ALREADY EXIST!"
    exit 0
fi

echo ""
echo "================================================================================"
echo "🔧 CHECKING OUT MISSING FILES"
echo "================================================================================"
echo ""

# Checkout each missing file from origin/continue-from-micro-fix
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "📥 Checking out $file..."
        git checkout origin/continue-from-micro-fix -- "$file" 2>&1
        
        if [ -f "$file" ]; then
            SIZE=$(ls -lh "$file" | awk '{print $5}')
            echo "   ✅ Got it! ($SIZE)"
        else
            echo "   ❌ Failed! File not in repo?"
        fi
    fi
done

echo ""
echo "================================================================================"
echo "✅ VERIFICATION"
echo "================================================================================"
echo ""

STILL_MISSING=0
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - STILL MISSING"
        STILL_MISSING=$((STILL_MISSING + 1))
    fi
done

echo ""
if [ $STILL_MISSING -eq 0 ]; then
    echo "🎉 ALL FILES SUCCESSFULLY CHECKED OUT!"
else
    echo "⚠️  $STILL_MISSING files still missing - they may not be in the repo"
fi

echo "================================================================================"
