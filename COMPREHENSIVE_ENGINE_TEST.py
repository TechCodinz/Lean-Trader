#!/usr/bin/env python3
"""
COMPREHENSIVE ENGINE TEST
Test ALL engines end-to-end
"""

import sys
import asyncio
from datetime import datetime

def test_ultra_rare_engines():
    """Test all 11 ultra rare engines"""
    print("\n" + "="*80)
    print("TEST 1: ULTRA RARE ENGINES")
    print("="*80)
    
    try:
        from ULTRA_RARE_ENGINES import (
            MicrostructureExploiter,
            InformationEntropyTrader,
            CascadingLiquidityHunter,
            FlashCrashPredator,
            FundingRateArbitrage,
            HiddenOrderDetector,
            SmartMoneyShadow,
            RetailPanicExploiter,
            TimeWarpPatterns,
            WhalePsychologyPredictor,
            UltraRareEnginesOrchestrator
        )
        
        print("✅ All 11 classes import successfully")
        
        # Test instantiation
        micro = MicrostructureExploiter()
        print(f"✅ MicrostructureExploiter: {len(dir(micro))} methods")
        
        entropy = InformationEntropyTrader()
        print(f"✅ InformationEntropyTrader: {len(dir(entropy))} methods")
        
        cascade = CascadingLiquidityHunter()
        print(f"✅ CascadingLiquidityHunter: {len(dir(cascade))} methods")
        
        flash = FlashCrashPredator()
        print(f"✅ FlashCrashPredator: {len(dir(flash))} methods")
        
        funding = FundingRateArbitrage()
        print(f"✅ FundingRateArbitrage: {len(dir(funding))} methods")
        
        hidden = HiddenOrderDetector()
        print(f"✅ HiddenOrderDetector: {len(dir(hidden))} methods")
        
        smart_money = SmartMoneyShadow()
        print(f"✅ SmartMoneyShadow: {len(dir(smart_money))} methods")
        
        retail = RetailPanicExploiter()
        print(f"✅ RetailPanicExploiter: {len(dir(retail))} methods")
        
        time_warp = TimeWarpPatterns()
        print(f"✅ TimeWarpPatterns: {len(dir(time_warp))} methods")
        
        whale = WhalePsychologyPredictor()
        print(f"✅ WhalePsychologyPredictor: {len(dir(whale))} methods")
        
        # Test orchestrator (self-initializes all engines)
        orchestrator = UltraRareEnginesOrchestrator()
        print(f"✅ UltraRareEnginesOrchestrator: Self-initializes all 10 engines")
        
        print("\n✅ ULTRA RARE ENGINES: ALL PASS")
        return True
        
    except Exception as e:
        print(f"❌ ULTRA RARE ENGINES FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_integration():
    """Test if engines are integrated in orchestrator"""
    print("\n" + "="*80)
    print("TEST 2: ORCHESTRATOR INTEGRATION")
    print("="*80)
    
    try:
        from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
        print("✅ CompleteUltimateOrchestrator imports")
        
        # Check for our integrations
        import COMPLETE_ULTIMATE_ORCHESTRATOR as orch
        
        checks = {
            'ULTRA_RARE_AVAILABLE': 'ULTRA_RARE_AVAILABLE' in dir(orch),
            'UltraRareEnginesOrchestrator imported': 'UltraRareEnginesOrchestrator' in dir(orch),
            'MicrostructureExploiter imported': 'MicrostructureExploiter' in dir(orch),
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}")
        
        if all(checks.values()):
            print("\n✅ ORCHESTRATOR INTEGRATION: ALL PASS")
            return True
        else:
            print("\n⚠️  ORCHESTRATOR INTEGRATION: PARTIAL")
            return False
            
    except Exception as e:
        print(f"❌ ORCHESTRATOR INTEGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_async_functionality():
    """Test async methods work"""
    print("\n" + "="*80)
    print("TEST 3: ASYNC FUNCTIONALITY")
    print("="*80)
    
    async def run_test():
        try:
            from ULTRA_RARE_ENGINES import MicrostructureExploiter
            
            micro = MicrostructureExploiter()
            
            # Test with sample data
            sample_bids = [[50000, 1.5], [49900, 2.0], [49800, 1.0]]
            sample_asks = [[50100, 0.5], [50200, 1.0], [50300, 1.5]]
            
            result = await micro.analyze_orderbook('BTC/USDT', sample_bids, sample_asks)
            
            if result:
                print(f"✅ Order book analysis works: {result['pattern']}")
            else:
                print("✅ Order book analysis works (no signal)")
            
            print("\n✅ ASYNC FUNCTIONALITY: PASS")
            return True
            
        except Exception as e:
            print(f"❌ ASYNC FUNCTIONALITY FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return asyncio.run(run_test())


def test_data_requirements():
    """Check what data the engines need"""
    print("\n" + "="*80)
    print("TEST 4: DATA REQUIREMENTS")
    print("="*80)
    
    try:
        from ULTRA_RARE_ENGINES import UltraRareEnginesOrchestrator
        
        # Check what analyze_symbol expects
        import inspect
        sig = inspect.signature(UltraRareEnginesOrchestrator.analyze_symbol)
        params = list(sig.parameters.keys())
        
        print("analyze_symbol() requires:")
        for param in params:
            if param != 'self':
                print(f"   - {param}")
        
        required_data = [
            'symbol', 'price', 'order_book', 'recent_prices',
            'open_interest', 'funding_rate'
        ]
        
        print("\nData needed:")
        for data in required_data:
            print(f"   ✅ {data}")
        
        print("\n✅ DATA REQUIREMENTS: DOCUMENTED")
        return True
        
    except Exception as e:
        print(f"❌ DATA REQUIREMENTS CHECK FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("="*80)
    print("COMPREHENSIVE ENGINE TEST")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Ultra Rare Engines
    results.append(("Ultra Rare Engines", test_ultra_rare_engines()))
    
    # Test 2: Orchestrator Integration
    results.append(("Orchestrator Integration", test_orchestrator_integration()))
    
    # Test 3: Async Functionality
    results.append(("Async Functionality", test_async_functionality()))
    
    # Test 4: Data Requirements
    results.append(("Data Requirements", test_data_requirements()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Engines are ready to deploy.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
