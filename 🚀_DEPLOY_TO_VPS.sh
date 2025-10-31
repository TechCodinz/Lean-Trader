#!/bin/bash
#
# 🚀 DEPLOY QUANTUM APEX TO VPS
#
# This script packages everything and gives you commands to deploy to VPS
#

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║         🚀 QUANTUM APEX VPS DEPLOYMENT PACKAGE 🚀                ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Get VPS details from user
echo "📋 VPS Connection Details:"
echo ""
read -p "VPS IP address: " VPS_IP
read -p "VPS username (default: root): " VPS_USER
VPS_USER=${VPS_USER:-root}
read -p "VPS directory (default: ~/bot): " VPS_DIR
VPS_DIR=${VPS_DIR:-~/bot}

echo ""
echo "✅ Configuration:"
echo "   VPS: $VPS_USER@$VPS_IP"
echo "   Directory: $VPS_DIR"
echo ""

# Create deployment package
echo "📦 Creating deployment package..."
DEPLOY_DIR="quantum_apex_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEPLOY_DIR"

# Core files
echo "  Copying core files..."
CORE_FILES=(
    "COMPLETE_PROFIT_SYSTEM.py"
    "EXECUTION_ORCHESTRATOR.py"
    "HIGH_VOLTAGE_NERVOUS_SYSTEM.py"
    "OMNISCIENT_MARKET_SENSOR.py"
    "PREDICTIVE_NEXT_MOVE_ENGINE.py"
    "STRATEGY_EVOLUTION_ENGINE.py"
    "INFINITE_GROWTH_ENGINE.py"
    "DYNAMIC_LEVERAGE_OPTIMIZER.py"
    "GODMODE_TRADING_CORE.py"
    "QUANTUM_ENHANCEMENTS.py"
    "RUN_BOT.py"
    ".env"
    "accounts.yml"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$DEPLOY_DIR/"
        echo "    ✅ $file"
    else
        echo "    ⚠️  $file (not found, skipping)"
    fi
done

# Create requirements.txt
echo ""
echo "  Creating requirements.txt..."
cat > "$DEPLOY_DIR/requirements.txt" << 'REQS'
ccxt>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
aiohttp>=3.8.0
loguru>=0.7.0
python-dotenv>=1.0.0
REQS
echo "    ✅ requirements.txt"

# Create VPS setup script
echo ""
echo "  Creating VPS setup script..."
cat > "$DEPLOY_DIR/setup_vps.sh" << 'SETUP'
#!/bin/bash
#
# Setup Quantum APEX on VPS
#

echo "🚀 Setting up Quantum APEX Bot on VPS..."
echo ""

# Install system dependencies
echo "1️⃣ Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# Create venv
echo ""
echo "2️⃣ Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo ""
echo "3️⃣ Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: bash start_bot.sh"
SETUP
chmod +x "$DEPLOY_DIR/setup_vps.sh"
echo "    ✅ setup_vps.sh"

# Create start script
echo ""
echo "  Creating start script..."
cat > "$DEPLOY_DIR/start_bot.sh" << 'START'
#!/bin/bash
#
# Start Quantum APEX Bot
#

echo "🚀 Starting Quantum APEX Bot..."
cd "$(dirname "$0")"
source venv/bin/activate

# Check if already running
if pgrep -f "RUN_BOT.py" > /dev/null; then
    echo "⚠️  Bot is already running!"
    echo "   Stop it first: bash stop_bot.sh"
    exit 1
fi

# Start bot
nohup python3 RUN_BOT.py --live > bot.log 2>&1 &
BOT_PID=$!

echo "✅ Bot started! PID: $BOT_PID"
echo ""
echo "📊 Monitor: tail -f bot.log"
echo "🛑 Stop: bash stop_bot.sh"
START
chmod +x "$DEPLOY_DIR/start_bot.sh"
echo "    ✅ start_bot.sh"

# Create stop script
cat > "$DEPLOY_DIR/stop_bot.sh" << 'STOP'
#!/bin/bash
#
# Stop Quantum APEX Bot
#

echo "🛑 Stopping Quantum APEX Bot..."

BOT_PID=$(pgrep -f "RUN_BOT.py")

if [ -z "$BOT_PID" ]; then
    echo "⚠️  Bot is not running"
    exit 0
fi

kill $BOT_PID
sleep 2

if pgrep -f "RUN_BOT.py" > /dev/null; then
    echo "⚠️  Bot didn't stop gracefully, forcing..."
    pkill -9 -f "RUN_BOT.py"
fi

echo "✅ Bot stopped"
STOP
chmod +x "$DEPLOY_DIR/stop_bot.sh"
echo "    ✅ stop_bot.sh"

# Create monitoring script
cat > "$DEPLOY_DIR/monitor.sh" << 'MONITOR'
#!/bin/bash
#
# Monitor Quantum APEX Bot
#

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              🌌 QUANTUM APEX MONITOR 🌌                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running
BOT_PID=$(pgrep -f "RUN_BOT.py")

if [ -z "$BOT_PID" ]; then
    echo "❌ Bot is NOT running"
    echo "   Start it: bash start_bot.sh"
    exit 1
fi

echo "✅ Bot Status: RUNNING (PID: $BOT_PID)"
echo ""

# Show options
echo "Select monitoring mode:"
echo "  1) Live log (all activity)"
echo "  2) APEX activity only"
echo "  3) Trades only"
echo "  4) Errors only"
echo "  5) Last 50 lines"
echo ""
read -p "Choice [1-5]: " choice

case $choice in
    1)
        echo "📊 Live log (Ctrl+C to exit):"
        tail -f bot.log
        ;;
    2)
        echo "⚡ APEX activity (Ctrl+C to exit):"
        tail -f bot.log | grep -E "APEX|⚡|🧬|🔮|💰|🌌"
        ;;
    3)
        echo "💰 Trades only (Ctrl+C to exit):"
        tail -f bot.log | grep -E "EXECUTING|CLOSED|profit|Balance"
        ;;
    4)
        echo "❌ Errors only (Ctrl+C to exit):"
        tail -f bot.log | grep -E "ERROR|FAIL|❌"
        ;;
    5)
        echo "📊 Last 50 lines:"
        tail -50 bot.log
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
MONITOR
chmod +x "$DEPLOY_DIR/monitor.sh"
echo "    ✅ monitor.sh"

