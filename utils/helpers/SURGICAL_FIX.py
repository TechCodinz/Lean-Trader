#!/usr/bin/env python3
"""
SURGICAL FIX for entry price calculation

Found the bug at lines 1316-1336!
Bot using order response (wrong on testnet)
Need to fetch market price BEFORE order instead!
"""

print("="*70)
print("🔧 SURGICAL FIX - Entry Price Calculation")
print("="*70)
print()

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        lines = f.readlines()
    
    print(f"Total lines in file: {len(lines)}")
    print()
    
    # Find the section to replace (around line 1316-1336)
    # Look for "actual_price = None" followed by the fallback logic
    
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if 'actual_price = None' in line and start_idx is None:
            start_idx = i
        if start_idx and 'Final entry_price' in line and end_idx is None:
            end_idx = i + 1  # Include this line
            break
    
    if start_idx and end_idx:
        print(f"Found section: lines {start_idx+1} to {end_idx}")
        print()
        print("OLD CODE:")
        print("-" * 70)
        for i in range(start_idx, end_idx):
            print(f"{i+1:4d}: {lines[i].rstrip()}")
        print()
        
        # Create NEW code
        indent = "            "  # Match existing indentation
        new_code = f'''{indent}# 🔧 FIX: Fetch CURRENT market price BEFORE using order response!
{indent}actual_price = None
{indent}
{indent}# Try to get current market price (most accurate!)
{indent}try:
{indent}    ticker = exchange.fetch_ticker(symbol)
{indent}    market_price = ticker.get('last') or ticker.get('close')
{indent}    if market_price:
{indent}        actual_price = market_price
{indent}        logger.info(f"   💰 Using CURRENT market price: ${{actual_price:.6f}}")
{indent}except Exception as e:
{indent}    logger.warning(f"    Could not fetch market price: {{e}}")
{indent}
{indent}# Fallback: Use order response if market fetch failed
{indent}if actual_price is None:
{indent}    if order.get('average'):
{indent}        actual_price = order.get('average')
{indent}        logger.info(f"   💡 Using order.average: ${{actual_price:.6f}}")
{indent}    elif order.get('price'):
{indent}        actual_price = order.get('price')
{indent}        logger.info(f"   💡 Using order.price: ${{actual_price:.6f}}")
{indent}    elif order.get('cost') and order.get('filled') and order.get('filled') > 0:
{indent}        actual_price = order.get('cost') / order.get('filled')
{indent}        logger.info(f"   💡 Calculated from cost/filled: ${{actual_price:.6f}}")
{indent}    else:
{indent}        actual_price = entry_price
{indent}        logger.warning(f"    Using fallback entry_price: ${{actual_price:.6f}}")
{indent}
{indent}logger.info(f"   [OK] Final entry_price: ${{actual_price:.6f}}")
'''
        
        # Replace the section
        new_lines = lines[:start_idx] + [new_code] + lines[end_idx:]
        
        # Write back
        with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
            f.writelines(new_lines)
        
        print("NEW CODE:")
        print("-" * 70)
        for line in new_code.split('\n')[:30]:  # Show first 30 lines
            print(line)
        print()
        
        print("="*70)
        print("[OK] SURGICAL FIX APPLIED!")
        print("="*70)
        print()
        print("Changes:")
        print("  ✓ Now fetches CURRENT market price first")
        print("  ✓ Only uses order response as fallback")
        print("  ✓ Entry prices will match reality!")
        print()
        print("Expected result:")
        print("  • ETH entry: ~$2,700 (not $3,140!)")
        print("  • BTC entry: ~$82,000 (not $79,000!)")
        print("  • TRUE P&L visible!")
        print()
        
    else:
        print("[X] Could not locate exact section!")
        print(f"   start_idx: {start_idx}")
        print(f"   end_idx: {end_idx}")

except Exception as e:
    print(f"[X] Error: {e}")
    import traceback
    traceback.print_exc()

print("="*70)

