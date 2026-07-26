
import ccxt
import time
import json
import os
from dotenv import load_dotenv

load_dotenv('/root/bot/.env')

def fetch_testnet_pairs():
    print("🌍 Connecting to Bybit Testnet...")
    exchange = ccxt.bybit({
        'apiKey': os.getenv('BYBIT_TESTNET_API_KEY'),
        'secret': os.getenv('BYBIT_TESTNET_API_SECRET'),
        'options': {'defaultType': 'spot'}
    })
    exchange.set_sandbox_mode(True)
    
    # Fetch ALL markets
    markets = exchange.load_markets()
    
    # Filter for active USDT pairs
    active_pairs = []
    for symbol, market in markets.items():
        if '/USDT' in symbol and market['active']:
            active_pairs.append(symbol)
            
    print(f"[OK] Found {len(active_pairs)} ACTIVE Testnet Pairs!")
    
    # Save to a config file that the Scalper can read
    with open('/root/bot/active_testnet_pairs.json', 'w') as f:
        json.dump(active_pairs, f)
        
    print("💾 Saved to active_testnet_pairs.json")
    print("Sample:", active_pairs[:5])
    return active_pairs

if __name__ == "__main__":
    fetch_testnet_pairs()

