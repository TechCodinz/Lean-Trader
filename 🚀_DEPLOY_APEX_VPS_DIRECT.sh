#!/bin/bash
#
# 🚀 DEPLOY APEX TO VPS - DIRECT METHOD
#
# Run this FROM LOCAL MACHINE (workspace)
# It will copy everything to vmi2817884.contaboserver.net
#

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║         🚀 DEPLOYING APEX TO vmi2817884 🚀                       ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

VPS_HOST="root@vmi2817884.contaboserver.net"

echo "Target VPS: $VPS_HOST"
echo ""
read -p "Continue? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Creating deployment package..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create temp directory
TEMP_DIR="apex_deploy_temp"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Copy files
echo "  Copying files..."
cp COMPLETE_PROFIT_SYSTEM.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ COMPLETE_PROFIT_SYSTEM.py"
cp EXECUTION_ORCHESTRATOR.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ EXECUTION_ORCHESTRATOR.py"
cp HIGH_VOLTAGE_NERVOUS_SYSTEM.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ HIGH_VOLTAGE_NERVOUS_SYSTEM.py"
cp OMNISCIENT_MARKET_SENSOR.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ OMNISCIENT_MARKET_SENSOR.py"
cp PREDICTIVE_NEXT_MOVE_ENGINE.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ PREDICTIVE_NEXT_MOVE_ENGINE.py"
cp STRATEGY_EVOLUTION_ENGINE.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ STRATEGY_EVOLUTION_ENGINE.py"
cp INFINITE_GROWTH_ENGINE.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ INFINITE_GROWTH_ENGINE.py"
cp DYNAMIC_LEVERAGE_OPTIMIZER.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ DYNAMIC_LEVERAGE_OPTIMIZER.py"
cp GODMODE_TRADING_CORE.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ GODMODE_TRADING_CORE.py"
cp QUANTUM_ENHANCEMENTS.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ QUANTUM_ENHANCEMENTS.py"
cp PERSISTENCE_MANAGER.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ PERSISTENCE_MANAGER.py"
cp RUN_BOT.py "$TEMP_DIR/" 2>/dev/null && echo "    ✅ RUN_BOT.py"
cp .env "$TEMP_DIR/" 2>/dev/null && echo "    ✅ .env"

# Create requirements.txt
cat > "$TEMP_DIR/requirements.txt" << 'EOF'
ccxt>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
aiohttp>=3.8.0
loguru>=0.7.0
python-dotenv>=1.0.0
EOF
echo "    ✅ requirements.txt"

# Create tarball
tar -czf apex_deploy.tar.gz "$TEMP_DIR"
echo "    ✅ apex_deploy.tar.gz"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Copying to VPS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

scp apex_deploy.tar.gz "$VPS_HOST":~/
echo "✅ Copied to VPS"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Setting up on VPS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh "$VPS_HOST" << 'REMOTE_COMMANDS'
# Extract
cd ~
tar -xzf apex_deploy.tar.gz

# Move to apex_bot
rm -rf apex_bot
mv apex_deploy_temp apex_bot
cd apex_bot

# Install system deps
echo "Installing system dependencies..."
apt-get update > /dev/null 2>&1
apt-get install -y python3-venv python3-pip > /dev/null 2>&1

# Create venv
echo "Creating Python venv..."
python3 -m venv apex_venv
source apex_venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# Create scripts
cat > start_apex.sh << 'STARTSCRIPT'
#!/bin/bash
cd ~/apex_bot
source apex_venv/bin/activate
nohup python3 RUN_BOT.py --live > apex_bot.log 2>&1 &
echo "✅ APEX Bot started! PID: $!"
echo "📊 Monitor: tail -f ~/apex_bot/apex_bot.log"
STARTSCRIPT
chmod +x start_apex.sh

cat > stop_apex.sh << 'STOPSCRIPT'
#!/bin/bash
pkill -f "RUN_BOT.py"
echo "✅ APEX Bot stopped"
STOPSCRIPT
chmod +x stop_apex.sh

cat > status_apex.sh << 'STATUSSCRIPT'
#!/bin/bash
if pgrep -f "RUN_BOT.py" > /dev/null; then
    echo "✅ APEX Bot is RUNNING"
    tail -20 ~/apex_bot/apex_bot.log
else
    echo "❌ APEX Bot is NOT running"
fi
STATUSSCRIPT
chmod +x status_apex.sh

echo ""
echo "✅ APEX Bot deployed to ~/apex_bot/"
echo "✅ Scripts created: start_apex.sh, stop_apex.sh, status_apex.sh"

REMOTE_COMMANDS

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║              ✅ DEPLOYMENT COMPLETE! ✅                           ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 TO START APEX BOT:"
echo ""
echo "ssh $VPS_HOST"
echo "cd ~/apex_bot"
echo "bash start_apex.sh"
echo ""
echo "📊 TO MONITOR:"
echo "tail -f ~/apex_bot/apex_bot.log"
echo ""
echo "Your 4.1 bot is UNTOUCHED in ~/bot/"
echo ""
