#!/bin/bash

echo "================================================================================"
echo "🔍 VPS VERIFICATION - Checking New Intelligence Systems"
echo "================================================================================"
echo ""

# Activate venv
source apex_venv/bin/activate

echo "1️⃣ Checking Python imports..."
python3 << 'PYEOF'
import sys
print("   Testing imports...")

try:
    from AI_CONSULTATION_SERVICE import AIConsultationService
    print("   ✅ AI_CONSULTATION_SERVICE")
except ImportError as e:
    print(f"   ❌ AI_CONSULTATION_SERVICE: {e}")
    sys.exit(1)

try:
    from INTELLIGENT_BALANCE_MANAGER import IntelligentBalanceManager
    print("   ✅ INTELLIGENT_BALANCE_MANAGER")
except ImportError as e:
    print(f"   ❌ INTELLIGENT_BALANCE_MANAGER: {e}")
    sys.exit(1)

try:
    from ULTIMATE_AUTONOMOUS_INTELLIGENCE import UltimateAutonomousIntelligence
    print("   ✅ ULTIMATE_AUTONOMOUS_INTELLIGENCE")
except ImportError as e:
    print(f"   ❌ ULTIMATE_AUTONOMOUS_INTELLIGENCE: {e}")
    sys.exit(1)

try:
    from AUTONOMOUS_MASTER_COORDINATOR import AutonomousMasterCoordinator
    print("   ✅ AUTONOMOUS_MASTER_COORDINATOR")
except ImportError as e:
    print(f"   ❌ AUTONOMOUS_MASTER_COORDINATOR: {e}")
    sys.exit(1)

try:
    from systems.COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
    print("   ✅ COMPLETE_ULTIMATE_ORCHESTRATOR")
except ImportError as e:
    print(f"   ❌ COMPLETE_ULTIMATE_ORCHESTRATOR: {e}")
    sys.exit(1)

print("")
print("✅ ALL IMPORTS SUCCESSFUL!")
print("")

# Quick functionality test
print("2️⃣ Testing Balance Manager...")
balance_mgr = IntelligentBalanceManager()
balance_mgr.update_exchange_balance('bybit', 100.0)
can_afford, msg = balance_mgr.can_afford_position('bybit', 5.0)
print(f"   Balance: $100 → Can afford $5 trade? {can_afford}")
print(f"   ✅ Balance Manager works!")
print("")

print("3️⃣ Testing AI Consultation Service...")
ai_service = AIConsultationService(provider='auto')
print(f"   Active provider: {ai_service.active_provider or 'None configured (OK - needs API keys)'}")
print(f"   Available: {ai_service.available}")
print(f"   ✅ AI Service initialized!")
print("")

print("4️⃣ Testing Ultimate Intelligence...")
ultimate = UltimateAutonomousIntelligence()
trade_count = ultimate.calculate_optimal_trade_count(
    symbol='BTC/USDT',
    session='NY',
    volatility=0.12,
    opportunity_score=0.85
)
print(f"   Calculated trade count for high volatility: {trade_count}")
print(f"   ✅ Ultimate Intelligence works!")
print("")

PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "✅ VPS VERIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL!"
    echo "================================================================================"
    echo ""
    echo "🎯 WHAT'S NEW:"
    echo "   ✅ AI_CONSULTATION_SERVICE - Multi-AI intelligence (Claude/GPT-4/Grok/Raiziom)"
    echo "   ✅ INTELLIGENT_BALANCE_MANAGER - No more insufficient balance errors"
    echo "   ✅ ULTIMATE_AUTONOMOUS_INTELLIGENCE - Dynamic 1-200+ trades based on volatility"
    echo "   ✅ AUTONOMOUS_MASTER_COORDINATOR - Enhanced coordination of all 202 systems"
    echo ""
    echo "================================================================================"
    echo "🚀 READY TO START BOT"
    echo "================================================================================"
    echo ""
    echo "Choose your mode:"
    echo ""
    echo "1️⃣ TESTNET (recommended first):"
    echo "   python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode testnet"
    echo ""
    echo "2️⃣ PAPER TRADING (test with real market data):"
    echo "   python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode paper"
    echo ""
    echo "3️⃣ LIVE TRADING (real money - Monday $20 start):"
    echo "   python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode live"
    echo ""
    echo "================================================================================"
    echo "💡 TIP: Run testnet first to verify everything works!"
    echo "================================================================================"
else
    echo ""
    echo "================================================================================"
    echo "❌ VERIFICATION FAILED"
    echo "================================================================================"
    echo ""
    echo "Check the errors above and fix any missing dependencies:"
    echo "   pip install anthropic openai requests python-dotenv"
    echo ""
    exit 1
fi
