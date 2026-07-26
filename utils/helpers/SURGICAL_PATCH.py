
import sys
import re

print("Starting analysis...")
target = '/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py'

with open(target, 'r') as f:
    lines = f.readlines()

modified = False

# 1. Add Import (if missing)
if not any('SAFE_EXECUTION_WRAPPER' in line for line in lines[:20]):
    print("Injecting import statement...")
    lines.insert(2, "from SAFE_EXECUTION_WRAPPER import get_safe_executor\n")
    modified = True
else:
    print("Import already present")

# 2. Add Execution Hook
# Looking for: logger.info(f"[OK] Published {len(scalp_signals)} signals to data hub")
found_hook = False
for i, line in enumerate(lines):
    if 'Published' in line and 'signals to data hub' in line and 'logger.info' in line:
        print(f"Found insertion point at line {i+1}")
        
        # Check if already patched
        if i+1 < len(lines) and 'get_safe_executor' in lines[i+1]:
            print("Already patched!")
            found_hook = True
            break
            
        # Get indentation
        indent = len(line) - len(line.lstrip())
        padding = ' ' * indent
        
        # Create hook code
        hook = []
        hook.append(f"{padding}# SURGICAL INJECTION: Execute signals on bridge\n")
        hook.append(f"{padding}try:\n")
        hook.append(f"{padding}    if 'scalp_signals' in locals() and scalp_signals:\n")
        hook.append(f"{padding}        get_safe_executor()(self, scalp_signals)\n")
        hook.append(f"{padding}except Exception as e:\n")
        hook.append(f"{padding}    print(f'Bridge Error: {{e}}')\n")
        
        # Insert
        for code_line in reversed(hook):
            lines.insert(i+1, code_line)
        
        modified = True
        found_hook = True
        print("Hook injected successfully")
        break

if not found_hook:
    print("ERROR: Could not find insertion point!")

if modified:
    print("Writing changes...")
    with open(target, 'w') as f:
        f.writelines(lines)
    print("File saved.")
else:
    print("No changes needed.")

