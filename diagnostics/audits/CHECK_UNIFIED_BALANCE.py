#!/usr/bin/env python3
import sys
import os
import asyncio
import ccxt.async_support as ccxt
import json

async def check_unified_balance():
    api_key = os.getenv('BYBIT_TESTNET_API_KEY')
    api_secret = os.getenv('BYBIT_TESTNET_API_SECRET')
    
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
    })
    exchange.set_sandbox_mode(True)

    try:
        print("Checking various balance types...")
        for btype in ['spot', 'unified', 'contract']:
            try:
                bal = await exchange.fetch_balance({'type': btype})
                print(f"--- TYPE: {btype} ---")
                # print(json.dumps(bal.get('USDT', {}), indent=2))
                usdt = bal.get('USDT', {})
                print(f"USDT: {usdt}")
                atom = bal.get('ATOM', {})
                print(f"ATOM: {atom}")
            except Exception as e:
                print(f"Failed to fetch {btype}: {e}")
                
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(check_unified_balance())
