#!/usr/bin/env python3
"""
Fix position sizing properly (corrected version)
Previous failed due to f-string error
"""

import re

print("="*70)
print("🔧 FIXING POSITION SIZING (CORRECTED)")
print("="*70)
print()

try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    # Find the complex position_size calculation
    if 'position_size = (base_risk' in content:
        print("Found complex position sizing")
        print()
        
        # Replace entire complex calculation with simple safe version
        old_code = '''position_size = (base_risk / stop_loss_pct) * kelly_fraction * volatility_adjustment * confidence_adjustment'''
        
        new_code = '''# 🎯 SAFE POSITION SIZING (5% of balance)
        base_pct = 0.05  # 5% of balance (SAFE!)
        position_size = max(5, balance * base_pct)
        
        # Hard cap at 10% maximum (safety)
        max_pos = balance * 0.10
        if position_size > max_pos:
            position_size = max_pos
            logger.warning(f"    Capping at 10%: ${max_pos:.2f}")
        
        logger.info(f"   💰 Safe position: ${position_size:.2f} ({position_size/balance*100:.1f}% of ${balance:.2f})")'''
        
        content = content.replace(old_code, new_code)
        
        with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
            f.write(content)
        
        print("[OK] Position sizing fixed!")
        print()
        print("New sizing:")
        print("  • 5% of balance per trade")
        print("  • Minimum $5")
        print("  • Maximum 10% cap")
        print("  • Safe and dynamic")
    else:
        print(" Could not find position sizing code")
        print("   Checking for alternative patterns...")
        
        # Try to find any position_size assignment
        matches = re.finditer(r'position_size\s*=\s*[^\n]+', content)
        for match in matches:
            print(f"   Found: {match.group()[:80]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)

