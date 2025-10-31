#!/usr/bin/env python3
"""
DIAGNOSTIC: Check what engines are actually wired vs available
Run this to see what's missing
"""
import sys
import os
from pathlib import Path

# Add current directory
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🔍 CHECKING WHAT ENGINES ARE AVAILABLE vs WIRED")
print("=" * 80)
print()

# Check what engine files exist
print("📁 ENGINES IN CODEBASE:")
engine_files = [
    f for f in os.listdir('.') 
    if any(x in f.upper() for x in ['ENGINE', 'SCALP', 'PROFIT', 'ULTRA', 'GOD', 'APE']) 
    and f.endswith('.py')
]
for f in sorted(engine_files):
    print(f"  ✅ {f}")

print()
print("=" * 80)
print("🔌 CHECKING WHAT'S ACTUALLY WIRED:")
print("=" * 80)
print()

try:
    from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
    import asyncio
    
    async def check():
        bot = CompleteUltimateOrchestrator(mode='testnet')
        
        print("⏳ Initializing...")
        await bot.initialize_all_systems()
        
        print("⏳ Wiring...")
        await bot.wire_all_systems()
        
        print()
        print("=" * 80)
        print("✅ ENGINES ACTUALLY WIRED:")
        print("=" * 80)
        
        if hasattr(bot, 'advanced_orchestrators'):
            for key, value in bot.advanced_orchestrators.items():
                if value:
                    print(f"  ✅ {key}: {type(value).__name__}")
                else:
                    print(f"  ❌ {key}: None")
        
        print()
        if hasattr(bot, 'advanced_systems'):
            print("=" * 80)
            print("✅ SYSTEMS ACTUALLY WIRED:")
            print("=" * 80)
            for key, value in bot.advanced_systems.items():
                if value:
                    print(f"  ✅ {key}: {type(value).__name__}")
                else:
                    print(f"  ❌ {key}: None")
        
        print()
        print("=" * 80)
        print("🔍 CHECKING SPECIFIC ENGINES:")
        print("=" * 80)
        
        checks = [
            ('aggressive_scalper', 'AggressiveScalpingEngine'),
            ('steady_profit', 'SteadyProfitExtractor'),
            ('micro_wallet_grower', 'MICRO_GATE_BOT'),
            ('auto_profit_taker', 'AutoProfitTaker'),
            ('quantum', 'IBMQuantumEngine'),
            ('ultra_rare_orchestrator', 'UltraRareEnginesOrchestrator'),
            ('money_printer', 'MoneyPrinterUltraRare'),
            ('single_arb', 'SingleExchangeArbitrage'),
        ]
        
        for attr, class_name in checks:
            if hasattr(bot, attr):
                obj = getattr(bot, attr)
                if obj:
                    print(f"  ✅ {attr}: {type(obj).__name__}")
                else:
                    print(f"  ❌ {attr}: None (not initialized)")
            else:
                print(f"  ❌ {attr}: Not found (missing attribute)")
    
    asyncio.run(check())
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 80)