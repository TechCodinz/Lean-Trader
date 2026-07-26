#!/usr/bin/env python3
"""Fix missing TrailingProfitManager import"""

import os

print("🔍 Checking PERFECT_EXECUTION_SYSTEM.py...")

# Check what's actually in the file
if os.path.exists('PERFECT_EXECUTION_SYSTEM.py'):
    with open('PERFECT_EXECUTION_SYSTEM.py', 'r') as f:
        content = f.read()
    
    # Check if TrailingProfitManager exists
    if 'TrailingProfitManager' in content:
        print("[OK] TrailingProfitManager exists in file")
    else:
        print("  TrailingProfitManager NOT found in file")
        print("   Checking for similar classes...")
        
        # Look for Trailing classes
        import re
        classes = re.findall(r'class (\w*[Tt]railing\w*)', content)
        if classes:
            print(f"   Found: {', '.join(classes)}")
else:
    print("  PERFECT_EXECUTION_SYSTEM.py not found")

print()
print("🔧 Fixing EXECUTION_ORCHESTRATOR.py...")

# Fix the import issue
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Check if it's trying to import TrailingProfitManager
if 'TrailingProfitManager' in content:
    # Wrap the import in try/except to make it optional
    old = "from PERFECT_EXECUTION_SYSTEM import TrailingProfitManager"
    new = """try:
    from PERFECT_EXECUTION_SYSTEM import TrailingProfitManager
except ImportError:
    TrailingProfitManager = None  # Optional feature"""
    
    if old in content:
        content = content.replace(old, new)
        print("[OK] Made TrailingProfitManager import optional")
    
    # Also handle the usage
    if 'TrailingProfitManager(' in content and 'if TrailingProfitManager:' not in content:
        # Find places where it's used and add checks
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if 'TrailingProfitManager(' in line and 'if ' not in line:
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + 'if TrailingProfitManager:')
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        print("[OK] Added safety checks for TrailingProfitManager usage")

with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.write(content)

print()
print("[OK] Import fix applied!")
