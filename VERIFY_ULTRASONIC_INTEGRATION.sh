#!/bin/bash
echo "═══════════════════════════════════════════════════════════════"
echo "🔍 VERIFYING ULTRASONIC CONSCIOUSNESS INTEGRATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd ~/bot 2>/dev/null || cd /workspace

echo "1️⃣ Checking Ultra-Rare Files..."
for file in ULTRASONIC_RARE_STRATEGIES.py ULTRASONIC_INTEGRATION_COMPLETE.py ADVANCED_TRADING_ACTIONS.py AUTO_ADAPTIVE_APEX.py DIRECT_GATE_EXECUTOR.py; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "   ✅ $file ($size)"
    else
        echo "   ❌ $file - MISSING!"
    fi
done

echo ""
echo "2️⃣ Testing Imports..."

python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

print("Testing ULTRASONIC_RARE_STRATEGIES...")
try:
    from ULTRASONIC_RARE_STRATEGIES import UltrasonicStrategiesManager
    print("   ✅ UltrasonicStrategiesManager imports")
except Exception as e:
    print(f"   ❌ Import failed: {e}")

print("\nTesting ADVANCED_TRADING_ACTIONS...")
try:
    from ADVANCED_TRADING_ACTIONS import MarketRegimeDetector, AdvancedActionDecider
    print("   ✅ Advanced actions import")
except Exception as e:
    print(f"   ❌ Import failed: {e}")

print("\nTesting ULTRASONIC_INTEGRATION_COMPLETE...")
try:
    from ULTRASONIC_INTEGRATION_COMPLETE import get_ultrasonic_integration
    integration = get_ultrasonic_integration()
    active = sum(1 for v in integration.systems_active.values() if v)
    total = len(integration.systems_active)
    print(f"   ✅ Integration successful: {active}/{total} systems active")
    
    if active >= 5:
        print("   🎉 ULTRA-RARE CONSCIOUSNESS FULLY OPERATIONAL!")
    elif active >= 3:
        print("   ⚡ ADVANCED SYSTEMS OPERATIONAL")
    else:
        print("   ⚠️ LIMITED SYSTEMS - Some features unavailable")
        
except Exception as e:
    print(f"   ❌ Integration failed: {e}")

print("\nTesting Main Orchestrator...")
try:
    import sys
    sys.path.insert(0, 'systems')
    from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
    print("   ✅ COMPLETE_ULTIMATE_ORCHESTRATOR imports")
except Exception as e:
    print(f"   ❌ Import failed: {e}")

PYEOF

echo ""
echo "3️⃣ Checking Consciousness Files..."
for file in CONSCIOUSNESS_HARMONIZER.py AI_COLLECTIVE_CONSCIOUSNESS.py GODMODE_TRADING_CORE.py; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ⚠️ $file - Not found (some ultrasonic features may be limited)"
    fi
done

echo ""
echo "4️⃣ Checking .env Configuration..."
if [ -f ".env" ]; then
    keys=$(grep -c "=" .env 2>/dev/null || echo "0")
    echo "   ✅ .env exists with $keys keys"
    
    # Check critical settings
    if grep -q "MULTI_AI_ENABLED=true" .env; then
        echo "   ✅ MULTI_AI_ENABLED=true"
    else
        echo "   ⚠️ MULTI_AI_ENABLED not set to true"
    fi
    
    if grep -q "DIVINE_HARMONY_ENABLED=true" .env; then
        echo "   ✅ DIVINE_HARMONY_ENABLED=true"
    else
        echo "   ⚠️ DIVINE_HARMONY_ENABLED not set to true"
    fi
else
    echo "   ❌ .env file not found!"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ VERIFICATION COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Review any warnings above"
echo "2. If all green, you're ready to trade!"
echo "3. Start bot: python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py"
echo ""

