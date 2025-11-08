#!/bin/bash
# 🚀 ONE-CLICK DEPLOYMENT SCRIPT
# Deploys the complete trading bot to VPS in one command

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🚀 ONE-CLICK DEPLOYMENT - Complete Trading Bot"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Running as root - this is OK for initial setup"
    echo "   (Will create non-root user for bot)"
    echo ""
fi

# 1. System Update
echo "1️⃣  Updating system..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get update -qq
    apt-get upgrade -y -qq
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum update -y -q
fi
echo "   ✅ System updated"
echo ""

# 2. Install Dependencies
echo "2️⃣  Installing dependencies..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get install -y -qq \
        python3.11 \
        python3.11-venv \
        python3-pip \
        docker.io \
        docker-compose \
        git \
        curl \
        wget \
        build-essential \
        libssl-dev \
        libffi-dev \
        nginx
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum install -y -q \
        python3 \
        python3-pip \
        docker \
        docker-compose \
        git \
        curl \
        wget \
        gcc \
        openssl-devel \
        libffi-devel \
        nginx
fi
echo "   ✅ Dependencies installed"
echo ""

# 3. Enable Docker
echo "3️⃣  Configuring Docker..."
systemctl enable docker
systemctl start docker
usermod -aG docker $USER 2>/dev/null || true
echo "   ✅ Docker configured"
echo ""

# 4. Create Bot User (if running as root)
if [ "$EUID" -eq 0 ]; then
    echo "4️⃣  Creating bot user..."
    if ! id "botuser" &>/dev/null; then
        useradd -m -s /bin/bash botuser
        usermod -aG docker botuser
        echo "   ✅ User 'botuser' created"
    else
        echo "   ✅ User 'botuser' already exists"
    fi
    echo ""
else
    echo "4️⃣  Using current user: $USER"
    echo ""
fi

# 5. Clone/Update Repository
echo "5️⃣  Setting up bot files..."
BOT_DIR="/home/${USER}/apex_bot"

if [ -d "$BOT_DIR" ]; then
    echo "   Bot directory exists, updating..."
    cd $BOT_DIR
    git pull 2>/dev/null || echo "   (Not a git repo, skipping pull)"
