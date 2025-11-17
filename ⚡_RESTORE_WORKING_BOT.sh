#!/bin/bash
# Restore working bot on VPS

cd ~/apex_bot
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR

echo "Restoring working version..."

# Restore from backup (Nov 14 - was working)
cp COMPLETE_ULTIMATE_ORCHESTRATOR.py.backup systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py 2>/dev/null || echo "Backup not found"
cp EXECUTION_ORCHESTRATOR.py.backup4 EXECUTION_ORCHESTRATOR.py 2>/dev/null || echo "Exec backup not found"

# Keep ONLY the good fixes that work:
# 1. Tuple import
sed -i 's/from typing import Dict, List, Optional$/from typing import Dict, List, Optional, Tuple/' TESTNET_TRAINER.py 2>/dev/null || true

# 2. Sandbox mode  
if ! grep -q "set_sandbox_mode" router.py; then
    sed -i '157a\            if self.testnet:\n                self.ex.set_sandbox_mode(True)\n                _log.info("[router] Testnet enabled")' router.py
fi

# 3. Add missing function
if ! grep -q "get_discovery_engine" DYNAMIC_PAIR_DISCOVERY.py; then
    echo "" >> DYNAMIC_PAIR_DISCOVERY.py
    echo "def get_discovery_engine(exchange, min_volume=50000):" >> DYNAMIC_PAIR_DISCOVERY.py
    echo "    return initialize_pair_discovery(exchange, min_volume)" >> DYNAMIC_PAIR_DISCOVERY.py
fi

# Export keys
export BYBIT_TESTNET=true
export API_KEY=$(grep BYBIT_TESTNET_API_KEY .env | cut -d= -f2)
export API_SECRET=$(grep BYBIT_TESTNET_API_SECRET .env | cut -d= -f2)

# Clear cache
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

echo "✅ Restored + minimal fixes applied"
echo "Starting bot..."

source apex_venv/bin/activate
python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex_restored.log 2>&1 &

sleep 15
tail -f apex_restored.log | grep -E "Total Trades|Profit|Balance"
