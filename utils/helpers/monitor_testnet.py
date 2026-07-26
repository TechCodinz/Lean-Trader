
import ccxt
import os
from datetime import datetime, timedelta

print("=" * 80)
print("💰 BYBIT TESTNET PROFITABILITY MONITOR")
print("=" * 80)

# Load env
env_vars = {}
with open('/root/bot/.env', 'r') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()

# Connect to Bybit Testnet
bybit = ccxt.bybit({
    'apiKey': env_vars.get('BYBIT_TESTNET_API_KEY', ''),
    'secret': env_vars.get('BYBIT_TESTNET_API_SECRET', '')
})
bybit.set_sandbox_mode(True)  # TESTNET

try:
    # Get current balance
    print("\n[1] CURRENT BALANCE:")
    balance = bybit.fetch_balance()
    usdt = balance.get('USDT', {})
    print(f"  USDT Total: ${usdt.get('total', 0):.2f}")
    print(f"  USDT Free: ${usdt.get('free', 0):.2f}")
    print(f"  USDT Used: ${usdt.get('used', 0):.2f}")
    
    # Show other balances
    print("\n  Other currencies:")
    for currency in balance:
        if currency not in ['info', 'free', 'used', 'total', 'USDT']:
            total = balance[currency].get('total', 0)
            if total > 0:
                print(f"    {currency}: {total:.8f}")
    
    # Get recent trades (last 24h)
    print("\n[2] RECENT TRADES (last 24h):")
    trades = []
    markets = bybit.load_markets()
    
    # Check major pairs
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    total_profit = 0
    trade_count = 0
    
    for symbol in symbols:
        try:
            symbol_trades = bybit.fetch_my_trades(symbol, limit=50)
            if symbol_trades:
                for trade in symbol_trades:
                    # Check if within last 24h
                    trade_time = datetime.fromtimestamp(trade['timestamp'] / 1000)
                    if datetime.now() - trade_time < timedelta(hours=24):
                        trades.append(trade)
                        trade_count += 1
        except:
            pass
    
    if trades:
        print(f"  Found {len(trades)} trades")
        # Show first 10
        for trade in trades[:10]:
            side = trade.get('side', 'unknown')
            price = trade.get('price', 0)
            amount = trade.get('amount', 0)
            symbol = trade.get('symbol', 'unknown')
            print(f"    {symbol}: {side.upper()} @ ${price:.2f} x {amount:.6f}")
    else:
        print("  No trades in last 24h")
    
    # Get open positions
    print("\n[3] OPEN POSITIONS:")
    try:
        positions = bybit.fetch_positions()
        open_positions = [p for p in positions if float(p.get('contracts', 0)) > 0]
        
        if open_positions:
            print(f"  {len(open_positions)} open positions:")
            for pos in open_positions[:10]:
                symbol = pos.get('symbol', 'unknown')
                side = pos.get('side', 'unknown')
                contracts = pos.get('contracts', 0)
                unrealized = pos.get('unrealizedPnl', 0)
                print(f"    {symbol}: {side} {contracts} contracts, PnL: ${unrealized:.2f}")
        else:
            print("  No open positions")
    except Exception as e:
        print(f"  Could not fetch positions: {str(e)[:100]}")
    
    # Check trading status
    print("\n[4] SYSTEM STATUS:")
    import subprocess
    result = subprocess.run(['tail', '-n', '50', '/root/bot/orchestrator.log'], capture_output=True, text=True)
    
    recent_signals = 0
    recent_executions = 0
    
    for line in result.stdout.split('\n'):
        if 'COLLECTIVE SCRUTINY' in line:
            recent_signals += 1
        if 'EXECUTING' in line and 'BUY' in line or 'SELL' in line:
            recent_executions += 1
    
    print(f"  Recent signals (last 50 lines): {recent_signals}")
    print(f"  Recent executions (last 50 lines): {recent_executions}")
    
    # Profitability assessment
    print("\n" + "=" * 80)
    print("PROFITABILITY ASSESSMENT")
    print("=" * 80)
    
    if trade_count > 0:
        print(f"[OK] ACTIVE TRADING - {trade_count} trades in 24h")
    else:
        print("  NO TRADES - System may not be executing")
    
    if usdt.get('total', 0) > 0:
        print(f"[OK] BALANCE PRESENT - ${usdt.get('total', 0):.2f}")
    else:
        print("  LOW BALANCE - May need testnet funds")
    
    if recent_signals > 0:
        print(f"[OK] SIGNALS GENERATING - {recent_signals} signals")
    else:
        print("  NO SIGNALS - Check engine activation")
    
    print("\n💡 TIP: Run this every hour to track profit growth")
    print("💡 Once consistently profitable, switch to LIVE with $20-30!")
    
except Exception as e:
    print(f"\n[X] Error: {e}")
    import traceback
    traceback.print_exc()
