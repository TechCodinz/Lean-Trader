#!/usr/bin/env python3
"""
CRITICAL FIX: Remove timeout from monitor_positions and ensure it runs
"""

print("🔧 Fixing position monitoring...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

fixed = False
for i, line in enumerate(lines):
    # Fix 1: Remove timeout from monitor_positions()
    if 'await asyncio.wait_for(self.monitor_positions(), timeout=3.0)' in line:
        lines[i] = '                    await self.monitor_positions()  # No timeout - let it run fully\n'
        print(f"   [OK] Fixed line {i+1}: Removed 3-second timeout")
        fixed = True
    
    # Fix 2: Remove the TimeoutError exception handler
    if i > 0 and 'except asyncio.TimeoutError:' in line:
        # Check if next line is about timeout
        if i+1 < len(lines) and 'timeout' in lines[i+1].lower():
            # Remove this exception block (2-3 lines)
            lines[i] = ''  # Remove exception line
            if i+1 < len(lines):
                lines[i+1] = ''  # Remove warning line
            print(f"   [OK] Removed TimeoutError handler at line {i+1}")
            fixed = True

if fixed:
    with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print()
    print("=" * 70)
    print("[OK] MONITORING FIXED")
    print("=" * 70)
else:
    print("     Could not find timeout code (may already be fixed)")

print()

# Check if run_execution_loop exists
print("2️⃣ Checking for run_execution_loop()...")

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

if 'def run_execution_loop' in content or 'async def run_execution_loop' in content:
    print("   [OK] run_execution_loop() exists")
    
    # Check if it calls monitor_positions
    if 'monitor_positions' in content:
        print("   [OK] Calls monitor_positions()")
    else:
        print("   [X] Does NOT call monitor_positions() - THIS IS THE PROBLEM!")
else:
    print("   [X] run_execution_loop() NOT FOUND!")
    print("   → COMPLETE_ULTIMATE_ORCHESTRATOR calls it but it doesn't exist!")
    print("   → Need to create it or fix the call")

print()

# Check what the main execution loop looks like
print("3️⃣ Checking main execution loop...")

# Find the loop that calls monitor_positions
if 'while True' in content:
    # Find the while True block
    import re
    while_blocks = re.findall(r'while True:.*?(?=async def|\Z)', content, re.DOTALL)
    if while_blocks:
        for i, block in enumerate(while_blocks[:1]):  # Just first one
            if 'monitor_positions' in block:
                print(f"   [OK] Found while True loop with monitor_positions()")
                if 'timeout' in block:
                    print(f"     But it has timeout - should be fixed above")
                else:
                    print(f"   [OK] No timeout found - should work!")
            else:
                print(f"     while True loop found but no monitor_positions()")

print()
print("=" * 70)
print("[OK] DIAGNOSIS COMPLETE")
print("=" * 70)

