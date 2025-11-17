#!/usr/bin/env python3
import os
import re

# Find all Ultra/Quantum/Divine engine files
engine_files = []
for f in os.listdir('.'):
    if f.endswith('.py') and any(x in f.upper() for x in ['ULTRA', 'QUANTUM', 'DIVINE']):
        engine_files.append(f)

print(f"Found {len(engine_files)} ultra engine files:")
for f in sorted(engine_files):
    print(f"  {f}")

# Check if they're imported in orchestrator
print("\nChecking COMPLETE_ULTIMATE_ORCHESTRATOR.py imports:")
with open('systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as orch:
    content = orch.read()
    
imported = []
not_imported = []

for f in engine_files:
    module_name = f.replace('.py', '')
    if f'from {module_name}' in content or f'import {module_name}' in content:
        imported.append(module_name)
    else:
        not_imported.append(module_name)

print(f"\n✅ Imported: {len(imported)}")
for m in imported[:10]:
    print(f"  {m}")

print(f"\n❌ NOT Imported: {len(not_imported)}")  
for m in not_imported[:20]:
    print(f"  {m}")
