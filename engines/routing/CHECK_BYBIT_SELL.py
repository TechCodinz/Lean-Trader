#!/usr/bin/env python3
import sys
import os
import asyncio
import ccxt.async_support as ccxt
import time

async def check_sell():
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
        
        # 1. Fetch balance
        bal1 = await exchange.fetch_balance()
        print(f"Pre-sell USDT: {bal1.get('USDT', {}).get('free')}")
        print(f"Pre-sell ATOM: {bal1.get('ATOM', {}).get('free')}")
        
        # 2. Sell
        amount = 5.0
        print(f"Selling {amount} ATOM...")
        order = await exchange.create_order(symbol, 'market', 'sell', amount, params={'category': 'spot'})
        print(f"Order ID: {order['id']}")
        
        # 3. Wait
        print("Waiting 5 seconds for settlement...")
        await asyncio.sleep(5)
        
        # 4. Fetch balance again
        bal2 = await exchange.fetch_balance()
        print(f"Post-sell USDT: {bal2.get('USDT', {}).get('free')}")
        print(f"Post-sell ATOM: {bal2.get('ATOM', {}).get('free')}")
        
        # 5. Check trades
        trades = await exchange.fetch_my_trades(symbol)
        if trades:
            last_trade = trades[-1]
            print(f"Last trade: {last_trade['side']} {last_trade['amount']} @ {last_trade['price']}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(check_sell())
