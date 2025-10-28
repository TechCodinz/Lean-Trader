#!/usr/bin/env python3
"""
Complete Engine Audit - Find ALL Engines and Their Status
==========================================================

Checks:
1. Which engines are initialized
2. Which engines have async tasks running
3. Which engines get signals from Data Hub
4. Which engines publish to Data Hub
5. Which engines execute trades
6. Which engines are orphaned (initialized but not used)
"""

import re
from collections import defaultdict

def audit_all_engines(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    print("="*80)
    print("COMPLETE ENGINE AUDIT")
    print("="*80)
    print()
    
    # ================================================================
    # PHASE 1: Find all engine initializations
    # ================================================================
    print("PHASE 1: ENGINE INITIALIZATION")
    print("-"*80)
    
    engines_initialized = []
    for i, line in enumerate(lines):
        # Match patterns like: self.ultra_scalping = UltraScalpingEngine()
        match = re.search(r'self\.([a-z_]+)\s*=\s*([A-Z][a-zA-Z]+)\(', line)
        if match and 'self.advanced_systems' not in line and 'self.trading_engines' not in line:
            engine_name = match.group(1)
            engine_class = match.group(2)
            engines_initialized.append({
                'name': engine_name,
                'class': engine_class,
                'line': i + 1
            })
    
    # Group by type
    profit_engines = []
    signal_engines = []
    execution_engines = []
    ai_engines = []
    utility_engines = []
    
    for eng in engines_initialized:
        name = eng['name'].lower()
        if any(x in name for x in ['profit', 'micro', 'steady', 'growth', 'compound']):
            profit_engines.append(eng)
        elif any(x in name for x in ['scalp', 'arb', 'moon', 'scout', 'scanner']):
            signal_engines.append(eng)
        elif any(x in name for x in ['execution', 'trade', 'broker', 'orchestrator']):
            execution_engines.append(eng)
        elif any(x in name for x in ['ai', 'ml', 'swarm', 'evolution', 'divine', 'brain', 'quantum']):
            ai_engines.append(eng)
        else:
            utility_engines.append(eng)
    
    print(f"📊 Total Engines Initialized: {len(engines_initialized)}")
    print()
    print(f"💰 Profit Engines: {len(profit_engines)}")
    for eng in profit_engines:
        print(f"   • {eng['name']} ({eng['class']}) - Line {eng['line']}")
    
    print()
    print(f"📡 Signal Engines: {len(signal_engines)}")
    for eng in signal_engines:
        print(f"   • {eng['name']} ({eng['class']}) - Line {eng['line']}")
    
    print()
    print(f"⚡ Execution Engines: {len(execution_engines)}")
    for eng in execution_engines:
        print(f"   • {eng['name']} ({eng['class']}) - Line {eng['line']}")
    
    print()
    print(f"🤖 AI/ML Engines: {len(ai_engines)}")
    for eng in ai_engines:
        print(f"   • {eng['name']} ({eng['class']}) - Line {eng['line']}")
    
    print()
    print(f"🔧 Utility Engines: {len(utility_engines)}")
    for eng in utility_engines[:10]:  # First 10 only
        print(f"   • {eng['name']} ({eng['class']}) - Line {eng['line']}")
    if len(utility_engines) > 10:
        print(f"   ... and {len(utility_engines)-10} more")
    
    # ================================================================
    # PHASE 2: Find async tasks
    # ================================================================
    print()
    print("="*80)
    print("PHASE 2: ASYNC TASKS (Which Engines Are Running Loops)")
    print("-"*80)
    
    tasks = re.findall(r'tasks\.append\(asyncio\.create_task\(([^\)]+)\)', content)
    active_tasks = [t for t in tasks if not re.search(r'#.*tasks\.append', content)]
    
    print(f"📊 Total Async Tasks: {len(active_tasks)}")
    print()
    
    for i, task in enumerate(active_tasks, 1):
        # Check if commented
        task_pattern = re.escape(task)
        if re.search(rf'^\s*#.*{task_pattern}', content, re.MULTILINE):
            status = "❌ DISABLED"
        else:
            status = "✅ RUNNING"
        print(f"{i:2}. {status} - {task}")
    
    # ================================================================
    # PHASE 3: Signal Flow Analysis
    # ================================================================
    print()
    print("="*80)
    print("PHASE 3: SIGNAL FLOW (Data Hub Connections)")
    print("-"*80)
    
    # Find publishers
    publishers = re.findall(r'await self\.data_hub\.publish[_signal]*\(', content)
    print(f"📤 Signal Publishers: {len(publishers)} publish calls")
    
    # Find consumers
    consumers = re.findall(r'self\.data_hub\.get_signals\([^\)]*\)', content)
    print(f"📥 Signal Consumers: {len(consumers)} get_signals calls")
    
    print()
    print("WHO PUBLISHES:")
    for match in re.finditer(r'(await self\.data_hub\.publish[_signal]*)\(', content):
        # Find context (which function/engine)
        pos = match.start()
        context = content[max(0, pos-500):pos]
        
        # Look for function name
        func_match = re.search(r'async def (\w+)\(', context[::-1])
        if func_match:
            func_name = func_match.group(1)[::-1]
            print(f"   • {func_name}")
    
    print()
    print("WHO CONSUMES:")
    for match in re.finditer(r'(self\.data_hub\.get_signals)\(', content):
        pos = match.start()
        context = content[max(0, pos-500):pos]
        func_match = re.search(r'async def (\w+)\(', context[::-1])
        if func_match:
            func_name = func_match.group(1)[::-1]
            print(f"   • {func_name}")
    
    # ================================================================
    # PHASE 4: Execution Analysis
    # ================================================================
    print()
    print("="*80)
    print("PHASE 4: TRADE EXECUTION (Who Actually Trades)")
    print("-"*80)
    
    # Find execution calls
    executions = []
    patterns = [
        r'create_market_buy_order',
        r'create_market_sell_order',
        r'execute_trade',
        r'execute_signal',
        r'\.place_order',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        if matches:
            executions.append((pattern, len(matches)))
    
    for pattern, count in executions:
        print(f"   • {pattern}: {count} calls")
    
    # ================================================================
    # PHASE 5: Orphaned Engines
    # ================================================================
    print()
    print("="*80)
    print("PHASE 5: ORPHANED ENGINES (Initialized But Not Used)")
    print("-"*80)
    
    engine_names = [eng['name'] for eng in engines_initialized]
    task_content = ' '.join(active_tasks)
    
    orphaned = []
    for eng in engines_initialized:
        name = eng['name']
        # Check if mentioned in any task
        if name not in task_content and name not in content[content.find('async def start'):]:
            # Check if used anywhere in start() method
            start_section = content[content.find('async def start'):]
            if f"self.{name}" not in start_section or start_section.count(f"self.{name}") == 1:
                orphaned.append(eng)
    
    if orphaned:
        print(f"⚠️  Found {len(orphaned)} orphaned engines:")
        for eng in orphaned[:15]:
            print(f"   • {eng['name']} ({eng['class']}) - INITIALIZED BUT NOT USED!")
    else:
        print("✅ No orphaned engines - all are used!")
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print()
    print("="*80)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*80)
    print()
    
    print(f"✅ {len(engines_initialized)} engines initialized")
    print(f"✅ {len(active_tasks)} async tasks running")
    print(f"⚠️  {len(orphaned)} engines orphaned")
    print()
    
    print("CRITICAL ACTIONS NEEDED:")
    if consumers:
        print("✅ Data Hub has consumers (engines getting signals)")
    else:
        print("❌ NO CONSUMERS - engines not getting signals from hub!")
    
    if publishers:
        print("✅ Data Hub has publishers (engines publishing signals)")
    else:
        print("❌ NO PUBLISHERS - no signals being created!")
    
    print()
    print("Next: Wire orphaned engines to:")
    print("  1. Get signals from Data Hub (if signal consumer)")
    print("  2. Publish signals to Data Hub (if signal generator)")
    print("  3. Execute via Execution Orchestrator (if profit engine)")

if __name__ == '__main__':
    audit_all_engines('/workspace/COMPLETE_ULTIMATE_ORCHESTRATOR.py')
