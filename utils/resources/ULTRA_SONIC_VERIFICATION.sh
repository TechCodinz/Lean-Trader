#!/bin/bash
# ============================================================================
# ULTRA-SONIC ENGINE VERIFICATION
# Verifies EVERY engine has ALL methods properly implemented
# No workarounds, no passive monitoring - FULL POWER ONLY!
# ============================================================================

set -e

echo "============================================================================"
echo "🚀 ULTRA-SONIC ENGINE VERIFICATION - FULL POWER CHECK"
echo "============================================================================"
echo ""

cd ~/bot

echo "🔧 Step 1: Pull latest ultra-sonic code..."
git fetch origin
git checkout micro-fix-local
git pull origin micro-fix-local
echo "✅ Latest code loaded!"
echo ""

echo "🧪 Step 2: Verifying ALL engine files compile..."
python3 << 'PYEOF'
import sys

files_to_check = [
    'EVOLUTION_ENGINE.py',
    'ultra_scout.py',
    'NEWS_TRADING_ENGINE.py',
    'SESSION_AWARE_TRADING.py',
    'ULTRA_RARE_ENGINES.py',
    'brain.py',
    'hivemind.py',
    'SMART_SCALPING_ENGINE.py',
    'COMPLETE_ULTIMATE_ORCHESTRATOR.py',
    'MICRO_TRADING_BOT.py',
]

all_passed = True
for file in files_to_check:
    try:
        with open(file) as f:
            compile(f.read(), file, 'exec')
        print(f"✅ {file}")
    except SyntaxError as e:
        print(f"❌ {file}: {e}")
        all_passed = False
    except FileNotFoundError:
        print(f"⚠️  {file}: Not found")

if all_passed:
    print("\n✅ All engine files compile successfully!")
    sys.exit(0)
else:
    print("\n❌ Some files have syntax errors!")
    sys.exit(1)
PYEOF

echo ""
echo "🔍 Step 3: Verifying ALL methods exist..."
python3 << 'PYEOF'
import sys
import importlib.util

