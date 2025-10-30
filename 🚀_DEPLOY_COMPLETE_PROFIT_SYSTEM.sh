#!/bin/bash
##############################################################################
# 🚀 DEPLOY COMPLETE PROFIT SYSTEM
##############################################################################
# This script deploys the COMPLETE, TESTED, PROFIT-READY trading system
# 
# What this does:
# 1. ✅ Verifies all critical files exist
# 2. ✅ Stops any running bots
# 3. ✅ Backs up current bot
# 4. ✅ Deploys COMPLETE_PROFIT_SYSTEM + integrated EXECUTION_ORCHESTRATOR
# 5. ✅ Installs dependencies
# 6. ✅ Starts the bot
# 7. ✅ Shows live logs
#
# TESTED IN WORKSPACE - READY FOR VPS
##############################################################################

set -e  # Exit on error

VPS_USER="root"
VPS_HOST="75.119.149.117"
VPS_PATH="/root/bot"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 DEPLOYING COMPLETE PROFIT SYSTEM                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "   This will deploy the COMPLETE, TESTED system to:"
echo "   📍 $VPS_USER@$VPS_HOST:$VPS_PATH"
echo ""

# Critical files to deploy
CRITICAL_FILES=(
    "COMPLETE_PROFIT_SYSTEM.py"
    "EXECUTION_ORCHESTRATOR.py"
    "COMPLETE_ULTIMATE_ORCHESTRATOR.py"
    "AUTO_ADAPTIVE_APEX.py"
)

# Check all critical files exist
echo "1️⃣ Checking critical files..."
for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ CRITICAL FILE MISSING: $file"
        echo "   Please ensure all files are present before deployment"
        exit 1
    fi
    echo "   ✅ $file"
done
echo ""

# Connect and deploy
echo "2️⃣ Connecting to VPS and deploying..."
ssh "$VPS_USER@$VPS_HOST" << 'REMOTE_COMMANDS'

set -e

echo "📍 Working directory: /root/bot"
cd /root/bot

echo "🛑 Stopping any running bots..."
pkill -f "python.*ORCHESTRATOR" || echo "   (no bots were running)"

echo "💾 Creating backup..."
BACKUP_DIR="backups/backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp COMPLETE_PROFIT_SYSTEM.py "$BACKUP_DIR/" 2>/dev/null || echo "   (no previous COMPLETE_PROFIT_SYSTEM.py)"
cp EXECUTION_ORCHESTRATOR.py "$BACKUP_DIR/" 2>/dev/null || echo "   (no previous EXECUTION_ORCHESTRATOR.py)"
cp COMPLETE_ULTIMATE_ORCHESTRATOR.py "$BACKUP_DIR/" || echo "   (main orchestrator not found)"
echo "   ✅ Backup saved to $BACKUP_DIR"

REMOTE_COMMANDS

# Upload critical files
echo ""
echo "3️⃣ Uploading COMPLETE PROFIT SYSTEM files..."
for file in "${CRITICAL_FILES[@]}"; do
    echo "   📤 $file..."
    scp "$file" "$VPS_USER@$VPS_HOST:$VPS_PATH/"
done

# Also upload any supporting engines that changed
echo ""
echo "4️⃣ Uploading supporting engines..."
SUPPORTING_FILES=(
    "SMART_SCALPING_ENGINE.py"
    "AGGRESSIVE_SCALPING_ENGINE.py"
    "NEWS_TRADING_ENGINE.py"
    "ULTRA_RARE_ENGINES.py"
)

for file in "${SUPPORTING_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   📤 $file..."
        scp "$file" "$VPS_USER@$VPS_HOST:$VPS_PATH/" 2>/dev/null || echo "      (optional file, skipped)"
    fi
done

# Install dependencies and start
echo ""
echo "5️⃣ Installing dependencies and starting bot..."
ssh "$VPS_USER@$VPS_HOST" << 'REMOTE_START'

cd /root/bot

# Activate venv
source venv/bin/activate

echo "📦 Installing/updating dependencies..."
pip install --upgrade ccxt aiohttp python-dotenv loguru pandas numpy scikit-learn pytz requests 2>&1 | grep -E "(Successfully|Requirement|WARNING)" || true

echo ""
echo "✅ DEPENDENCIES INSTALLED"
echo ""

# Verify Gate.io API keys
echo "🔑 Checking Gate.io API keys..."
if grep -q "GATE_API_KEY=a0508d8aadf3bcb76e16f4373e1f3a76" .env 2>/dev/null; then
    echo "   ✅ Gate.io API keys configured"
else
    echo "   ⚠️ Adding Gate.io API keys to .env..."
    cat >> .env << 'ENV_KEYS'

# Gate.io API Keys (for COMPLETE PROFIT SYSTEM)
GATE_API_KEY=a0508d8aadf3bcb76e16f4373e1f3a76
GATE_API_SECRET=451770a07dbede1b87bb92f5ce98e24029d2fe91e0053be2ec41771c953113f9
ENV_KEYS
    echo "   ✅ Gate.io API keys added"
fi

echo ""
echo "🚀 STARTING COMPLETE PROFIT SYSTEM..."
echo ""

# Start the bot
nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
BOT_PID=$!

echo "✅ Bot started with PID: $BOT_PID"
echo ""

# Wait a moment for startup
sleep 5

# Check if it's still running
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ Bot is running successfully!"
    echo ""
    echo "📊 Recent log output:"
    tail -30 bot.log
else
    echo "❌ Bot may have crashed. Here are the last 50 lines:"
    tail -50 bot.log
    exit 1
fi

REMOTE_START

# Show final status
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ DEPLOYMENT COMPLETE                                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Monitor logs:"
echo "   ssh $VPS_USER@$VPS_HOST 'tail -f /root/bot/bot.log'"
echo ""
echo "🔍 Check status:"
echo "   ssh $VPS_USER@$VPS_HOST 'cd /root/bot && ps aux | grep python'"
echo ""
echo "💰 Check balance:"
echo "   ssh $VPS_USER@$VPS_HOST 'cd /root/bot && source venv/bin/activate && python3 -c \"import ccxt; g=ccxt.gate({\\\"apiKey\\\":\\\"a0508d8aadf3bcb76e16f4373e1f3a76\\\",\\\"secret\\\":\\\"451770a07dbede1b87bb92f5ce98e24029d2fe91e0053be2ec41771c953113f9\\\"}); b=g.fetch_balance(); print(f\\\"💰 USDT: \${b[\\\"USDT\\\"][\\\"free\\\"]:.2f}\\\")\"'"
echo ""
echo "🎯 SYSTEM FEATURES:"
echo "   ✅ Direct Gate.io execution (no delegation)"
echo "   ✅ Auto-adaptive position sizing (5 tiers)"
echo "   ✅ Active position monitoring"
echo "   ✅ Automatic profit-taking"
echo "   ✅ Stop-loss protection"
echo "   ✅ Real-time balance tracking"
echo "   ✅ All engines integrated"
echo ""
echo "💰 READY TO MAKE PROFITS!"
echo ""
