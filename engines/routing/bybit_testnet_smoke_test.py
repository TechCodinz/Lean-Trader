#!/usr/bin/env python3
"""
bybit_testnet_smoke_test.py
Quick smoke test for Bybit testnet execution
Run this BEFORE starting the orchestrator to verify everything works
"""

import ccxt
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("=" * 80)
print("BYBIT TESTNET SMOKE TEST")
print(f"Time: {datetime.now().isoformat()}")
print("=" * 80)

# Step 1: Load credentials
print("\n1. LOADING CREDENTIALS...")
api_key = os.getenv('BYBIT_TESTNET_API_KEY')
api_secret = os.getenv('BYBIT_TESTNET_API_SECRET')

if not api_key:
    print("   [X] BYBIT_TESTNET_API_KEY not found in .env")
    print("\n   Add to .env:")
    print("   BYBIT_TESTNET_API_KEY=your_key_here")
    exit(1)

if not api_secret:
    print("   [X] BYBIT_TESTNET_API_SECRET not found in .env")
    print("\n   Add to .env:")
    print("   BYBIT_TESTNET_API_SECRET=your_secret_here")
    exit(1)

print(f"   [OK] API Key: {api_key[:8]}...")
print(f"   [OK] API Secret: {api_secret[:8]}...")

# Step 2: Initialize exchange
print("\n2. INITIALIZING BYBIT TESTNET...")
try:
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {'defaultType': 'spot'},
        'enableRateLimit': True
    })
    
    # CRITICAL: Enable sandbox/testnet mode
    exchange.set_sandbox_mode(True)
    
    print(f"   [OK] Exchange initialized")
    print(f"   Endpoint: {exchange.urls['api']}")
    print(f"   Testnet mode: {exchange.sandbox}")
    
except Exception as e:
    print(f"   [X] Initialization failed: {e}")
    exit(1)

# Step 3: Fetch balance
print("\n3. FETCHING BALANCE...")
try:
    balance = exchange.fetch_balance()
    
    print(f"   [OK] Balance fetched")
    
    # Show USDT balance
    usdt = balance.get('USDT', {})
    usdt_free = usdt.get('free', 0)
    usdt_total = usdt.get('total', 0)
    usdt_used = usdt.get('used', 0)
    
    print(f"\n   USDT Balances:")
    print(f"   - Free: ${usdt_free:.2f}")
    print(f"   - Used: ${usdt_used:.2f}")
    print(f"   - Total: ${usdt_total:.2f}")
    
    # Show all non-zero balances
    print(f"\n   Non-zero balances:")
    found_any = False
    for currency, bal in balance['total'].items():
        if bal > 0:
            print(f"   - {currency}: {bal}")
            found_any = True
    
    if not found_any:
        print(f"   (none - account is empty)")
    
    if usdt_free < 10:
        print(f"\n    INSUFFICIENT BALANCE FOR TRADING")
        print(f"   Minimum recommended: $100 USDT")
        print(f"   Current: ${usdt_free:.2f} USDT")
        print(f"\n   Request testnet funds:")
        print(f"   1. Go to https://testnet.bybit.com")
        print(f"   2. Login with your testnet account")
        print(f"   3. Request testnet USDT from faucet/support")
    
except Exception as e:
    print(f"   [X] Balance fetch failed: {e}")
    exit(1)

# Step 4: Fetch market info
print("\n4. FETCHING MARKET INFO...")
try:
    ticker = exchange.fetch_ticker('BTC/USDT')
    
    print(f"   [OK] Market data accessible")
    print(f"   BTC/USDT Price: ${ticker['last']:,.2f}")
    print(f"   24h Volume: ${ticker.get('quoteVolume', 0):,.0f}")
    
except Exception as e:
    print(f"   [X] Market fetch failed: {e}")
    exit(1)

# Step 5: Get market limits
print("\n5. CHECKING ORDER LIMITS...")
try:
    markets = exchange.load_markets()
    btc_market = markets.get('BTC/USDT')
    
    if btc_market:
        limits = btc_market.get('limits', {})
        amount_min = limits.get('amount', {}).get('min', 0)
        cost_min = limits.get('cost', {}).get('min', 0)
        
        print(f"   [OK] Market limits retrieved")
        print(f"   Minimum order amount: {amount_min} BTC")
        print(f"   Minimum order cost: ${cost_min:.2f}")
    
except Exception as e:
    print(f"   [X] Limits check failed: {e}")

# Step 6: Test order (dry-run only if balance > 0)
print("\n6. TEST ORDER CHECK...")

if usdt_free >= 20:
    print(f"   Balance sufficient for test order")
    print(f"    SKIPPING ACTUAL ORDER PLACEMENT (manual approval required)")
    print(f"\n   To place a real test order:")
    print(f"   1. Verify testnet mode is active")
    print(f"   2. Use exchange.create_order('BTC/USDT', 'market', 'buy', amount)")
else:
    print(f"    Insufficient balance for test order")
    print(f"   Need: $20+ USDT")
    print(f"   Have: ${usdt_free:.2f} USDT")

# Summary
print("\n" + "=" * 80)
print("SMOKE TEST SUMMARY")
print("=" * 80)

print("\n[OK] Credentials: VALID")
print(f"[OK] Connection: WORKING")
print(f"[OK] Testnet mode: ENABLED")
print(f"[OK] Market data: ACCESSIBLE")

if usdt_free >= 100:
    print(f"[OK] Balance: SUFFICIENT (${usdt_free:.2f})")
    print(f"\n>> READY TO TRADE!")
elif usdt_free >= 10:
    print(f" Balance: LOW (${usdt_free:.2f}) - recommend $100+")
    print(f"\n⚡ Can trade but with limited capital")
else:
    print(f"[X] Balance: INSUFFICIENT (${usdt_free:.2f})")
    print(f"\n[X] CANNOT TRADE - REQUEST TESTNET FUNDS FIRST")

print("\n" + "=" * 80)
