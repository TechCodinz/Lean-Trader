#!/usr/bin/env python3
"""
Quick test to verify bot can initialize properly
"""
import sys
import os

print("=" * 70)
print("TESTING BOT INITIALIZATION")
print("=" * 70)
print()

# Test 1: Import main modules
print("1. Testing core imports...")
try:
    from INTELLIGENT_EXCHANGE_ROUTER import IntelligentExchangeRouter, get_intelligent_router
    print("   ✅ INTELLIGENT_EXCHANGE_ROUTER imports OK")
except Exception as e:
    print(f"   ❌ INTELLIGENT_EXCHANGE_ROUTER failed: {e}")
    
try:
    from AI_CONSULTATION_SYSTEM import AIConsultationSystem
    print("   ✅ AI_CONSULTATION_SYSTEM imports OK")
except Exception as e:
    print(f"   ❌ AI_CONSULTATION_SYSTEM failed: {e}")

try:
    from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator
    print("   ✅ EXECUTION_ORCHESTRATOR imports OK")
except Exception as e:
    print(f"   ❌ EXECUTION_ORCHESTRATOR failed: {e}")

print()

# Test 2: Check router singleton
print("2. Testing router initialization...")
try:
    from INTELLIGENT_EXCHANGE_ROUTER import initialize_intelligent_router
    
    # Create mock exchange
    class MockExchange:
        def __init__(self, name):
            self.name = name
            
        def load_markets(self):
            return {'BTC/USDT': {'symbol': 'BTC/USDT', 'type': 'spot'}}
    
    test_exchanges = {'test_exchange': MockExchange('test')}
    router = initialize_intelligent_router(test_exchanges, None)
    
    if router:
        print("   ✅ Router initialization works")
        retrieved = get_intelligent_router()
        if retrieved is router:
            print("   ✅ Router singleton works")
        else:
            print("   ❌ Router singleton retrieval failed")
    else:
        print("   ❌ Router initialization returned None")
        
except Exception as e:
    print(f"   ❌ Router test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Check AI throttling
print("3. Testing AI consultation throttling...")
try:
    from AI_CONSULTATION_SYSTEM import AIConsultationSystem
    import asyncio
    
    ai_system = AIConsultationSystem()
    
    # Test low confidence (should skip)
    result = asyncio.run(ai_system.consult_strategy({
        'symbol': 'BTC/USDT',
        'confidence': 0.75,  # Below 88% threshold
        'signal': 'buy'
    }))
    
    if result.get('skipped') == 'confidence_too_low':
        print("   ✅ AI throttling works (75% confidence skipped)")
    else:
        print(f"   ⚠️  Unexpected result: {result}")
        
    # Test high confidence (would consult if AI keys present)
    result2 = asyncio.run(ai_system.consult_strategy({
        'symbol': 'ETH/USDT',
        'confidence': 0.92,  # Above 88% threshold
        'signal': 'buy'
    }))
    
    if 'skipped' in result2 or 'ai_available' in result2:
        print("   ✅ AI system responds correctly to high confidence")
    else:
        print(f"   ⚠️  High confidence result: {result2}")
        
except Exception as e:
    print(f"   ❌ AI throttling test failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print()
print("✅ = Pass    ❌ = Fail    ⚠️  = Warning")
print()
print("If all tests show ✅, the bot is ready to deploy!")
print("=" * 70)
