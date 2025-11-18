#!/usr/bin/env python3
"""
🔄 VPS SYNC CHECK
Compares VPS state with expected state to find discrepancies
"""

import sys
import os
from pathlib import Path
import subprocess
import json

print("="*80)
print("🔄 VPS SYNC CHECK - Comparing Expected vs Actual State")
print("="*80)
print()

# Expected state (what we configured)
EXPECTED_STATE = {
    "dependencies": [
        "numpy", "pandas", "scipy", "scikit-learn", 
        "ccxt", "aiohttp", "requests"
    ],
    "critical_files": [
        "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py",
        "EXECUTION_ORCHESTRATOR.py",
        "INTELLIGENT_EXECUTION_ENGINE.py",
        "ULTRA_GOLDMINE_FEATURES.py",
        "DIVINE_INTELLIGENCE_FEATURES.py",
        "critical_features_addon.py",
        "ALL_ENGINES_ACTIVATED.py",
        "router.py",
        ".env",
    ],
    "engines_activated": 39,
    "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
    "expected_features": [
        "ConsciousnessHarmonizer",
        "SwarmIntelligenceEngine",
        "FederatedLearningEngine",
        "GodModeCore",
        "EvolutionEngine",
    ]
}

def check_dependencies():
    """Check which dependencies are installed"""
    print("📦 Checking Dependencies...")
    missing = []
    installed = []
    
    for dep in EXPECTED_STATE["dependencies"]:
        try:
            __import__(dep)
            installed.append(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            missing.append(dep)
            print(f"  ❌ {dep} - MISSING")
    
    print(f"\n  Status: {len(installed)}/{len(EXPECTED_STATE['dependencies'])} installed")
    
    if missing:
        print(f"\n  ⚠️  Install missing: pip3 install {' '.join(missing)}")
    
    return missing

def check_files():
    """Check which critical files exist"""
    print("\n📁 Checking Critical Files...")
    missing = []
    present = []
    
    for file in EXPECTED_STATE["critical_files"]:
        if Path(file).exists():
            present.append(file)
            size = Path(file).stat().st_size
            print(f"  ✅ {file} ({size} bytes)")
        else:
            missing.append(file)
            print(f"  ❌ {file} - MISSING")
    
    print(f"\n  Status: {len(present)}/{len(EXPECTED_STATE['critical_files'])} present")
    
    return missing

def check_engine_activation():
    """Check how many engines are actually activated"""
    print("\n🚀 Checking Engine Activation...")
    
    try:
        # Try to import and count
        import ALL_ENGINES_ACTIVATED
        
        activated = sum(1 for name in dir(ALL_ENGINES_ACTIVATED) 
                       if name.endswith('_AVAILABLE') 
                       and getattr(ALL_ENGINES_ACTIVATED, name))
        total = sum(1 for name in dir(ALL_ENGINES_ACTIVATED) 
                   if name.endswith('_AVAILABLE'))
        
        print(f"  ✅ Engine activation module loaded")
        print(f"  📊 {activated}/{total} engines activated ({activated/total*100:.1f}%)")
        
        if activated < EXPECTED_STATE["engines_activated"]:
            print(f"  ⚠️  Expected {EXPECTED_STATE['engines_activated']}, got {activated}")
            print(f"     {EXPECTED_STATE['engines_activated'] - activated} engines failed to load")
        elif activated >= EXPECTED_STATE["engines_activated"]:
            print(f"  ✅ Meets or exceeds expected {EXPECTED_STATE['engines_activated']} engines")
        
        # List some activated engines
        print("\n  Activated engines sample:")
        activated_list = [name.replace('_AVAILABLE', '') for name in dir(ALL_ENGINES_ACTIVATED) 
                         if name.endswith('_AVAILABLE') 
                         and getattr(ALL_ENGINES_ACTIVATED, name)]
        
        for engine in activated_list[:10]:
            print(f"    • {engine}")
        
        if len(activated_list) > 10:
            print(f"    ... and {len(activated_list) - 10} more")
        
        return activated
        
    except Exception as e:
        print(f"  ❌ Failed to check engines: {e}")
        return 0

def check_imports():
    """Check if critical classes can be imported"""
    print("\n🔬 Checking Critical Imports...")
    
    imports_to_test = [
        ('ULTRA_GOLDMINE_FEATURES', 'GammaSqueezeDetector'),
        ('DIVINE_INTELLIGENCE_FEATURES', 'DivineIntelligenceManager'),
        ('critical_features_addon', 'TrailingStopManager'),
        ('EXECUTION_ORCHESTRATOR', 'ExecutionOrchestrator'),
        ('INTELLIGENT_EXECUTION_ENGINE', 'IntelligentExecutionEngine'),
    ]
    
    working = []
    broken = []
    
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                working.append(f"{module_name}.{class_name}")
                print(f"  ✅ {module_name}.{class_name}")
            else:
                broken.append(f"{module_name}.{class_name}")
                print(f"  ⚠️  {module_name}.{class_name} - class not found")
        except Exception as e:
            broken.append(module_name)
            print(f"  ❌ {module_name} - {str(e)[:60]}")
    
    print(f"\n  Status: {len(working)}/{len(imports_to_test)} imports working")
    
    return broken

def check_orchestrator_syntax():
    """Verify main orchestrator files compile"""
    print("\n🔍 Checking Orchestrator Syntax...")
    
    orchestrators = [
        "systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py",
        "COMPLETE_ULTIMATE_ORCHESTRATOR.py",
    ]
    
    valid = []
    invalid = []
    
    for orch in orchestrators:
        if not Path(orch).exists():
            print(f"  ⚠️  {orch} - not found")
            continue
        
        try:
            with open(orch) as f:
                compile(f.read(), orch, 'exec')
            valid.append(orch)
            print(f"  ✅ {orch}")
        except SyntaxError as e:
            invalid.append(orch)
            print(f"  ❌ {orch} - SYNTAX ERROR at line {e.lineno}")
        except Exception as e:
            print(f"  ⚠️  {orch} - {str(e)[:60]}")
    
    return invalid

def generate_sync_report():
    """Generate detailed sync report"""
    print("\n" + "="*80)
    print("📊 SYNC ANALYSIS REPORT")
    print("="*80)
    
    # Run all checks
    missing_deps = check_dependencies()
    missing_files = check_files()
    activated_engines = check_engine_activation()
    broken_imports = check_imports()
    invalid_syntax = check_orchestrator_syntax()
    
    # Calculate sync percentage
    checks = [
        len(missing_deps) == 0,
        len(missing_files) == 0,
        activated_engines >= 30,  # At least 30 engines
        len(broken_imports) == 0,
        len(invalid_syntax) == 0,
    ]
    
    sync_pct = (sum(checks) / len(checks)) * 100
    
    print("\n" + "="*80)
    print("📈 SYNC STATUS SUMMARY")
    print("="*80)
    
    print(f"\n  Dependencies:       {'✅' if len(missing_deps) == 0 else '❌'}")
    print(f"  Critical Files:     {'✅' if len(missing_files) == 0 else '❌'}")
    print(f"  Engine Activation:  {'✅' if activated_engines >= 30 else '❌'} ({activated_engines} active)")
    print(f"  Imports:            {'✅' if len(broken_imports) == 0 else '❌'}")
    print(f"  Syntax:             {'✅' if len(invalid_syntax) == 0 else '❌'}")
    
    print(f"\n  📊 Overall Sync: {sync_pct:.0f}%")
    
    if sync_pct == 100:
        print(f"  🎉 PERFECT SYNC - VPS matches expected state!")
    elif sync_pct >= 80:
        print(f"  ✅ GOOD SYNC - Minor issues to address")
    elif sync_pct >= 60:
        print(f"  ⚠️  PARTIAL SYNC - Several issues need fixing")
    else:
        print(f"  ❌ POOR SYNC - Major discrepancies found")
    
    # Action items
    if sync_pct < 100:
        print("\n" + "="*80)
        print("🔧 ACTION ITEMS TO FIX SYNC:")
        print("="*80)
        
        if missing_deps:
            print(f"\n  1. Install missing dependencies:")
            print(f"     pip3 install {' '.join(missing_deps)}")
        
        if missing_files:
            print(f"\n  2. Restore missing files:")
            for file in missing_files[:5]:
                print(f"     • {file}")
            if len(missing_files) > 5:
                print(f"     ... and {len(missing_files) - 5} more")
            print(f"     Consider: git pull or copy from backup")
        
        if activated_engines < 30:
            print(f"\n  3. Activate more engines:")
            print(f"     Currently: {activated_engines}, Expected: 39+")
            print(f"     Check: python3 -c 'import ALL_ENGINES_ACTIVATED'")
        
        if broken_imports:
            print(f"\n  4. Fix broken imports:")
            for imp in broken_imports[:5]:
                print(f"     • {imp}")
        
        if invalid_syntax:
            print(f"\n  5. Fix syntax errors:")
            for file in invalid_syntax:
                print(f"     • {file}")
    
    print("\n" + "="*80)
    
    return {
        'sync_percentage': sync_pct,
        'missing_deps': missing_deps,
        'missing_files': missing_files,
        'activated_engines': activated_engines,
        'broken_imports': broken_imports,
        'invalid_syntax': invalid_syntax,
    }

def main():
    # Change to workspace directory
    os.chdir('/workspace')
    
    report = generate_sync_report()
    
    # Save report to file
    report_file = Path('VPS_SYNC_REPORT.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: {report_file}")
    print("\n" + "="*80)
    
    return 0 if report['sync_percentage'] == 100 else 1

if __name__ == "__main__":
    sys.exit(main())
