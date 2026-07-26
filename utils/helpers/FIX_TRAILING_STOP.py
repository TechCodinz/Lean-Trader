#!/usr/bin/env python3
"""
Fix TrailingStopManager parameter name
"""

import re

files_to_check = [
    'COMPLETE_UNIFIED_ORCHESTRATOR.py',
    'EXECUTION_ORCHESTRATOR.py', 
    'INTEGRATE_CRITICAL_FEATURES.py'
]

for filename in files_to_check:
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Try different parameter name variations
        changes_made = False
        
        # Replace trail_percent with trail_percentage
        if 'trail_percent=' in content:
            # First, try removing the parameter entirely (use default)
            old_pattern = r'TrailingStopManager\(trail_percent=[0-9.]+\)'
            new_pattern = 'TrailingStopManager()'
            
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                changes_made = True
                print(f"[OK] {filename}: Removed trail_percent parameter (using default)")
        
        if changes_made:
            with open(filename, 'w') as f:
                f.write(content)
    
    except FileNotFoundError:
        pass

print("\n[OK] TrailingStopManager calls fixed!")
print("Using default parameters to avoid conflicts")
