#!/usr/bin/env python3
"""
Manually add spot position checking to monitor_positions()
"""

print("🔧 Adding spot position checking...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find monitor_positions method
found = False
for i, line in enumerate(lines):
    if 'async def monitor_positions(self):' in line:
        print(f"✅ Found monitor_positions at line {i+1}")
        
        # Find where positions_to_monitor is populated
        for j in range(i, min(len(lines), i+100)):
            if 'positions_to_monitor =' in lines[j] or 'positions_to_monitor.update' in lines[j]:
                print(f"✅ Found positions_to_monitor at line {j+1}")
                
                # Find a good insertion point (after positions are collected)
                # Look for the "if positions_to_monitor:" check
                for k in range(j, min(len(lines), j+30)):
                    if 'if positions_to_monitor:' in lines[k] or 'if len(positions_to_monitor)' in lines[k]:
                        print(f"✅ Found check at line {k+1}")
                        
                        # Insert spot checking BEFORE the check
                        indent = len(lines[k]) - len(lines[k].lstrip())
                        indent_str = ' ' * indent
                        
                        spot_code = f'''
{indent_str}# 🔥 CRITICAL: Check SPOT balance for open positions (fetch_positions is for futures!)
{indent_str}try:
{indent_str}    balance = await self.exchange.fetch_balance()
{indent_str}    # Check all currencies in balance
{indent_str}    for currency, amounts in balance.items():
{indent_str}        if currency in ['info', 'free', 'used', 'total']:
{indent_str}            continue
{indent_str}        
{indent_str}        if isinstance(amounts, dict):
{indent_str}            total = amounts.get('total', 0)
{indent_str}        else:
{indent_str}            total = float(amounts) if amounts else 0
{indent_str}        
{indent_str}        # If we have BTC (or other crypto) holdings, it's an open spot position
{indent_str}        if currency != 'USDT' and total > 0.0001:  # Minimum threshold
{indent_str}            # Create symbol (e.g., BTC -> BTC/USDT)
{indent_str}            symbol = f"{{currency}}/USDT"
{indent_str}            
{indent_str}            if symbol not in positions_to_monitor:
{indent_str}                # Get current price
{indent_str}                try:
{indent_str}                    ticker = await self.exchange.fetch_ticker(symbol)
{indent_str}                    current_price = ticker.get('last', ticker.get('close', 0))
{indent_str}                    
{indent_str}                    # Use current price as entry (approximate - real entry should come from order history)
{indent_str}                    positions_to_monitor[symbol] = {{
{indent_str}                        'entry_price': current_price,
{indent_str}                        'side': 'buy',  # Spot is always long
{indent_str}                        'order_id': None,
{indent_str}                        'timeframe': '1m',
{indent_str}                        'amount': total
{indent_str}                    }}
{indent_str}                    logger.info(f"✅ Found spot position: {{symbol}} ({{total}} {{currency}} @ ~${{current_price:.2f}})")
{indent_str}                except Exception as e:
{indent_str}                    logger.debug(f"Could not get price for {{symbol}}: {{e}}")
{indent_str}except Exception as e:
{indent_str}    logger.debug(f"Could not fetch spot balance: {{e}}")
'''
                        
                        # Insert before the check
                        lines.insert(k, spot_code)
                        print(f"   ✅ Inserted spot checking at line {k+1}")
                        found = True
                        break
                break
        break

if found:
    with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print()
    print("=" * 70)
    print("✅ SUCCESS! Spot position checking added")
    print("=" * 70)
else:
    print()
    print("❌ Could not find insertion point")
    print("   Showing monitor_positions structure...")
    for i, line in enumerate(lines):
        if 'monitor_positions' in line:
            print(f"Line {i+1}: {line.rstrip()}")
            for j in range(i+1, min(len(lines), i+20)):
                print(f"  {j+1}: {lines[j].rstrip()[:80]}")

