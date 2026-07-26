#!/usr/bin/env python3
"""Force sell ALL dust assets to USDT - no minimums check on testnet"""
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

print("=== FORCE CONSOLIDATING ALL ASSETS TO USDT ===")

bal = ex.fetch_balance()
total_recovered = 0

for asset, amount in bal['free'].items():
    if asset == 'USDT' or amount <= 0:
        continue
    
    symbol = f'{asset}/USDT'
    try:
        # Try to sell
        ticker = ex.fetch_ticker(symbol)
        price = ticker['last']
        value = amount * price
        
        if value < 0.01:
            print(f"Skip {asset}: ${value:.4f} too small")
            continue
            
        print(f"Selling {amount:.8f} {asset} (~${value:.2f})...")
        
        # Force sell with very small precision
        try:
            order = ex.create_order(symbol, 'market', 'sell', amount)
            print(f"  [OK] SUCCESS: {order['id']}")
            total_recovered += value
        except Exception as e:
            # Try with smaller amount
            market = ex.market(symbol)
            min_amt = market['limits']['amount']['min']
            if min_amt and amount < min_amt:
                print(f"  [X] Below min: {amount} < {min_amt}")
            else:
                print(f"  [X] Failed: {e}")
    except Exception as e:
        print(f"  [X] {asset}: {e}")

print(f"\n=== ESTIMATED RECOVERED: ${total_recovered:.2f} ===")

# Check final balance
new_bal = ex.fetch_balance()
print(f"=== FINAL USDT BALANCE: ${new_bal['USDT']['total']:.2f} ===")
