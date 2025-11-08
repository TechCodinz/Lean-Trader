#!/bin/bash
# ⚡ QUICK VERIFICATION - Verify bot is ready to trade

echo "════════════════════════════════════════════════════════════"
echo "⚡ QUICK VERIFICATION - Digital Trading God Status"
echo "════════════════════════════════════════════════════════════"
echo ""

# 1. Check all engines import successfully
echo "1️⃣  Checking engine imports..."
python3 -c "
from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator
from PROFESSIONAL_RISK_MANAGEMENT import get_risk_manager
from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem
from EVOLUTION_ENGINE import ULTIMATE_EVOLUTION_ENGINE
from ultra_swarm_consciousness import UltraSwarmConsciousness
from COLLECTIVE_SWARM_INTELLIGENCE import CollectiveSwarmIntelligence
from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
from AUTO_INTEGRATE_ALL_ENGINES import integrate_all_engines_to_consciousness
print('✅ All engines import successfully')
" 2>/dev/null && echo "   ✅ Imports: SUCCESS" || echo "   ❌ Imports: FAILED"

# 2. Check consciousness system
echo ""
echo "2️⃣  Checking consciousness system..."
python3 -c "
from CONSCIOUSNESS_HARMONIZER import get_consciousness_harmonizer
h = get_consciousness_harmonizer()
print(f'✅ Consciousness: {len(h.engines)} engines registered')
" 2>/dev/null && echo "   ✅ Consciousness: ACTIVE" || echo "   ❌ Consciousness: FAILED"

# 3. Check evolution database
echo ""
echo "3️⃣  Checking evolution database..."
if [ -f "enhanced_trading_bot.db" ]; then
    size=$(du -h enhanced_trading_bot.db | cut -f1)
    echo "   ✅ Evolution DB: $size"
else
    echo "   ⚠️  Evolution DB: Not found (will be created on first run)"
fi

# 4. Check environment variables
echo ""
echo "4️⃣  Checking environment..."
if [ -f ".env" ]; then
    mode=$(grep "TRADING_MODE" .env | cut -d'=' -f2)
    live=$(grep "ENABLE_LIVE" .env | cut -d'=' -f2)
    echo "   ✅ Environment file found"
    echo "   Mode: $mode"
    echo "   Live trading: $live"
else
    echo "   ⚠️  .env file not found"
fi

# 5. Check Gate.io credentials
echo ""
echo "5️⃣  Checking Gate.io credentials..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GATEIO_API_KEY', '')
api_secret = os.getenv('GATEIO_API_SECRET', '')
if api_key and api_secret:
    print('✅ Gate.io credentials configured')
else:
    print('⚠️  Gate.io credentials missing')
" 2>/dev/null

# 6. Check if bot is running
echo ""
echo "6️⃣  Checking if bot is already running..."
if pgrep -f "RUN_BOT.py\|AUTOMATED_ORCHESTRATOR" > /dev/null; then
    pid=$(pgrep -f "RUN_BOT.py\|AUTOMATED_ORCHESTRATOR")
    echo "   ⚠️  Bot is ALREADY RUNNING (PID: $pid)"
    echo "   Use: pkill -9 -f RUN_BOT.py  (to stop it)"
else
    echo "   ✅ No bot running - ready to start"
fi

# 7. Run complete systems audit
echo ""
echo "7️⃣  Running complete systems audit..."
python3 COMPLETE_SYSTEMS_AUDIT.py 2>&1 | grep -E "Pass Rate|AUDIT SUMMARY" | tail -5

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ VERIFICATION COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🚀 TO START THE BOT:"
echo "   python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py"
echo ""
echo "📊 TO MONITOR:"
echo "   tail -f bot.log | grep -E 'EXECUTED|PROFIT|P&L'"
echo ""
echo "🌟 TO CHECK CONSCIOUSNESS:"
echo "   tail -f bot.log | grep -E '🌟|Consciousness|Harmony'"
echo ""
echo "════════════════════════════════════════════════════════════"
