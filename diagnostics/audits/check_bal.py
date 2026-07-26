#!/usr/bin/env python3
import ccxt, os
from dotenv import load_dotenv
load_dotenv()
ex = ccxt.bybit({
    'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
    'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})
ex.set_sandbox_mode(True)
try:
    bal = ex.fetch_balance()
    print('USDT:', bal.get('USDT', {}))
except Exception as e:
    print(f'Error fetching balance: {e}')
