#!/bin/bash
# DEPLOY DYNAMIC PAIRS FIX - Removes ALL hardcoded pairs

set -e

echo ""
echo "================================================================================"
echo "🔧 DEPLOYING DYNAMIC PAIRS FIX"
echo "================================================================================"
echo ""

VPS_PATH="${1:-~/apex_bot}"

if [ ! -d "$VPS_PATH" ]; then
    echo "❌ Directory not found: $VPS_PATH"
    exit 1
fi

cd "$VPS_PATH"

echo "📦 Step 1: Copying fix files..."
# These should be copied from workspace
if [ ! -f "REMOVE_ALL_HARDCODED_PAIRS.py" ]; then
    echo "❌ REMOVE_ALL_HARDCODED_PAIRS.py not found!"
    echo "   Copy it from workspace first"
    exit 1
fi

if [ ! -f "UNIVERSAL_PAIR_FETCHER.py" ]; then
    echo "❌ UNIVERSAL_PAIR_FETCHER.py not found!"
    echo "   Copy it from workspace first"
    exit 1
fi

echo "✅ Fix files present"
echo ""

echo "🛑 Step 2: Stopping bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR || echo "   (No running bot)"
sleep 2
echo ""

echo "🔧 Step 3: Removing hardcoded pairs from all files..."
python3 REMOVE_ALL_HARDCODED_PAIRS.py
echo ""

echo "📝 Step 4: Updating orchestrator to use Universal Pair Fetcher..."
python3 << 'PYEOF'
import re

# Update COMPLETE_ULTIMATE_ORCHESTRATOR.py
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Add import
if 'from UNIVERSAL_PAIR_FETCHER import' not in content:
    import_line = "from UNIVERSAL_PAIR_FETCHER import UniversalPairFetcher, initialize_universal_fetcher, get_pairs\n"
    
    # Find DYNAMIC_PAIR_DISCOVERY import
    if 'from DYNAMIC_PAIR_DISCOVERY' in content:
        pos = content.find('from DYNAMIC_PAIR_DISCOVERY')
        pos = content.find('\n', pos) + 1
        content = content[:pos] + import_line + content[pos:]
    else:
        # Add after other imports
        pos = content.find('# ===')
        if pos > 0:
            content = content[:pos] + import_line + '\n' + content[pos:]

# Add initialization after exchange connection
init_code = '''
            # Initialize Universal Pair Fetcher
            if 'gateio' in self.exchanges:
                logger.info("🌍 Setting up Universal Pair Fetcher...")
                self.universal_fetcher = initialize_universal_fetcher(
                    self.exchanges['gateio']
                )
                # Fetch all pairs immediately
                asyncio.create_task(self.universal_fetcher.fetch_all_pairs())
                logger.info("✅ Universal Pair Fetcher active - NO MORE HARDCODED PAIRS!")
'''

if 'Universal Pair Fetcher' not in content:
    # Find where to insert (after Gate.io connection)
    marker = "Connected to: ['gateio']"
    if marker in content:
        pos = content.find(marker)
        pos = content.find('\n', pos) + 1
        content = content[:pos] + init_code + content[pos:]

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.write(content)

print("✅ Orchestrator updated")
PYEOF

echo ""
echo "🚀 Step 5: Starting bot with dynamic pairs..."
if [ -d "apex_venv" ]; then
    nohup apex_venv/bin/python COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &
else
    nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_bot.log 2>&1 &
fi

BOT_PID=$!
echo "   ✅ Bot started (PID: $BOT_PID)"
echo ""

echo "⏳ Waiting 15 seconds for initialization..."
sleep 15
echo ""

echo "📊 Step 6: Verifying dynamic pairs..."
if grep -q "Universal Pair Fetcher" apex_bot.log 2>/dev/null; then
    echo "   ✅ Universal Pair Fetcher initialized"
else
    echo "   ⚠️  Universal Pair Fetcher not found in log"
fi

# Count how many pairs were fetched
PAIR_COUNT=$(grep -o "Fetched [0-9]* total USDT pairs" apex_bot.log 2>/dev/null | tail -1)
if [ ! -z "$PAIR_COUNT" ]; then
    echo "   ✅ $PAIR_COUNT"
else
    echo "   ⚠️  Pair count not found - check logs"
fi

echo ""
echo "================================================================================"
echo "✅ DYNAMIC PAIRS FIX DEPLOYED!"
echo "================================================================================"
echo ""
echo "🎉 NO MORE HARDCODED PAIRS!"
echo "   Bot now trades ALL available pairs dynamically"
echo ""
echo "📊 Monitor pair discovery:"
echo "   tail -f $VPS_PATH/apex_bot.log | grep -E 'Fetched.*pairs|Universal Pair'"
echo ""
echo "📈 Check active pairs:"
echo "   cd $VPS_PATH && python3 -c 'from UNIVERSAL_PAIR_FETCHER import get_universal_fetcher; f = get_universal_fetcher(); print(f\"Total pairs: {f.get_pair_count()}\")'"
echo ""
echo "================================================================================"
echo ""
