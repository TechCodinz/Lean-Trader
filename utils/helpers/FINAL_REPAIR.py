#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE INDENTATION REPAIR
Fix ALL remaining try/except issues including CNS import
"""

print("🔧 Final repair of COMPLETE_ULTIMATE_ORCHESTRATOR.py...")
print("-" * 70)

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Strategy: Find ALL try statements and check if the next non-empty line is indented
fixed_lines = []
i = 0
fixes = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this is a try statement
    if line.strip() == 'try:':
        try_indent = len(line) - len(line.lstrip())
        
        # Look at next non-empty line
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        
        if j < len(lines):
            next_line = lines[j]
            next_indent = len(next_line) - len(next_line.lstrip())
            
            # Check if properly indented (should be > try_indent)
            if next_indent <= try_indent:
                print(f"   Fixing malformed try block at line {i+1}")
                
                # This is a malformed try block
                # Skip the try and find the except, then skip that too
                i += 1  # Skip try line
                
                # Keep lines until we hit except
                while i < len(lines):
                    current = lines[i]
                    
                    if current.strip().startswith('except '):
                        # Found the except - skip it and its pass statement
                        i += 1
                        if i < len(lines) and 'pass' in lines[i]:
                            i += 1
                        fixes += 1
                        break
                    else:
                        # Keep the actual code
                        fixed_lines.append(current)
                        i += 1
                
                continue
    
    # Keep all normal lines
    fixed_lines.append(line)
    i += 1

# Write fixed content
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.writelines(fixed_lines)

print(f"[OK] Fixed {fixes} malformed try/except blocks")
print()

# Verify syntax
print("Verifying Python syntax...")
import py_compile
import sys

try:
    py_compile.compile('COMPLETE_ULTIMATE_ORCHESTRATOR.py', doraise=True)
    print("[OK] SYNTAX IS NOW VALID!")
    print()
    sys.exit(0)  # Success
    
except SyntaxError as e:
    print(f"[X] Syntax error remains at line {e.lineno}")
    print()
    
    # Show context
    if e.lineno:
        with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
            all_lines = f.readlines()
        
        start = max(0, e.lineno - 5)
        end = min(len(all_lines), e.lineno + 5)
        
        print("Context around error:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:4d}: {all_lines[i]}", end='')
    
    print()
    sys.exit(1)  # Failed
