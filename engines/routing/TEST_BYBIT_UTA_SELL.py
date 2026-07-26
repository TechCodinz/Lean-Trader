#!/usr/bin/env python3
import sys
import os
import asyncio
import ccxt.async_support as ccxt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UTA_FIX")

async def test_uta_sell():
    # Load keys from env or placeholder
    # I'll try to find where they are stored or use the ones I suspect
    # Usually they are in the bot environment
    api_key = os.getenv('BYBIT_TESTNET_API_KEY', '8p79jG2K32') # Placeholder from previous context
    api_secret = os.getenv('BYBIT_TESTNET_API_SECRET', 'Jk14949102495105912401590124')
    
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)

    try:
        print("\n--- BYBIT UTA DIAGNOSIS ---")
        balance = await exchange.fetch_balance()
        print(f"USDT: {balance.get('USDT', {})}")
        print(f"ATOM: {balance.get('ATOM', {})}")
        
        symbol = 'ATOM/USDT'
        amount = 1.0 # Test with 1 ATOM
        
        print(f"\nAttempting Market SELL of {amount} {symbol}...")
        try:
            # Bybit UTA often needs 'category': 'spot' in params for createOrder
            order = await exchange.create_order(symbol, 'market', 'sell', amount)
            print("Order SUCCESS!")
            print(order)
        except Exception as e:
            print(f"Order FAILED: {type(e).__name__}: {e}")
            
            print("\nTrying with category: spot...")
            try:
                order = await exchange.create_order(symbol, 'market', 'sell', amount, params={'category': 'spot'})
                print("Order with category:spot SUCCESS!")
                print(order)
            except Exception as e2:
                print(f"Order with category:spot FAILED: {type(e2).__name__}: {e2}")

        # Final balance
        balance = await exchange.fetch_balance()
        print(f"\nFinal USDT: {balance.get('USDT', {})}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(test_uta_sell())
