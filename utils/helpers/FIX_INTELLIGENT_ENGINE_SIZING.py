#!/usr/bin/env python3
"""
Fix position sizing in INTELLIGENT_EXECUTION_ENGINE
Make it use 5% of actual balance, not fixed $20
"""

import re

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()

changes_made = 0

# Pattern 1: Look for fixed position_size = 20
if re.search(r'position_size\s*=\s*20(?:\.0+)?\s*(?:#.*)?$', content, re.MULTILINE):
    content = re.sub(
        r'position_size\s*=\s*20(?:\.0+)?\s*(?:#.*)?$',
        '''position_size = max(5.0, balance * 0.05)  # 5% of balance, min $5
        logger.info(f"   💰 Safe position: ${position_size:.2f} (5% of ${balance:.2f})")''',
        content,
        flags=re.MULTILINE
    )
    print("[OK] Fixed position_size = 20 → dynamic 5%")
    changes_made += 1

# Pattern 2: Show all position_size assignments found
pattern = r'position_size\s*=\s*\d+(?:\.\d+)?\s*(?:#.*)?$'
matches = list(re.finditer(pattern, content, re.MULTILINE))
if matches:
    print(f"   Found {len(matches)} position_size assignments")

# Pattern 3: Fix balance display showing $1000
if '(balance: $1000)' in content:
    content = re.sub(
        r'\(balance: \$1000\)',
        '(balance: ${balance:.2f})',
        content
    )
    print("[OK] Fixed balance display in logs")
    changes_made += 1

# Pattern 4: Fix any f-string with hardcoded balance
content = re.sub(
    r'balance:\s*\$1000',
    'balance: ${balance:.2f}',
    content
)

if changes_made > 0:
    # Backup first
    with open('INTELLIGENT_EXECUTION_ENGINE.py.backup', 'w') as f_backup:
        with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f_orig:
            f_backup.write(f_orig.read())
    
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
        f.write(content)
    
    print(f"\n[OK] Made {changes_made} fixes to INTELLIGENT_EXECUTION_ENGINE.py")
    print("   (Backup: INTELLIGENT_EXECUTION_ENGINE.py.backup)")
else:
    print("\n No obvious position sizing found")
    print("   Checking where position_size is set...")
    import subprocess
    result = subprocess.run(
        ['grep', '-n', 'position_size.*=', 'INTELLIGENT_EXECUTION_ENGINE.py'],
        capture_output=True,
        text=True
    )
    if result.stdout:
        print("\n   Position size assignments found:")
        lines = result.stdout.strip().split('\n')[:5]
        for line in lines:
            print(f"   {line[:80]}")

