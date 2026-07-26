#!/usr/bin/env python3
"""
CHECK PASSIVE ENGINES
Find which engines are initialized but NOT running
"""

import re

def check_engines():
    """Check which engines have tasks vs just initialized"""
    
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    print("="*80)
    print("CHECKING ALL ULTRA/ADVANCED ENGINES")
    print("="*80)
    
    # Find all initializations
    initialized = re.findall(r'self\.(\w+) = (\w+)\(\)', content)
    
    # Find all async tasks
    tasks = re.findall(r'tasks\.append.*run_(\w+)', content)
    
    print(f"\nTotal engines initialized: {len(initialized)}")
    print(f"Total async tasks: {len(tasks)}")
    
    # Check Ultra systems specifically
    ultra_systems = {
        'swarm_consciousness': 'SwarmConsciousnessSystem',
        'evolution_engine': 'ULTIMATE_EVOLUTION_ENGINE',
        'ultra_god': 'UltraGodMode',
        'bot_450': 'UltimateBot450Models',
        'revolutionary_ai': 'RevolutionaryAIManager',
        'ultra_core': 'UltraCore',
        'ultra_moon_system': 'UltraMoonSystem',
        'forex_master': 'UltraForexMaster',
        'business_system': 'UltraBusinessSystem',
        'ml_pipeline': 'UltraMLPipeline',
        'ultra_scalping': 'UltraScalpingEngine',
        'ultra_arbitrage': 'UltraArbitrageEngine',
        'continuous_trading': 'UltraContinuousTradingOrchestrator',
        'multi_platform': 'UltraMultiPlatformScanner',
    }
    
    print("\n" + "="*80)
    print("ULTRA SYSTEMS STATUS:")
    print("="*80)
    
    for var_name, class_name in ultra_systems.items():
        # Check if initialized
        init_pattern = f"self.{var_name} = {class_name}"
        initialized = init_pattern in content
        
        # Check if has async task
        has_task = any(var_name in task or var_name.replace('_', '') in task for task in tasks)
        
        # Also check if task function exists
        task_func = f"async def run_{var_name}"
        has_func = task_func in content
        
        status = "✅ RUNNING" if (initialized and (has_task or has_func)) else (
            "⚠️  INITIALIZED ONLY" if initialized else "❌ NOT FOUND"
        )
        
        print(f"{status:20} {var_name:30} ({class_name})")
    
    print("\n" + "="*80)
    print("RECOMMENDATION:")
    print("="*80)
    
    dormant = []
    for var_name, class_name in ultra_systems.items():
        init_pattern = f"self.{var_name} = {class_name}"
        initialized = init_pattern in content
        has_task = any(var_name in task or var_name.replace('_', '') in task for task in tasks)
        task_func = f"async def run_{var_name}"
        has_func = task_func in content
        
        if initialized and not (has_task or has_func):
            dormant.append((var_name, class_name))
    
    if dormant:
        print(f"\n⚠️  Found {len(dormant)} DORMANT engines (initialized but not running):")
        for var_name, class_name in dormant:
            print(f"   - {var_name} ({class_name})")
        print("\nThese should be wired with async tasks!")
    else:
        print("\n✅ All initialized Ultra systems have async tasks!")
    
    return len(dormant)

if __name__ == "__main__":
    dormant_count = check_engines()
    exit(0 if dormant_count == 0 else 1)
