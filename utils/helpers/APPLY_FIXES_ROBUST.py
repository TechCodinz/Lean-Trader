#!/usr/bin/env python3
import re

print("🔧 Applying fixes...")
with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

original = lines[:]
changes = []

# FIX 1: Position sizing
for i, line in enumerate(lines):
    if 'size_usd = max(5.0, min(usdt_balance * size_pct, usdt_balance * 0.25)' in line:
        if i+1 < len(lines) and 'Scaled up to meet $5 minimum' in lines[i+1]:
            break
        indent = len(line) - len(line.lstrip())
        fix = [
            f'{" " * indent}\n',
            f'{" " * indent}# 🔥 CRITICAL FIX: Ensure minimum $5.00 (Bybit requirement)\n',
            f'{" " * indent}if size_usd < 5.0 and usdt_balance >= 5.0:\n',
            f'{" " * indent}    size_usd = min(5.0, usdt_balance * 0.30)\n',
            f'{" " * indent}    logger.warning(f"     Scaled up to meet $5 minimum: ${{size_usd:.2f}}")\n',
            f'{" " * indent}\n',
            f'{" " * indent}size_usd = max(5.0, size_usd)\n'
        ]
        lines[i+1:i+1] = fix
        changes.append("Position sizing")
        break

# FIX 2: Position tracking logging
for i, line in enumerate(lines):
    if 'self.risk_manager.open_positions[symbol] = {' in line:
        j = i
        braces = 0
        while j < len(lines) and j < i+10:
            braces += lines[j].count('{') - lines[j].count('}')
            if braces == 0 and '}' in lines[j]:
                if j+1 < len(lines) and 'POSITION TRACKED:' in lines[j+1]:
                    break
                indent = len(lines[j]) - len(lines[j].lstrip())
                log = [
                    f'{" " * indent}\n',
                    f'{" " * indent}logger.warning(f"   [OK] Position tracked: {{symbol}} @ ${{entry_price:.4f}} (Total: {{len(self.risk_manager.open_positions)}})")\n',
                    f'{" " * indent}logger.info(f"[OK] POSITION TRACKED: {{symbol}} @ ${{entry_price:.4f}} | Total: {{len(self.risk_manager.open_positions)}}")\n'
                ]
                lines[j+1:j+1] = log
                changes.append("Position tracking")
                break
            j += 1
        break

# FIX 3: Position monitoring
for i, line in enumerate(lines):
    if 'positions_to_monitor.update(self.risk_manager.open_positions)' in line:
        if i > 0 and 'Found' in lines[i-1]:
            break
        indent = len(line) - len(line.lstrip())
        lines[i] = f'{" " * indent}if hasattr(self, \'risk_manager\') and self.risk_manager and hasattr(self.risk_manager, \'open_positions\'):\n'
        lines.insert(i+1, f'{" " * indent}    positions_to_monitor.update(self.risk_manager.open_positions)\n')
        lines.insert(i+2, f'{" " * indent}    if self.risk_manager.open_positions:\n')
        lines.insert(i+3, f'{" " * indent}        logger.debug(f"   Found {{len(self.risk_manager.open_positions)}} positions")\n')
        lines.insert(i+4, f'{" " * indent}else:\n')
        lines.insert(i+5, f'{" " * indent}    logger.warning("     risk_manager not available!")\n')
        changes.append("Position monitoring")
        break

if lines != original:
    with open('EXECUTION_ORCHESTRATOR.py.backup', 'w') as f:
        f.writelines(original)
    with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
        f.writelines(lines)
    print(f"[OK] Applied: {', '.join(changes)}")
else:
    print("[OK] All fixes already applied!")
