#!/usr/bin/env python3
"""Diagnostic: Check balance and execute test trade"""
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

# Check real balance
bal = ex.fetch_balance()
usdt = bal['USDT']['free']
print(f'REAL TIME USDT: {usdt}')

# Show all balances
print('\nAll non-zero balances:')
for k, v in bal['total'].items():
    if v > 0:
        print(f'  {k}: {v}')

# If enough balance, execute trade
if usdt > 5:
    print('\nExecuting test trade...')
    ticker = ex.fetch_ticker('BTC/USDT')
    price = ticker['last']
    amount = (usdt * 0.5) / price
    print(f'Buying {amount:.8f} BTC at ${price}')
    try:
        order = ex.create_order('BTC/USDT', 'market', 'buy', amount)
        print(f'SUCCESS: {order["id"]} - {order["status"]}')
        
        # Check new balance
        new_bal = ex.fetch_balance()
        print(f'\nNew USDT: {new_bal["USDT"]["free"]}')
        print(f'BTC: {new_bal["BTC"]["total"]}')
    except Exception as e:
        print(f'TRADE FAILED: {e}')
else:
    print(f'\nBalance too low to trade! Need > $5, have ${usdt}')
