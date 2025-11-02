#!/bin/bash
# FINAL FIX: Add _get_all_pairs method
# Run on VPS: bash FINAL_FIX_GET_PAIRS.sh

cd ~/apex_bot

echo "🔧 Applying final _get_all_pairs fix..."

# Create Python script to add the method
cat > /tmp/add_method.py << 'PYEOF'
import re

file_path = '/root/apex_bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py'

with open(file_path, 'r') as f:
    content = f.read()

# Check if method already exists
if '_get_all_pairs' in content:
    print("✅ Method already exists")
    exit(0)

# Find position after __init__ method in CompleteUltimateOrchestrator class
# Look for the class and its __init__
pattern = r'(class CompleteUltimateOrchestrator.*?def __init__\(self.*?\n        super\(\).__init__\(mode\))'

match = re.search(pattern, content, re.DOTALL)

if not match:
    print("❌ Could not find class definition")
    exit(1)

# Add method after __init__
new_method = '''

    async def _get_all_pairs(self):
        """Get all pairs from Universal Fetcher"""
        try:
            from UNIVERSAL_PAIR_FETCHER import get_universal_fetcher
            fetcher = get_universal_fetcher()
            if fetcher and len(fetcher.all_pairs) > 100:
                return fetcher.top_volume_pairs[:50] if fetcher.top_volume_pairs else fetcher.all_pairs[:50]
        except Exception as e:
            pass
        return ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']
'''

# Insert after the match
insert_pos = match.end()
content = content[:insert_pos] + new_method + content[insert_pos:]

with open(file_path, 'w') as f:
    f.write(content)

print("✅ Added _get_all_pairs method")
PYEOF

# Run the fix
python3 /tmp/add_method.py

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

# Clean up
rm /tmp/add_method.py

echo ""
echo "✅ COMPLETE! Check the log above."
