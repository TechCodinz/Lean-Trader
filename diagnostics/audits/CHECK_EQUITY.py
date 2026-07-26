
import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

try:
    from BYBIT_EXECUTION_BRIDGE import get_bybit_bridge
    bridge = get_bybit_bridge()
    balance = bridge.exchange.fetch_balance()
    
    usdt = balance.get('USDT', {})
    total_usdt = usdt.get('total', 0)
    
    print(f"USDT_FREE: {usdt.get('free', 0)}")
    print(f"USDT_USED: {usdt.get('used', 0)}")
    print(f"USDT_TOTAL: {total_usdt}")
    
    # Estimate total equity including other coins
    total_equity_est = total_usdt
    print("\n[Assets]")
    for coin, amount in balance.get('total', {}).items():
        if amount > 0 and coin != 'USDT':
            print(f"  {coin}: {amount}")
            try:
                ticker = bridge.exchange.fetch_ticker(f"{coin}/USDT")
                val = amount * ticker['last']
                total_equity_est += val
                print(f"    Value: ${val:.2f}")
            except: pass
            
    print(f"\nESTIMATED_TOTAL_EQUITY: ${total_equity_est:.2f}")

except Exception as e:
    print(f"Error: {e}")
