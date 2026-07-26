#!/usr/bin/env python3
"""
Fix position sizing to use actual fetched balance
Line ~610 shows: Position sizing: $20.00 (balance: $1000)
Need to ensure final_size calculation uses the REAL balance
"""

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    lines = f.readlines()

# Find the position sizing section (around line 600-615)
for i in range(len(lines)):
    # Find the line with position sizing log
    if 'Position sizing:' in lines[i] and 'balance:' in lines[i]:
        print(f"Found position sizing log at line {i+1}")
        print(f"Current: {lines[i].strip()}")
        
        # Now we need to look backwards to find where final_size is calculated
        # Look for lines like: final_size = ...
        for j in range(i-1, max(0, i-30), -1):
            if 'final_size' in lines[j] and '=' in lines[j]:
                print(f"\nFound final_size calculation at line {j+1}:")
                print(f"  {lines[j].strip()}")
                
                # Check if it uses 'balance' variable
                if 'balance' not in lines[j]:
                    print("\n WARNING: final_size doesn't use balance variable!")
                    print("Need to find where it's calculated from")
        
        # Look for the master_coordinator.calculate_optimal_position_size call
        for j in range(max(0, i-50), i):
            if 'calculate_optimal_position_size' in lines[j]:
                print(f"\nFound calculate_optimal_position_size at line {j+1}:")
                print(f"  {lines[j].strip()}")
                
                # Check what balance is passed
                if 'balance' in lines[j]:
                    print("  [OK] Uses 'balance' parameter")
                else:
                    print("  [X] Doesn't pass balance!")
        
        break

print("\n" + "="*70)
print("DIAGNOSIS:")
print("="*70)
print()
print("The issue is likely one of:")
print("1. final_size is hardcoded (not calculated)")
print("2. calculate_optimal_position_size gets wrong balance")
print("3. Balance variable is overwritten before use")
print()
print("Checking what balance value is used in position sizing...")

# Search for where balance might be set to 1000
for i, line in enumerate(lines):
    if i >= 480 and i <= 620:  # Focus on the execution section
        if 'balance' in line.lower() and ('1000' in line or '= ' in line):
            print(f"Line {i+1}: {line.strip()}")

