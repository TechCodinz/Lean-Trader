#!/usr/bin/env python3
import re

print("🔧 Applying fixes...")
with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

original = content

# Fix 1: Position sizing
if 'Scaled up to meet $5 minimum' not in content:
    pattern = r'(size_usd = max\(5\.0, min\(usdt_balance \* size_pct, usdt_balance \* 0\.25\)\)  # Min \$5, max 25% of balance)'
    replacement = r'''\1
            
            # 🔥 CRITICAL FIX: Ensure minimum $5.00 (Bybit requirement)
            if size_usd < 5.0 and usdt_balance >= 5.0:
                size_usd = min(5.0, usdt_balance * 0.30)
                logger.warning(f"     Scaled up to meet $5 minimum: ${size_usd:.2f}")
            size_usd = max(5.0, size_usd)'''
    content = re.sub(pattern, replacement, content)

# Fix 2: Position tracking logging
if 'POSITION TRACKED:' not in content:
    pattern = r'(logger\.warning\(f"   [OK] Position tracked in risk_manager: \{symbol\} @ \$\{entry_price:.4f\} \(Total tracked: \{len\(self\.risk_manager\.open_positions\)\}\)"\))'
    replacement = r'''\1
                        logger.info(f"[OK] POSITION TRACKED: {symbol} @ ${entry_price:.4f} | Total: {len(self.risk_manager.open_positions)}")'''
    if not re.search(pattern, content):
        # Try simpler
        pattern = r'(self\.risk_manager\.open_positions\[symbol\] = \{.*?\n                        \})'
        replacement = r'''\1
                        logger.warning(f"   [OK] Position tracked in risk_manager: {symbol} @ ${entry_price:.4f} (Total tracked: {len(self.risk_manager.open_positions)})")
                        logger.info(f"[OK] POSITION TRACKED: {symbol} @ ${entry_price:.4f} | Total: {len(self.risk_manager.open_positions)}")'''
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Fix 3: Position monitoring
if 'Found.*positions in risk_manager' not in content:
    pattern = r'(positions_to_monitor\.update\(self\.risk_manager\.open_positions\))'
    replacement = r'''if hasattr(self, 'risk_manager') and self.risk_manager and hasattr(self.risk_manager, 'open_positions'):
            positions_to_monitor.update(self.risk_manager.open_positions)
            if self.risk_manager.open_positions:
                logger.debug(f"   Found {len(self.risk_manager.open_positions)} positions in risk_manager")
        else:
            logger.warning("     risk_manager not available!")'''
    content = re.sub(pattern, replacement, content)

if content != original:
    with open('EXECUTION_ORCHESTRATOR.py.backup', 'w') as f:
        f.write(original)
    with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
        f.write(content)
    print("[OK] Fixes applied! Backup: EXECUTION_ORCHESTRATOR.py.backup")
else:
    print("[OK] Fixes already applied!")

print("Verify: grep -n 'POSITION TRACKED:' EXECUTION_ORCHESTRATOR.py")
