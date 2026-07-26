
import sys
target = '/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py'

with open(target, 'r') as f:
    lines = f.readlines()

modified = False

for i, line in enumerate(lines):
    # Match EXACTLY the scalp signal line
    if 'Published' in line and 'scalp_signals' in line and 'signals to data hub' in line:
        print(f"Found scalp signal line at {i+1}")
        
        # Check if already patched
        if i+1 < len(lines) and 'get_safe_executor' in lines[i+1]:
            print("Already patched!")
            break
            
        indent = len(line) - len(line.lstrip())
        padding = ' ' * indent
        
        hook = []
        hook.append(f"{padding}# SURGICAL INJECTION 2.0: Execute SCALP signals\n")
        hook.append(f"{padding}try:\n")
        hook.append(f"{padding}    if 'scalp_signals' in locals() and scalp_signals:\n")
        hook.append(f"{padding}        get_safe_executor()(self, scalp_signals)\n")
        hook.append(f"{padding}except Exception as e:\n")
        hook.append(f"{padding}    print(f'Bridge Error 2.0: {{e}}')\n")
        
        for code_line in reversed(hook):
            lines.insert(i+1, code_line)
        
        modified = True
        print("Hook injected")
        break

if modified:
    with open(target, 'w') as f:
        f.writelines(lines)
    print("Saved.")
else:
    print("No correct target found or already patched.")
