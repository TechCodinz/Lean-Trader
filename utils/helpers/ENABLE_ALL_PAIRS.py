#!/usr/bin/env python3
"""
Enable trading on ALL available pairs, not just ETH/BTC
"""

print("🔧 Enabling multi-pair trading...")
print()

# Fix 1: Lower confidence threshold (0.65 → 0.50)
print("1️⃣ Lowering confidence threshold 0.65 → 0.50...")
with open('ADAPTIVE_CONFIDENCE_ENGINE.py', 'r') as f:
    conf = f.read()

conf = conf.replace('self.base_min_confidence = 0.65', 'self.base_min_confidence = 0.50')
conf = conf.replace('min_confidence = 0.65', 'min_confidence = 0.50')

with open('ADAPTIVE_CONFIDENCE_ENGINE.py', 'w') as f:
    f.write(conf)

print("   [OK] Confidence lowered to 0.50")
print()

# Fix 2: Remove symbol limits in EXECUTION_ORCHESTRATOR
print("2️⃣ Removing symbol limits...")
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

changes = 0
for i, line in enumerate(lines):
    # Replace [:5], [:10], [:20], [:50] with larger limits
    if '[:5]' in line and 'symbols' in line.lower():
        lines[i] = line.replace('[:5]', '[:100]')
        changes += 1
    elif '[:10]' in line and 'symbols' in line.lower():
        lines[i] = line.replace('[:10]', '[:100]')
        changes += 1
    elif '[:20]' in line and 'symbols' in line.lower():
        lines[i] = line.replace('[:20]', '[:100]')
        changes += 1
    elif '[:50]' in line and 'symbols' in line.lower():
        lines[i] = line.replace('[:50]', '[:200]')
        changes += 1

with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.writelines(lines)

print(f"   [OK] Expanded {changes} symbol limits")
print()

# Fix 3: Ensure max_positions is high
print("3️⃣ Setting max_positions to unlimited...")
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    exec_content = f.read()

exec_content = re.sub(r'max_positions\s*=\s*\d+', 'max_positions = 999', exec_content)
exec_content = re.sub(r'max_open_positions\s*=\s*\d+', 'max_open_positions = 999', exec_content)

with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.write(exec_content)

print("   [OK] Max positions set to 999")
print()

print("=" * 70)
print("[OK] MULTI-PAIR TRADING ENABLED!")
print("=" * 70)
print()
print("Changes:")
print("  [OK] Confidence: 0.65 → 0.50 (more signals)")
print("  [OK] Symbol limits: 5-50 → 100-200 (more pairs)")
print("  [OK] Max positions: → 999 (unlimited)")
print()
print("Bot will now trade MANY more pairs!")

import re

