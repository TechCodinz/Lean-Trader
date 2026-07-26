#!/usr/bin/env python3
"""
Fix position sizing to ensure minimum $5 order size at the FINAL step
"""

print("🔧 Fixing final position size to ensure $5 minimum...")
print()

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the final_size calculation and bounds
# Line 631: final_size = max(min_size, min(final_size, max_size))

# The issue: With $19.46 balance, min_size = 3.0, but Bybit requires $5 minimum
# Fix: Ensure final_size is ALWAYS at least $5.00

old_final_bounds = '''            # Apply final bounds based on balance
            if balance < 100:
                min_size, max_size = 3.0, 20.0
            elif balance < 1000:
                min_size, max_size = 10.0, 100.0
            elif balance < 10000:
                min_size, max_size = 20.0, 500.0  # [OK] For $8K balance!
            else:
                min_size, max_size = 50.0, 2000.0
            
            final_size = max(min_size, min(final_size, max_size))'''

new_final_bounds = '''            # Apply final bounds based on balance
            if balance < 100:
                min_size, max_size = 5.0, 20.0  # FIXED: $5 minimum (Bybit requirement)
            elif balance < 1000:
                min_size, max_size = 5.0, 100.0  # FIXED: $5 minimum
            elif balance < 10000:
                min_size, max_size = 5.0, 500.0  # FIXED: $5 minimum
            else:
                min_size, max_size = 5.0, 2000.0  # FIXED: $5 minimum
            
            final_size = max(min_size, min(final_size, max_size))
            
            # CRITICAL: Ensure absolute $5 minimum (Bybit requirement)
            if final_size < 5.0 and balance >= 5.0:
                # Scale up to meet minimum (use up to 30% of balance if needed)
                final_size = min(5.0, balance * 0.30)
                logger.info(f"     Scaled up to meet $5 minimum: ${final_size:.2f}")
            final_size = max(5.0, final_size)  # Final safety check'''

if old_final_bounds in content:
    print("[OK] Found final bounds calculation")
    content = content.replace(old_final_bounds, new_final_bounds)
    print("   Fixed: All min_size values set to $5.00")
    print("   Added: Absolute $5 minimum check with scaling")
    
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 70)
    print("[OK] FIX APPLIED")
    print("=" * 70)
    print()
    print("Position sizing now:")
    print("  • Minimum: $5.00 (Bybit requirement)")
    print("  • With $19.46: Will use up to 30% = $5.84 if needed")
    print("  • All orders will be at least $5.00")
else:
    print("  Final bounds code not found at expected location")
    print("   Searching for alternative patterns...")
    
    # Try to find the line with final_size = max(min_size
    if 'final_size = max(min_size' in content:
        print("   Found final_size calculation, showing context:")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'final_size = max(min_size' in line:
                print(f"   Line {i+1}: {line.strip()}")
                # Show surrounding lines
                for j in range(max(0, i-5), min(len(lines), i+5)):
                    if j != i:
                        print(f"   Line {j+1}: {lines[j].strip()[:80]}")

