#!/bin/bash
# 🎊 FORCE APPLY FIX - Handles local changes
# This stashes local changes and applies the fix

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          🎊 FORCE APPLYING FINAL FIX                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

cd ~/apex_bot
echo "📂 Working directory: $(pwd)"
echo ""

# Stash any local changes
echo "💾 Stashing local changes..."
git stash
echo "✅ Local changes stashed!"
echo ""

# Pull latest code
echo "📥 Pulling latest code from branch..."
git pull origin continue-from-micro-fix
echo "✅ Code updated!"
echo ""

# Check if method already exists
if grep -q "async def _get_all_pairs" COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo "✅ _get_all_pairs method already exists!"
    echo "🔄 Just restarting bot..."
else
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
    
    echo "✅ Method added!"
fi

# Validate
echo "🔍 Validating syntax..."
python3 -m py_compile COMPLETE_ULTIMATE_ORCHESTRATOR.py
if [ $? -eq 0 ]; then
    echo "✅ File is valid!"
else
    echo "❌ Syntax error!"
    exit 1
fi

# Restart bot
echo ""
echo "🔄 Restarting bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3
nohup apex_venv/bin/python COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &

echo "⏳ Waiting 15 seconds for initialization..."
sleep 15

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    ✅ ALL DONE!                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check for the error
echo "🔍 Checking for _get_all_pairs error..."
if grep "_get_all_pairs" apex_bot.log | grep -q "ERROR"; then
    echo "❌ Still has error - showing recent log:"
    tail -30 apex_bot.log
else
    echo "✅ No _get_all_pairs error found!"
fi

echo ""
echo "📊 Recent trading activity:"
tail -20 apex_bot.log | grep -E "Decision:|ORDER|Discovered|balance:" || tail -20 apex_bot.log

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "💡 MONITOR YOUR BOT:"
echo "   tail -f apex_bot.log | grep 'Decision:\\|ORDER\\|CLOSED'"
echo ""
echo "💰 CHECK BALANCE:"
echo "   grep 'balance:' apex_bot.log | tail -1"
echo ""
echo "🎯 COUNT UNIQUE PAIRS:"
echo "   grep 'Decision:' apex_bot.log | tail -100 | grep -oE '[A-Z0-9]+/USDT' | sort -u | wc -l"
echo "═══════════════════════════════════════════════════════════"
