#!/usr/bin/env python3
"""
FORCE SELL ATOM AT BID - Take whatever price is available
"""
import sys
import os
import asyncio
import ccxt.async_support as ccxt

async def force_sell_at_bid():
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
        print(f"ATOM to sell: {atom_amt}")
        
        if atom_amt < 1:
            print("Not enough ATOM")
            return
        
        # Get ACTUAL bid price
        ob = await exchange.fetch_order_book(symbol, limit=5)
        bid_price = ob['bids'][0][0]
        bid_qty = ob['bids'][0][1]
        print(f"Best Bid: {bid_price} x {bid_qty}")
        
        # Sell in chunks that match the bid liquidity
        remaining = atom_amt
        total_usdt = 0
        
        while remaining > 0.5:
            # Sell up to what the bid can handle
            to_sell = min(remaining, bid_qty * 0.9)  # 90% of bid to ensure fill
            to_sell = exchange.amount_to_precision(symbol, to_sell)
            sell_price = exchange.price_to_precision(symbol, bid_price)
            
            print(f"Selling {to_sell} ATOM at ${sell_price}...")
            
            try:
                order = await exchange.create_order(
                    symbol, 'limit', 'sell', 
                    float(to_sell), float(sell_price),
                    params={'category': 'spot'}
                )
                print(f"  Order placed: {order['id']}")
                
                # Wait for fill
                await asyncio.sleep(3)
                
                # Check if filled
                order_status = await exchange.fetch_order(order['id'], symbol)
                print(f"  Status: {order_status.get('status')} | Filled: {order_status.get('filled')}")
                
                if order_status.get('status') == 'closed':
                    filled = float(order_status.get('filled', 0))
                    remaining -= filled
                    total_usdt += filled * float(sell_price)
                    print(f"  FILLED! Remaining ATOM: {remaining:.2f}")
                else:
                    # Cancel and try lower
                    await exchange.cancel_order(order['id'], symbol)
                    bid_price *= 0.95  # Go 5% lower
                    print(f"  Not filled, trying lower price: {bid_price}")
                    
            except Exception as e:
                print(f"  Error: {e}")
                bid_price *= 0.95
            
            # Refresh order book
            ob = await exchange.fetch_order_book(symbol, limit=5)
            if ob['bids']:
                bid_price = ob['bids'][0][0]
                bid_qty = ob['bids'][0][1]
        
        # Final balance
        await asyncio.sleep(2)
        bal = await exchange.fetch_balance()
        print(f"\n=== FINAL BALANCE ===")
        print(f"USDT: ${bal.get('USDT', {}).get('free', 0):.2f}")
        print(f"ATOM: {bal.get('ATOM', {}).get('free', 0):.4f}")
        print(f"Estimated recovered: ${total_usdt:.2f}")
        
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(force_sell_at_bid())
