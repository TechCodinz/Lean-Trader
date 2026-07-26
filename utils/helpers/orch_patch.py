#!/usr/bin/env python3
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

# Find and fix testnet setup
fixed_lines = []
for line in lines:
    # Ensure testnet is properly enabled
    if 'set_sandbox_mode(True)' in line:
        fixed_lines.append(line)  # Keep this - it enables testnet
        fixed_lines.append("                logger.info('REAL TESTNET MODE ENABLED')\n")
    elif 'simulation' in line.lower() and 'mode' in line.lower():
        # Skip or replace simulation mode lines
        continue
    else:
        fixed_lines.append(line)

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.writelines(fixed_lines)
print("Orchestrator patched for real testnet")
