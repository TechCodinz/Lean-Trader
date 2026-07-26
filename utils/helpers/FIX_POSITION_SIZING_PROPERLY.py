#!/usr/bin/env python3
"""
Replace fixed base_size tiers with intelligent adaptive sizing + logging
"""

print("🔧 Replacing position sizing code...")
print()

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the section with base_size calculations (lines 534-542)
# We need to replace the entire if/elif block with intelligent adaptive sizing

import re

# Pattern to find the base_size block
pattern = r'(\s+)(if balance < 100:.*?base_size = max\([^)]+\).*?)(elif balance < 500:.*?base_size = max\([^)]+\).*?)(elif balance < 1000:.*?base_size = max\([^)]+\).*?)(else:.*?base_size = max\([^)]+\))'

# Check if the old code exists
if 'base_size = max(5.0, balance * 0.08)' in content:
    print("[OK] Found old base_size tier system")
    print()
    
    # Get the line with first base_size
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if i >= 533 and 'if balance < 100:' in line:
            print(f"[OK] Found tier system at line {i+1}")
            
            # Get indentation from the if statement
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Find the end of the tier block (line 542)
            end_line = i
            for j in range(i, min(len(lines), i+15)):
                if 'else:' in lines[j] and 'base_size' in lines[j+1]:
                    end_line = j + 1
                    break
            
            print(f"   Block ends at line {end_line+1}")
            print()
            
            # Create new intelligent adaptive code
            new_code = f'''{indent_str}# Intelligent adaptive sizing: 2-5% of balance based on confidence
{indent_str}confidence = signal.get("confidence", 0.6) if isinstance(signal, dict) else 0.6
{indent_str}size_pct = min(0.05, max(0.02, confidence * 0.08))  # 2-5% based on confidence
{indent_str}base_size = max(5.0, balance * size_pct) if balance > 0 else 10.0
{indent_str}self.logger.info(f"📊 Position size: ${{base_size:.2f}} ({{size_pct*100:.1f}}% of ${{balance:.2f}})")'''
            
            # Replace lines i through end_line with new code
            new_lines = lines[:i] + [new_code] + lines[end_line+1:]
            
            content = '\n'.join(new_lines)
            
            print("[OK] Replaced with intelligent adaptive sizing!")
            print()
            print("New code:")
            print(new_code)
            print()
            
            break
    
    # Write the updated content
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("=" * 70)
    print("[OK] SUCCESS! Position sizing fixed")
    print("=" * 70)
    print()
    print("Changes:")
    print("  ✓ Removed fixed tier system (< 100, < 500, < 1000, else)")
    print("  ✓ Added confidence-based adaptive sizing (2-5%)")
    print("  ✓ Added position size logging")
    print()
    
else:
    print("  Could not find expected base_size code")
    print()

