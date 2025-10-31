#!/bin/bash
#
# 🚀 PULL APEX BOT TO VPS (Separate from 4.1 bot)
#
# This pulls the APEX bot to VPS and sets it up in its own directory
# with its own venv, completely separate from your existing 4.1 bot
#

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║       🚀 PULL QUANTUM APEX TO VPS (SEPARATE SETUP) 🚀            ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
echo "📋 VPS Configuration:"
echo ""
read -p "VPS IP: " VPS_IP
read -p "VPS User (default: root): " VPS_USER
VPS_USER=${VPS_USER:-root}
read -p "APEX Bot Directory (default: ~/apex_bot): " APEX_DIR
APEX_DIR=${APEX_DIR:-~/apex_bot}

echo ""
echo "✅ Configuration:"
echo "   VPS: $VPS_USER@$VPS_IP"
echo "   APEX Directory: $APEX_DIR"
echo "   (This is SEPARATE from your 4.1 bot)"
echo ""

# Confirm
read -p "Continue? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Creating deployment package..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create package directory
PACKAGE_DIR="apex_deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$PACKAGE_DIR"

# Core Python files
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
    "PERSISTENCE_MANAGER.py"
    "RUN_BOT.py"
    ".env"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$PACKAGE_DIR/"
        echo "    ✅ $file"
    fi
done

# Create requirements.txt
echo ""
echo "  Creating requirements.txt..."
cat > "$PACKAGE_DIR/requirements.txt" << 'REQS'
ccxt>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
aiohttp>=3.8.0
loguru>=0.7.0
python-dotenv>=1.0.0
REQS

# Create setup script for VPS
echo ""
echo "  Creating VPS setup script..."
cat > "$PACKAGE_DIR/setup_apex_vps.sh" << 'SETUP'
#!/bin/bash
echo "🚀 Setting up APEX Bot (separate from 4.1 bot)..."
echo ""

# Install system dependencies
echo "1️⃣ Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Create separate venv for APEX
echo ""
echo "2️⃣ Creating APEX virtual environment (separate from 4.1)..."
python3 -m venv apex_venv
source apex_venv/bin/activate

# Install packages
echo ""
echo "3️⃣ Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ APEX Bot setup complete!"
echo ""
echo "   Your APEX bot is in: $(pwd)"
echo "   Your APEX venv is: $(pwd)/apex_venv"
echo "   Your 4.1 bot is UNTOUCHED in its own directory"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: bash start_apex.sh"
SETUP
chmod +x "$PACKAGE_DIR/setup_apex_vps.sh"

# Create start script
cat > "$PACKAGE_DIR/start_apex.sh" << 'START'
#!/bin/bash
echo "🚀 Starting APEX Bot..."
cd "$(dirname "$0")"
source apex_venv/bin/activate

# Check if already running
if pgrep -f "apex.*RUN_BOT.py" > /dev/null; then
    echo "⚠️  APEX Bot is already running!"
    echo "   Stop it first: bash stop_apex.sh"
    exit 1
fi

# Start APEX bot
nohup python3 RUN_BOT.py --live > apex_bot.log 2>&1 &
APEX_PID=$!

echo "✅ APEX Bot started! PID: $APEX_PID"
echo ""
echo "   📊 Monitor: tail -f apex_bot.log"
echo "   🛑 Stop: bash stop_apex.sh"
echo ""
echo "   (Your 4.1 bot is still running separately)"
START
chmod +x "$PACKAGE_DIR/start_apex.sh"

# Create stop script
cat > "$PACKAGE_DIR/stop_apex.sh" << 'STOP'
#!/bin/bash
echo "🛑 Stopping APEX Bot..."

APEX_PID=$(pgrep -f "apex.*RUN_BOT.py")

if [ -z "$APEX_PID" ]; then
    echo "⚠️  APEX Bot is not running"
    exit 0
fi

kill $APEX_PID
sleep 2

if pgrep -f "apex.*RUN_BOT.py" > /dev/null; then
    echo "⚠️  APEX didn't stop gracefully, forcing..."
    pkill -9 -f "apex.*RUN_BOT.py"
