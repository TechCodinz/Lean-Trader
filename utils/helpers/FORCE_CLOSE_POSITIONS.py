#!/usr/bin/env python3
"""
FORCE CLOSE ALL POSITIONS - Free up locked capital
"""
import ccxt
import asyncio
import os

async def force_close_all_positions():
    """Force close ALL non-USDT positions on Bybit testnet"""
    
    # Initialize Bybit testnet
    exchange = ccxt.bybit({
        'apiKey': os.getenv('BYBIT_TESTNET_API_KEY', 'testnet_key'),
        'secret': os.getenv('BYBIT_TESTNET_SECRET', 'testnet_secret'),
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)
    
    print("🔍 Fetching all balances...")
    balance = await asyncio.to_thread(exchange.fetch_balance)
    
    closed_count = 0
    total_recovered = 0
    
    # Close ALL non-USDT holdings
    for asset, info in balance.items():
        if asset in ['USDT', 'info', 'free', 'used', 'total']:
            continue
            
        if isinstance(info, dict):
            total = info.get('total', 0)
            if total > 0:
                symbol = f"{asset}/USDT"
                
                try:
                    # Get current price
                    ticker = await asyncio.to_thread(exchange.fetch_ticker, symbol)
                    price = ticker.get('last', 0)
                    value = total * price
                    
                    print(f"\n💰 Closing {symbol}:")
                    print(f"   Amount: {total:.8f} {asset}")
                    print(f"   Value: ${value:.2f}")
                    
                    # Market sell ALL
                    order = await asyncio.to_thread(
                        exchange.create_market_sell_order,
                        symbol,
                        total
                    )
                    
                    print(f"   [OK] CLOSED - Order ID: {order.get('id', 'N/A')}")
                    closed_count += 1
                    total_recovered += value
                    
                except Exception as e:
                    error_msg = str(e)
                    if 'minimum' in error_msg.lower() or 'dust' in error_msg.lower():
                        print(f"   💤 Dust position (below minimum): ${value:.4f}")
                    else:
                        print(f"   [X] Error: {error_msg[:100]}")
    
    # Get final balance
    print("\n" + "="*60)
    final_balance = await asyncio.to_thread(exchange.fetch_balance)
    usdt_balance = final_balance.get('USDT', {}).get('free', 0)
    
    print(f"[OK] FORCE CLOSE COMPLETE!")
    print(f"   Closed: {closed_count} positions")
    print(f"   Recovered: ~${total_recovered:.2f}")
    print(f"   💰 Final USDT Balance: ${usdt_balance:.2f}")
    print("="*60)
    
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(force_close_all_positions())
