#!/usr/bin/env python3
"""
Set CNS init section to indent 8 (to match line 2650)
"""

print("🔧 Setting CNS section to indent 8...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

# Show what we're fixing
print("Current (lines 2648-2662):")
print("-" * 70)
for i in range(2647, min(2662, len(lines))):
    indent = len(lines[i]) - len(lines[i].lstrip())
    marker = "FIX" if 2650 <= i <= 2658 and indent > 8 else "   "
    print(f"{marker} {i+1:4d} [{indent:2d}]: {lines[i][:65]}", end='')
print()

# Line 2650 is at indent 8 - that's our target
# Lines 2651+ should ALSO be at indent 8
target_indent = 8

print(f"Setting lines 2651-2659 to indent {target_indent}...")
print()

for i in range(2650, min(2660, len(lines))):
    if i < len(lines):
        line = lines[i]
        if line.strip():  # Not empty
            content = line.lstrip()
            lines[i] = ' ' * target_indent + content
            print(f"  {i+1}: {repr(lines[i][:60])}")

print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.writelines(lines)

print("[OK] File saved")
print()

# Verify
import py_compile
import sys

try:
    py_compile.compile('COMPLETE_ULTIMATE_ORCHESTRATOR.py', doraise=True)
    print("=" * 70)
    print("[OK][OK][OK] SYNTAX IS VALID! [OK][OK][OK]")
    print("=" * 70)
    print()
    sys.exit(0)
    
except SyntaxError as e:
    print(f"  Line {e.lineno}: {e.msg}")
    
    if e.lineno and e.lineno < len(lines):
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        
        print("\nContext:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            indent = len(lines[i]) - len(lines[i].lstrip())
            print(f"{marker}{i+1:4d} [{indent:2d}]: {lines[i][:70]}", end='')
    
    print()
    sys.exit(1)

