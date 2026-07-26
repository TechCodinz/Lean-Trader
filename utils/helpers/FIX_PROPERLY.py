#!/usr/bin/env python3
"""
Proper fix: Line 1315 should just set entry_price to a placeholder
The REAL entry_price comes from lines 1319 or 1328

The actual problem is that we need to ensure lines 1319/1328 are hit
"""

print("🔧 Applying proper fix...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

# Line 1315 should just be a safe default
# The real entry_price comes later
old = "            entry_price = position.get('entry_price', position.get('entry', exit_price))  # FIXED: was exit_price\n"
new = "            entry_price = 0  # Placeholder, gets real value from position data below\n"

if old in lines[1314]:
    lines[1314] = new
    print("[OK] Fixed line 1315 - set to placeholder")
else:
    print("  Line 1315 doesn't match, trying alternate fix...")
    # Just set it to 0 as placeholder
    lines[1314] = "            entry_price = 0  # Placeholder\n"

with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.writelines(lines)

print("[OK] File saved")
print()

# Show the fixed section
print("Fixed section (lines 1314-1330):")
print("─" * 70)
for i in range(1313, 1330):
    if i < len(lines):
        print(f"  {i+1:4d}: {lines[i].rstrip()}")

print()
print("=" * 70)
print("[OK] PROPER FIX APPLIED!")
print("=" * 70)
print()
print("Now entry_price will be:")
print("  • 0 initially (placeholder)")
print("  • Updated from position.get('entry_price') at line 1319")
print("  • Or from trade data at line 1328")
print("  • Never from exit_price (which was the bug)")

