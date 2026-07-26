#!/usr/bin/env python3
"""
TEST COMPLETE SYSTEM
Test that all critical components can load and initialize
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_profit_system():
    """Test COMPLETE_PROFIT_SYSTEM"""
    try:
        from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem
        logger.info("[OK] COMPLETE_PROFIT_SYSTEM imports successfully")
        
        # Test initialization (won't actually connect without API keys in test)
        system = CompleteProfitSystem(api_key='test', api_secret='test')
        logger.info("[OK] COMPLETE_PROFIT_SYSTEM initializes")
        logger.info(f"   Tiers: {len(system.tiers)}")
        logger.info(f"   Current balance: ${system.current_balance}")
        
        return True
    except Exception as e:
        logger.error(f"[X] COMPLETE_PROFIT_SYSTEM error: {e}")
        return False

def test_execution_orchestrator():
    """Test EXECUTION_ORCHESTRATOR"""
    try:
        from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator
        logger.info("[OK] EXECUTION_ORCHESTRATOR imports successfully")
        return True
    except Exception as e:
        logger.error(f"[X] EXECUTION_ORCHESTRATOR error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_engines():
    """Test that key engines exist and load"""
    engines_to_test = [
        ('SMART_SCALPING_ENGINE', 'SmartScalpingEngine'),
        ('AGGRESSIVE_SCALPING_ENGINE', 'AggressiveScalpingEngine'),
        ('NEWS_TRADING_ENGINE', 'NewsTradingEngine'),
        ('ULTRA_RARE_ENGINES', 'UltraRareEnginesOrchestrator'),
    ]
    
    results = []
    for module_name, class_name in engines_to_test:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            logger.info(f"[OK] {module_name}.{class_name} loads")
            results.append(True)
        except Exception as e:
            logger.warning(f" {module_name}.{class_name}: {e}")
            results.append(False)
    
    return all(results)

def test_orchestrator():
    """Test main orchestrator"""
    try:
        from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator
        logger.info("[OK] COMPLETE_ULTIMATE_ORCHESTRATOR imports successfully")
        return True
    except Exception as e:
        logger.error(f"[X] COMPLETE_ULTIMATE_ORCHESTRATOR error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🧪 TESTING COMPLETE SYSTEM")
    logger.info("=" * 80)
    
    results = {}
    
    logger.info("\n1️⃣ Testing COMPLETE_PROFIT_SYSTEM...")
    results['profit_system'] = test_profit_system()
    
    logger.info("\n2️⃣ Testing EXECUTION_ORCHESTRATOR...")
    results['execution_orch'] = test_execution_orchestrator()
    
    logger.info("\n3️⃣ Testing Key Engines...")
    results['engines'] = test_all_engines()
    
    logger.info("\n4️⃣ Testing Main Orchestrator...")
    results['orchestrator'] = test_orchestrator()
    
    logger.info("\n" + "=" * 80)
    logger.info("📊 TEST RESULTS")
    logger.info("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "[OK] PASS" if result else "[X] FAIL"
        logger.info(f"   {name}: {status}")
    
    logger.info(f"\n   Total: {passed}/{total} passed")
    logger.info("=" * 80)
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! System is ready to deploy!")
        sys.exit(0)
    else:
        logger.error(" Some tests failed. Fix issues before deploying.")
        sys.exit(1)
