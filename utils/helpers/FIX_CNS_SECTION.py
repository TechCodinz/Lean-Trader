#!/usr/bin/env python3
"""
Fix CNS section - the entire block is over-indented
Lines 2654-2657+ need to be dedented by 4 spaces
"""

print("🔧 Fixing CNS section indentation...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

# The problem: Lines 2654+ are indented as if inside a block they're not in
# They're orphaned from removing broken try/except

# Show current state
print("Current state (lines 2648-2665):")
print("-" * 70)
for i in range(2647, min(2665, len(lines))):
    indent = len(lines[i]) - len(lines[i].lstrip())
    print(f"{i+1:4d} [{indent:2d}]: {lines[i][:70]}", end='')
print()

# Strategy: Find where except ImportError block ends, then dedent everything after
# Line 2651: try import
# Line 2652-2653: except fallback function
# Line 2654+: Should be back to original indent (probably 8 spaces)

# Lines 2652-2653 are at indent 4 and 8 (inside except)
# Line 2654+ should be at indent 8 (same as the try/except block itself)

# Find the base indentation by looking at line 2651 (the try or except line)
base_indent = 0
if len(lines) > 2650:
    # Line 2651 should tell us the base
    line_2651 = lines[2650]
    base_indent = len(line_2651) - len(line_2651.lstrip())
    print(f"Base indent (from line 2651): {base_indent}")

# Now fix lines 2654 onwards - they should be at base_indent + 4 (inside the __init__ method)
# Actually, let's look at what comes BEFORE line 2651 to determine proper indent

print()
print("Looking at structure before line 2651:")
for i in range(2645, 2651):
    if i < len(lines):
        indent = len(lines[i]) - len(lines[i].lstrip())
        print(f"{i+1:4d} [{indent:2d}]: {lines[i][:60]}", end='')

print()
print()

# The CNS section should match the indentation of other self.xxx = lines
# Let's find a self.xxx assignment before line 2651 to get correct indent
proper_indent = 8  # Default guess

for i in range(2650, max(0, 2650-50), -1):
    if i < len(lines) and 'self.' in lines[i] and '=' in lines[i]:
        proper_indent = len(lines[i]) - len(lines[i].lstrip())
        print(f"Found self assignment at line {i+1} with indent {proper_indent}")
        print(f"   {lines[i][:70]}", end='')
        break

print()
print(f"Proper indent for CNS init should be: {proper_indent}")
print()

# Fix lines 2654-2660 (the CNS initialization block)
# Dedent them to proper_indent
print("Fixing lines 2654-2660...")

for i in range(2653, min(2660, len(lines))):
    line = lines[i]
    if line.strip():  # If not empty
        # Remove all leading whitespace and add proper amount
        content = line.lstrip()
        lines[i] = ' ' * proper_indent + content
        print(f"  Line {i+1}: {repr(lines[i][:60])}")

print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.writelines(lines)

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
    
    # Show context
    if e.lineno and e.lineno < len(lines):
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        
        print("Context:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            indent = len(lines[i]) - len(lines[i].lstrip()) if i < len(lines) else 0
            print(f"{marker}{i+1:4d} [{indent:2d}]: {lines[i][:70]}", end='')
    
    print()
    sys.exit(1)

