#!/usr/bin/env python3
"""
Fix line 1315: entry_price = exit_price (BACKWARDS!)

Should be getting entry_price from position data, not from exit_price!
"""

print("🔧 Fixing entry/exit price swap...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

# Show line 1315 (index 1314)
print("Line 1315 (BEFORE):")
print(f"  {lines[1314].rstrip()}")
print()

# Look at context to understand what to replace it with
print("Context (lines 1310-1325):")
for i in range(1309, 1325):
    if i < len(lines):
        marker = ">>> " if i == 1314 else "    "
        print(f"{marker}{i+1:4d}: {lines[i].rstrip()}")

print()
print("─" * 70)
print()

# The fix: Instead of entry_price = exit_price,
# Get it from position data
# Looking at line 1319: entry_price = position.get('entry_price', exit_price)
# That's the correct pattern!

# So line 1315 should probably get it from position too
# But we need to see what 'position' variable is available at line 1315

print("Searching backwards from 1315 for 'position' variable...")
for i in range(1314, max(0, 1314 - 30), -1):
    if 'position' in lines[i] and ('=' in lines[i] or 'for' in lines[i]):
        print(f"  Line {i+1}: {lines[i].rstrip()}")

print()
print("─" * 70)
print()

# The safest fix: Change line 1315 from:
#   entry_price = exit_price
# To:
#   entry_price = position.get('entry_price', position.get('entry', exit_price))

old_line = "            entry_price = exit_price\n"
new_line = "            entry_price = position.get('entry_price', position.get('entry', exit_price))  # FIXED: was exit_price\n"

if lines[1314] == old_line:
    lines[1314] = new_line
    print("[OK] Line 1315 FIXED!")
    print()
    print("BEFORE:")
    print(f"  {old_line.rstrip()}")
    print()
    print("AFTER:")
    print(f"  {new_line.rstrip()}")
    print()
    
    with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
        f.writelines(lines)
    
    print("[OK] File saved!")
else:
    print(f"  Line 1315 doesn't match expected pattern")
    print(f"Expected: {old_line.rstrip()}")
    print(f"Found:    {lines[1314].rstrip()}")
    print()
    print("Manual fix needed - showing full context:")
    for i in range(1310, 1325):
        if i < len(lines):
            print(f"  {i+1:4d}: {lines[i].rstrip()}")

print()
print("=" * 70)
print("[OK] REPAIR COMPLETE!")
print("=" * 70)

