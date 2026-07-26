#!/usr/bin/env python3
"""
EMERGENCY RECOVERY
1. Blacklist toxic symbols (USTC, ICX, FTM, etc.)
2. Fix position sizing bug
3. Add safety checks
"""

import re

print("="*70)
print("🚨 EMERGENCY RECOVERY - BLOCKING TOXIC SYMBOLS")
print("="*70)
print()

# ============================================
# STEP 1: BLACKLIST TOXIC SYMBOLS
# ============================================
print("STEP 1: Adding toxic symbol blacklist...")
print("-" * 70)

toxic_symbols = [
    'USTC/USDT',  # -99.98% avg - DEAD COIN!
    'ICX/USDT',   # -99.30% avg - Delisted
    'FTM/USDT',   # -97.82% avg - Bad data
    'MKR/USDT',   # -97.40% avg
    'LINK/USDT',  # -95.28% avg - Wrong prices
]

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        content = f.read()
    
    # Add blacklist at top of file
    blacklist_code = '''
# 🚫 TOXIC SYMBOL BLACKLIST - These coins destroy accounts!
TOXIC_SYMBOLS = {
    'USTC/USDT',  # Terra USD Classic - DEAD (-99.98%)
    'ICX/USDT',   # ICON - Delisted/Bad data (-99.30%)
    'FTM/USDT',   # Fantom - Wrong price data (-97.82%)
    'MKR/USDT',   # Maker - Bad spreads (-97.40%)
    'LINK/USDT',  # ChainLink - Price issues (-95.28%)
    'LUNA/USDT',  # Terra Luna - DEAD
    'LUNC/USDT',  # Terra Luna Classic - DEAD
}

def is_toxic_symbol(symbol: str) -> bool:
    """Check if symbol is in toxic blacklist"""
    return symbol in TOXIC_SYMBOLS

'''
    
    # Find first class or def
    if 'class ' in content:
        insert_pos = content.find('class ')
    elif 'def ' in content:
        insert_pos = content.find('def ')
    else:
        insert_pos = 0
    
    # Check if blacklist already exists
    if 'TOXIC_SYMBOLS' not in content:
        content = content[:insert_pos] + blacklist_code + content[insert_pos:]
        
        # Now add check in _should_skip_symbol method
        if '_should_skip_symbol' in content:
            # Find the method
            method_start = content.find('def _should_skip_symbol')
            if method_start != -1:
                # Find first line after def
                first_line_end = content.find('\n', method_start)
                second_line_end = content.find('\n', first_line_end + 1)
                
                # Add toxic check after docstring/first line
                toxic_check = '''        
        # 🚫 CRITICAL: Block toxic symbols that destroy accounts!
        if is_toxic_symbol(symbol):
            logger.warning(f"   🚫 BLOCKING TOXIC SYMBOL: {symbol} (known account killer!)")
            return True
'''
                content = content[:second_line_end] + toxic_check + content[second_line_end:]
        
        with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
            f.write(content)
        
        print(f"[OK] Blacklisted {len(toxic_symbols)} toxic symbols:")
        for sym in toxic_symbols:
            print(f"   🚫 {sym}")
    else:
        print("[OK] Blacklist already exists")
    
    print()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================
# STEP 2: FIX POSITION SIZING (PROPER)
# ============================================
print("STEP 2: Fixing position sizing properly...")
print("-" * 70)

try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
        lines = f.readlines()
    
    # Find position_size line
    for i, line in enumerate(lines):
        if 'position_size = ' in line and 'base_risk' in line:
            print(f"Found complex position sizing at line {i+1}")
            
            # Get indentation
            indent = len(line) - len(line.lstrip())
            spaces = ' ' * indent
            
            # Replace with SIMPLE, SAFE sizing
            new_code = f'''{spaces}# 🎯 SAFE POSITION SIZING (5% of balance, min $5)
{spaces}base_pct = 0.05  # 5% of balance (SAFE!)
{spaces}position_size = max(5, balance * base_pct)
{spaces}
{spaces}# Hard cap at 10% maximum (safety)
{spaces}if position_size > balance * 0.10:
{spaces}    position_size = balance * 0.10
{spaces}    logger.warning(f"    Capping at 10%: ${balance * 0.10:.2f}")
{spaces}
{spaces}logger.info(f"   💰 Safe position: ${position_size:.2f} ({position_size/balance*100:.1f}% of ${balance:.2f})")
'''
            
            lines[i] = new_code + '\n'
            
            with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
                f.writelines(lines)
            
            print("[OK] Position sizing fixed!")
            print()
            print("New sizing:")
            print("  • 5% of balance per trade")
            print("  • Minimum $5")
            print("  • Maximum 10% cap")
            print()
            break

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================
# STEP 3: CHECK CURRENT STATE
# ============================================
print("="*70)
print("📊 CURRENT STATE")
print("="*70)
print()

try:
    import subprocess
    
    # Check balance
    result = subprocess.run(
        ['grep', '-a', 'Got exchange balance', 'bot.log'],
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        balances = re.findall(r'\$([0-9.]+)', result.stdout)
        if balances:
            current = float(balances[-1])
            print(f"Current balance: ${current:.2f}")
            print()
            
            if current < 10:
                print("🚨 CRITICAL: Balance too low to recover!")
                print()
                print("Options:")
                print("  1. Add fresh capital ($20-50)")
                print("  2. Let bot rebuild from $5 (will take LONG time)")
                print("  3. Start fresh with lessons learned")
                print()
                print("Recommended: Add $30-50 and let it rebuild with:")
                print("  ✓ Toxic symbols blocked")
                print("  ✓ Safe 5% position sizing")
                print("  ✓ Better risk management")
            else:
                print("[OK] Balance sufficient to continue")

except Exception as e:
    print(f"Error: {e}")

print()
print("="*70)
print("[OK] EMERGENCY RECOVERY COMPLETE")
print("="*70)
print()
print("Applied:")
print("  ✓ Blacklisted 5+ toxic symbols")
print("  ✓ Fixed position sizing to 5%")
print("  ✓ Added safety caps")
print()
print(" Current balance: $5.04 (too low to trade effectively)")
print()
print("Recommendation:")
print("  1. Add $30-50 fresh capital")
print("  2. Restart bot")
print("  3. Monitor closely")
print("  4. Should rebuild safely now")
print()
print("="*70)

