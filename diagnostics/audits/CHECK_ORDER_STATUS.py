#!/usr/bin/env python3
import sys
import os
import asyncio
import ccxt.async_support as ccxt
import json

async def check_order_status():
    api_key = os.getenv('BYBIT_TESTNET_API_KEY')
    api_secret = os.getenv('BYBIT_TESTNET_API_SECRET')
    
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
    })
    exchange.set_sandbox_mode(True)

    try:
        order_id = '2124488617517908736'
        print(f"Checking status for order {order_id}...")
        
        # In Bybit V5, we need the category
        order = await exchange.privateGetV5OrderHistory({'category': 'spot', 'orderId': order_id})
        print(json.dumps(order, indent=2))
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(check_order_status())
