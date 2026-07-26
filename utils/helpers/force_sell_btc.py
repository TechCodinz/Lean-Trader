#!/usr/bin/env python3
import ccxt
import asyncio
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def sell_all_btc():
    '''Sell ALL BTC on Bybit testnet'''
    exchange = ccxt.bybit({
        'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
        'secret': os.getenv('BYBIT_TESTNET_SECRET'),
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)
    
    try:
        balance = await exchange.fetch_balance()
        btc_total = balance.get('BTC', {}).get('total', 0)
        
        logger.info(f"BTC Balance: {btc_total}")
        
        if btc_total >= 0.000001:  # Bybit minimum
            logger.info(f"Selling {btc_total} BTC...")
            order = await exchange.create_market_sell_order('BTC/USDT', btc_total)
            logger.info(f"SUCCESS: {order}")
            return True
        else:
            logger.warning(f"BTC balance {btc_total} below minimum 0.000001")
            return False
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(sell_all_btc())
    print(f"Result: {result}")
