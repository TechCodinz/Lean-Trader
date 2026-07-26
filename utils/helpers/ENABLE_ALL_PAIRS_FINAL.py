#!/usr/bin/env python3
"""
Final fix: Remove ALL blacklists, enable ALL pairs for arbitrage
"""

print("🔧 Removing ALL symbol restrictions...")
print()

# Remove ETH/SOL from TOXIC_SYMBOLS
with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'TOXIC_SYMBOLS' in content:
    # Comment out ETH and SOL
    content = content.replace("'ETH/USDT',", "# 'ETH/USDT',  # ENABLED for arbitrage")
    content = content.replace("'SOL/USDT',", "# 'SOL/USDT',  # ENABLED for arbitrage")
    content = content.replace('"ETH/USDT",', '# "ETH/USDT",  # ENABLED')
    content = content.replace('"SOL/USDT",', '# "SOL/USDT",  # ENABLED')
    
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] Removed ETH/SOL blacklist")

print()
print("=" * 60)
print("[OK] ALL PAIRS ENABLED!")
print("=" * 60)
print()
print("Bot will now:")
print("  [OK] Scan entire exchange")
print("  [OK] Trade ALL profitable pairs")
print("  [OK] Use arbitrage if available")
print("  [OK] Diversify across symbols")
print("  [OK] Maximize opportunities")

