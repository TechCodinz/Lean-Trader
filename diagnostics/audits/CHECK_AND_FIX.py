#!/usr/bin/env python3
"""
Check what code is currently in PROFIT_MONITORING_SYSTEM.py
and apply the appropriate fix
"""

print("="*70)
print("🔍 CHECKING CURRENT CODE")
print("="*70)
print()

try:
    with open('PROFIT_MONITORING_SYSTEM.py', 'r') as f:
        lines = f.readlines()
    
    # Find the relevant section (around stop-loss check)
    for i, line in enumerate(lines):
        if 'Check stop loss' in line:
            print(f"Found 'Check stop loss' at line {i+1}")
            print()
            print("Current code around this area (20 lines before):")
            print("-" * 70)
            start = max(0, i-20)
            for j in range(start, min(i+10, len(lines))):
                print(f"{j+1:4d}: {lines[j]}", end='')
            print("-" * 70)
            print()
            
            # Check if intelligent exit already exists
            context = ''.join(lines[max(0, i-25):i])
            
            if 'INTELLIGENT EXIT' in context:
                print("✅ Intelligent exit code EXISTS")
                
                if 'pnl_pct < -0.01 and pnl_pct > -0.03' in context:
                    print("✅ Has CORRECT logic (exit on -1% to -3% loss)")
                    print()
                    print("👍 NO CHANGES NEEDED!")
                    
                elif 'pnl_pct > 0.001 and pnl_pct < 0.005' in context:
                    print("❌ Has BUGGY logic (exit on positive profit)")
                    print()
                    print("🔧 FIXING NOW...")
                    
                    # Find and replace the buggy logic
                    for k in range(max(0, i-25), i):
                        if 'pnl_pct > 0.001 and pnl_pct < 0.005' in lines[k]:
                            lines[k] = lines[k].replace(
                                'pnl_pct > 0.001 and pnl_pct < 0.005',
                                'pnl_pct < -0.01 and pnl_pct > -0.03'
                            )
                            lines[k] = lines[k].replace('# 0.1-0.5% profit', '# -1% to -3% loss')
                            print(f"   Fixed line {k+1}")
                        
                        # Update the log messages
                        if 'Exiting with +' in lines[k] and 'profit' in lines[k]:
                            lines[k] = lines[k].replace(
                                'Exiting with +{pnl_pct:.2%} profit - avoiding potential -5% loss!',
                                'Exiting at {pnl_pct:.2%} - avoiding -5% stop-loss!'
                            )
                            lines[k] = lines[k].replace('logger.info', 'logger.warning')
                            print(f"   Fixed line {k+1}")
                        
                        if 'danger zone detected' in lines[k]:
                            lines[k] = lines[k].replace(
                                'danger zone detected!',
                                'cutting loss early!'
                            )
                            lines[k] = lines[k].replace('logger.info', 'logger.warning')
                            print(f"   Fixed line {k+1}")
                    
                    # Write the fixed file
                    with open('PROFIT_MONITORING_SYSTEM.py', 'w') as f:
                        f.writelines(lines)
                    
                    print()
                    print("✅ BUG FIXED!")
                    print()
                    print("Changed:")
                    print("  pnl_pct > 0.001 and pnl_pct < 0.005  →  pnl_pct < -0.01 and pnl_pct > -0.03")
                    print("  (Exit on profit) → (Exit on loss)")
                else:
                    print("⚠️ Has different logic - check manually")
                    
            else:
                print("❌ NO intelligent exit code found!")
                print()
                print("Need to ADD the intelligent exit block.")
                print("Insert point: line", i)
                
                # Insert the intelligent exit code
                insert_code = [
                    "                # 🔮 INTELLIGENT EXIT: Exit BEFORE massive stop-loss hits!\n",
                    "                # Exit when loss is -1% to -3% (don't wait for -5% SL!)\n",
                    "                if pnl_pct < -0.01 and pnl_pct > -0.03:  # -1% to -3% loss\n",
                    "                    logger.warning(f\"🔮 INTELLIGENT EXIT: {symbol} cutting loss early!\")\n",
                    "                    logger.warning(f\"   💡 Exiting at {pnl_pct:.2%} - avoiding -5% stop-loss!\")\n",
                    "                    logger.warning(f\"   🎯 Saved {(-0.05 - pnl_pct)*100:.1f}% by exiting early!\")\n",
                    "                    await close_position_at_market(exchange, symbol, entry_price, side, pnl_pct, orchestrator)\n",
                    "                    return\n",
                    "                \n"
                ]
                
                # Insert before stop-loss check
                lines = lines[:i] + insert_code + lines[i:]
                
                with open('PROFIT_MONITORING_SYSTEM.py', 'w') as f:
                    f.writelines(lines)
                
                print("✅ INTELLIGENT EXIT CODE ADDED!")
            
            break
    else:
        print("❌ Could not find 'Check stop loss' in file!")
        print("File may have unexpected structure.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
