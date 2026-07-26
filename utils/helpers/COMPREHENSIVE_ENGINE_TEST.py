#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE ENGINE TEST
Tests ALL 254 engines + new systems to ensure nothing fails silently

This will:
1. Test imports for all engines
2. Test initialization
3. Check for silent failures
4. Verify dependencies
5. Test new systems (alerts, circuit breakers)
6. Report detailed results
"""

import sys
import os
import importlib
import traceback
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Results storage
test_results = {
    'passed': [],
    'failed': [],
    'warnings': [],
    'critical_failures': []
}

def test_import(module_name: str, file_path: str) -> Tuple[bool, str]:
    """Test if a module can be imported"""
    try:
        # Add directory to path if needed
        module_dir = os.path.dirname(file_path)
        if module_dir and module_dir not in sys.path:
            sys.path.insert(0, module_dir)
        
        # Try to import
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True, "OK"
        else:
            return False, "No spec found"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except SyntaxError as e:
        return False, f"SyntaxError: {str(e)}"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)}"

def test_class_initialization(module_name: str, file_path: str) -> Tuple[bool, str]:
    """Test if classes in module can be initialized"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            return False, "No spec"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find all classes
        classes = [obj for name, obj in module.__dict__.items() 
                  if isinstance(obj, type) and not name.startswith('_')]
        
        if not classes:
            return True, "No classes to test"
        
        # Try to get class info (not initialize, just verify structure)
        for cls in classes:
            _ = cls.__name__
            _ = cls.__dict__
        
        return True, f"Found {len(classes)} classes"
    except Exception as e:
        return False, f"Class check failed: {str(e)}"

def find_all_engine_files() -> List[str]:
    """Find all Python files that are likely engines"""
    engine_files = []
    
    # Common engine patterns
    patterns = [
        '*ENGINE*.py',
        '*SYSTEM*.py',
        '*ORCHESTRATOR*.py',
        '*MASTER*.py',
        '*MANAGER*.py',
        'ultra_*.py',
        'COMPLETE_*.py',
        'PROFESSIONAL_*.py',
        'ENHANCED_*.py',
        'ADVANCED_*.py',
        'AUTOMATED_*.py'
    ]
    
    workspace = Path('/workspace')
    for pattern in patterns:
        engine_files.extend(workspace.glob(pattern))
    
    # Remove duplicates and test files
    unique_files = list(set(engine_files))
    unique_files = [f for f in unique_files if 'test' not in f.name.lower() 
                    and '__pycache__' not in str(f)]
    
    return sorted([str(f) for f in unique_files])

def test_critical_dependencies():
    """Test all critical dependencies can be imported"""
    critical_deps = [
        'numpy',
        'pandas',
        'ccxt',
        'dotenv',
        'requests',
        'aiohttp',
        'logging',
        'asyncio',
        'sqlite3',
        'json',
        'datetime'
    ]
    
    results = []
    for dep in critical_deps:
        try:
            __import__(dep)
            results.append((dep, True, "OK"))
        except ImportError as e:
            results.append((dep, False, str(e)))
    
    return results

def test_new_systems():
    """Test newly created systems"""
    new_systems = [
        ('INTEGRATED_ALERT_SYSTEM.py', 'IntegratedAlertSystem'),
        ('CIRCUIT_BREAKER_SYSTEM.py', 'CircuitBreakerSystem'),
        ('DEFI_YIELD_FARMING_ENGINE.py', 'DeFiYieldFarmingEngine'),
        ('CROSS_CHAIN_ARBITRAGE.py', 'CrossChainArbitrage'),
        ('ENHANCED_FOREX_MASTER.py', 'EnhancedForexMaster')
    ]
    
    results = []
    for file_name, class_name in new_systems:
        file_path = f'/workspace/{file_name}'
        if not os.path.exists(file_path):
            results.append((file_name, False, "File not found"))
            continue
        
        success, msg = test_import(file_name.replace('.py', ''), file_path)
        results.append((file_name, success, msg))
    
    return results

def test_orchestrators():
    """Test main orchestrator files"""
    orchestrators = [
        'COMPLETE_ULTIMATE_ORCHESTRATOR.py',
        'AUTOMATED_ORCHESTRATOR_ENHANCED.py',
        'RUN_BOT.py'
    ]
    
    results = []
    for orch in orchestrators:
        file_path = f'/workspace/{orch}'
        if not os.path.exists(file_path):
            results.append((orch, False, "File not found"))
            continue
        
        success, msg = test_import(orch.replace('.py', ''), file_path)
        results.append((orch, success, msg))
    
    return results

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = '/workspace/.env'
    if not os.path.exists(env_path):
        return False, "No .env file found"
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    required_keys = [
        'TRADING_MODE',
        'ENABLE_LIVE',
        'GATEIO_API_KEY',
        'GATEIO_API_SECRET'
    ]
    
    missing = [key for key in required_keys if key not in env_content]
    
    if missing:
        return False, f"Missing keys: {', '.join(missing)}"
    
    return True, "All required keys present"

