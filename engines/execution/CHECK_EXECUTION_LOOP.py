#!/usr/bin/env python3
"""
Check if execution loop exists and is being called
"""

print("🔍 Checking execution loop...")
print()

# Check EXECUTION_ORCHESTRATOR
with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    exec_content = f.read()

# Check if run_execution_loop exists
if 'def run_execution_loop' in exec_content or 'async def run_execution_loop' in exec_content:
    print("[OK] run_execution_loop() EXISTS in EXECUTION_ORCHESTRATOR")
    
    # Find the method
    import re
    method_match = re.search(r'(async\s+)?def\s+run_execution_loop.*?(?=\n\s*(?:async\s+)?def|\Z)', exec_content, re.DOTALL)
    if method_match:
        method_code = method_match.group(0)
        print(f"   Method found: {len(method_code)} characters")
        
        # Check if it has while loop
        if 'while' in method_code:
            print("   [OK] Has while loop")
        else:
            print("   [X] NO while loop - method may not run continuously!")
        
        # Check if it calls monitor_positions
        if 'monitor_positions' in method_code:
            print("   [OK] Calls monitor_positions()")
        else:
            print("   [X] Does NOT call monitor_positions()")
        
        # Check if it processes signals
        if 'execute_signal' in method_code or 'execute_trade' in method_code:
            print("   [OK] Processes signals/trades")
        else:
            print("     May not process signals")
else:
    print("[X] run_execution_loop() NOT FOUND in EXECUTION_ORCHESTRATOR!")
    print("   → COMPLETE_ULTIMATE_ORCHESTRATOR calls it but it doesn't exist!")
    print("   → This is why trades aren't happening!")

print()

# Check COMPLETE_ULTIMATE_ORCHESTRATOR
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    orch_content = f.read()

if 'run_execution_loop' in orch_content:
    print("[OK] COMPLETE_ULTIMATE_ORCHESTRATOR calls run_execution_loop()")
    
    # Check how it's called
    if 'asyncio.create_task.*run_execution_loop' in orch_content or 'create_task.*execution.*run_execution_loop' in orch_content:
        print("   [OK] Called with asyncio.create_task (runs in background)")
    else:
        print("     May not be called correctly")
else:
    print("[X] COMPLETE_ULTIMATE_ORCHESTRATOR does NOT call run_execution_loop()!")

