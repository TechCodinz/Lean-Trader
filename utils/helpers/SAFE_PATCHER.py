#!/usr/bin/env python3
import sys
import os

target_file = '/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py'
backup_file = target_file + '.backup_safe'

# Backup if not exists
if not os.path.exists(backup_file):
    os.system(f'cp {target_file} {backup_file}')
    print("Backup created")

with open(target_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Define the integration block
integration_lines = [
    "# Bybit Testnet Execution Bridge Integration",
    "try:",
    "    from BYBIT_EXECUTION_BRIDGE import get_bybit_bridge",
    "    signals = getattr(self.data_hub, 'get_signals', lambda: [])()",
    "    if signals:",
    "        get_bybit_bridge().execute_signals(signals[:3])",
    "except Exception as e:",
    "    logger.error(f'Bybit Bridge Error: {e}')"
]

new_lines = []
modified = False
already_patched = False

for line in lines:
    if 'get_bybit_bridge' in line and 'import' in line:
        already_patched = True
        
    # Check for target line
    if 'self.micro_wallet_grower.execute_signals()' in line and not modified and not already_patched:
        # Calculate indentation
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]
        
        # Add integration block with correct indentation
        for code_line in integration_lines:
            new_lines.append(indent_str + code_line + '\n')
            
        new_lines.append(line)
        modified = True
        print("Patch inserted successfully")
    else:
        new_lines.append(line)

if modified:
    with open(target_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("File updated safely")
else:
    print("File not modified (already patched or target not found)")