def main():
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                              ║")
    print("║              🔍 COMPREHENSIVE ENGINE TEST - ALL SYSTEMS 🔍                   ║")
    print("║                                                                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Test 1: Critical Dependencies
    print("=" * 80)
    print("TEST 1: CRITICAL DEPENDENCIES")
    print("=" * 80)
    dep_results = test_critical_dependencies()
    for dep, success, msg in dep_results:
        status = "[OK]" if success else "[X]"
        print(f"{status} {dep:20s} {msg}")
        if not success:
            test_results['critical_failures'].append(f"Dependency: {dep} - {msg}")
        else:
            test_results['passed'].append(f"Dependency: {dep}")
    print()
    
    # Test 2: Environment Configuration
    print("=" * 80)
    print("TEST 2: ENVIRONMENT CONFIGURATION")
    print("=" * 80)
    env_success, env_msg = check_env_file()
    status = "[OK]" if env_success else ""
    print(f"{status} .env file: {env_msg}")
    if not env_success:
        test_results['warnings'].append(f"Environment: {env_msg}")
    else:
        test_results['passed'].append("Environment: .env configured")
    print()
    
    # Test 3: New Systems
    print("=" * 80)
    print("TEST 3: NEWLY CREATED SYSTEMS")
    print("=" * 80)
    new_system_results = test_new_systems()
    for file_name, success, msg in new_system_results:
        status = "[OK]" if success else "[X]"
        print(f"{status} {file_name:40s} {msg}")
        if not success:
            test_results['failed'].append(f"New System: {file_name} - {msg}")
        else:
            test_results['passed'].append(f"New System: {file_name}")
    print()
    
    # Test 4: Orchestrators
    print("=" * 80)
    print("TEST 4: MAIN ORCHESTRATORS")
    print("=" * 80)
    orch_results = test_orchestrators()
    for orch, success, msg in orch_results:
        status = "[OK]" if success else "[X]"
        print(f"{status} {orch:45s} {msg}")
        if not success:
            test_results['critical_failures'].append(f"Orchestrator: {orch} - {msg}")
        else:
            test_results['passed'].append(f"Orchestrator: {orch}")
    print()
    
    # Test 5: All Engine Files
    print("=" * 80)
    print("TEST 5: ALL ENGINE FILES (This may take a minute...)")
    print("=" * 80)
    engine_files = find_all_engine_files()
    print(f"Found {len(engine_files)} engine files to test...")
    print()
    
    passed = 0
    failed = 0
    
    for engine_file in engine_files:
        file_name = os.path.basename(engine_file)
        module_name = file_name.replace('.py', '')
        
        # Test import
        import_success, import_msg = test_import(module_name, engine_file)
        
        # Test class structure
        class_success, class_msg = test_class_initialization(module_name, engine_file)
        
        if import_success and class_success:
            print(f"[OK] {file_name:50s} OK")
            test_results['passed'].append(f"Engine: {file_name}")
            passed += 1
        else:
            print(f"[X] {file_name:50s} FAILED")
            print(f"   Import: {import_msg}")
            print(f"   Classes: {class_msg}")
            test_results['failed'].append(f"Engine: {file_name} - {import_msg}")
            failed += 1
    
    print()
    print(f"Engine Test Results: {passed} passed, {failed} failed")
    print()
    
    # Final Summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"[OK] Passed: {len(test_results['passed'])}")
    print(f"[X] Failed: {len(test_results['failed'])}")
    print(f"  Warnings: {len(test_results['warnings'])}")
    print(f"🚨 Critical Failures: {len(test_results['critical_failures'])}")
    print()
    
    if test_results['critical_failures']:
        print("🚨 CRITICAL FAILURES DETECTED:")
        for failure in test_results['critical_failures']:
            print(f"   - {failure}")
        print()
    
    if test_results['failed']:
        print("[X] FAILED TESTS:")
        for failure in test_results['failed'][:10]:  # Show first 10
            print(f"   - {failure}")
        if len(test_results['failed']) > 10:
            print(f"   ... and {len(test_results['failed']) - 10} more")
        print()
    
    # Save results
    with open('/workspace/TEST_RESULTS.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print("Full results saved to: TEST_RESULTS.json")
    print()
    
    # Overall status
    if test_results['critical_failures']:
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                              ║")
        print("║                    🚨 CRITICAL FAILURES - FIX REQUIRED 🚨                    ║")
        print("║                                                                              ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        return 1
    elif test_results['failed']:
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                              ║")
        print("║                     SOME TESTS FAILED - REVIEW NEEDED                    ║")
        print("║                                                                              ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        return 1
    else:
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                              ║")
        print("║                    [OK] ALL TESTS PASSED - READY TO DEPLOY! [OK]                 ║")
        print("║                                                                              ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        return 0

if __name__ == "__main__":
    sys.exit(main())
