#!/usr/bin/env python3
import sys
import os
import asyncio
import ccxt.async_support as ccxt
import json

async def force_sell_atom_fixed():
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
        bal = await exchange.fetch_balance()
        atom_amt = bal.get('ATOM', {}).get('free', 0)
        print(f"Current ATOM: {atom_amt}")
        
        if atom_amt < 1.0:
            print("Not enough ATOM.")
            return

        # Truncate to 2 decimals (common for ATOM on Bybit)
        # Better: use exchange.amount_to_precision
        clean_amt = exchange.amount_to_precision(symbol, atom_amt)
        print(f"Attempting Market SELL of {clean_amt} ATOM...")
        
        try:
            order = await exchange.create_order(symbol, 'market', 'sell', float(clean_amt), params={'category': 'spot'})
            print(f"Order SUCCESS! ID: {order['id']}")
            
            await asyncio.sleep(5)
            bal2 = await exchange.fetch_balance()
            print(f"Final USDT: {bal2.get('USDT', {}).get('free')}")
        except Exception as e:
            print(f"Order Failed: {e}")
            
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(force_sell_atom_fixed())
