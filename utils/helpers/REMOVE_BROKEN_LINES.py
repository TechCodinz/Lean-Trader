#!/usr/bin/env python3
"""
Remove lines 2651-2653 which are broken remnants from failed fix
Then properly indent the real code that follows
"""

print("🔧 Removing broken lines 2651-2653...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

print("Current state:")
print("-" * 70)
for i in range(2648, min(2665, len(lines))):
    indent = len(lines[i]) - len(lines[i].lstrip())
    marker = "DEL" if 2650 <= i <= 2652 else "   "
    print(f"{marker} {i+1:4d} [{indent:2d}]: {lines[i][:65]}", end='')
print()

# Remove lines 2651-2653 (indices 2650-2652)
print("Removing broken lines 2651, 2652, 2653...")
del lines[2650:2653]

print(f"[OK] Removed 3 broken lines")
print(f"New total: {len(lines)} lines")
print()

# Now fix indentation of what's left
# The self.cns line (now at 2651) should match surrounding self.xxx assignments
# Based on the output, proper indent is 12

print("New state after removal:")
print("-" * 70)
for i in range(2648, min(2662, len(lines))):
    indent = len(lines[i]) - len(lines[i].lstrip())
    print(f"    {i+1:4d} [{indent:2d}]: {lines[i][:65]}", end='')
print()

# Find proper indent from surrounding context
proper_indent = 12  # From the output, we know it should be 12

# Fix lines that are now 2651+ (the CNS init code)
# They should be at indent 12
print("Fixing indentation of CNS init section...")

for i in range(2650, min(2660, len(lines))):
    if i < len(lines):
        line = lines[i]
        if line.strip() and not line.strip().startswith('#'):
            # This is code that needs fixing
            content = line.lstrip()
            lines[i] = ' ' * proper_indent + content
            print(f"  Line {i+1}: indent {proper_indent}")

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
    print("[OK][OK][OK] SYNTAX IS VALID! [OK][OK][OK]")
    print("=" * 70)
    print()
    print("All broken lines removed!")
    print("Indentation fixed!")
    print("Ready to start FULL POWER bot!")
    print()
    sys.exit(0)
    
except SyntaxError as e:
    print(f"  Error at line {e.lineno}: {e.msg}")
    print()
    
    if e.lineno and e.lineno < len(lines):
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        
        print("Context:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            indent = len(lines[i]) - len(lines[i].lstrip()) if i < len(lines) else 0
            print(f"{marker}{i+1:4d} [{indent:2d}]: {lines[i][:70]}", end='')
    
    print()
    print("We'll fix this next!")
    sys.exit(1)

