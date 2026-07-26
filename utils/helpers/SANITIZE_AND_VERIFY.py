
import importlib
import sys
import os
import time
import signal
import threading

# Modules to verify (The Supreme & Critical List)
MODULES_TO_TEST = [
    "EXECUTION_ORCHESTRATOR",
    "INTELLIGENT_EXECUTION_ENGINE",
    "COMPLETE_PROFIT_SYSTEM",
    "COLLECTIVE_CONSENSUS_ENGINE",
    "ENRICHED_SIGNAL_SYSTEM",
    "CONSCIOUSNESS_HARMONIZER",
    "EVOLUTION_ENGINE",
    "MARKET_DATA_INTELLIGENCE",
    "INTELLIGENT_EXCHANGE_ROUTER",
    "HYBRID_INTELLIGENCE_COORDINATOR"
]

def test_import(module_name):
    print(f"Testing import: {module_name}...")
    start_time = time.time()
    
    def target():
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"[X] Error importing {module_name}: {e}")

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    
    thread.join(timeout=60.0) # 60 seconds strict timeout
    
    if thread.is_alive():
        print(f"[X] TIMEOUT: {module_name} HUNG on import (auto-execution detected!)")
        return False
    
    elapsed = time.time() - start_time
    print(f"[OK] Success: {module_name} imported in {elapsed:.2f}s")
    return True

def main():
    print("🔬 SANITIZATION CHECK: Verifying Safe Imports...")
    sys.path.append(os.getcwd())
    
    results = {}
    for mod in MODULES_TO_TEST:
        results[mod] = test_import(mod)
        print("-" * 40)
        
    print("\n📊 SUMMARY:")
    passed = 0
    for mod, success in results.items():
        status = "[OK] CLEAN" if success else "[X] DIRTY/MISSING"
        print(f"{mod}: {status}")
        if success: passed += 1
        
    print(f"\nScore: {passed}/{len(MODULES_TO_TEST)}")
    
    if passed == len(MODULES_TO_TEST):
        print("🎉 ALL SYSTEMS GO! Ready for Activation.")
    else:
        print(" DETECTED DIRTY MODULES. Auto-sanitization required.")

if __name__ == "__main__":
    main()
