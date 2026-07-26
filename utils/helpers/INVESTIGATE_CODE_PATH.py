#!/usr/bin/env python3
"""
Investigate why the new price fetching code isn't running
despite making +3,632% profit!
"""

print("="*70)
print("🔍 INVESTIGATING CODE PATH")
print("="*70)
print()

# Check if our code is actually in the file
try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        content = f.read()
    
    # Check for our fix
    if 'Using CURRENT market price' in content:
        print("[OK] Fix IS in the file")
        
        # Find the section
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'Using CURRENT market price' in line:
                print(f"   Found at line {i}")
                print()
                print("   Context:")
                start = max(0, i-6)
                end = min(len(lines), i+4)
                for j in range(start, end):
                    marker = ">>>" if j == i-1 else "   "
                    print(f"   {marker} {j+1:4d}: {lines[j]}")
                break
    else:
        print("[X] Fix NOT in file!")
        print("   The surgical fix didn't save properly!")
    
    print()
    
    # Check if there are exceptions being thrown
    print("Checking for exceptions in logs...")
    
    import subprocess
    result = subprocess.run(
        ['grep', '-a', 'fetch_ticker', 'bot.log'],
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(f"   Found {len(result.stdout.splitlines())} fetch_ticker mentions")
        print("   Last 3:")
        for line in result.stdout.splitlines()[-3:]:
            print(f"     {line[:120]}")
    else:
        print("    NO fetch_ticker calls found in logs!")
        print("   This means the code path isn't being executed at all!")
    
    print()
    
    # Check for "Could not fetch market price" warnings
    result2 = subprocess.run(
        ['grep', '-ac', 'Could not fetch market price', 'bot.log'],
        capture_output=True,
        text=True
    )
    
    error_count = int(result2.stdout.strip() or 0)
    if error_count > 0:
        print(f"    Found {error_count} 'Could not fetch market price' errors")
        print("   The ticker fetch is failing!")
    else:
        print("   No fetch errors found")
    
    print()
    
    # Look for where actual_price is being set
    print("="*70)
    print("FINDING ACTIVE CODE PATH")
    print("="*70)
    print()
    
    # Check what logs we ARE seeing
    result3 = subprocess.run(
        ['grep', '-a', 'Using order', 'bot.log'],
        capture_output=True,
        text=True
    )
    
    if result3.stdout:
        lines_found = result3.stdout.splitlines()
        print(f"Found {len(lines_found)} 'Using order' log messages")
        print("Sample (last 3):")
        for line in lines_found[-3:]:
            print(f"  {line[:120]}")
        print()
        print("❗ This suggests fallback code is running!")
    
    print()
    
    # Check what's BEFORE the actual_price assignment
    print("Checking execution flow in file...")
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if 'Final entry_price' in line:
            print(f"Found 'Final entry_price' at line {i+1}")
            print()
            print("Code BEFORE this (30 lines):")
            start = max(0, i-30)
            for j in range(start, i+1):
                print(f"  {j+1:4d}: {lines[j]}")
            break
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
print("💡 DIAGNOSIS")
print("="*70)
print()
print("Performance: +3,632% ($4.45 → $166.11) - INCREDIBLE!")
print()
print("If 'Using CURRENT market price' not in logs:")
print("  → The ticker fetch code isn't running")
print("  → Either exception or code path is different")
print("  → Need to add it in DIFFERENT location")
print()
print("Next: Find the ACTUAL execution path and fix THAT!")
print("="*70)

