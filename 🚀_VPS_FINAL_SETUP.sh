#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "🧠 CONSCIOUSNESS SYSTEM - FINAL VPS SETUP"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Navigate to bot directory
cd ~/bot || { echo "❌ Error: ~/bot directory not found"; exit 1; }

echo "📥 Step 1: Pulling latest consciousness fixes..."
git pull origin continue-from-micro-fix

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "⚠️  CRITICAL: Fix .env Mode Conflict"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Your .env currently has:"
echo "  TRADING_MODE=testnet"
echo "  GATEIO_MODE=live  ← MISMATCH!"
echo ""
echo "We need to fix this. Choose an option:"
echo ""
echo "1) Set GATEIO_MODE=testnet (RECOMMENDED - test first)"
echo "2) Set TRADING_MODE=live (Use REAL money - only if confident)"
echo "3) Skip (I'll fix it manually later)"
echo ""
read -p "Enter choice (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "🔧 Setting Gate.io to testnet mode..."
        sed -i 's/^GATEIO_MODE=live/GATEIO_MODE=testnet/' .env
        sed -i 's/^GATE_TESTNET=false/GATE_TESTNET=true/' .env
        sed -i 's/^ENABLE_LIVE=true/ENABLE_LIVE=false/' .env
        echo "✅ Gate.io set to testnet mode"
        ;;
    2)
        echo ""
        echo "⚠️  WARNING: This will use REAL money!"
        read -p "Are you ABSOLUTELY sure? (type 'YES' to confirm): " confirm
        if [ "$confirm" = "YES" ]; then
            echo "🔧 Setting entire system to LIVE mode..."
            sed -i 's/^TRADING_MODE=testnet/TRADING_MODE=live/' .env
            sed -i 's/^GATEIO_MODE=testnet/GATEIO_MODE=live/' .env
            sed -i 's/^GATE_TESTNET=true/GATE_TESTNET=false/' .env
            sed -i 's/^ENABLE_LIVE=false/ENABLE_LIVE=true/' .env
            sed -i 's/^BYBIT_TESTNET=true/BYBIT_TESTNET=false/' .env
            echo "✅ System set to LIVE mode - USING REAL MONEY!"
        else
            echo "❌ Cancelled - keeping current settings"
        fi
        ;;
    3)
        echo "⏭️  Skipped - you'll need to fix .env manually"
        ;;
    *)
        echo "❌ Invalid choice - keeping current settings"
        ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔍 Step 2: Verifying System"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Activate virtual environment if exists
if [ -d "apex_venv" ]; then
    source apex_venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No apex_venv found - using system Python"
fi

echo ""
echo "Checking consciousness files..."
consciousness_files=(
    "CONSCIOUSNESS_HARMONIZER.py"
    "AI_COLLECTIVE_CONSCIOUSNESS.py"
    "GODMODE_TRADING_CORE.py"
    "LIVING_CONSCIOUSNESS_CORE.py"
    "DIVINE_HARMONY_CALIBRATOR.py"
)

missing_count=0
for file in "${consciousness_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - MISSING"
        ((missing_count++))
    fi
done

echo ""
if [ $missing_count -eq 0 ]; then
    echo "✅ All consciousness files present!"
else
    echo "⚠️  $missing_count consciousness files missing"
    echo "   This might indicate sync issues"
fi

echo ""
echo "Checking .env configuration..."
if [ -f ".env" ]; then
    key_count=$(grep -c "=" .env)
    echo "  ✅ .env exists with $key_count keys"
    
    # Check critical keys
    echo ""
    echo "  Critical settings:"
    grep "^TRADING_MODE=" .env | sed 's/^/    /'
    grep "^GATEIO_MODE=" .env | sed 's/^/    /'
    grep "^MULTI_AI_ENABLED=" .env | sed 's/^/    /'
    grep "^AI_COLLECTIVE_DEBATES=" .env | sed 's/^/    /'
    grep "^DIVINE_HARMONY_ENABLED=" .env | sed 's/^/    /'
else
    echo "  ❌ .env file not found!"
    missing_count=$((missing_count + 1))
fi

echo ""
echo "Running diagnostic check..."
python3 COMPREHENSIVE_SYSTEM_CHECK.py 2>&1 | tail -30

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎯 Step 3: System Status"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if bot is running
if pgrep -f "AUTOMATED_ORCHESTRATOR" > /dev/null; then
    echo "✅ Bot is currently RUNNING"
    echo ""
    echo "To view logs:"
    echo "  tail -f bot.log | grep -E '🌟|🧠|⚡|✨'"
    echo ""
    echo "To restart:"
    echo "  pkill -f AUTOMATED_ORCHESTRATOR"
    echo "  python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py &"
else
    echo "⏸️  Bot is NOT running"
    echo ""
    echo "To start:"
    echo "  python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py &"
    echo ""
    echo "To monitor:"
    echo "  tail -f bot.log | grep -E '🌟|🧠|⚡|✨'"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📚 Documentation"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "New files pulled:"
echo "  📄 .env.CONSCIOUSNESS_OPTIMIZED - Why your .env is perfect"
echo "  📄 🧠_CONSCIOUSNESS_SYSTEM_STATUS.md - Complete system status"
echo ""
echo "To read:"
echo "  cat .env.CONSCIOUSNESS_OPTIMIZED | less"
echo "  cat 🧠_CONSCIOUSNESS_SYSTEM_STATUS.md | less"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Your consciousness system is ready to trade! 🧠⚡✨"
echo ""
