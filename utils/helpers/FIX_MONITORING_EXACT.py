#!/usr/bin/env python3
"""
Find and fix the exact monitoring line with flexible matching
"""

print("🔧 Finding exact monitoring line...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find the line with monitor_positions and timeout
found = False
for i, line in enumerate(lines):
    if 'monitor_positions()' in line and 'timeout' in line:
        print(f"[OK] Found at line {i+1}:")
        print(f"   {line.rstrip()}")
        print()
        
        # Replace with version without timeout
        # Keep indentation
        indent = len(line) - len(line.lstrip())
        indent_str = ' ' * indent
        
        # New line without timeout
        new_line = f"{indent_str}await self.monitor_positions()  # No timeout - let it run fully\n"
        
        lines[i] = new_line
        print(f"   Replaced with: {new_line.rstrip()}")
        found = True
        
        # Also remove the timeout exception handler
        # Look for except asyncio.TimeoutError in next few lines
        for j in range(i+1, min(len(lines), i+10)):
            if 'except asyncio.TimeoutError' in lines[j]:
                print(f"   Found timeout handler at line {j+1}")
                # Remove this line and the warning line
                lines[j] = ''  # Remove exception handler
                if j+1 < len(lines) and 'timed out' in lines[j+1]:
                    lines[j+1] = ''  # Remove warning
                    print(f"   Removed timeout warning at line {j+2}")
                break
        
        break

if found:
    # Write back
    with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print()
    print("=" * 70)
    print("[OK] SUCCESS! Timeout removed")
    print("=" * 70)
else:
    print("  Could not find timeout line")
    print()
    print("Searching for monitor_positions calls...")
    for i, line in enumerate(lines):
        if 'monitor_positions' in line:
            print(f"Line {i+1}: {line.rstrip()[:80]}")

