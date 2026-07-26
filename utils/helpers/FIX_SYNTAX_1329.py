#!/usr/bin/env python3
"""
Fix the broken line 1329 - remove comment from inside dict
"""

print("🔧 Fixing SyntaxError at line 1329...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 1329 (index 1328)
if len(lines) > 1328:
    original = lines[1328]
    print(f"Broken line 1329:")
    print(f"  {original.rstrip()}")
    print()
    
    # Replace the broken line with correct syntax
    fixed = "                        position = {'side': 'buy', 'entry_price': trade.get('entry_price') or trade.get('entry') or position.get('entry_price'), 'size': trade.get('size', 0)}  # Force buy for spot\n"
    
    lines[1328] = fixed
    
    print(f"Fixed line 1329:")
    print(f"  {fixed.rstrip()}")
    print()
    
    # Also fix lines 1318 and 1322 if they have comments in wrong place
    if len(lines) > 1317:
        if '# Always long for spot' in lines[1317]:
            lines[1317] = "            side = 'buy'\n"
            print("[OK] Fixed line 1318")
    
    if len(lines) > 1321:
        if '# Always long for spot' in lines[1321]:
            lines[1321] = "                side = 'buy'\n"
            print("[OK] Fixed line 1322")
    
    # Write back
    with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print()
    print("=" * 60)
    print("[OK] SYNTAX FIXED!")
    print("=" * 60)
    print()
    print("All trades now forced to 'buy' (long) for correct P&L")

else:
    print("[X] File too short!")

