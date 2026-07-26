#!/usr/bin/env python3
"""Fix specific indentation error at line 2654"""

print("🔧 Fixing line 2654 indentation...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

# Show context around line 2654
print("Context around line 2654:")
print("-" * 70)
for i in range(2650, min(2658, len(lines))):
    marker = ">>> " if i == 2653 else "    "
    print(f"{marker}{i+1:4d}: {repr(lines[i][:80])}")
print()

# The issue: Line 2654 (index 2653) has extra indentation
# It's likely orphaned from a removed try block

# Check what should be the correct indentation by looking at surrounding lines
line_2654 = lines[2653]

# Look at line before (2653) to determine correct indent
if len(lines) > 2652:
    prev_line = lines[2652]
    prev_indent = len(prev_line) - len(prev_line.lstrip())
    
    # Look at line after (2655) too
    if len(lines) > 2654:
        next_line = lines[2654]
        next_indent = len(next_line) - len(next_line.lstrip())
        
        print(f"Previous line indent: {prev_indent}")
        print(f"Current line indent: {len(line_2654) - len(line_2654.lstrip())}")
        print(f"Next line indent: {next_indent}")
        print()
        
        # Fix: Set to same indent as next line (they should match)
        content = line_2654.lstrip()
        lines[2653] = ' ' * next_indent + content
        
        print(f"[OK] Fixed line 2654 indentation to match line 2655")
        print(f"   New: {repr(lines[2653][:80])}")

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.writelines(lines)

print()
print("[OK] File saved")
print()

# Verify syntax
import py_compile
import sys

try:
    py_compile.compile('COMPLETE_ULTIMATE_ORCHESTRATOR.py', doraise=True)
    print("=" * 70)
    print("[OK] SYNTAX IS NOW VALID!")
    print("=" * 70)
    print()
    sys.exit(0)
    
except SyntaxError as e:
    print(f"  Still has error at line {e.lineno}: {e.msg}")
    print()
    
    # Show new context
    if e.lineno:
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 3)
        
        print("Context:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:4d}: {lines[i][:80]}", end='')
    
    sys.exit(1)

