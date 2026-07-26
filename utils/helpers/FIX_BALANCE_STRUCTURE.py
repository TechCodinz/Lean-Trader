#!/usr/bin/env python3
"""
Fix balance checking to handle Bybit's actual structure
"""

print("🔧 Fixing balance structure handling...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the spot checking code
old_balance_code = '''# Check all currencies in balance
            for currency, amounts in balance.items():
                if currency in ['info', 'free', 'used', 'total']:
                    continue
                
                if isinstance(amounts, dict):
                    total = amounts.get('total', 0)
                else:
                    total = float(amounts) if amounts else 0
                
                # If we have BTC (or other crypto) holdings, it's an open spot position
                if currency != 'USDT' and total > 0.0001:  # Minimum threshold'''

new_balance_code = '''# Check all currencies in balance (Bybit structure: balance['BTC'] = {'free': X, 'total': Y})
            for currency, amounts in balance.items():
                # Skip metadata keys
                if currency in ['info', 'free', 'used', 'total', 'timestamp', 'datetime']:
                    continue
                
                # Bybit returns: balance['BTC'] = {'free': 0.001, 'total': 0.001, 'used': 0}
                if isinstance(amounts, dict):
                    total = amounts.get('total', amounts.get('free', 0))
                    free = amounts.get('free', 0)
                else:
                    total = float(amounts) if amounts else 0
                    free = total
                
                # If we have BTC (or other crypto) holdings, it's an open spot position
                if currency != 'USDT' and total > 0.0001:  # Minimum threshold'''

if old_balance_code in content:
    print("[OK] Found balance checking code")
    content = content.replace(old_balance_code, new_balance_code)
    print("   Fixed balance structure handling")
    
    # Also add better logging
    if 'logger.info(f"[OK] Found spot position:' in content:
        # Make logging more verbose
        content = content.replace(
            'logger.info(f"[OK] Found spot position:',
            'logger.warning(f"[OK] Found spot position:'  # Use warning level so it shows up'
        )
        print("   Enhanced logging level")
    
    with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 70)
    print("[OK] FIX APPLIED")
    print("=" * 70)
    print()
    print("Now handles Bybit balance structure correctly:")
    print("  balance['BTC'] = {'free': X, 'total': Y, 'used': Z}")
    print()
    print("BTC position should now be detected!")
else:
    print("  Balance code not found - might already be fixed")

