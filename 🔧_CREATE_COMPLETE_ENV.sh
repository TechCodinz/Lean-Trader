#!/bin/bash
##############################################################################
# 🔧 CREATE COMPLETE .ENV WITH ALL SETTINGS
# Includes MT5, AI keys, futures, scanner, everything!
##############################################################################

echo "🔧 Creating COMPLETE .env with ALL settings..."

# Remove read-only if set
chmod 644 .env 2>/dev/null

# Copy template
cp .env.COMPLETE_TEMPLATE .env

echo "✅ .env created from complete template!"
echo ""
echo "📝 Now edit .env and add your keys:"
echo ""
echo "nano .env"
echo ""
echo "Required keys to add:"
echo "  1. BYBIT_TESTNET_API_KEY (get from testnet.bybit.com)"
echo "  2. BYBIT_TESTNET_API_SECRET"
echo "  3. AI keys (optional): ANTHROPIC_API_KEY, OPENAI_API_KEY, etc"
echo ""
echo "After editing, protect it:"
echo "  chmod 444 .env"
echo ""
echo "Then restart bot:"
echo "  pkill -f RUN_BOT && nohup python3 RUN_BOT.py > apex.log 2>&1 &"
