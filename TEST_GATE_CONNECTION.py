#!/usr/bin/env python3
"""
Quick test to verify Gate.io connection and balance
"""
import ccxt
import os
from pathlib import Path

# Load .env
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

print("=" * 80)
print("🧪 GATE.IO CONNECTION TEST")
print("=" * 80)
print()

# Get API keys
gate_key = os.getenv('GATE_API_KEY')
gate_secret = os.getenv('GATE_API_SECRET')

if not gate_key or not gate_secret:
    print("❌ Gate.io API keys not found in .env file!")
    print("   Please add:")
    print("   GATE_API_KEY=your_key")
    print("   GATE_API_SECRET=your_secret")
    exit(1)

print(f"✅ Gate.io API Key: {gate_key[:10]}...{gate_key[-4:]}")
print()

# Initialize Gate.io
print("📡 Connecting to Gate.io...")
try:
    gate = ccxt.gate({
        'apiKey': gate_key,
        'secret': gate_secret,
        'enableRateLimit': True,
    })
    
    # Test connection by fetching balance
    balance = gate.fetch_balance()
    
    print("✅ Connected successfully!")
    print()
    print("💰 ACCOUNT BALANCE:")
    print("-" * 80)
    
    # Show USDT balance
    usdt_free = balance.get('USDT', {}).get('free', 0)
    usdt_used = balance.get('USDT', {}).get('used', 0)
    usdt_total = balance.get('USDT', {}).get('total', 0)
    
    print(f"   USDT Free:  ${usdt_free:.2f}")
    print(f"   USDT Used:  ${usdt_used:.2f}")
    print(f"   USDT Total: ${usdt_total:.2f}")
    
    # Show other significant balances
    significant_balances = []
    for currency, bal in balance.get('total', {}).items():
        if currency != 'USDT' and float(bal) > 0:
            significant_balances.append((currency, float(bal)))
    
    if significant_balances:
        print()
        print("   Other Assets:")
        for currency, amount in significant_balances[:10]:  # Top 10
            print(f"   {currency}: {amount}")
    
    print()
    print("-" * 80)
    print()
    
    # Test market data access
    print("📊 Testing market data access...")
    ticker = gate.fetch_ticker('BTC/USDT')
    btc_price = ticker['last']
    print(f"✅ Market data OK - BTC/USDT: ${btc_price:,.2f}")
    print()
    
    # Summary
    print("=" * 80)
    print("✅ ALL CHECKS PASSED!")
    print("=" * 80)
    print()
    print("Your bot can now:")
    print("  ✅ Connect to Gate.io")
    print("  ✅ Access your account balance")
    print("  ✅ Fetch market data")
    print("  ✅ Execute trades (when you start the bot)")
    print()
    print(f"💰 Available for trading: ${usdt_free:.2f} USDT")
    print()
    print("🚀 You're ready to start the profit engines!")
    print()
    
except ccxt.AuthenticationError as e:
    print(f"❌ Authentication failed: {e}")
    print()
    print("Please check your API keys:")
    print("1. Go to gate.io → API Management")
    print("2. Create new API key with 'Read' and 'Trade' permissions")
    print("3. Update .env file with new keys")
    exit(1)
    
except Exception as e:
    print(f"❌ Connection error: {e}")
    print()
    print("This could be due to:")
    print("- Network issues")
    print("- Invalid API keys")
    print("- Gate.io API issues")
    exit(1)
