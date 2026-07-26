
import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

try:
    from BYBIT_EXECUTION_BRIDGE import get_bybit_bridge
    bridge = get_bybit_bridge()
    bal = bridge.exchange.fetch_balance()
    
    usdt = bal.get('USDT', {}).get('free', 0)
    print(f"USDT_BALANCE: {usdt}")
    
    print("ASSETS_HELD:")
    count = 0
    for coin, details in bal.items():
        if isinstance(details, dict) and 'free' in details:
            amount = details['free']
            if amount > 0 and coin != 'USDT':
                # Check value
                try:
                    ticker = bridge.exchange.fetch_ticker(f"{coin}/USDT")
                    value = amount * ticker['last']
                    if value > 1.0: # Only show significant holdings
                        print(f"  {coin}: {amount} (Value: ${value:.2f})")
                        count += 1
                except:
                    pass
    
    if count == 0:
        print("  [NONE] - All clean!")

except Exception as e:
    print(f"ERROR: {e}")
