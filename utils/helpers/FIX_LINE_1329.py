#!/usr/bin/env python3
"""
Fix the entry/exit swap at line 1329
Remove dangerous fallback: trade.get('entry_price', exit_price)
"""

print("🔧 Fixing line 1329 in EXECUTION_ORCHESTRATOR.py...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 1329 (index 1328)
if len(lines) > 1329:
    original_line = lines[1328]
    print(f"Original line 1329:")
    print(f"  {original_line.rstrip()}")
    print()
    
    # Replace the dangerous fallback
    if "trade.get('entry_price', exit_price)" in original_line:
        # Change fallback from exit_price to None, then check
        fixed_line = original_line.replace(
            "trade.get('entry_price', exit_price)",
            "trade.get('entry_price') or trade.get('entry') or position.get('entry_price')"
        )
        
        lines[1328] = fixed_line
        
        print(f"Fixed line 1329:")
        print(f"  {fixed_line.rstrip()}")
        print()
        print("[OK] Removed dangerous exit_price fallback!")
        
        # Write back
        with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print()
        print("=" * 60)
        print("[OK] FIX APPLIED!")
        print("=" * 60)
        print()
        print("Now entry_price will use:")
        print("  1. trade.get('entry_price') - primary source")
        print("  2. trade.get('entry') - alternative key")
        print("  3. position.get('entry_price') - from risk manager")
        print()
        print("NO MORE exit_price fallback = NO MORE SWAPS!")
        
    else:
        print("  Line 1329 doesn't match expected pattern")
        print("   Maybe already fixed?")
else:
    print("[X] File has fewer than 1329 lines!")

