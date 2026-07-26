#!/usr/bin/env python3
import ccxt
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check_positions():
    exchange = ccxt.bybit({
        'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
        'secret': os.getenv('BYBIT_TESTNET_SECRET'),
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)
    
    try:
        balance = await exchange.fetch_balance()
        print("\n=== BALANCE ===")
        for currency, amounts in balance.items():
            if currency not in ['info', 'free', 'used', 'total', 'timestamp', 'datetime']:
                if isinstance(amounts, dict):
                    total = amounts.get('total', 0)
                    if total > 0:
                        print(f"{currency}: {total}")
        
        # Check specifically for BTC
        btc_balance = balance.get('BTC', {}).get('total', 0)
        usdt_balance = balance.get('USDT', {}).get('total', 0)
        
        print(f"\nBTC: {btc_balance}")
        print(f"USDT: {usdt_balance}")
        
        if btc_balance > 0.000001:
            print(f"\n⚠ FOUND STUCK BTC: {btc_balance}")
            print("Selling ALL BTC to USDT...")
            
            order = await exchange.create_market_sell_order('BTC/USDT', btc_balance)
            print(f"✓ BTC SOLD: {order}")
        else:
            print("\n✓ No BTC position")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(check_positions())
