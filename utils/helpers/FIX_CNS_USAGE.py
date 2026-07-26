#!/usr/bin/env python3
"""
Wrap CNS usage (lines after self.cns = initialize_cns()) in if self.cns: check
"""

print("🔧 Fixing CNS usage safety check...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

# Find the line where self.cns = initialize_cns() is called
# Then find all lines that use self.cns after that and wrap them

# Look for lines that use self.cns (after initialization)
# Around line 2658-2665 based on previous errors

print("Finding CNS usage lines...")
print()

# Show current state around line 2658
for i in range(2655, min(2670, len(lines))):
    indent = len(lines[i]) - len(lines[i].lstrip())
    uses_cns = 'self.cns.' in lines[i] or 'self.cns =' in lines[i]
    marker = "CNS" if uses_cns else "   "
    print(f"{marker} {i+1:4d} [{indent:2d}]: {lines[i][:70]}", end='')

print()
print()

# Strategy: Find first line with self.cns = initialize_cns()
# Then wrap subsequent self.cns usage in if self.cns:

cns_init_line = None
for i in range(2650, min(2670, len(lines))):
    if 'self.cns = initialize_cns()' in lines[i]:
        cns_init_line = i
        print(f"Found CNS init at line {i+1}")
        break

if cns_init_line is not None:
    # Find the indent level of the cns init line
    init_indent = len(lines[cns_init_line]) - len(lines[cns_init_line].lstrip())
    
    # After the init line, add an if self.cns: check
    # Then indent all CNS usage lines by +4
    
    # Find where CNS usage starts (next non-empty line after init)
    usage_start = cns_init_line + 1
    while usage_start < len(lines) and not lines[usage_start].strip():
        usage_start += 1
    
    # Find where CNS usage ends (look for else, except, or dedent)
    usage_end = usage_start
    for i in range(usage_start, min(usage_start + 20, len(lines))):
        line_indent = len(lines[i]) - len(lines[i].lstrip())
        if lines[i].strip() and line_indent <= init_indent:
            usage_end = i
            break
        if 'logger.error' in lines[i] and 'CNS' in lines[i]:
            usage_end = i + 1
            break
    
    print(f"CNS usage block: lines {usage_start+1} to {usage_end}")
    print()
    
    # Insert if self.cns: after the init line
    if_check = ' ' * init_indent + 'if self.cns:\n'
    lines.insert(cns_init_line + 1, if_check)
    
    print(f"[OK] Inserted 'if self.cns:' at line {cns_init_line + 2}")
    
    # Indent the CNS usage lines by +4
    for i in range(cns_init_line + 2, cns_init_line + 2 + (usage_end - usage_start)):
        if i < len(lines) and lines[i].strip():
            lines[i] = '    ' + lines[i]
    
    print(f"[OK] Indented CNS usage block")
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
    print(f"[X] Syntax error at line {e.lineno}: {e.msg}")
    
    if e.lineno and e.lineno < len(lines):
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 3)
        
        print("\nContext:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:4d}: {lines[i][:70]}", end='')
    
    sys.exit(1)

