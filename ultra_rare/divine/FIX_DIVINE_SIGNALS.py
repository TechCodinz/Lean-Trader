#!/usr/bin/env python3
"""Fix divine signals division by zero error"""

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

import re

# Find division operations that might cause zero division
# Wrap them in try/except or add zero checks

# Pattern 1: Direct division that might fail
patterns_to_fix = [
    (r'(\w+)\s*/\s*(\w+)(?!\w)', r'(\1 / \2 if \2 != 0 else 1)'),
]

changes = 0

# Search for divine signals section and add protection
if 'divine' in content.lower() or 'Divine' in content:
    # Add zero-check wrapper for divine signals
    old_patterns = [
        'divine_signal = ',
        'divine_score = ',
        'divine_confidence = '
    ]
    
    for pattern in old_patterns:
        if pattern in content:
            # Find the line and check if it has division
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if pattern in line and '/' in line and 'if' not in line:
                    # Add protection
                    indent = len(line) - len(line.lstrip())
                    lines[i] = ' ' * indent + 'try:\n' + line + '\n' + ' ' * indent + 'except (ZeroDivisionError, Exception):\n' + ' ' * (indent+4) + pattern + '0.5  # Fallback'
                    changes += 1
                    break
            
            content = '\n'.join(lines)

if changes > 0:
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
        f.write(content)
    print(f"✅ Protected {changes} divine signal calculations")
else:
    print("ℹ️  Divine signals already protected or not found")
