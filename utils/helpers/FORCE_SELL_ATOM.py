#!/usr/bin/env python3
import sys
import os
import asyncio
import ccxt.async_support as ccxt
import json

async def force_sell_atom():
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
        bal = await exchange.fetch_balance()
        atom_amt = bal.get('ATOM', {}).get('free', 0)
        print(f"Current ATOM: {atom_amt}")
        
        if atom_amt < 1.0:
            print("Not enough ATOM to sell.")
            return

        # 2. Try raw V5 Order
        print(f"Attempting Market SELL of {atom_amt} ATOM via V5 API...")
        # amount needs to be string for precision?
        # Bybit V5 Spot Market Sell: qty is base currency
        params = {
            'category': 'spot',
            'symbol': 'ATOMUSDT',
            'side': 'Sell',
            'orderType': 'Market',
            'qty': str(atom_amt),
        }
        
        try:
            response = await exchange.privatePostV5OrderCreate(params)
            print("Raw V5 Response:")
            print(json.dumps(response, indent=2))
            
            order_id = response.get('result', {}).get('orderId')
            if order_id:
                print(f"Polling order {order_id}...")
                for _ in range(5):
                    await asyncio.sleep(2)
                    order_status = await exchange.privateGetV5OrderHistory({'category': 'spot', 'orderId': order_id})
                    res = order_status.get('result', {}).get('list', [])
                    if res:
                        print(f"Status: {res[0]['orderStatus']} | Filled: {res[0]['cumExecQty']}")
                        if res[0]['orderStatus'] == 'Filled':
                            break
                    else:
                        print("Order not found in history yet...")
        except Exception as e:
            print(f"Raw V5 Order Failed: {e}")

        # 3. Final Balance
        await asyncio.sleep(3)
        bal2 = await exchange.fetch_balance()
        print(f"Final USDT: {bal2.get('USDT', {}).get('free')}")
        print(f"Final ATOM: {bal2.get('ATOM', {}).get('free', 0)}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(force_sell_atom())
