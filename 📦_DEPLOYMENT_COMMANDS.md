# 📦 DEPLOYMENT COMMANDS

## Complete deployment instructions for VPS and GitHub Desktop

---

## 🚀 PUSH TO GITHUB (From Workspace/Desktop)

### **Option 1: GitHub Desktop (Easy)**

1. **Open GitHub Desktop**
2. **Select Repository:**
   - Repository → Show in GitHub Desktop
   - Or File → Add Local Repository → Browse to `/workspace`

3. **Stage Changes:**
   - All new/modified files will show in left panel
   - Check the boxes for files to commit

4. **Commit:**
   - Summary: `🚀 Complete Enhancement - Production + DeFi + Forex + Alerts`
   - Description:
     ```
     Added critical features:
     - Integrated alert system (telegram + business)
     - Circuit breaker system (emergency stop)
     - DeFi yield farming engine
     - Cross-chain arbitrage
     - Enhanced forex master
     - Production deployment (Docker + security)
     - Streamlit dashboard
     
     All systems verified and ready for deployment!
     ```
   - Click **"Commit to cursor/check-last-agent-stop-point-for-bot-functionality-8296"**

5. **Push to GitHub:**
   - Click **"Push origin"** button at top
   - Wait for upload to complete

6. **Verify:**
   - Click "View on GitHub" to confirm files uploaded

---

### **Option 2: Command Line (Git)**

```bash
# From workspace directory
cd /workspace

# Stage all changes
git add -A

# Commit with message
git commit -m "$(cat <<'EOF'
🚀 Complete Enhancement - All Critical Features

Added:
1. INTEGRATED_ALERT_SYSTEM.py - Premium telegram alerts
2. CIRCUIT_BREAKER_SYSTEM.py - Emergency stop protection
3. DEFI_YIELD_FARMING_ENGINE.py - Yield farming (20-100% APY)
4. CROSS_CHAIN_ARBITRAGE.py - Cross-chain profits
5. ENHANCED_FOREX_MASTER.py - Professional forex
6. Production deployment (Docker + security)
7. Streamlit dashboard

Status: 100% ready for VPS deployment
EOF
)"

# Push to GitHub
git push origin cursor/check-last-agent-stop-point-for-bot-functionality-8296

# Verify
git log --oneline -1
```

---

## 📥 PULL TO VPS (On Your VPS)

### **Step 1: Connect to VPS**

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Or if you have a specific user
ssh your-user@your-vps-ip
```

### **Step 2: Navigate to Bot Directory**

```bash
# If bot is in /root/apex_bot
cd /root/apex_bot

# Or wherever your bot is located
cd ~/trading_bot
cd /home/your-user/bot
# etc.
```

### **Step 3: Pull Latest Code**

```bash
# Check current branch
git branch

# Make sure you're on the right branch
git checkout cursor/check-last-agent-stop-point-for-bot-functionality-8296

# Pull latest changes
git pull origin cursor/check-last-agent-stop-point-for-bot-functionality-8296

# Verify what was pulled
git log --oneline -5
```

### **Step 4: Install New Dependencies (if any)**

```bash
# Activate virtual environment (if using one)
source venv/bin/activate
# or
source apex_venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Verify critical packages
pip list | grep -E "telegram|stripe|ccxt|streamlit"
```

### **Step 5: Update Environment Variables**

```bash
# Edit .env file to add telegram credentials
nano .env

# Add these lines (if not already present):
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_CHAT=your_chat_id_here
TELEGRAM_VIP_CHAT=your_vip_channel_id (optional)
TELEGRAM_FREE_CHAT=your_free_channel_id (optional)

# Save: Ctrl+O, Enter, Ctrl+X
```

### **Step 6: Restart Bot**

#### **If using Docker:**
```bash
# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f trading-bot
```

#### **If using systemd service:**
```bash
# Restart service
sudo systemctl restart apex-bot
# or
sudo systemctl restart trading-bot

# Check status
sudo systemctl status apex-bot

# View logs
sudo journalctl -u apex-bot -f
```

#### **If running directly:**
```bash
# Stop old bot (find PID)
ps aux | grep python | grep BOT

# Kill old process
kill <PID>

# Start new bot
nohup python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py > logs/bot.log 2>&1 &

# Save PID
echo $! > bot.pid

# Check it's running
tail -f logs/bot.log
```

---

## ✅ VERIFICATION

### **1. Check Bot Started**
```bash
# Check process is running
ps aux | grep python | grep -i bot

