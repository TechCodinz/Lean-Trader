#!/usr/bin/env python3
"""
Replace fetch_positions() (futures) with spot balance checking
"""

print("🔧 Replacing futures code with spot checking...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find the fetch_positions block (lines 1225-1238)
found = False
for i, line in enumerate(lines):
    if 'exchange_positions = await self.exchange.fetch_positions()' in line:
        print(f"[OK] Found fetch_positions at line {i+1}")
        
        # Find the start of the try block
        start = i - 1
        while start > 0 and 'try:' not in lines[start]:
            start -= 1
        
        # Find the end of the except block
        end = i + 15
        while end < len(lines) and 'except' not in lines[end]:
            end += 1
        # Include the except block
        while end < len(lines) and 'except' in lines[end]:
            end += 1
            if 'logger.debug' in lines[end-1] or 'logger.error' in lines[end-1]:
                break
        
        print(f"   Block from line {start+1} to {end}")
        
        # Get indentation
        indent = len(lines[start]) - len(lines[start].lstrip())
        indent_str = ' ' * indent
        
        # Create spot checking code
        spot_code = f'''{indent_str}# 🔥 CRITICAL: Check SPOT balance for open positions (fetch_positions is for futures!)
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
{indent_str}                    logger.info(f"[OK] Found spot position: {{symbol}} ({{total}} {{currency}} @ ~${{current_price:.2f}})")
{indent_str}                except Exception as e:
{indent_str}                    logger.debug(f"Could not get price for {{symbol}}: {{e}}")
{indent_str}except Exception as e:
{indent_str}    logger.debug(f"Could not fetch spot balance: {{e}}")
'''
        
        # Replace the block
        new_lines = lines[:start] + [spot_code + '\n'] + lines[end:]
        
        with open('EXECUTION_ORCHESTRATOR.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"   [OK] Replaced futures code with spot checking")
        found = True
        break

if found:
    print()
    print("=" * 70)
    print("[OK] SUCCESS! Spot checking added")
    print("=" * 70)
else:
    print()
    print("[X] Could not find fetch_positions block")

