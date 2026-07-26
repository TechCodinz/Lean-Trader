#!/usr/bin/env python3
"""
Insert the missing intelligent adaptive position sizing code
"""

import re

print("🔧 Inserting position sizing code...")
print()

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

original_content = content

# Find where position_size is calculated
lines = content.split('\n')

# Look for balance fetching (this is where we need to add sizing)
for i, line in enumerate(lines):
    if 'balance = ' in line and 'fetch_balance' in lines[max(0, i-3):i+3]:
        print(f"[OK] Found balance fetch at line {i+1}")
        
        # Look ahead for position_size calculation
        for j in range(i, min(len(lines), i+50)):
            if 'position_size' in lines[j].lower() and '=' in lines[j]:
                print(f"[OK] Found position_size at line {j+1}: {lines[j].strip()}")
                
                # Get indentation
                indent = len(lines[j]) - len(lines[j].lstrip())
                indent_str = ' ' * indent
                
                # Create new sizing code
                new_code = f'''{indent_str}# Intelligent adaptive sizing: 2-5% of balance
{indent_str}confidence = signal.get("confidence", 0.6) if isinstance(signal, dict) else 0.6
{indent_str}size_pct = min(0.05, max(0.02, confidence * 0.08))  # 2-5% based on confidence
{indent_str}position_size = max(5.0, balance * size_pct) if balance > 0 else 10.0
{indent_str}logger.info(f"📊 Position size: ${{position_size:.2f}} ({{size_pct*100:.1f}}% of ${{balance:.2f}})")'''
                
                # Replace the line
                lines[j] = new_code
                
                content = '\n'.join(lines)
                
                print()
                print("[OK] Inserted intelligent sizing code!")
                print()
                print("New code:")
                print(new_code)
                
                break
        break

if content != original_content:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 70)
    print("[OK] SUCCESS! Position sizing restored")
    print("=" * 70)
    print()
    print("Changes:")
    print("  ✓ Intelligent adaptive sizing (2-5% of balance)")
    print("  ✓ Confidence-based adjustment")
    print("  ✓ Position size logging")
    print()
else:
    print()
    print("[X] Could not find position_size assignment")
    print()
    print("Showing all 'balance' and 'position' references for manual fix:")
    for i, line in enumerate(lines):
        if ('balance' in line.lower() or 'position' in line.lower()) and '=' in line:
            print(f"  Line {i+1}: {line.strip()[:80]}")

