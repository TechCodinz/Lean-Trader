
from BYBIT_EXECUTION_BRIDGE import get_bybit_bridge
try:
    bridge = get_bybit_bridge()
    print(f'Initial Balance: ${bridge.check_balance()}')
    
    signal = {
        'symbol': 'BTC/USDT',
        'side': 'buy',
        'confidence': 99,
        'target_profit': 0.015
    }
    
    print('Executing signal...')
    result = bridge.execute_signal(signal)
    print(f'Result: {result}')
    
    if result:
        print('Order Success!')
        print(f'Order ID: {result.get("id")}')
    else:
        print('Order Failed (returned None)')
except Exception as e:
    print(f'Error: {e}')
