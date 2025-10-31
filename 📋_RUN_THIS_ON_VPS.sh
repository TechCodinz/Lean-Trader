#!/bin/bash
#
# 📋 RUN THIS DIRECTLY ON VPS
# Copy-paste this entire script into your VPS terminal
#

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║         🚀 PULLING APEX BOT FROM GIT TO VPS 🚀                   ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

cd ~

# Clone/pull the repo
APEX_DIR="apex_bot"
BRANCH="cursor/review-past-and-current-conversations-for-missing-implementations-d672"

if [ -d "$APEX_DIR/.git" ]; then
    echo "✅ APEX bot directory exists, pulling latest..."
    cd "$APEX_DIR"
    git fetch origin
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
else
    echo "📥 Cloning APEX bot from git..."
    
    # Get repo URL (replace with your actual git remote)
    read -p "Enter your git repository URL: " REPO_URL
    
    git clone "$REPO_URL" "$APEX_DIR"
    cd "$APEX_DIR"
    git checkout "$BRANCH"
fi

echo ""
echo "✅ Code pulled to ~/apex_bot/"
echo ""

# Create Python venv (separate from 4.1 bot)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setting up Python environment (separate from 4.1)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install system dependencies
apt-get update > /dev/null 2>&1
apt-get install -y python3-venv python3-pip > /dev/null 2>&1

# Create apex_venv
if [ -d "apex_venv" ]; then
    echo "⚠️  apex_venv exists, removing..."
    rm -rf apex_venv
fi

python3 -m venv apex_venv
source apex_venv/bin/activate

# Install packages
echo "Installing Python packages..."
pip install --upgrade pip > /dev/null 2>&1
pip install ccxt pandas numpy scipy scikit-learn aiohttp loguru python-dotenv

echo ""
echo "✅ apex_venv created and packages installed"
echo ""

# Create control scripts
cat > start_apex.sh << 'STARTSCRIPT'
#!/bin/bash
cd ~/apex_bot
source apex_venv/bin/activate

# Check if already running
if pgrep -f "apex.*RUN_BOT" > /dev/null; then
    echo "⚠️  APEX Bot already running"
    echo "   Stop first: bash stop_apex.sh"
    exit 1
fi

# Start
nohup python3 RUN_BOT.py --live > apex_bot.log 2>&1 &
PID=$!
echo "✅ APEX Bot started! PID: $PID"
echo "📊 Monitor: tail -f ~/apex_bot/apex_bot.log"
STARTSCRIPT
chmod +x start_apex.sh

cat > stop_apex.sh << 'STOPSCRIPT'
#!/bin/bash
pkill -f "apex.*RUN_BOT"
echo "✅ APEX Bot stopped"
STOPSCRIPT
chmod +x stop_apex.sh

cat > status_apex.sh << 'STATUSSCRIPT'
#!/bin/bash
if pgrep -f "apex.*RUN_BOT" > /dev/null; then
    echo "✅ APEX Bot: RUNNING"
    tail -20 ~/apex_bot/apex_bot.log
else
    echo "❌ APEX Bot: NOT running"
    echo "Start: cd ~/apex_bot && bash start_apex.sh"
fi
STATUSSCRIPT
chmod +x status_apex.sh

echo "✅ Control scripts created"
echo ""

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║              ✅ APEX BOT SETUP COMPLETE! ✅                       ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Location: ~/apex_bot/"
echo "Venv: ~/apex_bot/apex_venv/"
echo "Log: ~/apex_bot/apex_bot.log"
echo ""
echo "Your 4.1 bot in ~/bot/ is UNTOUCHED!"
echo ""
echo "🚀 TO START:"
echo "   bash start_apex.sh"
echo ""
echo "📊 TO MONITOR:"
echo "   tail -f apex_bot.log"
echo ""
echo "🛑 TO STOP:"
echo "   bash stop_apex.sh"
echo ""
