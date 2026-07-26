#!/usr/bin/env python3
"""
DEEP ORDER BOOK CHECK - Find ANY tradeable pair on testnet
"""
import sys
import os
import asyncio
import ccxt.async_support as ccxt

async def deep_check():
    api_key = os.getenv('BYBIT_TESTNET_API_KEY')
    api_secret = os.getenv('BYBIT_TESTNET_API_SECRET')
    
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)

    try:
        print("=== DEEP ORDER BOOK CHECK ===")
        
        # Check order books for major pairs
        pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ATOM/USDT', 'XRP/USDT']
        
        for symbol in pairs:
            try:
                ob = await exchange.fetch_order_book(symbol, limit=10)
                best_bid = ob['bids'][0] if ob['bids'] else None
                best_ask = ob['asks'][0] if ob['asks'] else None
                bid_depth = sum([b[1] for b in ob['bids'][:5]]) if ob['bids'] else 0
                ask_depth = sum([a[1] for a in ob['asks'][:5]]) if ob['asks'] else 0
                
                print(f"{symbol}:")
                print(f"  Best Bid: {best_bid}")
                print(f"  Best Ask: {best_ask}")
                print(f"  Bid Depth (5): {bid_depth:.4f}")
                print(f"  Ask Depth (5): {ask_depth:.4f}")
                print()
            except Exception as e:
                print(f"{symbol}: ERROR - {e}")
        
        # Check current balance
        print("=== CURRENT BALANCE ===")
        bal = await exchange.fetch_balance()
        for currency in ['USDT', 'ATOM', 'BTC', 'ETH']:
            info = bal.get(currency, {})
            if info.get('total', 0) > 0:
                print(f"{currency}: {info}")
        
        # Try to fetch open orders
        print("\n=== OPEN ORDERS ===")
        orders = await exchange.fetch_open_orders()
        if orders:
            for o in orders[:5]:
                print(f"  {o['symbol']} {o['side']} {o['amount']} @ {o['price']}")
        else:
            print("  No open orders")
            
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(deep_check())
