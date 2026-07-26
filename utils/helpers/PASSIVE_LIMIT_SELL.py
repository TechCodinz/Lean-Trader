#!/usr/bin/env python3
"""
PASSIVE LIMIT SELL - Place at bid and wait for fill
"""
import sys
import os
import asyncio
import ccxt.async_support as ccxt

async def passive_limit():
    api_key = os.getenv('BYBIT_TESTNET_API_KEY')
    api_secret = os.getenv('BYBIT_TESTNET_API_SECRET')
    
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)
    await exchange.load_markets()

    try:
        symbol = 'ATOM/USDT'
        
        # Get best bid
        ob = await exchange.fetch_order_book(symbol, limit=5)
        bid_price = ob['bids'][0][0]
        bid_qty = ob['bids'][0][1]
        print(f"Best Bid: {bid_price} x {bid_qty}")
        
        # Cancel any open orders first
        try:
            open_orders = await exchange.fetch_open_orders(symbol)
            for o in open_orders:
                await exchange.cancel_order(o['id'], symbol)
                print(f"Cancelled order {o['id']}")
        except: pass
        
        # Place a limit sell at EXACTLY the bid price
        amount = min(18.0, bid_qty * 0.95)  # Don't exceed bid depth
        price = bid_price
        
        amount = exchange.amount_to_precision(symbol, amount)
        price = exchange.price_to_precision(symbol, price)
        
        print(f"\nPlacing LIMIT SELL: {amount} ATOM @ ${price}")
        order = await exchange.create_limit_sell_order(
            symbol, float(amount), float(price),
            params={'category': 'spot', 'timeInForce': 'GTC'}
        )
        print(f"Order ID: {order['id']}")
        
        # Wait and check
        print("Waiting for fill...")
        for i in range(10):
            await asyncio.sleep(3)
            try:
                open_orders = await exchange.fetch_open_orders(symbol)
                if not open_orders:
                    print("Order filled!")
                    break
                else:
                    print(f"  Still open... ({i+1}/10)")
            except: pass
        
        # Check final balance
        bal = await exchange.fetch_balance()
        print(f"\nFinal USDT: {bal.get('USDT', {}).get('free', 0)}")
        print(f"Final ATOM: {bal.get('ATOM', {}).get('free', 0)}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(passive_limit())