# Check logs for startup message
tail -100 logs/bot.log | grep "BOT STARTED"
# or
docker-compose logs trading-bot | grep "BOT STARTED"
```

### **2. Verify Telegram Alerts**
```bash
# Check if startup alert was sent
# You should receive a Telegram message saying "🚀 BOT STARTED"

# Test alert manually
python3 -c "
import asyncio
from INTEGRATED_ALERT_SYSTEM import test_alerts
asyncio.run(test_alerts())
"
```

### **3. Check Circuit Breaker**
```bash
# Verify circuit breaker loaded
grep -i "circuit breaker" logs/bot.log

# Check state file
cat bot_data/circuit_breaker_state.json
```

### **4. Monitor Trading**
```bash
# Watch trades in real-time
tail -f logs/bot.log | grep -E "TRADE|EXECUTED|PROFIT|SIGNAL"

# Check consciousness is active
tail -f logs/bot.log | grep -E "Consciousness|254 engines"

# Watch for alerts
tail -f logs/bot.log | grep -i "alert"
```

### **5. Access Dashboard**
```bash
# Get your VPS IP
curl ifconfig.me

# Access dashboard in browser:
http://YOUR_VPS_IP:8501
```

---

## 🔥 QUICK REFERENCE

### **Complete Pull & Restart (Copy-Paste Ready)**

```bash
# === VPS QUICK DEPLOYMENT ===

# 1. Navigate to bot directory
cd /root/apex_bot  # Change to your path

# 2. Pull latest code
git checkout cursor/check-last-agent-stop-point-for-bot-functionality-8296
git pull origin cursor/check-last-agent-stop-point-for-bot-functionality-8296

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 4. Restart bot (choose ONE method):

# Docker:
docker-compose down && docker-compose build && docker-compose up -d

# Systemd:
sudo systemctl restart apex-bot && sudo journalctl -u apex-bot -f

# Direct:
pkill -f "python.*BOT" && nohup python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py > logs/bot.log 2>&1 &

# 5. Verify
tail -f logs/bot.log | grep -E "STARTED|ALERT|TRADE"
```

---

## 🆘 TROUBLESHOOTING

### **Issue: Git pull fails with conflicts**
```bash
# Stash local changes
git stash

# Pull
git pull

# Reapply changes (if needed)
git stash pop
```

### **Issue: Can't find bot directory**
```bash
# Search for bot
find / -name "AUTOMATED_ORCHESTRATOR_ENHANCED.py" 2>/dev/null

# Or search for common names
find ~ -type d -name "*bot*" -o -name "*apex*" -o -name "*trading*"
```

### **Issue: Telegram alerts not working**
```bash
# Check environment variables
cat .env | grep TELEGRAM

# Test telegram directly
python3 -c "
from telegram_notifier import send_message
send_message('Test message')
"

# Check bot token is valid
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

### **Issue: Dependencies fail to install**
```bash
# Update pip first
pip install --upgrade pip

# Install dependencies one by one
pip install python-telegram-bot
pip install streamlit
pip install ccxt

# Check for conflicts
pip check
```

---

## 📋 DEPLOYMENT CHECKLIST

Before deploying, verify:

- [ ] Code pushed to GitHub successfully
- [ ] VPS has internet connection
- [ ] Git is installed on VPS
- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] .env file has all required keys
- [ ] Telegram bot token added to .env
- [ ] Telegram chat IDs configured
- [ ] Firewall allows ports (8501 for dashboard)
- [ ] Sufficient disk space (check with `df -h`)
- [ ] Bot directory has write permissions

After deploying, verify:

- [ ] Bot process is running (`ps aux | grep python`)
- [ ] Startup telegram alert received
- [ ] Logs show "254 engines loaded"
- [ ] Logs show "Circuit breaker initialized"
- [ ] Dashboard accessible at http://VPS_IP:8501
- [ ] No errors in logs (`grep -i error logs/bot.log`)
- [ ] Trading activity visible in logs

---

## 💡 TIPS

1. **Always backup before pulling:**
   ```bash
   # Create backup
   tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .
   ```

2. **Use screen/tmux for monitoring:**
   ```bash
   # Start screen session
   screen -S bot_monitor
   
   # Watch logs
   tail -f logs/bot.log
   
   # Detach: Ctrl+A then D
   # Reattach: screen -r bot_monitor
   ```

3. **Set up telegram first:**
   - Create bot with @BotFather
   - Get bot token
   - Start chat with bot
   - Get your chat ID from: https://api.telegram.org/bot<TOKEN>/getUpdates

4. **Test locally first:**
   - Pull to local machine
   - Test all features
   - Then deploy to VPS

---

🚀 **Your bot is now ready to deploy with all premium features!**
