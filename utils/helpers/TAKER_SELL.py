#!/usr/bin/env python3
"""
TAKER SELL - Force immediate execution with opposite side orderbook
"""
import sys
import os
import asyncio
import ccxt.async_support as ccxt

async def taker_sell():
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
        
        # Get balance
        bal = await exchange.fetch_balance()
        atom_amt = float(bal.get('ATOM', {}).get('free', 0))
        print(f"ATOM available: {atom_amt}")
        
        # Get order book
        ob = await exchange.fetch_order_book(symbol, limit=5)
        print(f"Best Bid: {ob['bids'][0] if ob['bids'] else 'None'}")
        print(f"Best Ask: {ob['asks'][0] if ob['asks'] else 'None'}")
        
        if atom_amt < 1:
            print("Not enough ATOM")
            return
        
        # Try to sell just 1 ATOM as a test
        test_amount = 1.0
        
        # Method 1: Pure market order
        print(f"\n--- Attempting MARKET SELL of {test_amount} ATOM ---")
        try:
            order = await exchange.create_order(
                symbol, 'market', 'sell', test_amount,
                params={'category': 'spot'}
            )
            print(f"Market Order ID: {order['id']}")
            
            # Check order status
            await asyncio.sleep(2)
            status = await exchange.fetch_order(order['id'], symbol)
            print(f"Status: {status['status']} | Filled: {status['filled']}")
            
        except Exception as e:
            print(f"Market order failed: {e}")
        
        # Final balance
        await asyncio.sleep(2)
        bal = await exchange.fetch_balance()
        print(f"\nFinal USDT: {bal.get('USDT', {}).get('free', 0)}")
        print(f"Final ATOM: {bal.get('ATOM', {}).get('free', 0)}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(taker_sell())
