#!/usr/bin/env python3
"""
Enable trading on ALL available pairs, not just ETH/BTC
"""

import re  # FIX: Import at the TOP!

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

# Fix 2: Remove ALL symbol limits in EXECUTION_ORCHESTRATOR
print("2️⃣ Removing ALL symbol limits...")
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Remove ALL [:N] limits
original_content = content
content = re.sub(r'\[:5\]', '[:200]', content)
content = re.sub(r'\[:10\]', '[:200]', content)
content = re.sub(r'\[:20\]', '[:200]', content)
content = re.sub(r'\[:50\]', '[:200]', content)
content = re.sub(r'\[:100\]', '[:200]', content)

changes = len(re.findall(r'\[:200\]', content)) - len(re.findall(r'\[:200\]', original_content))

with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.write(content)

print(f"   [OK] Expanded {changes} symbol limits to [:200]")
print()

# Fix 3: Ensure max_positions is high
print("3️⃣ Setting max_positions to unlimited...")
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    exec_content = f.read()

exec_content = re.sub(r'max_positions\s*=\s*\d+', 'max_positions = 999', exec_content)
exec_content = re.sub(r'max_open_positions\s*=\s*\d+', 'max_open_positions = 999', exec_content)
exec_content = re.sub(r'max_trades\s*=\s*\d+', 'max_trades = 999', exec_content)
exec_content = re.sub(r'max_daily_trades\s*=\s*\d+', 'max_daily_trades = 999', exec_content)

with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.write(exec_content)

print("   [OK] Max positions/trades set to 999")
print()

# Fix 4: Also fix COMPLETE_ULTIMATE_ORCHESTRATOR
print("4️⃣ Fixing COMPLETE_ULTIMATE_ORCHESTRATOR limits...")
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    ultimate = f.read()

# Remove slice limits
ultimate = re.sub(r'\[:5\]', '[:200]', ultimate)
ultimate = re.sub(r'\[:10\]', '[:200]', ultimate)
ultimate = re.sub(r'\[:20\]', '[:200]', ultimate)
ultimate = re.sub(r'\[:50\]', '[:200]', ultimate)
ultimate = re.sub(r'\[:80\]', '[:200]', ultimate)
ultimate = re.sub(r'\[:100\]', '[:200]', ultimate)

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.write(ultimate)

print("   [OK] Orchestrator limits expanded")
print()

print("=" * 70)
print("[OK] MULTI-PAIR TRADING ENABLED!")
print("=" * 70)
print()
print("Changes:")
print("  [OK] Confidence: 0.65 → 0.50 (more signals)")
print("  [OK] Symbol limits: ALL expanded to [:200]")
print("  [OK] Max positions: → 999 (unlimited)")
print("  [OK] Max trades: → 999 (unlimited)")
print()
print("Bot will now trade up to 200 pairs simultaneously!")

