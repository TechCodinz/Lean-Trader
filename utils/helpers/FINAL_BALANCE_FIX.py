#!/usr/bin/env python3
"""
After fetching balance, we need to UPDATE self.actual_balance
Currently it's fetched into 'balance' variable but self.actual_balance stays at 100
"""

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    lines = f.readlines()

# Find line 481: logger.info(f"   💰 Got exchange balance: ${balance:.2f}")
# After this line, add: self.actual_balance = balance

for i, line in enumerate(lines):
    if 'Got exchange balance:' in line and i == 480:  # Line 481 (index 480)
        print(f"Found balance fetch log at line {i+1}")
        
        # Check if next line already has self.actual_balance = balance
        if i+1 < len(lines) and 'self.actual_balance = balance' not in lines[i+1]:
            # Get indentation from current line
            indent = len(line) - len(line.lstrip())
            spaces = ' ' * indent
            
            # Insert new line after current line
            new_line = f'{spaces}self.actual_balance = balance  # 🔧 FIX: Update stored balance\n'
            lines.insert(i+1, new_line)
            
            print(f"[OK] Added self.actual_balance = balance after line {i+1}")
            
            # Write back
            with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
                f.writelines(lines)
            
            print("[OK] File updated successfully!")
            break
        else:
            print(" Fix already applied or different structure")
            break

