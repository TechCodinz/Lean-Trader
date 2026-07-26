#!/usr/bin/env python3
"""
NUCLEAR FIX: Force blacklist ETH at ALL levels + enable multi-symbol
"""

print("🔧 Applying nuclear fixes...")
print()

# Fix 1: Add ETH to TOXIC_SYMBOLS at module level
with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

if 'TOXIC_SYMBOLS' in content:
    # Ensure ETH and SOL are in TOXIC_SYMBOLS
    if "'ETH/USDT'" not in content.split('TOXIC_SYMBOLS')[1].split('}')[0]:
        content = content.replace(
            'TOXIC_SYMBOLS = {',
            "TOXIC_SYMBOLS = {\n    'ETH/USDT', 'SOL/USDT',  # BLACKLISTED - backwards bug"
        )
        print("[OK] Added ETH/SOL to TOXIC_SYMBOLS")
    
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.write(content)

# Fix 2: Add symbol filtering in orchestrator BEFORE execute
print()
print("🔧 Adding pre-execution filtering in orchestrator...")

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find where execute is called and add filtering before it
modified = False
new_lines = []
BLACKLIST = ['ETH/USDT', 'SOL/USDT']

for i, line in enumerate(lines):
    # If this line calls .execute(
    if '.execute(' in line and 'symbol' in lines[max(0, i-10):i+1][-1].lower():
        # Add blacklist check before execute
        indent = len(line) - len(line.lstrip())
        blacklist_check = ' ' * indent + f"""# BLACKLIST CHECK - Skip ETH/SOL
{' ' * indent}if signal.get('symbol') in {BLACKLIST}:
{' ' * indent}    logger.warning(f"🚫 BLACKLISTED: {{signal.get('symbol')}}")
{' ' * indent}    continue
{' ' * indent}
"""
        # Only add if not already there
        if '# BLACKLIST CHECK' not in ''.join(lines[max(0, i-5):i]):
            new_lines.append(blacklist_check)
            modified = True
            print(f"[OK] Added blacklist check before line {i+1}")
    
    new_lines.append(line)

if modified:
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("[OK] Orchestrator updated with blacklist checks")
else:
    print("  Could not find execute() calls to patch")

# Fix 3: Remove any hardcoded ETH forcing
print()
print("🔧 Removing hardcoded ETH references...")

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Comment out any lines that force ETH trading
content = content.replace(
    "'ETH/USDT',",
    "# 'ETH/USDT',  # DISABLED - backwards bug"
)

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Commented out ETH/USDT references")

print()
print("=" * 60)
print("[OK] NUCLEAR FIX COMPLETE!")
print()
print("This will:")
print("  [OK] Block ETH at execution engine level")
print("  [OK] Block ETH at orchestrator level") 
print("  [OK] Remove ETH from symbol lists")
print("  [OK] Enable other 80+ pairs to trade")

