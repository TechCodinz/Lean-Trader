
import asyncio
import os
import sys

# Add path to find modules
sys.path.append('/root/bot')

async def check_exchanges():
    try:
        from EXCHANGE_MANAGER import ExchangeManager
        print("Initializing ExchangeManager...")
        em = ExchangeManager()
        # Initialize async exchanges
        if hasattr(em, '_initialize_async_exchanges'):
            await em._initialize_async_exchanges()
        
        print(f"Async Exchanges: {list(em.async_exchanges.keys())}")
        
        if 'bybit' in em.async_exchanges:
            print("✅ Bybit (Live) DETECTED!")
            exchange = em.async_exchanges['bybit']
            try:
                print("Checking Balance on Live Bybit...")
                balance = await exchange.fetch_balance()
                total_usdt = balance.get('USDT', {}).get('total', 0)
                print(f"✅ Bybit Live Balance: ${total_usdt}")
            except Exception as e:
                print(f"❌ Bybit Live Auth Failed: {e}")
        else:
            print("❌ Bybit (Live) NOT FOUND in async_exchanges.")
            
        if 'bybit_testnet' in em.async_exchanges:
            print("✅ Bybit Testnet DETECTED!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_exchanges())
