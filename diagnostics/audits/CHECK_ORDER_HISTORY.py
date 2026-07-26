#!/usr/bin/env python3
"""
CHECK ORDER HISTORY - Find out why orders are being cancelled
"""
import sys
import os
import asyncio
import ccxt.async_support as ccxt
import json

async def check_order_history():
    api_key = os.getenv('BYBIT_TESTNET_API_KEY')
    api_secret = os.getenv('BYBIT_TESTNET_API_SECRET')
    
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)

    try:
        print("=== RECENT ORDER HISTORY ===")
        
        # Get order history
        response = await exchange.privateGetV5OrderHistory({
            'category': 'spot',
            'symbol': 'ATOMUSDT'
        })
        
        orders = response.get('result', {}).get('list', [])
        
        for o in orders[:5]:
            print(f"\nOrder: {o['orderId']}")
            print(f"  Side: {o['side']}, Type: {o['orderType']}")
            print(f"  Qty: {o['qty']}, Price: {o['price']}")
            print(f"  Status: {o['orderStatus']}")
            print(f"  Filled: {o['cumExecQty']}, Value: {o['cumExecValue']}")
            print(f"  Reject Reason: {o.get('rejectReason', 'None')}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(check_order_history())
