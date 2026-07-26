
import sys
# Force stdout to utf-8 safe
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

try:
    from BYBIT_EXECUTION_BRIDGE import get_bybit_bridge
    bridge = get_bybit_bridge()
    
    # 1. Balance
    bal = bridge.check_balance()
    print(f"BALANCE_CHECK: {bal}")
    
    # 2. Closed Orders (Proof of trading)
    # We access the internal exchange object for this
    orders = bridge.exchange.fetch_closed_orders(limit=10)
    print(f"RECENT_ORDERS_COUNT: {len(orders)}")
    
    for o in orders[:5]:
        symbol = o.get('symbol', 'UNKNOWN')
        side = o.get('side', 'unknown')
        amount = o.get('filled', 0)
        cost = o.get('cost', 0)
        status = o.get('status', 'unknown')
        print(f"ORDER: {side} {symbol} | Filled: {amount} | Cost: ${cost} | Status: {status}")

except Exception as e:
    print(f"ERROR: {e}")
