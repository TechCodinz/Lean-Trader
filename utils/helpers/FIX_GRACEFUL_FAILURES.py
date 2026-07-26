#!/usr/bin/env python3
"""Wrap all optional feature initializations in try/except"""

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

# Features that should be optional
optional_features = [
    'quantum_predictor',
    'divine_signal',
    'consciousness',
    'harmony',
    'intuition',
    'cns'
]

new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this line initializes an optional feature
    is_optional_init = False
    for feature in optional_features:
        if feature in line.lower() and ('=' in line or 'initialize' in line.lower()):
            is_optional_init = True
            break
    
    if is_optional_init and 'try:' not in lines[i-1] if i > 0 else False:
        # Wrap in try/except if not already wrapped
        indent = len(line) - len(line.lstrip())
        
        new_lines.append(' ' * indent + 'try:\n')
        new_lines.append(line)
        new_lines.append(' ' * indent + 'except Exception as e:\n')
        new_lines.append(' ' * indent + f'    pass  # Optional feature\n')
    else:
        new_lines.append(line)
    
    i += 1

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.writelines(new_lines)

print("[OK] Wrapped optional features in try/except blocks")
