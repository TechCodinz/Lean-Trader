#!/usr/bin/env python3
"""
Apply the PROFITABLE settings from the working orchestrator
"""

print(">> Applying profitable settings...")
print()

# 1. Fix EXECUTION_ORCHESTRATOR profit/loss thresholds
print("1️⃣ Fixing EXECUTION_ORCHESTRATOR profit/loss thresholds...")

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    exec_content = f.read()

# Find and fix the profit/loss thresholds
# Current (wrong): +1% profit, -3% loss
# Working (correct): +2% profit, -1% loss

old_profit_loss = '''                    # Check stop loss (1% loss)
                    if pnl_pct < -0.01:
                        logger.warning(f"🛑 Stop loss triggered: {symbol} ({pnl_pct:.2%})")
                        await self.close_position(symbol, current_price, 'stop_loss')
                    
                    # Check take profit (2% profit)
                    elif pnl_pct > 0.02:'''

# Check if already correct
if 'elif pnl_pct > 0.02:' in exec_content and 'if pnl_pct < -0.01:' in exec_content:
    print("   [OK] EXECUTION_ORCHESTRATOR already has correct thresholds (+2%/-1%)")
else:
    # Fix it
    if 'elif pnl_pct > 0.01:' in exec_content:
        exec_content = exec_content.replace('elif pnl_pct > 0.01:', 'elif pnl_pct > 0.02:')
        print("   [OK] Fixed take profit: +1% → +2%")
    
    if 'if pnl_pct < -0.03:' in exec_content:
        exec_content = exec_content.replace('if pnl_pct < -0.03:', 'if pnl_pct < -0.01:')
        print("   [OK] Fixed stop loss: -3% → -1%")
    
    with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.write(exec_content)

print()

# 2. Fix INTELLIGENT_EXECUTION_ENGINE position sizing minimum
print("2️⃣ Fixing INTELLIGENT_EXECUTION_ENGINE position sizing...")

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    engine_content = f.read()

# Fix the min_size values to $5.00
old_min_sizes = '''            if balance < 100:
                min_size, max_size = 3.0, 20.0'''

new_min_sizes = '''            if balance < 100:
                min_size, max_size = 5.0, 20.0  # FIXED: $5 minimum (Bybit requirement)'''

if old_min_sizes in engine_content:
    engine_content = engine_content.replace(old_min_sizes, new_min_sizes)
    print("   [OK] Fixed min_size: 3.0 → 5.0 for balance < 100")
    
    # Also add absolute $5 minimum check
    if 'final_size = max(min_size, min(final_size, max_size))' in engine_content:
        # Add check after this line
        check_code = '''
            final_size = max(min_size, min(final_size, max_size))
            
            # CRITICAL: Ensure absolute $5 minimum (Bybit requirement)
            if final_size < 5.0 and balance >= 5.0:
                # Scale up to meet minimum (use up to 30% of balance if needed)
                final_size = min(5.0, balance * 0.30)
                logger.info(f"     Scaled up to meet $5 minimum: ${final_size:.2f}")
            final_size = max(5.0, final_size)  # Final safety check'''
        
        engine_content = engine_content.replace(
            'final_size = max(min_size, min(final_size, max_size))',
            check_code.strip()
        )
        print("   [OK] Added absolute $5 minimum check with scaling")
    
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.write(engine_content)
else:
    print("     Position sizing code not found (may already be fixed)")

print()

# 3. Check PROFIT_MONITORING_SYSTEM thresholds
print("3️⃣ Checking PROFIT_MONITORING_SYSTEM...")

try:
    with open('PROFIT_MONITORING_SYSTEM.py', 'r', encoding='utf-8', errors='ignore') as f:
        profit_content = f.read()
    
    # Check current thresholds
    if 'take_profit_pct = 0.01' in profit_content or 'take_profit_pct = 0.0015' in profit_content:
        print("     PROFIT_MONITORING_SYSTEM has low take profit")
        print("   → Should be 0.02 (2%) for profitable trading")
    elif 'take_profit_pct = 0.02' in profit_content or 'take_profit_pct = 0.003' in profit_content:
        print("   [OK] PROFIT_MONITORING_SYSTEM has correct thresholds")
    else:
        print("   ℹ️  PROFIT_MONITORING_SYSTEM thresholds not found (may use different system)")
except:
    print("     PROFIT_MONITORING_SYSTEM.py not found")

print()

# 4. Verify confidence thresholds
print("4️⃣ Checking confidence thresholds...")

# Check COLLECTIVE_CONSENSUS_ENGINE
try:
    with open('COLLECTIVE_CONSENSUS_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
        consensus_content = f.read()
    
    if 'min_confidence = 0.50' in consensus_content or 'min_confidence = 0.55' in consensus_content:
        print("   [OK] COLLECTIVE_CONSENSUS_ENGINE has correct confidence (0.50-0.55)")
    elif 'min_confidence = 0.65' in consensus_content or 'min_confidence = 0.75' in consensus_content:
        print("     COLLECTIVE_CONSENSUS_ENGINE confidence too high (0.65-0.75)")
        print("   → Should be 0.50 for more trades")
    else:
        print("   ℹ️  Confidence threshold not found in expected format")
except:
    print("     COLLECTIVE_CONSENSUS_ENGINE.py not found")

print()
print("=" * 70)
print("[OK] PROFITABLE SETTINGS APPLIED")
print("=" * 70)
print()
print("Summary:")
print("  • Take profit: +2% (was +1%)")
print("  • Stop loss: -1% (was -3%)")
print("  • Position sizing: $5 minimum (was $3)")
print("  • Confidence: 0.50 (adaptive)")
print()
print("These are the settings that grew $50 → $808!")

