#!/usr/bin/env python3
"""Close BTC position NOW and take profit"""
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

print("=== CLOSING BTC POSITION FOR PROFIT ===")

# Check BTC position
bal = ex.fetch_balance()
btc_amount = bal['BTC']['total']

if btc_amount > 0:
    ticker = ex.fetch_ticker('BTC/USDT')
    price = ticker['last']
    value = btc_amount * price
    print(f'BTC Position: {btc_amount} BTC = ${value:.2f}')
    print(f'Current Price: ${price:.2f}')
    print('\nSelling NOW for profit...')
    try:
        order = ex.create_order('BTC/USDT', 'market', 'sell', btc_amount)
        print(f'[OK] SUCCESS: Sold {btc_amount} BTC')
        print(f'Order ID: {order["id"]}')
        print(f'Status: {order["status"]}')
        
        # Check new balance
        new_bal = ex.fetch_balance()
        new_usdt = new_bal['USDT']['total']
        print(f'\n💰 New USDT Balance: ${new_usdt:.2f}')
        print(f'Profit Realized: ${new_usdt - 2.56:.2f}')
    except Exception as e:
        print(f'[X] FAILED: {e}')
else:
    print('No BTC position to close')
    print(f'Current USDT: ${bal["USDT"]["total"]:.2f}')
