#!/usr/bin/env python3
"""
Restore intelligent adaptive position sizing (2-5% of balance)
"""

import os

print("🔧 Restoring position sizing in INTELLIGENT_EXECUTION_ENGINE.py...")
print()

if not os.path.exists('INTELLIGENT_EXECUTION_ENGINE.py'):
    print("[X] INTELLIGENT_EXECUTION_ENGINE.py not found!")
    print()
    print("This file was deleted, which explains:")
    print("  • Why position sizing shows $0.00")
    print("  • Why 'Position size:' logs are missing")
    print("  • Why trades execute but P&L isn't captured")
    print()
    print("SOLUTION: Need to recreate or restore this file")
    print()
    exit(1)

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Check if sizing already exists
if 'confidence * 0.08' in content and 'Position size:' in content:
    print("[OK] Position sizing code already exists!")
    print()
    
    # Show the existing code
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'confidence * 0.08' in line:
            print("Found at line", i+1)
            print("Context:")
            for j in range(max(0, i-3), min(len(lines), i+5)):
                print(f"  {j+1}: {lines[j]}")
            break
    
    exit(0)

print("[X] Position sizing code is MISSING!")
print()
print("Need to find where to insert it...")
print()

# Find the execute method
if 'def execute(' in content:
    print("[OK] Found execute() method")
    
    # Find where position_size is calculated
    if 'position_size' in content:
        print("[OK] Found position_size references")
        
        # Show where they are
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'position_size' in line.lower() and '=' in line:
                print(f"  Line {i+1}: {line.strip()[:80]}")
    else:
        print("[X] No position_size variable found")

print()
print("=" * 70)
print("MANUAL FIX REQUIRED")
print("=" * 70)
print()
print("The position sizing code needs to be manually restored.")
print("Expected code:")
print()
print("```python")
print("# Intelligent adaptive sizing: 2-5% of balance")
print("confidence = signal.get('confidence', 0.6) if isinstance(signal, dict) else 0.6")
print("size_pct = min(0.05, max(0.02, confidence * 0.08))  # 2-5% based on confidence")
print("position_size = max(5.0, balance * size_pct) if balance > 0 else 10.0")
print("logger.info(f'📊 Position size: ${position_size:.2f} ({size_pct*100:.1f}% of ${balance:.2f})')")
print("```")

