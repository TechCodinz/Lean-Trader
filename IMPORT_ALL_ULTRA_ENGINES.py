#!/usr/bin/env python3
"""Generate imports for all ultra engines"""

import os

ultra_files = [f for f in os.listdir('.') if f.endswith('.py') and 
               any(x in f.upper() for x in ['ULTRA', 'QUANTUM', 'DIVINE'])]

print("# Add these imports to COMPLETE_ULTIMATE_ORCHESTRATOR.py:\n")
print("# ULTRA/QUANTUM/DIVINE ENGINES")

for f in sorted(ultra_files):
    module = f.replace('.py', '')
    # Skip test files
    if 'test' in module.lower() or 'smoke' in module.lower():
        continue
    
    # Try to find main class
    try:
        with open(f, 'r') as file:
            content = file.read()
            # Find class definitions
            classes = []
            for line in content.split('\n'):
                if line.startswith('class ') and ('Ultra' in line or 'Quantum' in line or 'Divine' in line):
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    classes.append(class_name)
            
            if classes:
                main_class = classes[0]  # Use first class
                print(f"try:")
                print(f"    from {module} import {main_class}")
                print(f"    {module.upper()}_AVAILABLE = True")
                print(f"except:")
                print(f"    {module.upper()}_AVAILABLE = False")
                print()
    except:
        continue

print("\n# Then in initialize_all_systems(), add initialization for each")
