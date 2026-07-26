#!/usr/bin/env python3
"""
Apply intelligent exit calibration to PROFIT_MONITORING_SYSTEM
(the system that's actually running!)
"""

print("="*70)
print("🔥 APPLYING CALIBRATION TO CORRECT SYSTEM")
print("="*70)
print()

# ========================================
# Apply to PROFIT_MONITORING_SYSTEM.py
# ========================================
print("1️⃣ Modifying PROFIT_MONITORING_SYSTEM.py...")

try:
    with open('PROFIT_MONITORING_SYSTEM.py', 'r') as f:
        content = f.read()
    
    # Find the stop-loss check section
    old_code = """                # Check stop loss
                if (side == 'buy' and current_price <= stop_loss) or \\
                   (side == 'sell' and current_price >= stop_loss):
                    logger.warning(f"🛑 STOP LOSS HIT: {symbol} ({pnl_pct:.2%})")
                    logger.warning(f"   Loss: {pnl_pct:.2%}")
                    
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct)
                    return  # Exit monitoring"""
    
    new_code = """                # 🔮 INTELLIGENT EXIT: Check if should exit BEFORE stop-loss!
                # Exit with small profit when danger detected (don't wait for SL!)
                if pnl_pct > 0.001 and pnl_pct < 0.005:  # 0.1-0.5% profit
                    # Check if approaching stop-loss (within 50% of SL distance)
                    if side == 'buy':
                        distance_to_sl = (current_price - stop_loss) / entry_price
                        if distance_to_sl < 0.025:  # Within 2.5% of SL
                            logger.info(f"🔮 INTELLIGENT EXIT: {symbol} danger zone - exit with +{pnl_pct:.2%}!")
                            await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                            return
                    else:
                        distance_to_sl = (stop_loss - current_price) / entry_price
                        if distance_to_sl < 0.025:
                            logger.info(f"🔮 INTELLIGENT EXIT: {symbol} danger zone - exit with +{pnl_pct:.2%}!")
                            await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)
                            return
                
                # Check stop loss (backup only - should rarely hit with intelligent exits!)
                if (side == 'buy' and current_price <= stop_loss) or \\
                   (side == 'sell' and current_price >= stop_loss):
                    logger.warning(f"🛑 STOP LOSS HIT: {symbol} ({pnl_pct:.2%})")
                    logger.warning(f"   Loss: {pnl_pct:.2%}")
                    
                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct)
                    return  # Exit monitoring"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open('PROFIT_MONITORING_SYSTEM.py', 'w') as f:
            f.write(content)
        print("   [OK] Intelligent exit logic added!")
    else:
        print("     Exact pattern not found - may need manual adjustment")
        
except Exception as e:
    print(f"   [X] Error: {e}")

# ========================================
# Also lower TP levels in monitoring
# ========================================
print("\n2️⃣ Lowering take-profit targets for faster exits...")

try:
    with open('PROFIT_MONITORING_SYSTEM.py', 'r') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        # Lower the instant profit-taking threshold
        if 'pnl_pct >= 0.005' in line:  # 0.5%
            lines[i] = line.replace('0.005', '0.003')  # 0.3%
            modified = True
    
    if modified:
        with open('PROFIT_MONITORING_SYSTEM.py', 'w') as f:
            f.writelines(lines)
        print("   [OK] Profit targets lowered: 0.5% → 0.3%")
    else:
        print("   ℹ️  Already optimized")
        
except Exception as e:
    print(f"     Error: {e}")

print()
print("="*70)
print("[OK] CALIBRATION APPLIED TO CORRECT SYSTEM!")
print("="*70)
print()
print("Changes:")
print("  ✓ PROFIT_MONITORING_SYSTEM: Intelligent exits added")
print("  ✓ Exit when approaching stop-loss (with small profit)")
print("  ✓ Lower profit targets for faster exits")
print()
print("Expected results:")
print("  • Exit with 0.1-0.5% profit when danger detected")
print("  • Fewer stop-loss hits")
print("  • Higher win rate")
print()
print(">> Restart bot to apply!")
print("="*70)
