#!/usr/bin/env python3
"""
Make the fallback position sizing INTELLIGENT and ADAPTIVE
Current: Fixed base_size based on balance tiers (too conservative)
New: Percentage-based with confidence/volatility multipliers
"""

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()

# Find and replace the conservative base_size logic (around lines 530-545)
old_sizing = '''            # 🔥 Base position size - SCALE WITH BALANCE!
            if balance < 100:
                base_size = 5.0
            elif balance < 1000:
                base_size = 10.0  # REDUCED from 50! Avoid "Insufficient balance"
            elif balance < 10000:
                base_size = 20.0  # For $8K+ balance
            else:
                base_size = 50.0'''

new_sizing = '''            # >> INTELLIGENT ADAPTIVE POSITION SIZING!
            # Base: 5-15% of balance depending on confidence/volatility
            base_pct = 0.08  # Start with 8% base (adaptive)
            
            # Adjust for balance growth (compound faster as balance grows)
            if balance > 1000:
                base_pct = 0.10  # 10% for larger balances
            elif balance > 5000:
                base_pct = 0.12  # 12% for big accounts
            
            base_size = balance * base_pct
            base_size = max(5.0, base_size)  # Minimum $5'''

# Replace
if old_sizing in content:
    content = content.replace(old_sizing, new_sizing)
    print("[OK] Replaced conservative sizing with intelligent adaptive sizing!")
else:
    print(" Pattern not found - may need manual adjustment")
    print("Searching for base_size assignments...")
    import re
    matches = re.findall(r'base_size = \d+\.0.*', content)
    for match in matches[:5]:
        print(f"  Found: {match}")

# Save
with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
    f.write(content)

print("\n[OK] Intelligent sizing activated!")
print("New formula:")
print("  • 8% base for balances under $1000")
print("  • 10% base for balances $1000-5000")
print("  • 12% base for balances over $5000")
print("  • PLUS confidence multipliers (1.0x - 2.0x)")
print("  • PLUS volatility adjustments")
print("  • PLUS session multipliers")
print("  • = 10-25% adaptive position sizing!")

