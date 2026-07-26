
import asyncio
import logging
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DIAGNOSE")

# Add path
sys.path.append('/root/bot')

# Import
try:
    from INTELLIGENT_EXECUTION_ENGINE import get_intelligent_engine
    from CONFIG_LOADER import load_config
    
    async def main():
        print("\n[DIAGNOSTIC START]")
        
        # Load Config
        config = load_config()
        print(f"Config loaded. Testnet? {config.get('paper_trading') or config.get('mode') == 'testnet'}")
        
        # Get Engine
        # We need to mock the exchange object creation or use the one from config
        # Assuming get_intelligent_engine does it if we pass an exchange
        
        # Let's manually create the exchange using the bot's logic
        import ccxt.async_support as ccxt
        
        # Keys for Bybit Testnet (Hardcoded in User's previous artifacts or config?)
        # We'll try to find them in config.
        
        # Actually, let's just try to instantiate the Exchange Router which handles this
        from INTELLIGENT_EXCHANGE_ROUTER import IntelligentExchangeRouter
        router = IntelligentExchangeRouter()
        exchange_id, exchange = await router.get_execution_venue('SOL/USDT')
        
        print(f"\n[EXCHANGE INFO]")
        print(f"Router Selected Venue: {exchange_id}")
        print(f"Exchange Object ID: {exchange.id}")
        
        print(f"\n[BALANCE CHECK]")
        balance = await exchange.fetch_balance()
        if 'USDT' in balance:
            print(f"USDT Free: {balance['USDT']['free']}")
            print(f"USDT Total: {balance['USDT']['total']}")
        
        # Dump all non-zero
        print("\n[ALL ASSETS]")
        for cur, amt in balance.items():
            if isinstance(amt, dict) and amt.get('total', 0) > 0:
                print(f"{cur}: {amt}")
        
        print(f"\n[ERROR SIMULATION]")
        # Check if Gate attributes are set
        if 'gate' in exchange.id:
            print("Is Gate.io")
            # Check params
            print(f"Options: {exchange.options}")
            
        await exchange.close()
        
    asyncio.run(main())

except Exception as e:
    print(f"CRITICAL FAILURE: {e}")
    import traceback
    traceback.print_exc()

