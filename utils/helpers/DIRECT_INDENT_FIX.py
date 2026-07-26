#!/usr/bin/env python3
"""
Direct fix: Indent lines 2660-2666 by 4 spaces
(They're inside the if self.cns: block)
"""

print("🔧 Direct indent fix...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

# Show current state
print("Current (lines 2657-2670):")
print("-" * 70)
for i in range(2656, min(2670, len(lines))):
    indent = len(lines[i]) - len(lines[i].lstrip())
    print(f"{i+1:4d} [{indent:2d}]: {lines[i][:70]}", end='')

print()
print()

# Lines 2660-2666 need +4 indent (they're after if self.cns: on line 2659)
# But skip empty lines

print("Indenting lines 2660-2666 by +4 spaces...")

for i in range(2659, 2666):  # Lines 2660-2666 (indices 2659-2665)
    if i < len(lines) and lines[i].strip():  # If not empty
        lines[i] = '    ' + lines[i]
        print(f"  Line {i+1}: +4 indent")

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
    print("[OK] SYNTAX VALID!")
    print("=" * 70)
    sys.exit(0)
    
except SyntaxError as e:
    print(f"[X] Line {e.lineno}: {e.msg}")
    
    if e.lineno and e.lineno < len(lines):
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 3)
        
        print("\nContext:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            indent = len(lines[i]) - len(lines[i].lstrip())
            print(f"{marker}{i+1:4d} [{indent:2d}]: {lines[i][:70]}", end='')
    
    sys.exit(1)

