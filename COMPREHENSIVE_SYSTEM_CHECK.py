#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE SYSTEM CHECK 🔍

Checks ALL systems, engines, and identifies what's working and what needs fixing
"""

import sys
import os
from pathlib import Path
import importlib

sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n" + "="*80)
    print("📦 CHECKING DEPENDENCIES")
    print("="*80)
    
    required = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'ccxt': 'ccxt',
        'aiohttp': 'aiohttp',
        'requests': 'requests',
        'scipy': 'scipy',
        'sklearn': 'scikit-learn'
    }
    
    missing = []
    installed = []
    
    for module, package in required.items():
        try:
            importlib.import_module(module)
            installed.append(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package} - MISSING!")
    
    print(f"\n📊 Results: {len(installed)}/{len(required)} installed")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print(f"   Install with: pip3 install {' '.join(missing)}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists"""
    print("\n" + "="*80)
    print("🔐 CHECKING ENVIRONMENT CONFIGURATION")
    print("="*80)
    
    env_path = Path("/workspace/.env")
    template_path = Path("/workspace/.env.template")
    
    if env_path.exists():
        print("  ✅ .env file exists")
        
        # Check if it has content
        with open(env_path) as f:
            content = f.read()
            if 'your_' in content.lower() or len(content) < 100:
                print("  ⚠️  .env file exists but may not be configured")
                print("     Please fill in your actual API keys")
                return False
            else:
                print("  ✅ .env file appears to be configured")
                return True
    else:
        print("  ❌ .env file does NOT exist")
        if template_path.exists():
            print(f"  📝 Template available at: {template_path}")
            print(f"     Copy it: cp {template_path} {env_path}")
        return False

def check_critical_files():
    """Check if critical bot files exist"""
    print("\n" + "="*80)
    print("📁 CHECKING CRITICAL FILES")
    print("="*80)
    
    critical = [
        "router.py",
        "EXECUTION_ORCHESTRATOR.py",
        "INTELLIGENT_EXECUTION_ENGINE.py",
        "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py",
        "ULTRA_GOLDMINE_FEATURES.py",
        "DIVINE_INTELLIGENCE_FEATURES.py",
        "critical_features_addon.py",
    ]
    
    workspace = Path("/workspace")
    all_exist = True
    
    for file in critical:
        path = workspace / file
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
            all_exist = False
    
    return all_exist

def check_engine_imports():
    """Check if main engines can be imported"""
    print("\n" + "="*80)
    print("🚀 CHECKING ENGINE IMPORTS")
    print("="*80)
    
    engines_to_test = [
        ('ULTRA_GOLDMINE_FEATURES', 'GammaSqueezeDetector'),
        ('DIVINE_INTELLIGENCE_FEATURES', 'DivineIntelligenceManager'),
        ('critical_features_addon', 'TrailingStopManager'),
        ('EXECUTION_ORCHESTRATOR', 'ExecutionOrchestrator'),
        ('INTELLIGENT_EXECUTION_ENGINE', 'IntelligentExecutionEngine'),
    ]
    
    working = []
    broken = []
    
    for module_name, class_name in engines_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                working.append(f"{module_name}.{class_name}")
                print(f"  ✅ {module_name}.{class_name}")
            else:
                broken.append(f"{module_name}.{class_name} - class not found")
                print(f"  ⚠️  {module_name}.{class_name} - class not found")
        except Exception as e:
            broken.append(f"{module_name} - {str(e)[:50]}")
            print(f"  ❌ {module_name} - {str(e)[:50]}")
    
    print(f"\n📊 Results: {len(working)}/{len(engines_to_test)} engines working")
    
    return len(broken) == 0

