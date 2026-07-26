#!/usr/bin/env python3
"""
REPAIR INDENTATION DAMAGE
Fix malformed try/except blocks that broke indentation
"""

import re

print("🔧 Repairing COMPLETE_ULTIMATE_ORCHESTRATOR.py...")
print("-" * 60)

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Problem: FIX_GRACEFUL_FAILURES.py added try/except without proper indentation
# Solution: Remove the broken try/except wrappers and keep the original code

# Pattern: Find try blocks followed by non-indented code
# Example of broken code:
#         try:
#         PERFECT_CONSCIOUSNESS_AVAILABLE = True  # WRONG! Should be indented
#         except Exception as e:
#             pass

lines = content.split('\n')
fixed_lines = []
i = 0
fixes_applied = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this is a try block followed by non-indented code
    if line.strip() == 'try:' and i + 1 < len(lines):
        try_indent = len(line) - len(line.lstrip())
        next_line = lines[i + 1]
        next_indent = len(next_line) - len(next_line.lstrip())
        
        # If next line is not indented more than try, it's broken
        if next_indent <= try_indent and next_line.strip():
            # This is a broken try block - skip it and the corresponding except
            print(f"   Removing broken try/except at line {i+1}")
            
            # Skip the try line
            i += 1
            
            # Keep the actual code line(s)
            while i < len(lines):
                current_line = lines[i]
                
                # Stop at the except block
                if 'except Exception' in current_line and 'pass' in current_line:
                    i += 1  # Skip except
                    if i < len(lines) and 'pass' in lines[i]:
                        i += 1  # Skip pass
                    fixes_applied += 1
                    break
                elif current_line.strip().startswith('except '):
                    # Multi-line except
                    i += 1
                    if i < len(lines) and 'pass' in lines[i]:
                        i += 1
                    fixes_applied += 1
                    break
                else:
                    # Keep the actual code
                    fixed_lines.append(current_line)
                    i += 1
            continue
    
    # Keep normal lines
    fixed_lines.append(line)
    i += 1

# Write repaired content
content = '\n'.join(fixed_lines)

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.write(content)

print(f"[OK] Removed {fixes_applied} broken try/except blocks")
print(f"[OK] Preserved original code structure")
print()

# Now verify syntax
print("Verifying syntax...")
import py_compile

try:
    py_compile.compile('COMPLETE_ULTIMATE_ORCHESTRATOR.py', doraise=True)
    print("[OK] Syntax is now VALID!")
    print()
except SyntaxError as e:
    print(f"[X] Still has syntax error: {e}")
    print(f"   Line {e.lineno}: {e.text}")
    print()
    print("Checking the specific area...")
    
    # Show the problematic area
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        lines = f.readlines()
        
    if e.lineno:
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 3)
        print("\nContext:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:4d}: {lines[i]}", end='')
