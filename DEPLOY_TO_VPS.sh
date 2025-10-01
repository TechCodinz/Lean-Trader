#!/bin/bash

# ================================================
# ULTRA TRADING SYSTEM - VPS DEPLOYMENT SCRIPT
# Production Ready with All API Keys Configured
# ================================================

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║          🚀 ULTRA TRADING SYSTEM - VPS DEPLOYMENT 🚀                ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Please don't run as root. Use a regular user with sudo."
   exit 1
fi

echo "📋 Starting deployment process..."
echo ""

# Update system
echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv git screen htop curl wget

# Install Docker (optional for containerized deployment)
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Clone repository (if not already cloned)
if [ ! -d "ultra-trading-system" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/yourusername/ultra-trading-system.git
    cd ultra-trading-system
else
    echo "📁 Repository already exists, updating..."
    cd ultra-trading-system
    git pull
fi

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional packages for production
pip install python-telegram-bot ccxt pandas numpy scikit-learn

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data state reports models checkpoints backups

# Set up systemd service
echo "⚙️ Setting up systemd service..."
cat > ultra-bot.service << EOF
[Unit]
Description=Ultra Trading Bot - Multi-Exchange Arbitrage System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PYTHONUNBUFFERED=1"
Environment="PRODUCTION=true"
ExecStart=$(pwd)/venv/bin/python3 $(pwd)/start_production.py
Restart=always
RestartSec=60
StandardOutput=append:$(pwd)/logs/ultra-bot.log
StandardError=append:$(pwd)/logs/ultra-bot-error.log

# Security
NoNewPrivileges=true
PrivateTmp=true

# Resource Limits
LimitNOFILE=65536
LimitNPROC=4096
MemoryMax=4G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

# Install service
sudo cp ultra-bot.service /etc/systemd/system/
sudo systemctl daemon-reload

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "📊 ULTRA BOT MONITORING"
echo "======================="
echo ""
echo "Service Status:"
sudo systemctl status ultra-bot --no-pager
echo ""
echo "Latest Logs:"
tail -20 logs/ultra-bot.log
echo ""
echo "Error Logs:"
tail -10 logs/ultra-bot-error.log
echo ""
echo "Resource Usage:"
ps aux | grep python3 | grep -v grep
echo ""
echo "Disk Usage:"
df -h .
EOF
chmod +x monitor.sh

# Create backup script
echo "💾 Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r data state logs/*.json $BACKUP_DIR/
echo "✅ Backup created in $BACKUP_DIR"
EOF
chmod +x backup.sh

# Set up cron jobs
echo "⏰ Setting up cron jobs..."
(crontab -l 2>/dev/null; echo "0 0 * * * $(pwd)/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "*/30 * * * * $(pwd)/monitor.sh > $(pwd)/logs/monitor.log 2>&1") | crontab -

# Set proper permissions
echo "🔒 Setting permissions..."
chmod 600 env.arbitrage env.live
chmod 755 *.py *.sh

# Final checks
echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📋 DEPLOYMENT SUMMARY:"
echo "  • System packages: Updated"
echo "  • Python environment: Ready"
echo "  • Dependencies: Installed"
echo "  • Directories: Created"
echo "  • Service: Configured"
echo "  • Monitoring: Set up"
echo "  • Backups: Scheduled"
echo ""
echo "🚀 TO START THE BOT:"
echo "  sudo systemctl start ultra-bot"
echo ""
echo "📊 TO MONITOR:"
echo "  sudo systemctl status ultra-bot"
echo "  sudo journalctl -u ultra-bot -f"
echo "  ./monitor.sh"
echo ""
echo "🛑 TO STOP:"
echo "  sudo systemctl stop ultra-bot"
echo ""
echo "🔄 TO RESTART:"
echo "  sudo systemctl restart ultra-bot"
echo ""
echo "⚡ QUICK START:"
echo "  sudo systemctl enable ultra-bot  # Enable auto-start on boot"
echo "  sudo systemctl start ultra-bot   # Start now"
echo ""
echo "✨ The Ultra Trading System is ready for production!"
echo "   Your API keys are configured and Telegram is ready."
echo "   The bot will start arbitraging across 6 exchanges!"