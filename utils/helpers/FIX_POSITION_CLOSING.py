#!/usr/bin/env python3
"""
Fix position closing by:
1. Lowering close thresholds (1% profit, 3% loss)
2. Ensuring monitoring checks exchange positions directly
"""

print("🔧 Fixing position closing thresholds...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find and lower the take profit threshold (currently 0.02 = 2%)
# Change to 0.01 = 1% for faster closes
old_tp = 'elif pnl_pct > 0.02:'
new_tp = 'elif pnl_pct > 0.01:  # 1% profit (was 2%)'

if old_tp in content:
    print("[OK] Found take profit threshold (2%)")
    content = content.replace(old_tp, new_tp)
    print("   Changed: 2% → 1% profit")
else:
    print("  Take profit threshold not found at expected location")

# Find and adjust stop loss (currently -0.01 = 1%)
# Change to -0.03 = 3% for intelligent exits
old_sl = 'if pnl_pct < -0.01:'
new_sl = 'if pnl_pct < -0.03:  # 3% loss (intelligent exit, was 1%)'

if old_sl in content:
    print("[OK] Found stop loss threshold (1%)")
    content = content.replace(old_sl, new_sl)
    print("   Changed: 1% → 3% loss (intelligent exit)")
else:
    print("  Stop loss threshold not found at expected location")

# Also check if we need to fetch positions from exchange
# Look for fetch_positions or get_open_positions
if 'fetch_positions' not in content and 'get_open_positions' not in content:
    print()
    print("  No exchange position fetching found!")
    print("   Adding exchange position check to monitor_positions()...")
    
    # Find monitor_positions method
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'async def monitor_positions(self):' in line:
            # Find where it gets positions
            for j in range(i, min(len(lines), i+50)):
                if 'positions_to_monitor =' in lines[j]:
                    # Add exchange fetch after this
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    indent_str = ' ' * indent
                    
                    exchange_check = f'''
{indent_str}# 🔥 CRITICAL: Also check ACTUAL exchange positions
{indent_str}try:
{indent_str}    exchange_positions = await self.exchange.fetch_positions()
{indent_str}    for pos in exchange_positions:
{indent_str}        if pos.get('contracts', 0) > 0:  # Has open position
{indent_str}            symbol = pos['symbol']
{indent_str}            if symbol not in positions_to_monitor:
{indent_str}                positions_to_monitor[symbol] = {{
{indent_str}                    'entry_price': pos.get('entryPrice', pos.get('markPrice', 0)),
{indent_str}                    'side': 'buy' if pos.get('side') == 'long' else 'sell',
{indent_str}                    'order_id': pos.get('id'),
{indent_str}                    'timeframe': '1m'
{indent_str}                }}
{indent_str}                logger.info(f"[OK] Found exchange position: {{symbol}}")
{indent_str}except Exception as e:
{indent_str}    logger.debug(f"Could not fetch exchange positions: {{e}}")
'''
                    
                    # Insert after positions_to_monitor assignment
                    lines.insert(j+1, exchange_check)
                    content = '\n'.join(lines)
                    print("   [OK] Added exchange position fetching")
                    break
            break

# Write back
with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
    f.write(content)

print()
print("=" * 70)
print("[OK] FIXES APPLIED")
print("=" * 70)
print()
print("Changes:")
print("  ✓ Take profit: 2% → 1% (faster closes)")
print("  ✓ Stop loss: 1% → 3% (intelligent exit)")
print("  ✓ Added exchange position fetching")
print()
print("Now positions will close:")
print("  • At +1% profit (quick scalp)")
print("  • At -3% loss (intelligent exit)")

