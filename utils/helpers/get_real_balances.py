
import ccxt
import os

print("=" * 80)
print("💰 GETTING ACTUAL BALANCES - ALL EXCHANGES")
print("=" * 80)

# Initialize exchanges from orchestrator code
try:
    # Try importing orchestrator to get exchange initialization
    import sys
    sys.path.insert(0, '/root/bot')
    
    # Read .env directly
    env_vars = {}
    try:
        with open('/root/bot/.env', 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except:
        pass
    
    # Check Gate.io
    if 'GATE_API_KEY' in env_vars and 'GATE_SECRET' in env_vars:
        print("\n[GATE.IO] LIVE MODE:")
        try:
            gate = ccxt.gateio({
                'apiKey': env_vars['GATE_API_KEY'],
                'secret': env_vars['GATE_SECRET'],
                'options': {'defaultType': 'spot'}
            })
            gate.set_sandbox_mode(False)
            
            balance = gate.fetch_balance()
            
            # Show USDT
            usdt = balance.get('USDT', {})
            print(f"  USDT Free: ${usdt.get('free', 0):.2f}")
            print(f"  USDT Used: ${usdt.get('used', 0):.2f}")
            print(f"  USDT Total: ${usdt.get('total', 0):.2f}")
            
            # Show all non-zero balances
            print("\n  Non-zero balances:")
            for currency in balance:
                if currency not in ['info', 'free', 'used', 'total']:
                    total = balance[currency].get('total', 0)
                    if total > 0:
                        free = balance[currency].get('free', 0)
                        used = balance[currency].get('used', 0)
                        print(f"    {currency}: {total:.8f} (free: {free:.8f}, used: {used:.8f})")
        except Exception as e:
            print(f"  Error: {str(e)[:200]}")
    else:
        print("\n[GATE.IO] No API keys")
    
    # Check Bybit
    if 'BYBIT_API_KEY' in env_vars and 'BYBIT_SECRET' in env_vars:
        print("\n[BYBIT] LIVE MODE:")
        try:
            bybit = ccxt.bybit({
                'apiKey': env_vars['BYBIT_API_KEY'],
                'secret': env_vars['BYBIT_SECRET']
            })
            bybit.set_sandbox_mode(False)
            
            balance = bybit.fetch_balance()
            usdt = balance.get('USDT', {})
            print(f"  USDT Total: ${usdt.get('total', 0):.2f}")
        except Exception as e:
            print(f"  Error: {str(e)[:200]}")
    
    # Check Binance
    if 'BINANCE_API_KEY' in env_vars and 'BINANCE_SECRET' in env_vars:
        print("\n[BINANCE] LIVE MODE:")
        try:
            binance = ccxt.binance({
                'apiKey': env_vars['BINANCE_API_KEY'],
                'secret': env_vars['BINANCE_SECRET']
            })
            binance.set_sandbox_mode(False)
            
            balance = binance.fetch_balance()
            usdt = balance.get('USDT', {})
            print(f"  USDT Total: ${usdt.get('total', 0):.2f}")
        except Exception as e:
            print(f"  Error: {str(e)[:200]}")
    
    print("\n" + "=" * 80)
    print("Found API keys for:", list(env_vars.keys()))
    
except Exception as e:
    print(f"Fatal error: {e}")
    import traceback
    traceback.print_exc()
