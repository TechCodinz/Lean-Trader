#!/usr/bin/env python3
"""
Add position monitoring directly to EXECUTION_ORCHESTRATOR.py
"""

print("🔧 Adding position monitoring to orchestrator...")
print()

# Check which orchestrator file exists and is being used
import os

target_file = None
if os.path.exists('EXECUTION_ORCHESTRATOR.py'):
    target_file = 'EXECUTION_ORCHESTRATOR.py'
    print("[OK] Found EXECUTION_ORCHESTRATOR.py")
elif os.path.exists('COMPLETE_ULTIMATE_ORCHESTRATOR.py'):
    target_file = 'COMPLETE_ULTIMATE_ORCHESTRATOR.py'
    print("[OK] Found COMPLETE_ULTIMATE_ORCHESTRATOR.py")

if not target_file:
    print("[X] No orchestrator file found!")
    exit(1)

with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Check if monitor_positions already exists
if 'def monitor_positions' in content:
    print("[OK] monitor_positions() method exists")
    print()
    
    # Check if it actually closes positions
    if 'close_position' in content:
        print("[OK] Has close_position calls")
        print()
        print("Checking if monitoring loop is active...")
        
        # Check if it's being called in a loop
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'monitor_positions' in line and 'await' in line and 'while' not in lines[max(0,i-20):i]:
                print(f"  monitor_positions called but NOT in main loop!")
                print(f"   Line {i+1}: {line.strip()}")
                break
        else:
            print("[OK] Monitoring appears to be in loop")
    else:
        print("[X] Does NOT call close_position!")
        print("   This is why positions never close!")

print()
print("=" * 70)
print("SOLUTION: Enable EXECUTION_ORCHESTRATOR's monitor_positions()")
print("=" * 70)
print()

print("The orchestrator HAS monitoring code but it's not active.")
print("We need to ensure:")
print("  1. monitor_positions() is called in the main loop")
print("  2. It checks positions every 5-10 seconds")
print("  3. It closes at profit (+1%) or loss (-3%)")
print()
print("This requires checking the main() or run() method...")

# Find the main loop
for i, line in enumerate(content.split('\n')):
    if 'while True' in line or 'while self.running' in line:
        print(f"[OK] Found main loop at line {i+1}")
        # Show next 20 lines
        lines = content.split('\n')
        print()
        print("Main loop context:")
        for j in range(i, min(len(lines), i+20)):
            if lines[j].strip():
                print(f"  {j+1}: {lines[j][:80]}")
        break

