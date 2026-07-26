#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/bot')

import ccxt
import os
from dotenv import load_dotenv

load_dotenv('/root/bot/.env')

print("Connecting to Bybit testnet...")

# Get API keys
api_key = os.getenv('BYBIT_TESTNET_API_KEY') or os.getenv('BYBIT_API_KEY')
secret = os.getenv('BYBIT_TESTNET_SECRET') or os.getenv('BYBIT_SECRET')

if not api_key or not secret:
    print("Checking .env file...")
    with open('/root/bot/.env', 'r') as f:
        for line in f:
            if 'BYBIT' in line and 'KEY' in line:
                print(f"  Found: {line.strip()[:50]}...")
    print("ERROR: Missing API credentials")
    exit(1)

print(f"API Key found: {api_key[:10]}...")

exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': secret,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})
exchange.set_sandbox_mode(True)

try:
    balance = exchange.fetch_balance()
    
    print("\n=== CURRENT BALANCE ===")
    for currency, amounts in balance.items():
        if currency in ['info', 'free', 'used', 'total', 'timestamp', 'datetime']:
            continue
        if isinstance(amounts, dict):
            total = amounts.get('total', 0)
            if total > 0:
                print(f"{currency}: {total}")
    
    # Get BTC balance
    btc_balance = balance.get('BTC', {})
    btc_total = btc_balance.get('total', 0) if isinstance(btc_balance, dict) else 0
    btc_free = btc_balance.get('free', 0) if isinstance(btc_balance, dict) else 0
    
    usdt_balance = balance.get('USDT', {})
    usdt_total = usdt_balance.get('total', 0) if isinstance(usdt_balance, dict) else 0
    
    print(f"\nBTC: {btc_total} (free: {btc_free})")
    print(f"USDT: {usdt_total}")
    
    if btc_free > 0.000001:
        print(f"\n🔥 CLOSING BTC POSITION: Selling {btc_free} BTC...")
        try:
            exchange.load_markets()
            order = exchange.create_market_sell_order('BTC/USDT', btc_free)
            print(f"[OK] BTC SOLD! Order ID: {order.get('id', 'unknown')}")
            
            # Check new balance
            new_balance = exchange.fetch_balance()
            new_usdt = new_balance.get('USDT', {}).get('total', 0)
            print(f"\nNew USDT balance: {new_usdt}")
        except Exception as e:
            print(f"Sell error: {e}")
    else:
        print("\n✓ No BTC to sell")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

