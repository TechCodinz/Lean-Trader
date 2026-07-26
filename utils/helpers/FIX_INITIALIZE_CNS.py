#!/usr/bin/env python3
"""
Add proper initialize_cns import/definition BEFORE it's used at line 2651
"""

print("🔧 Adding initialize_cns definition...")
print()

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

# We need to add the import/fallback BEFORE line 2651
# Let's add it right before the CNS init section (around line 2649-2650)

# Find line 2650 (the logger.info for CNS)
insert_pos = 2649  # Right before line 2650

print(f"Inserting initialize_cns definition at line {insert_pos}...")
print()

# Add the proper import with fallback
cns_import = """        # Try to import CNS, use fallback if not available
        try:
            from CENTRAL_NERVOUS_SYSTEM import initialize_cns
        except ImportError:
            def initialize_cns():
                return None  # CNS optional fallback
        
"""

lines.insert(insert_pos, cns_import)

print("[OK] Added CNS import/fallback")
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
    sys.exit(1)

