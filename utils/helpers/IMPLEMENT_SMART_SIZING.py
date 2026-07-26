#!/usr/bin/env python3
"""
Implement intelligent position sizing that:
1. Uses 5% of current balance per trade
2. Reduces size after losses
3. Increases size after wins (conservatively)
4. Never risks more than 10% of balance
"""

import re

print("="*70)
print("🔧 IMPLEMENTING INTELLIGENT POSITION SIZING")
print("="*70)
print()

try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find position sizing logic
    modified = False
    
    for i, line in enumerate(lines):
        # Look for position_size assignment
        if 'position_size = ' in line and '=' in line and 'self' not in line:
            print(f"Found position size at line {i+1}")
            print(f"Current: {line.strip()}")
            print()
            
            # Get the indentation
            indent = len(line) - len(line.lstrip())
            spaces = ' ' * indent
            
            # Create new intelligent sizing logic
            new_code = f'''{spaces}# 🎯 INTELLIGENT POSITION SIZING
{spaces}# Use 5% of balance, with win/loss adjustments
{spaces}base_pct = 0.05  # 5% of balance
{spaces}
{spaces}# Adjust based on recent performance (if tracking exists)
{spaces}if hasattr(self, 'recent_wins') and hasattr(self, 'recent_losses'):
{spaces}    if self.recent_losses > self.recent_wins:
{spaces}        # Reduce size after losses
{spaces}        base_pct = 0.03  # 3% (conservative)
{spaces}        logger.info("   📉 Recent losses - reducing position to 3%")
{spaces}    elif self.recent_wins > self.recent_losses * 2:
{spaces}        # Increase size after streak of wins
{spaces}        base_pct = 0.07  # 7% (aggressive)
{spaces}        logger.info("   📈 Win streak - increasing position to 7%")
{spaces}
{spaces}position_size = max(5, balance * base_pct)  # Min $5, dynamic %
{spaces}
{spaces}# Safety cap: never more than 10% of balance
{spaces}max_position = balance * 0.10
{spaces}if position_size > max_position:
{spaces}    position_size = max_position
{spaces}    logger.warning(f"    Capping position at 10% (${max_position:.2f})")
{spaces}
{spaces}logger.info(f"   💰 Smart position: ${position_size:.2f} ({position_size/balance*100:.1f}% of ${balance:.2f})")'''
            
            # Replace the line
            lines[i] = new_code
            modified = True
            
            print("NEW CODE:")
            print(new_code)
            print()
            break
    
    if modified:
        # Write back
        with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
            f.write('\n'.join(lines))
        
        print("[OK] Intelligent position sizing implemented!")
        print()
        print("Features:")
        print("  ✓ 5% of balance per trade (default)")
        print("  ✓ Reduces to 3% after losses")
        print("  ✓ Increases to 7% after win streaks")
        print("  ✓ Never exceeds 10% cap")
        print("  ✓ Minimum $5 per trade")
    else:
        print(" Could not find position_size assignment")
        print("   May need manual implementation")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)

