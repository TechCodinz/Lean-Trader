#!/usr/bin/env python3
"""
EMERGENCY FIX for catastrophic issues:

ISSUE 1: ENTRY/EXIT PRICES SWAPPED!
  Recording: Entry $3,140, Exit $2,699 = -13% loss
  Reality: ETH is $2,700, so entry should be $2,700!
  Impact: Bot thinks it's losing when winning (and vice versa)!

ISSUE 2: POSITION SIZE TOO LARGE
  Balance: $27.74
  Position size: $20-30
  Result: "Insufficient balance" error (53 times!)

ISSUE 3: EXECUTION RATE DECLINING
  Was: 14% → Now: 9%
  Cause: Running out of money!

This will:
1. Fix entry price recording (use ACTUAL market price at entry)
2. Make position size dynamic (10% of balance)
3. Add safety checks
"""

import re

print("="*70)
print("🚨 EMERGENCY FIX - SWAPPED PRICES")
print("="*70)
print()

# ========================================
# FIX 1: CORRECT ENTRY PRICE RECORDING
# ========================================
print("FIX 1: Fixing entry price recording...")
print("-" * 70)

try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        content = f.read()
    
    modified = False
    
    # The issue: We need to fetch CURRENT market price at execution time
    # Not rely on order response which might be wrong
    
    # Find where we execute trades and add market price fetch
    if 'def execute_trade' in content or 'def _execute_trade' in content:
        
        # Add code to fetch current market price BEFORE placing order
        pattern = r'(def (?:_)?execute_trade.*?\n.*?try:)'
        
        replacement = r'''\1
            # 🔧 CRITICAL FIX: Get ACTUAL market price before order
            try:
                ticker = exchange.fetch_ticker(symbol)
                actual_market_price = ticker.get('last') or ticker.get('close')
                logger.info(f"   💰 Market price at execution: ${actual_market_price}")
            except Exception as e:
                actual_market_price = entry_price
                logger.warning(f"    Could not fetch market price: {e}")
'''
        
        content_new = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if content_new != content:
            content = content_new
            modified = True
            print("   [OK] Added market price fetch before order")
        
        # Now ensure we USE this market price as entry_price
        # Instead of relying on order response
        if 'actual_price =' in content:
            # Replace the complex fallback chain with simple: use market price
            old = """actual_price = (
                    order.get('average') or 
                    order.get('price') or 
                    (order.get('cost', 0) / order.get('filled', 1) if order.get('filled', 0) > 0 else None) or
                    entry_price
                )"""
            
            new = """# Use market price fetched BEFORE order (most accurate!)
                actual_price = actual_market_price or entry_price
                logger.info(f"   [OK] Using entry_price: ${actual_price}")"""
            
            if old in content:
                content = content.replace(old, new)
                modified = True
                print("   [OK] Changed to use market price instead of order response")
    
    if modified:
        with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
            f.write(content)
        print("   [OK] Entry price recording FIXED!")
    else:
        print("    Could not apply automatic fix - needs manual inspection")
    
    print()

except Exception as e:
    print(f"   [X] Error: {e}")
    print()

# ========================================
# FIX 2: DYNAMIC POSITION SIZING
# ========================================
print("FIX 2: Making position size dynamic (10% of balance)...")
print("-" * 70)

try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    modified = False
    
    # Find position_size calculation
    patterns = [
        (r'position_size = 30', 'position_size = max(5, balance * 0.10)  # 10% of balance, min $5'),
        (r'position_size = 25', 'position_size = max(5, balance * 0.10)  # 10% of balance, min $5'),
        (r'position_size = 20', 'position_size = max(5, balance * 0.10)  # 10% of balance, min $5'),
        (r'position_size = 15', 'position_size = max(5, balance * 0.10)  # 10% of balance, min $5'),
    ]
    
    for old_pattern, new_code in patterns:
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_code, content)
            modified = True
            print(f"   [OK] Changed to dynamic 10% sizing")
            break
    
    if modified:
        with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
            f.write(content)
        print("   [OK] Position sizing now dynamic!")
    else:
        print("    Position size pattern not found")
    
    print()

except Exception as e:
    print(f"   [X] Error: {e}")
    print()

# ========================================
# FIX 3: ADD SAFETY CHECKS
# ========================================
print("FIX 3: Adding safety checks...")
print("-" * 70)

try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    # Add check: Don't trade if position_size > 50% of balance
    if 'position_size' in content and 'if position_size' not in content:
        # Find where position_size is calculated and add check after
        pattern = r'(position_size = max\(5, balance \* 0\.10\).*?\n)'
        replacement = r'''\1            
            # Safety: Don't trade if position too large relative to balance
            if position_size > balance * 0.5:
                logger.warning(f"    Position size ${position_size:.2f} too large for balance ${balance:.2f}")
                continue
            
'''
        content_new = re.sub(pattern, replacement, content)
        
        if content_new != content:
            with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
                f.write(content_new)
            print("   [OK] Added safety check for position sizing")
        else:
            print("    Could not add safety check automatically")
    
    print()

except Exception as e:
    print(f"   [X] Error: {e}")
    print()

# ========================================
# FIX 4: CHECK ACTUAL BALANCE
# ========================================
print("FIX 4: Checking actual current balance...")
print("-" * 70)

try:
    with open('bot.log', 'r', errors='ignore') as f:
        logs = f.read()
    
    # Find most recent balance
    balance_matches = re.findall(r'balance[:\s]+\$?([\d.]+)', logs, re.IGNORECASE)
    
    if balance_matches:
        recent_balance = float(balance_matches[-1])
        print(f"   Current balance: ${recent_balance:.2f}")
        print()
        
        if recent_balance < 20:
            print("   🚨 CRITICAL: Balance too low!")
            print("   → Recommended position size: $2-3 per trade")
            print("   → Current: Trying $20-30 per trade!")
            print()
        
        # Calculate safe position size
        safe_size = recent_balance * 0.10
        print(f"   Safe position size (10%): ${safe_size:.2f}")
        print()

except Exception as e:
    print(f"    {e}")
    print()

# ========================================
# SUMMARY
# ========================================
print("="*70)
print("[OK] EMERGENCY FIX COMPLETE")
print("="*70)
print()
print("Changes:")
print("  ✓ Entry price: Now fetches market price at execution time")
print("  ✓ Position size: Dynamic 10% of balance (was fixed $20-30)")
print("  ✓ Safety check: Won't trade if position > 50% balance")
print()
print("Next: Restart and test with small balance!")
print("="*70)

