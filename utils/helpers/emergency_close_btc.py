#!/usr/bin/env python3
import ccxt
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def close_btc_position():
    # Initialize Bybit testnet
    exchange = ccxt.bybit({
        'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
        'secret': os.getenv('BYBIT_TESTNET_SECRET'),
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    })
    exchange.set_sandbox_mode(True)
    
    try:
        # Get balance
        balance = await exchange.fetch_balance()
        btc_balance = balance.get('BTC', {}).get('total', 0)
        
        print(f"Current BTC balance: {btc_balance}")
        
        if btc_balance > 0.00001:  # If we have any BTC
            print(f"SELLING {btc_balance} BTC to USDT...")
            
            # Create market sell order
            order = await exchange.create_market_sell_order('BTC/USDT', btc_balance)
            print(f"Order created: {order}")
            print("BTC POSITION CLOSED!")
        else:
            print("No BTC to sell")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(close_btc_position())
