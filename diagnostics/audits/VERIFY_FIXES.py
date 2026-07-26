#!/usr/bin/env python3
import sys

print("Checking INTELLIGENT_EXECUTION_ENGINE.py...")
with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()
    
if 'TOXIC_SYMBOLS' in content:
    print("  ✅ Toxic symbols blacklist present")
else:
    print("  ❌ Toxic symbols blacklist MISSING!")
    sys.exit(1)

print("\nChecking EXECUTION_ORCHESTRATOR.py...")
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()
    
if 'base_pct = 0.05' in content:
    print("  ✅ Safe 5% position sizing present")
else:
    print("  ❌ Safe position sizing MISSING!")
    # Show what's there
    import re
    matches = list(re.finditer(r'position_size\s*=.*', content))
    if matches:
        print("\n  Current position sizing code:")
        for match in matches[:3]:
            print(f"    {match.group()[:80]}")
    sys.exit(1)

print("\n✅ All fixes verified in code!")
