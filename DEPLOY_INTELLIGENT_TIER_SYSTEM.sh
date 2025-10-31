#!/bin/bash
# DEPLOY INTELLIGENT TIER SYSTEM TO VPS

echo ""
echo "================================================================================"
echo "🚀 DEPLOYING INTELLIGENT TIER SYSTEM TO VPS"
echo "================================================================================"
echo ""

# Check if we're in workspace
if [ ! -f "BALANCE_TIER_COORDINATOR.py" ]; then
    echo "❌ Run this from the workspace directory!"
    exit 1
fi

echo "📦 Files to deploy:"
echo "   1. BALANCE_TIER_COORDINATOR.py"
echo "   2. DYNAMIC_PAIR_DISCOVERY.py"
echo "   3. ENHANCED_AGGRESSIVE_MICRO_SCALPER.py"
echo "   4. INTEGRATE_INTELLIGENT_TIER_SYSTEM.py"
echo ""

# Define VPS path
VPS_PATH="~/apex_bot"

echo "🔄 Step 1: Copying new files to VPS..."
echo ""

# Copy the 3 new engine files
for file in BALANCE_TIER_COORDINATOR.py DYNAMIC_PAIR_DISCOVERY.py ENHANCED_AGGRESSIVE_MICRO_SCALPER.py; do
    if [ -f "$file" ]; then
        cp "$file" "$VPS_PATH/" 2>/dev/null || {
            echo "⚠️  Could not copy $file (might not be on VPS yet)"
            echo "   Manual copy: scp $file user@vps:$VPS_PATH/"
        }
        echo "   ✅ $file"
    else
        echo "   ❌ $file not found!"
    fi
done

echo ""
echo "🔧 Step 2: Running integration script..."
echo ""

# Check if already on VPS
if [ -d "$VPS_PATH" ]; then
    cd "$VPS_PATH"
    python3 INTEGRATE_INTELLIGENT_TIER_SYSTEM.py
else
    echo "⚠️  Not on VPS - manual integration needed"
    echo "   On VPS, run: cd ~/apex_bot && python3 INTEGRATE_INTELLIGENT_TIER_SYSTEM.py"
fi

echo ""
echo "================================================================================"
echo "✅ DEPLOYMENT INSTRUCTIONS"
echo "================================================================================"
echo ""
echo "IF YOU'RE DEPLOYING TO A REMOTE VPS:"
echo ""
echo "1. Copy files:"
echo "   scp BALANCE_TIER_COORDINATOR.py DYNAMIC_PAIR_DISCOVERY.py \\"
echo "       ENHANCED_AGGRESSIVE_MICRO_SCALPER.py INTEGRATE_INTELLIGENT_TIER_SYSTEM.py \\"
echo "       user@your-vps:~/apex_bot/"
echo ""
echo "2. SSH into VPS:"
echo "   ssh user@your-vps"
echo ""
echo "3. Run integration:"
echo "   cd ~/apex_bot"
echo "   python3 INTEGRATE_INTELLIGENT_TIER_SYSTEM.py"
echo ""
echo "4. Restart bot:"
echo "   pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR"
echo "   nohup apex_venv/bin/python COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &"
echo ""
echo "5. Monitor:"
echo "   tail -f apex_bot.log | grep -E 'Tier|MICRO SCALP|Dynamic Pair'"
echo ""
echo "================================================================================"
echo ""