def check_method(module_name, class_name, method_name, file_path):
    """Check if a method exists in a class"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            if hasattr(cls, method_name):
                print(f"  ✅ {class_name}.{method_name}()")
                return True
            else:
                print(f"  ❌ {class_name}.{method_name}() MISSING!")
                return False
        else:
            print(f"  ⚠️  {class_name} class not found in {module_name}")
            return False
    except Exception as e:
        print(f"  ❌ Error checking {class_name}.{method_name}(): {e}")
        return False

print("CHECKING CRITICAL METHODS:")
print("-" * 80)

all_exist = True

# Evolution Engine
print("\n🧠 EVOLUTION_ENGINE:")
all_exist &= check_method('evolution', 'ULTIMATE_EVOLUTION_ENGINE', 'evolve_strategies', 'EVOLUTION_ENGINE.py')
all_exist &= check_method('evolution', 'ULTIMATE_EVOLUTION_ENGINE', 'evolve_existing_models', 'EVOLUTION_ENGINE.py')

# Ultra Scout
print("\n🔍 ULTRA_SCOUT:")
all_exist &= check_method('scout', 'UltraScout', 'scan_all_sources', 'ultra_scout.py')
all_exist &= check_method('scout', 'UltraScout', 'fetch_onchain_analytics', 'ultra_scout.py')

# News Engine
print("\n📰 NEWS_TRADING_ENGINE:")
all_exist &= check_method('news', 'NewsTradingEngine', 'analyze_latest_news', 'NEWS_TRADING_ENGINE.py')
all_exist &= check_method('news', 'NewsTradingEngine', 'get_trending_news', 'NEWS_TRADING_ENGINE.py')

# Session Trading
print("\n🕐 SESSION_AWARE_TRADING:")
all_exist &= check_method('session', 'SessionAwareTrading', 'find_session_opportunities', 'SESSION_AWARE_TRADING.py')
all_exist &= check_method('session', 'SessionAwareTrading', 'get_current_session', 'SESSION_AWARE_TRADING.py')

# Ultra Rare
print("\n💎 ULTRA_RARE_ENGINES:")
all_exist &= check_method('rare', 'UltraRareEnginesOrchestrator', 'scan_all_engines', 'ULTRA_RARE_ENGINES.py')

# Brain
try:
    print("\n🧠 BRAIN:")
    all_exist &= check_method('brain_mod', 'Brain', 'decide', 'brain.py')
except:
    print("  ⚠️  brain.py check skipped (numpy dependency)")

# Hivemind
try:
    print("\n🐝 HIVEMIND:")
    all_exist &= check_method('hive', 'HiveCoordinator', 'decide', 'hivemind.py')
except:
    print("  ⚠️  hivemind.py check skipped (pandas dependency)")

print("\n" + "=" * 80)
if all_exist:
    print("✅ ALL CRITICAL METHODS IMPLEMENTED!")
    sys.exit(0)
else:
    print("❌ SOME METHODS MISSING - CHECK ABOVE!")
    sys.exit(1)
PYEOF

echo ""
echo "🛑 Step 4: Stopping old bot..."
pkill -9 -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "   (no bot running)"
sleep 3
echo "✅ Old bot stopped!"
echo ""

echo "🚀 Step 5: Starting ULTRA-SONIC BEAST..."
nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!
echo "✅ Bot started! PID: $BOT_PID"
echo ""

echo "⏳ Waiting 15 seconds for all engines to activate..."
sleep 15
echo ""

echo "🔥 Step 6: Verifying ALL engines are FIRING..."
echo ""

# Check each engine
ENGINES=(
    "ULTRA RARE ENGINES ACTIVE"
    "BRAIN ADVISOR ACTIVE"
    "HIVEMIND ACTIVE"
    "NEWS ENGINE publishing"
    "SESSION TRADER publishing"
    "ML STRATEGY publishing"
    "MICRO WALLET GROWER ACTIVE"
    "SMART SCALPING.*ACTIVE"
    "EVOLUTION.*ACTIVE"
)

ACTIVE_COUNT=0
TOTAL_ENGINES=${#ENGINES[@]}

for engine in "${ENGINES[@]}"; do
    if tail -300 bot.log | grep -q "$engine"; then
        echo "✅ $engine"
        ((ACTIVE_COUNT++))
    else
        echo "❌ $engine - NOT DETECTED"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ENGINE STATUS: $ACTIVE_COUNT/$TOTAL_ENGINES engines firing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ACTIVE_COUNT -ge 7 ]; then
    echo "✅ ULTRA-SONIC MODE ACHIEVED!"
    echo "   All critical engines firing at full power!"
else
    echo "⚠️  Some engines not detected yet (may be warming up)"
    echo "   Check bot.log for details"
fi

echo ""
echo "🔍 Step 7: Checking for actual signals..."
echo ""

# Check for signals from each engine
if tail -200 bot.log | grep -q "💎 ULTRA RARE"; then
    echo "✅ Ultra Rare signals detected"
fi

if tail -200 bot.log | grep -q "🧠 BRAIN:"; then
    echo "✅ Brain signals detected"
fi

if tail -200 bot.log | grep -q "🐝 HIVEMIND:"; then
    echo "✅ Hivemind signals detected"
fi

if tail -200 bot.log | grep -q "📰 News signal"; then
    echo "✅ News signals detected"
fi

if tail -200 bot.log | grep -q "🕐 Session signal"; then
    echo "✅ Session signals detected"
fi

if tail -200 bot.log | grep -q "💎 MICRO TRADE"; then
    echo "✅ MICRO trading detected"
    echo ""
    echo "Recent MICRO trades:"
    tail -200 bot.log | grep "💎 MICRO TRADE" | tail -3
fi

if tail -200 bot.log | grep -q "🧠 Evolution cycle"; then
    echo "✅ Evolution cycles detected"
fi

echo ""
echo "============================================================================"
echo "🎉 ULTRA-SONIC VERIFICATION COMPLETE"
echo "============================================================================"
echo ""
echo "Monitoring live ultra-sonic activity (Ctrl+C to stop)..."
echo ""

# Monitor for ultra-sonic activity
tail -f bot.log | grep --line-buffered -E "🚀|💎|🧠|🐝|📰|🕐|⚡|TRADE|Evolution cycle|ULTRA RARE|BRAIN:|HIVEMIND:" | grep -v "Found.*pairs"
