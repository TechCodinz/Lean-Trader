#!/usr/bin/env python3
"""
Test script for complete integration
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_complete_integration():
    print('🔧 Testing complete integration...')
    
    try:
        from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
        orchestrator = CompleteUltimateOrchestrator(mode='testnet')
        
        # Try to wire systems
        print('🔌 Attempting to wire all systems...')
        await orchestrator.wire_all_systems()
        print('✅ Parent systems wired successfully!')
        
        # Now call our custom initialization
        print('🔌 Initializing custom systems...')
        await orchestrator.initialize_all_systems()
        print('✅ Custom systems initialized successfully!')
        
        # Check systems
        systems_to_check = [
            ('ultra_arbitrage', 'Ultra Arbitrage Engine'),
            ('ultra_scalping', 'Ultra Scalping Engine'),
            ('ultra_moon_spotter', 'Ultra Moon Spotter'),
            ('ultra_quantum', 'Ultra Quantum Intelligence'),
            ('ultra_swarm', 'Ultra Swarm Consciousness'),
            ('ultra_fluid', 'Ultra Fluid Mechanics'),
            ('ultra_ml', 'Ultra ML Pipeline'),
            ('trade_planner', 'Trade Planner'),
            ('ultimate_bot', 'Ultimate Bot 450 Models'),
            ('trader_core', 'Trader Core'),
            ('unified_trading', 'Unified Trading System')
        ]
        
        print('\n📊 SYSTEM AVAILABILITY CHECK:')
        available_count = 0
        for attr_name, display_name in systems_to_check:
            if hasattr(orchestrator, attr_name):
                system = getattr(orchestrator, attr_name)
                if system is not None:
                    print(f'   ✅ {display_name}: Available')
                    available_count += 1
                else:
                    print(f'   ⚠️  {display_name}: Not initialized')
            else:
                print(f'   ❌ {display_name}: Not found')
        
        print(f'\n📈 INTEGRATION SUMMARY:')
        print(f'   Available: {available_count}/{len(systems_to_check)} systems')
        print(f'   Success Rate: {(available_count/len(systems_to_check))*100:.1f}%')
        
        return available_count == len(systems_to_check)
        
    except Exception as e:
        print(f'❌ Error during integration: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_integration())
    if success:
        print('\n🎉 ALL SYSTEMS INTEGRATED SUCCESSFULLY!')
        sys.exit(0)
    else:
        print('\n❌ INTEGRATION FAILED!')
        sys.exit(1)