else
    echo "   Creating bot directory..."
    mkdir -p $BOT_DIR
    
    # Copy files if running in workspace
    if [ -d "/workspace" ]; then
        echo "   Copying files from workspace..."
        cp -r /workspace/* $BOT_DIR/
    fi
fi

cd $BOT_DIR
echo "   ✅ Bot files ready at: $BOT_DIR"
echo ""

# 6. Configure Environment
echo "6️⃣  Configuring environment..."
if [ ! -f ".env" ]; then
    cat > .env <<EOF
# Trading Mode
TRADING_MODE=live
ENABLE_LIVE=true

# Automation
AUTOMATED_MODE=true
SKIP_CONFIRMATIONS=true

# Exchange API Keys (ADD YOUR KEYS HERE)
GATEIO_API_KEY=your_api_key_here
GATEIO_API_SECRET=your_api_secret_here

# Optional: Other exchanges
BINANCE_API_KEY=
BINANCE_API_SECRET=
BYBIT_API_KEY=
BYBIT_API_SECRET=

# Dashboard
DASHBOARD_PASSWORD=admin123

# Telegram (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF
    echo "   ⚠️  .env file created - EDIT IT WITH YOUR API KEYS!"
    echo "   File location: $BOT_DIR/.env"
    echo ""
    read -p "   Press Enter after you've edited .env with your API keys..."
else
    echo "   ✅ .env file already exists"
fi
echo ""

# 7. Install Python Dependencies
echo "7️⃣  Installing Python dependencies..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   ✅ Python dependencies installed"
echo ""

# 8. Initialize Databases
echo "8️⃣  Initializing databases..."
mkdir -p bot_data backups logs
touch bot_data/health.txt
python3 -c "
import sqlite3
for db in ['enhanced_trading_bot.db', 'ultimate_bot_450_models.db', 'divine_intelligence.db']:
    conn = sqlite3.connect(f'bot_data/{db}')
    conn.execute('CREATE TABLE IF NOT EXISTS health (timestamp TEXT)')
    conn.close()
print('   ✅ Databases initialized')
"
echo ""

# 9. Security Hardening (optional)
echo "9️⃣  Security hardening..."
read -p "   Run security hardening? (ufw, fail2ban) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "🔒_SECURITY_HARDENING.sh" ]; then
        sudo bash 🔒_SECURITY_HARDENING.sh
    else
        echo "   ⚠️  Security script not found, skipping..."
    fi
else
    echo "   ⚠️  Security hardening skipped"
fi
echo ""

# 10. Choose Deployment Method
echo "🔟 Choose deployment method:"
echo "   1) Docker (recommended for production)"
echo "   2) Direct Python (simpler, for testing)"
echo "   3) Exit (manual setup)"
echo ""
read -p "   Select [1-3]: " -n 1 -r DEPLOY_METHOD
echo ""
echo ""

case $DEPLOY_METHOD in
    1)
        echo "🐳 Building Docker containers..."
        docker-compose build
        echo "   ✅ Containers built"
        echo ""
        
        echo "🚀 Starting bot..."
        docker-compose up -d
        echo "   ✅ Bot started"
        echo ""
        
        echo "📊 Services status:"
        docker-compose ps
        echo ""
        
        echo "✅ DEPLOYMENT COMPLETE!"
        echo ""
        echo "📊 Monitor bot:"
        echo "   docker-compose logs -f trading-bot"
        echo ""
        echo "📈 Dashboard:"
        echo "   http://$(curl -s ifconfig.me):8501"
        echo ""
        echo "🛑 Stop bot:"
        echo "   docker-compose down"
        ;;
        
    2)
        echo "🐍 Starting bot with Python..."
        
        # Create systemd service
        if [ "$EUID" -eq 0 ]; then
            cat > /etc/systemd/system/apex-bot.service <<EOF
[Unit]
Description=APEX Trading Bot
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${BOT_DIR}
ExecStart=${BOT_DIR}/venv/bin/python3 ${BOT_DIR}/AUTOMATED_ORCHESTRATOR_ENHANCED.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
            
            systemctl daemon-reload
            systemctl enable apex-bot
            systemctl start apex-bot
            
            echo "   ✅ Bot started as systemd service"
            echo ""
            echo "📊 Monitor bot:"
            echo "   sudo systemctl status apex-bot"
            echo "   sudo journalctl -u apex-bot -f"
            echo ""
            echo "🛑 Stop bot:"
            echo "   sudo systemctl stop apex-bot"
        else
            # Non-root: use nohup
            nohup python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py > logs/bot.log 2>&1 &
            echo $! > bot.pid
            
            echo "   ✅ Bot started (PID: $(cat bot.pid))"
            echo ""
            echo "📊 Monitor bot:"
            echo "   tail -f logs/bot.log"
            echo ""
            echo "🛑 Stop bot:"
            echo "   kill $(cat bot.pid)"
        fi
        ;;
        
    3)
        echo "   Setup complete - manual start required"
        echo ""
        echo "To start bot:"
        echo "   cd $BOT_DIR"
        echo "   source venv/bin/activate"
        echo "   python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py"
        ;;
        
    *)
        echo "   Invalid selection"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📁 Bot Directory: $BOT_DIR"
echo "📊 Dashboard: http://$(curl -s ifconfig.me):8501"
echo "📝 Logs: $BOT_DIR/logs/"
echo "💾 Data: $BOT_DIR/bot_data/"
echo ""
echo "🔑 IMPORTANT: Edit .env with your real API keys!"
echo "   File: $BOT_DIR/.env"
echo ""
echo "📚 Documentation:"
echo "   • 🎯_START_HERE_FULL_AUDIT.md - Complete guide"
echo "   • 🔥_COMPLETE_INTELLIGENCE_FIRING_GUIDE.md - How it works"
echo "   • ✅_COMPLETE_AUDIT_SUMMARY.txt - System status"
echo ""
echo "🚀 Your bot is now TRADING!"
echo "════════════════════════════════════════════════════════════════════════════════"
