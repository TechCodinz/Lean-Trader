#!/bin/bash
# FINAL FIX: Add _get_all_pairs method
# Run on VPS: bash FINAL_FIX_GET_PAIRS.sh

cd ~/apex_bot

echo "🔧 Applying final _get_all_pairs fix..."

# First, check if already fixed
if grep -q "async def _get_all_pairs" COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "✅ Method already exists - no fix needed!"
    echo "🔄 Just restarting bot..."
    pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
    sleep 3
    nohup apex_venv/bin/python COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &
    sleep 5
    tail -20 apex_bot.log
    exit 0
fi

echo "📝 Adding _get_all_pairs method..."

# Use sed to insert the method before _get_account_balance
sed -i '/async def _get_account_balance/i\
    async def _get_all_pairs(self):\
        """Get all pairs from Universal Fetcher"""\
        try:\
            from UNIVERSAL_PAIR_FETCHER import get_universal_fetcher\
            fetcher = get_universal_fetcher()\
            if fetcher and len(fetcher.all_pairs) > 100:\
                return fetcher.top_volume_pairs[:50] if fetcher.top_volume_pairs else fetcher.all_pairs[:50]\
        except Exception as e:\
            pass\
        return ['"'"'BTC/USDT'"'"', '"'"'ETH/USDT'"'"', '"'"'SOL/USDT'"'"', '"'"'BNB/USDT'"'"', '"'"'XRP/USDT'"'"']\
\
' COMPLETE_ULTIMATE_ORCHESTRATOR.py

# Validate
python3 -m py_compile COMPLETE_ULTIMATE_ORCHESTRATOR.py
if [ $? -eq 0 ]; then
    echo "✅ File is valid"
else
    echo "❌ Syntax error!"
    exit 1
fi

# Restart bot
echo "🔄 Restarting bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3
nohup apex_venv/bin/python COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &

echo "⏳ Waiting 10 seconds..."
sleep 10

# Check for error
if grep "_get_all_pairs" apex_bot.log | grep -q "ERROR"; then
    echo "❌ Still has error"
    tail -20 apex_bot.log
else
    echo "✅ Fixed!"
    tail -20 apex_bot.log
fi

echo ""
echo "✅ COMPLETE! Check the log above."
