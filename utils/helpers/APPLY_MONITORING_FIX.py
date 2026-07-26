#!/usr/bin/env python3
"""
Remove the 3-second timeout that kills position monitoring
"""

print("🔧 Removing timeout wrapper from monitor_positions()...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find and replace the timeout wrapper
old_code = 'await asyncio.wait_for(self.monitor_positions(), timeout=3.0)'
new_code = 'await self.monitor_positions()  # No timeout - let it run fully'

if old_code in content:
    print("[OK] Found timeout wrapper")
    print()
    print("OLD:", old_code)
    print("NEW:", new_code)
    print()
    
    content = content.replace(old_code, new_code)
    
    # Also remove the timeout exception handler since we don't need it
    lines = content.split('\n')
    new_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if 'except asyncio.TimeoutError:' in line:
            # Skip this line and the next one
            skip_next = True
            print(f"Removing timeout handler at line {i+1}")
            continue
        
        if skip_next:
            if 'logger.warning' in line and 'timed out' in line:
                print(f"Removing warning at line {i+1}")
                skip_next = False
                continue
            else:
                skip_next = False
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 70)
    print("[OK] SUCCESS! Monitoring will now run continuously")
    print("=" * 70)
    print()
    print("Changes:")
    print("  ✓ Removed 3-second timeout")
    print("  ✓ Removed timeout exception handler")
    print("  ✓ monitor_positions() will run fully each iteration")
    print()
else:
    print("  Timeout wrapper not found - may have been fixed already")

