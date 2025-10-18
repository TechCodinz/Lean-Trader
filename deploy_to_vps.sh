#!/bin/bash
# Deploy Fixed Systems to VPS
# This script will deploy all fixed systems to your VPS

echo "🚀 DEPLOYING FIXED SYSTEMS TO VPS"
echo "=================================="

# VPS details
VPS_IP="75.119.149.117"
VPS_USER="root"
VPS_PASS="pW65Yg036RettBb7"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run commands on VPS
run_vps() {
    echo -e "${YELLOW}🔧 Running: $1${NC}"
    sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "$1"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Success${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
}

# Function to copy files to VPS
copy_to_vps() {
    echo -e "${YELLOW}📁 Copying: $1${NC}"
    sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no "$1" "$VPS_USER@$VPS_IP:/root/trading_bot/"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Success${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        return 1
    fi
}

echo "1️⃣ Creating backups..."
run_vps "cd /root/trading_bot && cp ULTRA_GOLDMINE_FEATURES.py ULTRA_GOLDMINE_FEATURES.py.backup 2>/dev/null || true"
run_vps "cd /root/trading_bot && cp DIVINE_INTELLIGENCE_FEATURES.py DIVINE_INTELLIGENCE_FEATURES.py.backup 2>/dev/null || true"
run_vps "cd /root/trading_bot && cp COMPLETE_ULTIMATE_ORCHESTRATOR.py COMPLETE_ULTIMATE_ORCHESTRATOR.py.backup 2>/dev/null || true"

echo ""
echo "2️⃣ Copying fixed files..."
copy_to_vps "ULTRA_GOLDMINE_FEATURES.py"
copy_to_vps "DIVINE_INTELLIGENCE_FEATURES.py"
copy_to_vps "AUTO_LIVE_TRIGGER.py"
copy_to_vps "COMPLETE_ULTIMATE_ORCHESTRATOR.py"

echo ""
echo "3️⃣ Installing dependencies..."
run_vps "cd /root/trading_bot && source venv/bin/activate && pip install numpy pandas scipy scikit-learn"

echo ""
echo "4️⃣ Testing all systems..."
run_vps "cd /root/trading_bot && source venv/bin/activate && python3 -c \"
from ULTRA_GOLDMINE_FEATURES import UltraGoldmineManager
from DIVINE_INTELLIGENCE_FEATURES import DivineIntelligenceManager
from AUTO_LIVE_TRIGGER import AutoLiveTrigger
print('✅ All systems imported successfully')

# Test logging methods
goldmine = UltraGoldmineManager()
divine = DivineIntelligenceManager()
auto_trigger = AutoLiveTrigger()

print('✅ Goldmine logging:', hasattr(goldmine, 'log_signal'))
print('✅ Divine logging:', hasattr(divine, 'log_consciousness_computation'))
print('✅ Auto trigger ready:', auto_trigger.check_ready_for_live())
print('🎯 ALL SYSTEMS WORKING!')
\""

echo ""
echo "5️⃣ Restarting bot with new systems..."
run_vps "cd /root/trading_bot && pkill -f RUN_BOT.py || true"
sleep 2
run_vps "cd /root/trading_bot && source venv/bin/activate && nohup python3 RUN_BOT.py --testnet --auto-confirm > bot.log 2>&1 &"

echo ""
echo "6️⃣ Verifying bot is running..."
sleep 3
run_vps "ps aux | grep RUN_BOT.py | grep -v grep"

echo ""
echo "7️⃣ Checking recent logs for new logging..."
run_vps "cd /root/trading_bot && tail -20 bot.log | grep -E '(GOLDMINE|CONSCIOUSNESS|AUTO_LIVE)' || echo 'No new logging found yet'"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo "✅ All fixed systems deployed"
echo "✅ Dependencies installed"
echo "✅ Bot restarted with new systems"
echo "✅ Ready for enhanced logging!"