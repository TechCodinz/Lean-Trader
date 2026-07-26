#!/usr/bin/env python3
import re

print("🔧 FORCE APPLYING fixes...")
with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

original = content
changes = []

# FIX 1: Position sizing
if 'size_usd = max(5.0, min(usdt_balance * size_pct, usdt_balance * 0.25)' in content:
    if 'Scaled up to meet $5 minimum' not in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'size_usd = max(5.0, min(usdt_balance * size_pct, usdt_balance * 0.25)' in line:
                indent = len(line) - len(line.lstrip())
                fix = f'{" " * indent}\n{" " * indent}# 🔥 CRITICAL FIX: Ensure minimum $5.00\n{" " * indent}if size_usd < 5.0 and usdt_balance >= 5.0:\n{" " * indent}    size_usd = min(5.0, usdt_balance * 0.30)\n{" " * indent}    logger.warning(f"     Scaled up to meet $5 minimum: ${{size_usd:.2f}}")\n{" " * indent}\n{" " * indent}size_usd = max(5.0, size_usd)'
                lines.insert(i+1, fix)
                content = '\n'.join(lines)
                changes.append("Position sizing")
                break

# FIX 2: Position tracking
if 'self.risk_manager.open_positions[symbol] = {' in content:
    if 'POSITION TRACKED:' not in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'self.risk_manager.open_positions[symbol] = {' in line:
                j = i
                braces = 0
                while j < len(lines) and j < i+15:
                    braces += lines[j].count('{') - lines[j].count('}')
                    if braces == 0 and '}' in lines[j]:
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        log = f'{" " * indent}\n{" " * indent}logger.warning(f"   [OK] Position tracked: {{symbol}} @ ${{entry_price:.4f}} (Total: {{len(self.risk_manager.open_positions)}})")\n{" " * indent}logger.info(f"[OK] POSITION TRACKED: {{symbol}} @ ${{entry_price:.4f}} | Total: {{len(self.risk_manager.open_positions)}}")'
                        lines.insert(j+1, log)
                        content = '\n'.join(lines)
                        changes.append("Position tracking")
                        break
                    j += 1
                break

# FIX 3: Position monitoring
if 'positions_to_monitor.update(self.risk_manager.open_positions)' in content:
    if 'Found {len' not in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'positions_to_monitor.update(self.risk_manager.open_positions)' in line and 'if hasattr' not in line:
                indent = len(line) - len(line.lstrip())
                lines[i] = f'{" " * indent}if hasattr(self, \'risk_manager\') and self.risk_manager and hasattr(self.risk_manager, \'open_positions\'):'
                lines.insert(i+1, f'{" " * indent}    positions_to_monitor.update(self.risk_manager.open_positions)')
                lines.insert(i+2, f'{" " * indent}    if self.risk_manager.open_positions:')
                lines.insert(i+3, f'{" " * indent}        logger.debug(f"   Found {{len(self.risk_manager.open_positions)}} positions")')
                lines.insert(i+4, f'{" " * indent}else:')
                lines.insert(i+5, f'{" " * indent}    logger.warning("     risk_manager not available!")')
                content = '\n'.join(lines)
                changes.append("Position monitoring")
                break

if content != original:
    with open('EXECUTION_ORCHESTRATOR.py.backup', 'w') as f:
        f.write(original)
    with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
        f.write(content)
    print(f"[OK] APPLIED: {', '.join(changes)}")
else:
    print("  No changes - checking what's there...")
    if 'POSITION TRACKED:' in content:
        print("  [OK] POSITION TRACKED already exists")
    if 'Scaled up to meet' in content:
        print("  [OK] Position sizing fix already exists")

print("\nVerifying...")
print("Run: grep -n 'POSITION TRACKED:' EXECUTION_ORCHESTRATOR.py")
