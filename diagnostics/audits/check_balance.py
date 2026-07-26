#!/usr/bin/env python3
"""Quick balance check for Bybit testnet"""
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('BYBIT_TESTNET_API_KEY')
secret = os.getenv('BYBIT_TESTNET_API_SECRET')

print(f"API Key found: {bool(api_key)}")
print(f"Secret found: {bool(secret)}")

if api_key and secret:
    try:
        ex = ccxt.bybit({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        ex.set_sandbox_mode(True)
        
        print("Fetching balance...")
        bal = ex.fetch_balance()
        
        usdt = bal.get('USDT', {})
        print(f"\n=== BYBIT TESTNET BALANCE ===")
        print(f"USDT Total: ${usdt.get('total', 0):.2f}")
        print(f"USDT Free: ${usdt.get('free', 0):.2f}")
        print(f"USDT Used: ${usdt.get('used', 0):.2f}")
        
        # Check for other assets
        print("\n=== OTHER ASSETS ===")
        for asset, info in bal.items():
            if asset not in ['USDT', 'info', 'total', 'used', 'free', 'timestamp', 'datetime']:
                if isinstance(info, dict) and info.get('total', 0) > 0:
                    print(f"{asset}: {info.get('total', 0)}")
                    
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No API keys found!")