# Create status script
cat > "$DEPLOY_DIR/status.sh" << 'STATUS'
#!/bin/bash
#
# Show Quantum APEX Bot Status
#

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              🌌 QUANTUM APEX STATUS 🌌                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running
BOT_PID=$(pgrep -f "RUN_BOT.py")

if [ -z "$BOT_PID" ]; then
    echo "Status: ❌ NOT RUNNING"
    exit 1
fi

echo "Status: ✅ RUNNING (PID: $BOT_PID)"
echo ""

# Show recent activity
echo "Recent Activity (last 20 lines):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -20 bot.log
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Commands:"
echo "  📊 Monitor: bash monitor.sh"
echo "  🛑 Stop: bash stop_bot.sh"
echo "  🔄 Restart: bash stop_bot.sh && bash start_bot.sh"
STATUS
chmod +x "$DEPLOY_DIR/status.sh"
echo "    ✅ status.sh"

# Create README
cat > "$DEPLOY_DIR/README.md" << 'README'
# 🌌 Quantum APEX Trading Bot - VPS Deployment

## Quick Start

1. **Initial Setup** (first time only):
   ```bash
   bash setup_vps.sh
   ```

2. **Configure API Keys**:
   Edit `.env` file with your Gate.io API keys

3. **Start Bot**:
   ```bash
   bash start_bot.sh
   ```

4. **Monitor**:
   ```bash
   bash monitor.sh
   ```

## Commands

- `bash start_bot.sh` - Start the bot
- `bash stop_bot.sh` - Stop the bot
- `bash monitor.sh` - Monitor bot activity
- `bash status.sh` - Quick status check
- `tail -f bot.log` - Raw log file

## System Details

- **APEX Systems**: 5/5 active (73%)
- **Quantum Systems**: 4/4 active (+15% = 88%)
- **Total**: 88% Hyperconscious Implementation

## APEX Features

- ⚡ High Voltage Nervous System (neural processing)
- 👁️ Omniscient Market Sensor (8D awareness)
- 🔮 Predictive Next-Move Engine (3-5 moves ahead)
- 🧬 Strategy Evolution Engine (genetic algorithms)
- ♾️ Infinite Growth Engine (infinite scaling)
- 💰 Dynamic Leverage Optimizer (1x-100x)

## Quantum Features

- 🌌 Quantum Annealing Optimizer
- 🔗 Entanglement Correlation Detector
- 🧠 Meta-Learning Framework
- 🔬 Causal Inference Engine

## Support

Check logs: `tail -f bot.log`
Report issues: Check bot.log for errors
README
echo "    ✅ README.md"

# Create tarball
echo ""
echo "📦 Creating deployment tarball..."
tar -czf "${DEPLOY_DIR}.tar.gz" "$DEPLOY_DIR"
echo "    ✅ ${DEPLOY_DIR}.tar.gz"

# Show deployment commands
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║              ✅ DEPLOYMENT PACKAGE READY! ✅                      ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Package: ${DEPLOY_DIR}.tar.gz"
echo ""
echo "🚀 DEPLOYMENT COMMANDS:"
echo ""
echo "# 1. Copy to VPS:"
echo "scp ${DEPLOY_DIR}.tar.gz $VPS_USER@$VPS_IP:~/"
echo ""
echo "# 2. SSH to VPS:"
echo "ssh $VPS_USER@$VPS_IP"
echo ""
echo "# 3. On VPS, run:"
echo "tar -xzf ${DEPLOY_DIR}.tar.gz"
echo "cd ${DEPLOY_DIR}"
echo "bash setup_vps.sh"
echo "# Edit .env with your API keys"
echo "bash start_bot.sh"
echo ""
echo "# 4. Monitor:"
echo "bash monitor.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Or copy the entire directory:"
echo "scp -r $DEPLOY_DIR $VPS_USER@$VPS_IP:$VPS_DIR"
echo ""
