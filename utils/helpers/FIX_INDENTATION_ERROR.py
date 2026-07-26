#!/usr/bin/env python3
"""
Fix indentation error at line 1268
"""

print("🔧 Fixing indentation error...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find line 1268 (0-indexed is 1267)
if len(lines) > 1267:
    print(f"Line 1268: {lines[1267].rstrip()}")
    print()
    
    # Check indentation
    line = lines[1267]
    indent = len(line) - len(line.lstrip())
    print(f"Current indentation: {indent} spaces")
    
    # Check surrounding lines for context
    print()
    print("Context (lines 1265-1270):")
    for i in range(1264, min(len(lines), 1270)):
        marker = ">>> " if i == 1267 else "    "
        print(f"{marker}{i+1}: {lines[i].rstrip()}")
    
    print()
    
    # Find the correct indentation by looking at the except block
    # The except should be at the same level as the try
    for i in range(1267, max(0, 1267-20), -1):
        if 'except Exception as e:' in lines[i]:
            correct_indent = len(lines[i]) - len(lines[i].lstrip())
            print(f"Found except at line {i+1} with {correct_indent} spaces")
            
            # Fix line 1268 to match
            fixed_line = ' ' * correct_indent + line.lstrip()
            lines[1267] = fixed_line
            
            print(f"Fixed line 1268 indentation to {correct_indent} spaces")
            break
    else:
        # If no except found, check the for loop above
        for i in range(1267, max(0, 1267-30), -1):
            if 'for symbol, position in' in lines[i]:
                correct_indent = len(lines[i]) - len(lines[i].lstrip())
                print(f"Found for loop at line {i+1} with {correct_indent} spaces")
                
                # The logger.debug should be indented one level more than the for
                fixed_line = ' ' * (correct_indent + 4) + line.lstrip()
                lines[1267] = fixed_line
                
                print(f"Fixed line 1268 indentation to {correct_indent + 4} spaces")
                break
    
    # Write back
    with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print()
    print("=" * 70)
    print("[OK] FIX APPLIED")
    print("=" * 70)
else:
    print("[X] File doesn't have 1268 lines")

