#!/usr/bin/env python3
import sys
import os
import asyncio
import ccxt.async_support as ccxt

async def chunked_sell():
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
        bal = await exchange.fetch_balance()
        atom_amt = float(bal.get('ATOM', {}).get('free', 0))
        print(f"Total ATOM: {atom_amt}")
        
        # Sell in chunks of 5 to avoid "EC_ReachMarketPriceLimit"
        chunk_size = 5.0
        while atom_amt >= 1.0:
            to_sell = min(atom_amt, chunk_size)
            # Precision check
            to_sell_str = exchange.amount_to_precision(symbol, to_sell)
            print(f"Selling chunk: {to_sell_str}...")
            
            try:
                order = await exchange.create_order(symbol, 'market', 'sell', float(to_sell_str), params={'category': 'spot'})
                print(f"Order Success: {order['id']}")
            except Exception as e:
                print(f"Chunk failed: {e}")
            
            await asyncio.sleep(3) # Wait for fill/liquidity
            bal = await exchange.fetch_balance()
            atom_amt = float(bal.get('ATOM', {}).get('free', 0))
            print(f"Remaining ATOM: {atom_amt} | New USDT: {bal.get('USDT', {}).get('free')}")
            
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(chunked_sell())
