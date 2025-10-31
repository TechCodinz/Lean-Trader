#!/bin/bash
# QUICK DEPLOY - One command to deploy entire intelligent tier system to VPS

set -e  # Exit on error

echo ""
echo "================================================================================"
echo "🚀 QUICK DEPLOY - INTELLIGENT TIER SYSTEM"
echo "================================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "BALANCE_TIER_COORDINATOR.py" ]; then
    echo "❌ Error: Not in workspace directory!"
    echo "   This script should be run from /workspace"
    exit 1
fi

VPS_PATH="${1:-~/apex_bot}"

echo "📍 Deployment target: $VPS_PATH"
echo ""

# List of files to deploy
FILES=(
    "BALANCE_TIER_COORDINATOR.py"
    "DYNAMIC_PAIR_DISCOVERY.py"
    "ENHANCED_AGGRESSIVE_MICRO_SCALPER.py"
    "INTEGRATE_INTELLIGENT_TIER_SYSTEM.py"
)

echo "📦 Files to deploy:"
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - NOT FOUND!"
        exit 1
    fi
done
echo ""

# Check if VPS_PATH exists
if [ ! -d "$VPS_PATH" ]; then
    echo "⚠️  Warning: $VPS_PATH does not exist!"
    echo "   Creating directory..."
    mkdir -p "$VPS_PATH" || {
        echo "❌ Failed to create directory"
        echo "   Are you on the VPS? If remote, specify VPS path."
        exit 1
    }
fi

echo "📋 Step 1: Copying files to $VPS_PATH..."
for file in "${FILES[@]}"; do
    cp "$file" "$VPS_PATH/" && echo "   ✅ Copied $file" || {
        echo "   ❌ Failed to copy $file"
        exit 1
    }
done
echo ""

echo "🔧 Step 2: Running integration script..."
cd "$VPS_PATH"

if [ ! -f "COMPLETE_ULTIMATE_ORCHESTRATOR.py" ]; then
    echo "⚠️  COMPLETE_ULTIMATE_ORCHESTRATOR.py not found in $VPS_PATH"
    echo "   Are you sure this is the apex_bot directory?"
    exit 1
fi

python3 INTEGRATE_INTELLIGENT_TIER_SYSTEM.py || {
    echo "❌ Integration failed!"
    echo "   Check the error messages above"
    exit 1
}
echo ""

echo "🛑 Step 3: Stopping old bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "   (No running bot found)"
sleep 2
echo ""

echo "🚀 Step 4: Starting bot with intelligent tier system..."
if [ ! -d "apex_venv" ]; then
    echo "⚠️  apex_venv not found - using system python"
    nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &
else
    nohup apex_venv/bin/python COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &
fi
BOT_PID=$!
echo "   ✅ Bot started (PID: $BOT_PID)"
echo ""

echo "⏳ Waiting 10 seconds for initialization..."
sleep 10
echo ""

echo "📊 Step 5: Checking deployment..."
if ps -p $BOT_PID > /dev/null; then
    echo "   ✅ Bot is running!"
else
    echo "   ❌ Bot failed to start!"
    echo "   Check apex_bot.log for errors"
    exit 1
fi
echo ""

# Check for tier system initialization
if grep -q "Tier Coordinator initialized" apex_bot.log 2>/dev/null; then
    echo "   ✅ Tier Coordinator active"
else
    echo "   ⚠️  Tier Coordinator not found in log"
fi

if grep -q "Dynamic Pair Discovery" apex_bot.log 2>/dev/null; then
    echo "   ✅ Dynamic Pair Discovery active"
else
    echo "   ⚠️  Dynamic Pair Discovery not found in log"
fi

if grep -q "Enhanced Micro Scalper" apex_bot.log 2>/dev/null; then
    echo "   ✅ Enhanced Micro Scalper active"
else
    echo "   ⚠️  Enhanced Micro Scalper not found in log"
fi
echo ""

echo "================================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================================================"
echo ""
echo "📊 Monitor the bot:"
echo "   tail -f $VPS_PATH/apex_bot.log | grep -E 'Tier|MICRO SCALP|Dynamic Pair'"
echo ""
echo "📈 Check status:"
echo "   cd $VPS_PATH && python3 -c 'from BALANCE_TIER_COORDINATOR import get_tier_coordinator; tc = get_tier_coordinator(); print(f\"Tier: {tc.current_tier}\")'"
echo ""
echo "🔍 View logs:"
echo "   tail -100 $VPS_PATH/apex_bot.log"
echo ""
echo "================================================================================"
echo ""
