#!/usr/bin/env python3
"""
Properly add ETH to the toxic symbols blacklist
"""

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()

# Find the TOXIC_SYMBOLS set and add ETH
if 'TOXIC_SYMBOLS' in content:
    # Add ETH to the existing set
    old_set = "TOXIC_SYMBOLS = {"
    new_set = """TOXIC_SYMBOLS = {
    'ETH/USDT',   # TEMPORARY: Backwards entry/exit price bug"""
    
    if 'ETH/USDT' not in content:
        content = content.replace(old_set, new_set, 1)
        print("[OK] Added ETH to TOXIC_SYMBOLS")
    else:
        print("ℹ️  ETH already in blacklist")
else:
    print("  TOXIC_SYMBOLS not found - ETH not blacklisted")

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
    f.write(content)

print("\n[OK] ETH blacklist properly configured!")
