#!/usr/bin/env python3
import sys
import os
import asyncio
import ccxt.async_support as ccxt

async def limit_sell_atom():
    api_key = os.getenv('BYBIT_TESTNET_API_KEY')
    api_secret = os.getenv('BYBIT_TESTNET_API_SECRET')
    
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)

    try:
        symbol = 'ATOM/USDT'
        # Get current price
        ticker = await exchange.fetch_ticker(symbol)
        price = ticker['last']
        print(f"Current price: {price}")
        
        # Limit sell at 10% below market to ensure fill
        limit_price = price * 0.9
        amount = 1.0
        
        print(f"Attempting Limit SELL of {amount} ATOM @ {limit_price}...")
        order = await exchange.create_order(symbol, 'limit', 'sell', amount, limit_price, params={'category': 'spot'})
        print(f"Order ID: {order['id']} | Status: {order['status']}")
        
        await asyncio.sleep(5)
        bal = await exchange.fetch_balance()
        print(f"USDT: {bal.get('USDT', {}).get('free')}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(limit_sell_atom())
