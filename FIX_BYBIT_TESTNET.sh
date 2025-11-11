#!/bin/bash
cd ~/apex_bot

echo "=========================================="
echo "🧪 BYBIT TESTNET FIX"
echo "=========================================="
echo ""

echo "1️⃣ Checking current .env..."
echo ""
if [ -f .env ]; then
    echo "📋 Current Bybit Testnet keys:"
    grep "BYBIT_TESTNET" .env | sed 's/=.*/=****HIDDEN****/'
    echo ""
    
    # Check if keys exist
    if ! grep -q "BYBIT_TESTNET_API_KEY" .env || ! grep -q "BYBIT_TESTNET_SECRET" .env; then
        echo "❌ Missing testnet keys!"
        echo ""
        echo "Add these lines to .env:"
        echo ""
        echo "BYBIT_TESTNET_API_KEY=your_key_here"
        echo "BYBIT_TESTNET_SECRET=your_secret_here"
        echo ""
        exit 1
    fi
    
    # Check if keys look valid (not empty, not placeholder)
    KEY=$(grep "BYBIT_TESTNET_API_KEY" .env | cut -d'=' -f2)
    SECRET=$(grep "BYBIT_TESTNET_SECRET" .env | cut -d'=' -f2)
    
    if [ -z "$KEY" ] || [ "$KEY" == "your_key_here" ]; then
        echo "❌ API key is empty or placeholder!"
        echo ""
        echo "Get real testnet keys from:"
        echo "https://testnet.bybit.com"
        echo ""
        exit 1
    fi
    
    echo "✅ Keys are present"
else
    echo "❌ No .env file!"
    exit 1
fi

echo ""
echo "2️⃣ Testing Bybit Testnet connection..."
echo ""

# Create a simple test script
cat > /tmp/test_bybit.py << 'PYEOF'
import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('BYBIT_TESTNET_API_KEY')
secret = os.getenv('BYBIT_TESTNET_SECRET')

print(f"Testing with key: {key[:8]}...{key[-4:]}")
print("")

try:
    exchange = ccxt.bybit({
        'apiKey': key,
        'secret': secret,
        'options': {
            'defaultType': 'swap',
            'testnet': True
        }
    })
    
    # Set testnet URL
    exchange.set_sandbox_mode(True)
    
    print("🔗 Connecting to Bybit testnet...")
    balance = exchange.fetch_balance()
    
    print("✅ CONNECTION SUCCESSFUL!")
    print("")
    print("💰 Testnet Balance:")
    for currency in ['USDT', 'BTC', 'ETH']:
        if currency in balance['total']:
            amt = balance['total'][currency]
            if amt > 0:
                print(f"   {currency}: {amt}")
    
    print("")
    print("🌍 Fetching testnet pairs...")
    markets = exchange.load_markets()
    usdt_pairs = [s for s in markets.keys() if '/USDT' in s]
    print(f"   Found {len(usdt_pairs)} USDT pairs on testnet")
    
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print("")
    print("Possible issues:")
    print("1. API keys are wrong/expired")
    print("2. API keys don't have testnet permissions")
    print("3. Need to regenerate keys at https://testnet.bybit.com")
    print("")
    print("Steps to fix:")
    print("1. Go to: https://testnet.bybit.com")
    print("2. Login/Register")
    print("3. Go to API Management")
    print("4. Create NEW API key")
    print("5. Copy key and secret")
    print("6. Update .env file")
PYEOF

python3 /tmp/test_bybit.py

echo ""
echo "=========================================="
echo "3️⃣ Next Steps"
echo "=========================================="
echo ""
echo "If connection failed:"
echo ""
echo "1. Go to: https://testnet.bybit.com"
echo "2. Login (or register new account)"
echo "3. Click 'API Management'"
echo "4. Create NEW API key with these permissions:"
echo "   ✅ Read-Write"
echo "   ✅ Contract Trading"
echo "   ✅ Spot Trading"
echo "5. Copy the API key and secret"
echo "6. Update .env:"
echo "   nano .env"
echo "   # Replace with NEW keys:"
echo "   BYBIT_TESTNET_API_KEY=your_new_key"
echo "   BYBIT_TESTNET_SECRET=your_new_secret"
echo ""
echo "7. Restart bot:"
echo "   pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR"
echo "   bash START_TESTNET.sh"
echo ""
