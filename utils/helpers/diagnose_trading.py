
import ccxt
import os
import subprocess
from datetime import datetime

print("=" * 80)
print("🔍 COMPREHENSIVE TRADING DIAGNOSTIC")
print("=" * 80)

# Load env
env_vars = {}
with open('/root/bot/.env', 'r') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()

# [1] Check balance
print("\n[1] BALANCE CHECK:")
try:
    bybit = ccxt.bybit({
        'apiKey': env_vars.get('BYBIT_TESTNET_API_KEY', ''),
        'secret': env_vars.get('BYBIT_TESTNET_API_SECRET', '')
    })
    bybit.set_sandbox_mode(True)
    
    balance = bybit.fetch_balance()
    usdt = balance.get('USDT', {}).get('free', 0)
    total = balance.get('USDT', {}).get('total', 0)
    
    print(f"  USDT Free: ${usdt:.2f}")
    print(f"  USDT Total: ${total:.2f}")
    
    if usdt > 0:
        print("  [OK] Balance available for trading")
    else:
        print("    NO FREE USDT - Can't make new trades!")
        
except Exception as e:
    print(f"  [X] Balance check failed: {str(e)[:100]}")

# [2] Test API - can we make orders?
print("\n[2] API TEST - Can place orders?")
try:
    # Try to get markets
    markets = bybit.load_markets()
    print(f"  [OK] Connected to {len(markets)} markets")
    
    # Check if we can query orderbook
    ticker = bybit.fetch_ticker('BTC/USDT')
    print(f"  [OK] Can fetch market data (BTC: ${ticker['last']:.2f})")
    
    # Try to create test order (will fail with insufficient funds if needed)
    print("  Testing order creation capability...")
    try:
        # This will fail but we'll see WHY
        test_order = bybit.create_market_buy_order('BTC/USDT', 0.00001)
        print("  [OK] Order creation works!")
    except ccxt.InsufficientFunds:
        print("  [OK] API works (insufficient funds is expected for tiny order)")
    except Exception as e:
        error_msg = str(e)
        if 'permissions' in error_msg.lower():
            print(f"  [X] API PERMISSION ERROR: {error_msg[:200]}")
        elif 'invalid' in error_msg.lower():
            print(f"  [X] API KEY INVALID: {error_msg[:200]}")
        else:
            print(f"    API Error: {error_msg[:200]}")
            
except Exception as e:
    print(f"  [X] API test failed: {str(e)[:200]}")

# [3] Check orchestrator logs - is it running?
print("\n[3] ORCHESTRATOR STATUS:")
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
if 'COMPLETE_ULTIMATE_ORCHESTRATOR' in result.stdout:
    print("  [OK] Orchestrator running")
else:
    print("  [X] ORCHESTRATOR NOT RUNNING!")

# [4] Check recent logs for signals
print("\n[4] SIGNAL GENERATION (last 100 lines):")
result = subprocess.run(['tail', '-n', '100', '/root/bot/orchestrator.log'], capture_output=True, text=True)

signal_count = 0
execution_count = 0
error_count = 0

for line in result.stdout.split('\n'):
    if 'COLLECTIVE SCRUTINY' in line:
        signal_count += 1
    if 'EXECUTING' in line and ('BUY' in line or 'SELL' in line):
        execution_count += 1
    if 'ERROR' in line or 'Failed' in line:
        error_count += 1

print(f"  Signals generated: {signal_count}")
print(f"  Executions attempted: {execution_count}")
print(f"  Errors: {error_count}")

if signal_count == 0:
    print("  [X] NO SIGNALS - Engines not generating trades!")
elif execution_count == 0:
    print("  [X] SIGNALS BUT NO EXECUTIONS - Execution blocked!")
else:
    print("  [OK] Signals and executions happening")

# [5] Check for specific errors
print("\n[5] ERROR ANALYSIS (last 50 lines):")
result = subprocess.run(['tail', '-n', '50', '/root/bot/orchestrator.log'], capture_output=True, text=True)

balance_errors = 0
api_errors = 0
permission_errors = 0

for line in result.stdout.split('\n'):
    if 'balance too low' in line.lower() or 'insufficient' in line.lower():
        balance_errors += 1
    if 'api' in line.lower() and 'error' in line.lower():
        api_errors += 1
    if 'permission' in line.lower() or 'forbidden' in line.lower():
        permission_errors += 1

if balance_errors > 0:
    print(f"    {balance_errors} balance errors - May need more testnet funds")
if api_errors > 0:
    print(f"    {api_errors} API errors - Check API keys")
if permission_errors > 0:
    print(f"  [X] {permission_errors} permission errors - API keys may lack trading permission")

# [6] Show recent log lines
print("\n[6] RECENT LOGS (last 10 lines):")
result = subprocess.run(['tail', '-n', '10', '/root/bot/orchestrator.log'], capture_output=True, text=True)
print(result.stdout)

# [7] Final diagnosis
print("\n" + "=" * 80)
print("DIAGNOSIS & ACTION ITEMS")
print("=" * 80)

if signal_count == 0:
    print("[X] CRITICAL: No signals being generated")
    print("   → Check if engines are active")
    print("   → Verify market data is flowing")
    print("   → Check engine initialization")
elif execution_count == 0:
    print("[X] CRITICAL: Signals generated but not executing")
    print("   → Check API permissions")
    print("   → Verify exchange can execute trades")
    print("   → Check execution pipeline")
elif balance_errors > 5:
    print("  WARNING: Many balance errors")
    print("   → May need more testnet funds")
elif permission_errors > 0:
    print("[X] CRITICAL: API permission errors")
    print("   → Regenerate API keys with trading permission")
else:
    print("[OK] System appears functional")
    print("   → Trades may be executing slowly")
    print("   → Check longer time period for growth")
