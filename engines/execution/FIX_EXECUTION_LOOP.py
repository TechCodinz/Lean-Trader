#!/usr/bin/env python3
"""
Fix execution loop to ensure it runs properly
"""

print("🔧 Fixing execution loop...")
print()

# Check how it's called in COMPLETE_ULTIMATE_ORCHESTRATOR
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    orch_content = f.read()

# Find where run_execution_loop is called
import re
call_match = re.search(r'execution.*run_execution_loop|run_execution_loop.*execution', orch_content, re.IGNORECASE | re.DOTALL)

if call_match:
    print("[OK] Found call to run_execution_loop")
    context = call_match.group(0)
    print(f"   Context: {context[:200]}")
    
    # Check if it's in a task
    if 'asyncio.create_task' in context or 'create_task' in context:
        print("   [OK] Called with create_task")
    else:
        print("     May not be called as async task")
else:
    print("[X] Could not find call to run_execution_loop")
    print("   → This is the problem!")

print()

# Check EXECUTION_ORCHESTRATOR for the method
with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    exec_content = f.read()

# Find the method definition
method_match = re.search(r'(async\s+)?def\s+run_execution_loop\s*\([^)]*\)\s*:', exec_content)

if method_match:
    print("[OK] run_execution_loop() method found")
    
    # Get the full method
    start_pos = method_match.end()
    # Find the end of the method (next def or class)
    end_match = re.search(r'\n\s*(?:async\s+)?def\s+|\nclass\s+', exec_content[start_pos:])
    if end_match:
        method_code = exec_content[start_pos:start_pos + end_match.start()]
    else:
        method_code = exec_content[start_pos:start_pos + 5000]
    
    # Check if it has the main loop
    if 'while' in method_code:
        print("   [OK] Has while loop")
        # Check if it's while True or while self.execution_enabled
        if 'while True' in method_code:
            print("   [OK] Uses while True (runs forever)")
        elif 'while self.execution_enabled' in method_code:
            print("   [OK] Uses while self.execution_enabled")
        else:
            print("     Uses different while condition")
    else:
        print("   [X] NO while loop - method won't run continuously!")
    
    # Check if it calls monitor_positions
    if 'monitor_positions' in method_code:
        print("   [OK] Calls monitor_positions()")
    else:
        print("   [X] Does NOT call monitor_positions()")
    
    # Check if it processes signals
    if 'execute_signal' in method_code or 'execute_trade' in method_code or 'data_hub' in method_code:
        print("   [OK] Processes signals")
    else:
        print("     May not process signals")
else:
    print("[X] run_execution_loop() method NOT FOUND!")
    print("   → Need to create it!")

