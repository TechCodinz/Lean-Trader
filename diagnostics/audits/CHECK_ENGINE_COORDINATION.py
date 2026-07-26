#!/usr/bin/env python3
"""
Check Engine Coordination - See What's Working Together
"""

import re

def analyze_engine_coordination(orch_file):
    with open(orch_file, 'r') as f:
        content = f.read()
    
    print("🔍 ANALYZING ENGINE COORDINATION")
    print("="*60)
    print()
    
    # Find all tasks being created
    tasks = re.findall(r'tasks\.append\(asyncio\.create_task\((.+?)\)\)', content)
    
    print(f"📊 Total Async Tasks: {len(tasks)}")
    print()
    
    print("PROFIT ENGINES:")
    print("-" * 40)
    for i, task in enumerate(tasks, 1):
        if any(word in task.lower() for word in ['profit', 'micro', 'steady', 'growth']):
            # Check if commented out
            line_match = re.search(rf'(#\s*)?tasks\.append\(asyncio\.create_task\({re.escape(task)}\)\)', content)
            status = "❌ DISABLED" if line_match and line_match.group(1) else "✅ ACTIVE"
            print(f"{i}. {status} - {task}")
    
    print()
    print("SIGNAL ENGINES:")
    print("-" * 40)
    for i, task in enumerate(tasks, 1):
        if any(word in task.lower() for word in ['scalp', 'scout', 'arb', 'moon', 'signal']):
            line_match = re.search(rf'(#\s*)?tasks\.append\(asyncio\.create_task\({re.escape(task)}\)\)', content)
            status = "❌ DISABLED" if line_match and line_match.group(1) else "✅ ACTIVE"
            print(f"{i}. {status} - {task}")
    
    print()
    print("COORDINATION CHECKS:")
    print("-" * 40)
    
    # Check if Steady Profit gets signals from hub
    if 'self.data_hub.get_signals' in content and 'run_steady_profit' in content:
        print("✅ Steady Profit → Data Hub (connected)")
    else:
        print("❌ Steady Profit → Data Hub (NOT connected)")
    
    # Check if MICRO gets signals from hub
    if 'run_micro_wallet_growth' in content and 'hub_signals = self.data_hub.get_signals' in content:
        print("✅ MICRO → Data Hub (connected)")
    else:
        print("❌ MICRO → Data Hub (NOT connected)")
    
    # Check if Scalper publishes to hub
    if 'await self.data_hub.publish_signal' in content or 'Published.*signals to data hub' in content:
        print("✅ Engines → Data Hub (publishing)")
    else:
        print("❌ Engines → Data Hub (NOT publishing)")
    
    # Check if Execution Orchestrator monitors decisions
    if 'self.execution' in content and 'execute_signal' in content:
        print("✅ Execution Orchestrator → Wired")
    else:
        print("❌ Execution Orchestrator → NOT wired")
    
    print()
    print("SIGNAL FLOW:")
    print("-" * 40)
    print("Expected: Scalper → Data Hub → MICRO/Steady → Execution → Profit")
    print()
    
    # Check if signals have what's needed
    print("SIGNAL QUALITY CHECK:")
    print("-" * 40)
    
    if "'stop_loss':" in content and 'SMART_SCALPING' in content:
        print("✅ Scalper signals include stop_loss")
    else:
        print("⚠️  Scalper signals missing stop_loss")
    
    if "'take_profit':" in content and 'SMART_SCALPING' in content:
        print("✅ Scalper signals include take_profit")
    else:
        print("⚠️  Scalper signals missing take_profit")

if __name__ == '__main__':
    analyze_engine_coordination('/workspace/COMPLETE_ULTIMATE_ORCHESTRATOR.py')
