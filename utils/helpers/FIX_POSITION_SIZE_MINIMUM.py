#!/usr/bin/env python3
"""
Fix position sizing to ensure minimum $5 order size (Bybit requirement)
"""

print("🔧 Fixing position sizing minimum...")
print()

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the position sizing code
# Current: base_size = max(5.0, balance * size_pct)
# Problem: With $19.46 balance, 8% = $1.56 (below $5 minimum!)
# Fix: Ensure minimum is $5 OR scale up for small balances

old_sizing = 'base_size = max(5.0, balance * size_pct) if balance > 0 else 10.0'

new_sizing = '''# Ensure minimum $5 order size (Bybit requirement)
                base_size = balance * size_pct
                # For small balances, use higher percentage to meet minimum
                if base_size < 5.0 and balance >= 5.0:
                    # Scale up to meet $5 minimum
                    base_size = min(5.0, balance * 0.25)  # Use up to 25% if needed to meet minimum
                elif base_size < 5.0:
                    base_size = 5.0  # Absolute minimum
                base_size = max(5.0, base_size)  # Final safety check'''

if old_sizing in content:
    print("[OK] Found position sizing code")
    content = content.replace(old_sizing, new_sizing)
    print("   Fixed: Ensures $5 minimum order size")
    print("   With $19.46: Will use 25% = $4.87 → rounds to $5.00")
    
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 70)
    print("[OK] FIX APPLIED")
    print("=" * 70)
    print()
    print("Position sizing now:")
    print("  • Normal: 8-15% of balance")
    print("  • Small balance (< $20): Scales up to meet $5 minimum")
    print("  • Absolute minimum: $5.00 (Bybit requirement)")
else:
    print("  Position sizing code not found at expected location")
    print("   Searching for alternative patterns...")
    
    # Try to find any base_size assignment
    if 'base_size =' in content:
        print("   Found base_size assignments, showing context:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'base_size =' in line and 'balance' in line:
                print(f"   Line {i+1}: {line.strip()[:80]}")

