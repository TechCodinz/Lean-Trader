import os
from dotenv import load_dotenv
load_dotenv()
try:
    import ccxt
    testnet = os.getenv("BYBIT_TESTNET", "true").lower() == "true"
    api_key = os.getenv("BYBIT_TESTNET_API_KEY" if testnet else "BYBIT_API_KEY")
    api_secret = os.getenv("BYBIT_TESTNET_API_SECRET" if testnet else "BYBIT_API_SECRET")
    exchange = ccxt.bybit({'apiKey': api_key, 'secret': api_secret, 'enableRateLimit': True})
    if testnet: exchange.set_sandbox_mode(True)
    
    print("\n  EMERGENCY CLOSE ALL POSITIONS")
    print("═══════════════════════════════════\n")
    
    balance = exchange.fetch_balance()
    
    positions_to_close = []
    for currency, bal in balance['total'].items():
        if currency != 'USDT' and bal > 0:
            try:
                symbol = f"{currency}/USDT"
                market = exchange.market(symbol)
                # Round amount to valid precision
                amount = exchange.amount_to_precision(symbol, bal)
                if float(amount) > 0:
                    positions_to_close.append((symbol, float(amount)))
                    print(f"📋 Will close: {symbol} | Amount: {amount}")
            except Exception as e:
                print(f"[X] Skip {currency}: {e}")
    
    if not positions_to_close:
        print("\n[OK] No positions to close!")
    else:
        print(f"\n🔍 Found {len(positions_to_close)} positions to close")
        response = input("\n  Type 'YES' to close all positions: ")
        
        if response.strip().upper() == 'YES':
            print("\n>> Closing positions...\n")
            for symbol, amount in positions_to_close:
                try:
                    print(f"🔄 Selling {amount} {symbol}...")
                    order = exchange.create_market_sell_order(symbol, amount)
                    print(f"[OK] Closed! Order ID: {order['id']}")
                except Exception as e:
                    print(f"[X] Failed to close {symbol}: {e}")
            
            print("\n[OK] Done! Checking new balance...")
            balance = exchange.fetch_balance()
            usdt = balance.get('USDT', {}).get('total', 0)
            print(f"\n💰 New USDT Balance: ${usdt:.2f}")
        else:
            print("\n[X] Cancelled. No positions closed.")
except Exception as e:
    print(f"[X] ERROR: {e}")
    import traceback
    traceback.print_exc()
