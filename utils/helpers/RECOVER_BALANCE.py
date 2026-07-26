#!/usr/bin/env python3
"""Check all assets and sell dust back to USDT"""
import ccxt
import os
from dotenv import load_dotenv
load_dotenv('/root/bot/.env')

ex = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
    'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
    'sandbox': True,
    'options': {'defaultType': 'spot'}
})

bal = ex.fetch_balance()
print('=== ALL ASSETS WITH BALANCE ===')
total_value = 0
assets_to_sell = []

# Get the 'total' dict from balance
for asset, amount in bal['total'].items():
    if amount > 0:
        try:
            if asset == 'USDT':
                value = amount
                print(f'{asset}: {amount:.6f} (${value:.2f})')
            else:
                ticker = ex.fetch_ticker(f'{asset}/USDT')
                value = amount * ticker['last']
                print(f'{asset}: {amount:.6f} (~${value:.2f})')
                free_amount = bal['free'].get(asset, 0)
                if free_amount > 0:
                    assets_to_sell.append((asset, free_amount, value))
            total_value += value
        except Exception as e:
            print(f'{asset}: {amount:.6f} (cant price: {e})')

print(f'\n=== TOTAL PORTFOLIO VALUE: ${total_value:.2f} ===')

# Sell all assets back to USDT
print('\n=== SELLING ALL ASSETS TO USDT ===')
for asset, amount, value in assets_to_sell:
    if value > 1:  # Only sell if worth more than $1
        try:
            symbol = f'{asset}/USDT'
            market = ex.market(symbol)
            min_amount = market.get('limits', {}).get('amount', {}).get('min', 0)
            if amount >= (min_amount or 0):
                print(f'Selling {amount} {asset} (~${value:.2f})...')
                order = ex.create_order(symbol, 'market', 'sell', amount)
                print(f'  SUCCESS: {order["id"]}')
            else:
                print(f'  Skip {asset}: amount {amount} < min {min_amount}')
        except Exception as e:
            print(f'  FAILED {asset}: {e}')

# Check final balance
bal = ex.fetch_balance()
print(f'\n=== FINAL USDT BALANCE: ${bal["USDT"]["total"]:.2f} ===')