def check_orchestrator_syntax():
    """Check if main orchestrator has valid syntax"""
    print("\n" + "="*80)
    print("🔍 CHECKING ORCHESTRATOR SYNTAX")
    print("="*80)
    
    orchestrators = [
        "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py",
        "COMPLETE_ULTIMATE_ORCHESTRATOR.py",
        "AUTOMATED_ORCHESTRATOR_ENHANCED.py",
    ]
    
    workspace = Path("/workspace")
    all_valid = True
    
    for orch in orchestrators:
        path = workspace / orch
        if not path.exists():
            print(f"  ⚠️  {orch} - not found")
            continue
        
        # Try to compile
        try:
            with open(path) as f:
                compile(f.read(), path, 'exec')
            print(f"  ✅ {orch} - valid syntax")
        except SyntaxError as e:
            print(f"  ❌ {orch} - SYNTAX ERROR at line {e.lineno}")
            all_valid = False
        except Exception as e:
            print(f"  ⚠️  {orch} - {str(e)[:50]}")
    
    return all_valid

def test_engine_activation():
    """Test if engine activation module works"""
    print("\n" + "="*80)
    print("⚡ TESTING ENGINE ACTIVATION")
    print("="*80)
    
    try:
        import ALL_ENGINES_ACTIVATED
        print("  ✅ ALL_ENGINES_ACTIVATED module imports successfully")
        
        # Count how many engines loaded
        activated = sum(1 for name in dir(ALL_ENGINES_ACTIVATED) 
                       if name.endswith('_AVAILABLE') and getattr(ALL_ENGINES_ACTIVATED, name))
        total = sum(1 for name in dir(ALL_ENGINES_ACTIVATED) if name.endswith('_AVAILABLE'))
        
        print(f"  📊 {activated}/{total} engines activated ({activated/total*100:.1f}%)")
        
        return activated > 10  # At least 10 engines should work
        
    except Exception as e:
        print(f"  ❌ Engine activation failed: {e}")
        return False

def generate_fix_script():
    """Generate a script to fix common issues"""
    print("\n" + "="*80)
    print("🔧 GENERATING FIX SCRIPT")
    print("="*80)
    
    fix_script = """#!/bin/bash
# Auto-generated fix script

echo "🔧 FIXING TRADING BOT ISSUES..."
echo "================================"

# Install missing dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install numpy pandas scipy scikit-learn ccxt aiohttp requests 2>&1 | tail -5

# Create .env from template if missing
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env from template..."
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "✅ .env created - PLEASE EDIT IT with your API keys!"
    fi
fi

# Run diagnostic
echo ""
echo "🔍 Running diagnostic..."
python3 COMPREHENSIVE_ENGINE_DIAGNOSTIC.py

echo ""
echo "✅ Fixes applied!"
echo "   Next: Edit .env file with your API keys"
"""
    
    fix_path = Path("/workspace/AUTO_FIX_ALL_ISSUES.sh")
    with open(fix_path, 'w') as f:
        f.write(fix_script)
    
    os.chmod(fix_path, 0o755)
    print(f"  ✅ Created: {fix_path}")
    print(f"     Run with: bash {fix_path.name}")
    
    return fix_path

def main():
    print("="*80)
    print("🔍 COMPREHENSIVE SYSTEM CHECK")
    print("="*80)
    print("Checking all systems, dependencies, and configurations...")
    
    results = {
        'dependencies': check_dependencies(),
        'env_file': check_env_file(),
        'critical_files': check_critical_files(),
        'engine_imports': check_engine_imports(),
        'orchestrator_syntax': check_orchestrator_syntax(),
        'engine_activation': test_engine_activation(),
    }
    
    # Summary
    print("\n" + "="*80)
    print("📊 SYSTEM CHECK SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {check.replace('_', ' ').title()}")
    
    print(f"\n📈 Overall Score: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed < total:
        print("\n⚠️  ISSUES FOUND!")
        print("   Some systems need attention.")
        
        # Generate fix script
        fix_script = generate_fix_script()
        
        print(f"\n💡 QUICK FIX:")
        print(f"   Run: bash {fix_script.name}")
        
    else:
        print("\n✅ ALL SYSTEMS OPERATIONAL!")
        print("   Bot is ready to trade!")
    
    print("="*80)
    
    return results

if __name__ == "__main__":
    results = main()
    sys.exit(0 if all(results.values()) else 1)
