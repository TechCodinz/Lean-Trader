
import ccxt
import os
from dotenv import load_dotenv
import json

load_dotenv('/root/bot/.env')

exchange = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
    'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
    'sandbox': True,
})

print("Fetching open orders...")
orders = exchange.fetch_open_orders()
print(f"Total Open Orders: {len(orders)}")

for order in orders:
    print(f" - {order['symbol']} {order['side']} {order['amount']} @ {order['price']} (Type: {order['type']})")
