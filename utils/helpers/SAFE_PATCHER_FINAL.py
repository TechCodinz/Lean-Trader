#!/usr/bin/env python3
import sys
import os

target_file = '/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py'
backup_file = target_file + '.backup_safe_final'

# Create backup
if not os.path.exists(backup_file):
    os.system(f'cp {target_file} {backup_file}')

with open(target_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Bridge integration code
integration_block = [
    "# Bybit Testnet Execution Bridge Integration",
    "try:",
    "    from BYBIT_EXECUTION_BRIDGE import get_bybit_bridge",
    "    # Execute immediately before async task creation",
    "    bridge_signals = getattr(self.data_hub, 'get_signals', lambda: [])()",
    "    if bridge_signals:",
    "        get_bybit_bridge().execute_signals(bridge_signals[:3])",
    "except Exception as e:",
    "    logger.error(f'Bybit Bridge Error: {e}')"
]

new_lines = []
modified = False
already_patched = False

# Logic: Find target `execute_signals` line, then look BACKWARDS for `tasks.append` parent
# We will iterate and buffer. Or simpler: identify the line index first.

target_line_idx = -1
parent_line_idx = -1

for i, line in enumerate(lines):
    if 'get_bybit_bridge' in line and 'import' in line:
        already_patched = True
        break
    if 'self.micro_wallet_grower.execute_signals()' in line:
        target_line_idx = i
        # Search backwards safely
        for j in range(i, max(0, i-50), -1):
            if 'tasks.append' in lines[j] and 'asyncio.create_task' in lines[j]:
                parent_line_idx = j
                break
        break

if already_patched:
    print("Already patched")
elif parent_line_idx != -1:
    # We found the parent line. We will insert BEFORE it.
    parent_indent = len(lines[parent_line_idx]) - len(lines[parent_line_idx].lstrip())
    indent_str = lines[parent_line_idx][:parent_indent]
    
    # Construct new file content
    new_lines = lines[:parent_line_idx]
    
    # Add integration block
    for code in integration_block:
        new_lines.append(indent_str + code + '\n')
        
    new_lines.extend(lines[parent_line_idx:])
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("SUCCESS: Patch applied before line", parent_line_idx + 1)
else:
    print("FAILED: Could not find target lines")

