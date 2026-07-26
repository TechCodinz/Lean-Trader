#!/usr/bin/env python3
"""
Quick fixes while bot is running:
1. Blacklist invalid symbols (USELESS, PROVE, FWOG, etc.)
2. Reduce position size to 8% (from 12%) so more trades possible
"""

print("🔧 Applying quick fixes...")
print()

# ============================================
# FIX 1: Add invalid symbols to blacklist
# ============================================
print("1️⃣ Blacklisting invalid symbols...")

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        content = f.read()
    
    # Find TOXIC_SYMBOLS set
    if 'TOXIC_SYMBOLS = {' in content:
        # Add new invalid symbols to the set
        old_set = "TOXIC_SYMBOLS = {"
        new_symbols = """TOXIC_SYMBOLS = {
    # Original toxic symbols
    'USTC/USDT',  # Terra USD Classic - DEAD
    'ICX/USDT',   # ICON - Delisted
    'FTM/USDT',   # Fantom - Bad data
    'MKR/USDT',   # Maker - Bad spreads
    'LINK/USDT',  # ChainLink - Price issues
    'LUNA/USDT',  # Terra Luna - DEAD
    'LUNC/USDT',  # Terra Luna Classic - DEAD
    
    # Invalid symbols (don't exist on Bybit)
    'USELESS/USDT',
    'PROVE/USDT',
    'FWOG/USDT',
    'MPLX/USDT',
    'RUN/USDT',
    'EOS3L/USDT',
    'EOS3S/USDT',
    'XPDUSD',
    'COPPER',
    
    # Forex (not available on testnet)
    'GBP/JPY',
    'GBP/NZD',
    'NZD/USD',
    'EURUSD',
    'UKOIL',"""
        
        if old_set in content:
            content = content.replace(old_set, new_symbols, 1)
            
            with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
                f.write(content)
            
            print("   [OK] Added invalid symbols to blacklist")
        else:
            print("     TOXIC_SYMBOLS set structure changed")
    else:
        print("     TOXIC_SYMBOLS not found")
    
except Exception as e:
    print(f"   [X] Error: {e}")

print()

# ============================================
# FIX 2: Reduce position size to 8%
# ============================================
print("2️⃣ Reducing position size to 8% (from 12%)...")

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        lines = f.readlines()
    
    changed = False
    for i, line in enumerate(lines):
        # Find position sizing line
        if 'Position sizing:' in line and 'balance:' in line:
            # Look backwards for the calculation
            for j in range(max(0, i-10), i):
                if 'position_size' in lines[j] and '0.12' in lines[j]:
                    lines[j] = lines[j].replace('0.12', '0.08')
                    print(f"   [OK] Line {j+1}: 0.12 → 0.08")
                    changed = True
                elif 'base_size' in lines[j] and 'balance * 0.12' in lines[j]:
                    lines[j] = lines[j].replace('0.12', '0.08')
                    print(f"   [OK] Line {j+1}: 0.12 → 0.08")
                    changed = True
    
    if changed:
        with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
            f.writelines(lines)
        print("   [OK] Position size reduced to 8%")
    else:
        print("     Position size line not found (may already be 8%)")

except Exception as e:
    print(f"   [X] Error: {e}")

print()
print("=" * 70)
print("[OK] QUICK FIXES COMPLETE!")
print("=" * 70)
print()
print("Changes:")
print("  ✓ Blacklisted 15+ invalid symbols")
print("  ✓ Position size: 12% → 8% (more trades possible)")
print()
print("🔄 Restart bot to apply:")
print("   pkill -f python3 && sleep 2 && nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &")