fi

echo "✅ APEX Bot stopped"
echo "   (Your 4.1 bot is still running)"
STOP
chmod +x "$PACKAGE_DIR/stop_apex.sh"

# Create monitor script
cat > "$PACKAGE_DIR/monitor_apex.sh" << 'MONITOR'
#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              🌌 APEX BOT MONITOR 🌌                              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

APEX_PID=$(pgrep -f "apex.*RUN_BOT.py")

if [ -z "$APEX_PID" ]; then
    echo "❌ APEX Bot is NOT running"
    exit 1
fi

echo "✅ APEX Bot: RUNNING (PID: $APEX_PID)"
echo ""
echo "Select monitoring mode:"
echo "  1) Live log"
echo "  2) APEX/Quantum activity only"
echo "  3) Trades only"
echo "  4) Last 50 lines"
echo ""
read -p "Choice [1-4]: " choice

case $choice in
    1) tail -f apex_bot.log ;;
    2) tail -f apex_bot.log | grep -E "APEX|⚡|🧬|🔮|💰|🌌" ;;
    3) tail -f apex_bot.log | grep -E "EXECUTING|CLOSED|profit|Balance" ;;
    4) tail -50 apex_bot.log ;;
    *) echo "Invalid choice" ;;
esac
MONITOR
chmod +x "$PACKAGE_DIR/monitor_apex.sh"

# Create README
cat > "$PACKAGE_DIR/README.md" << 'README'
# 🌌 Quantum APEX Trading Bot

## Separate from Your 4.1 Bot

This APEX bot runs in its own directory with its own venv.
Your existing 4.1 bot is UNTOUCHED and continues running separately.

## Setup

```bash
bash setup_apex_vps.sh
# Edit .env with your API keys
bash start_apex.sh
```

## Commands

- `bash start_apex.sh` - Start APEX bot
- `bash stop_apex.sh` - Stop APEX bot
- `bash monitor_apex.sh` - Monitor APEX bot
- `tail -f apex_bot.log` - View logs

## Persistence

APEX bot saves learned knowledge in `bot_data/`:
- Evolved strategies
- Performance history
- Trade logs
- Market knowledge
- Meta-learning data
- Quantum data

This persists across restarts - bot learns and remembers!

## Both Bots Running

You can have both running simultaneously:
- 4.1 bot: in its directory, its venv, its log
- APEX bot: in apex_bot/, apex_venv/, apex_bot.log

Completely separate!
README

# Create tarball
echo ""
echo "📦 Creating tarball..."
tar -czf "${PACKAGE_DIR}.tar.gz" "$PACKAGE_DIR"
echo "    ✅ ${PACKAGE_DIR}.tar.gz"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Copying to VPS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

scp "${PACKAGE_DIR}.tar.gz" "$VPS_USER@$VPS_IP":~/
echo "✅ Copied to VPS"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Setting up on VPS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh "$VPS_USER@$VPS_IP" << REMOTE
# Extract
tar -xzf ${PACKAGE_DIR}.tar.gz

# Move to apex_bot directory
rm -rf $APEX_DIR
mv $PACKAGE_DIR $APEX_DIR
cd $APEX_DIR

# Run setup
bash setup_apex_vps.sh
REMOTE

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║              ✅ APEX BOT DEPLOYED TO VPS! ✅                      ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "APEX Bot Location: $APEX_DIR"
echo "APEX venv: $APEX_DIR/apex_venv"
echo "Your 4.1 bot: UNTOUCHED (still running in its directory)"
echo ""
echo "🚀 TO START APEX BOT:"
echo ""
echo "ssh $VPS_USER@$VPS_IP"
echo "cd $APEX_DIR"
echo "# Edit .env with your API keys"
echo "nano .env"
echo "# Start APEX bot"
echo "bash start_apex.sh"
echo ""
echo "📊 TO MONITOR:"
echo "bash monitor_apex.sh"
echo ""
echo "Both bots can run simultaneously - they're completely separate!"
echo ""
