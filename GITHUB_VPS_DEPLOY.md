# 🚀 GitHub Private Repo & VPS Deployment Guide

## 📦 Step 1: Push to GitHub Private Repo

### On your local machine (this workspace):

```bash
# Add all files to git
git add -A

# Commit everything
git commit -m "Ultra Trading System - Complete Multi-Exchange Bot with Universal Scanner"

# Add your private repo (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_PRIVATE_REPO.git

# Or if using SSH (recommended for private repos):
git remote add origin git@github.com:YOUR_USERNAME/YOUR_PRIVATE_REPO.git

# Push to GitHub
git push -u origin main

# If branch is different:
git push -u origin master
```

## 🖥️ Step 2: Deploy to VPS

### Connect to your VPS:
```bash
ssh root@75.119.148.117
# Enter password: pW65Yg036RettBb7
```

### On your VPS, run these commands:

```bash
# 1. Clone your private repository
# Using HTTPS (will ask for username/password):
git clone https://github.com/YOUR_USERNAME/YOUR_PRIVATE_REPO.git ultra-bot
cd ultra-bot

# OR using SSH (need to setup SSH key first):
git clone git@github.com:YOUR_USERNAME/YOUR_PRIVATE_REPO.git ultra-bot
cd ultra-bot

# 2. Make installer executable and run it
chmod +x install_all_dependencies.sh
./install_all_dependencies.sh

# 3. Copy and configure your API keys
cp env.arbitrage.template env.arbitrage
nano env.arbitrage
# Add all your API keys and save (Ctrl+X, Y, Enter)

# 4. Create necessary directories
mkdir -p logs data state checkpoints models reports backups

# 5. Test the bot first
python3 ultra_launcher.py --mode paper

# 6. If test works, run live
python3 ultra_launcher.py --mode live
```

## 🔧 Step 3: Setup as System Service (Auto-start)

```bash
# Create service file
sudo nano /etc/systemd/system/ultra-bot.service
```

Add this content:
```ini
[Unit]
Description=Ultra Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ultra-bot
ExecStart=/usr/bin/python3 /root/ultra-bot/ultra_launcher.py --mode live
Restart=always
RestartSec=60
StandardOutput=append:/root/ultra-bot/logs/bot.log
StandardError=append:/root/ultra-bot/logs/bot-error.log

[Install]
WantedBy=multi-user.target
```

Then:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable ultra-bot

# Start the bot
sudo systemctl start ultra-bot

# Check status
sudo systemctl status ultra-bot

# View logs
tail -f logs/bot.log

# Stop if needed
sudo systemctl stop ultra-bot
```

## 📋 Complete VPS Setup Script (All-in-One)

Save this as `vps_setup.sh` on your VPS:

```bash
#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Ultra Trading Bot VPS Setup${NC}"
echo "================================"

# Update system
echo -e "${YELLOW}Updating system...${NC}"
apt update && apt upgrade -y

# Install Python and Git if needed
echo -e "${YELLOW}Installing dependencies...${NC}"
apt install -y python3 python3-pip git screen htop

# Clone repository (replace with your repo)
echo -e "${YELLOW}Enter your GitHub username:${NC}"
read GITHUB_USER
echo -e "${YELLOW}Enter your repository name:${NC}"
read REPO_NAME

git clone https://github.com/$GITHUB_USER/$REPO_NAME.git ultra-bot
cd ultra-bot

# Install Python packages
echo -e "${YELLOW}Installing Python packages...${NC}"
chmod +x install_all_dependencies.sh
./install_all_dependencies.sh

# Setup directories
mkdir -p logs data state checkpoints models reports backups

# Configure
echo -e "${YELLOW}Ready to configure!${NC}"
echo "1. Edit env.arbitrage to add your API keys"
echo "2. Run: python3 ultra_launcher.py --mode paper (to test)"
echo "3. Run: python3 ultra_launcher.py --mode live (to trade)"

echo -e "${GREEN}✅ Setup complete!${NC}"
```

## 🔐 GitHub Authentication for Private Repo

### Option 1: Personal Access Token (Easier)
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with 'repo' scope
3. Use token as password when cloning:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
Username: YOUR_USERNAME
Password: YOUR_PERSONAL_ACCESS_TOKEN
```

### Option 2: SSH Key (More Secure)
```bash
# On VPS, generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy the public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub → Settings → SSH and GPG keys

# Clone using SSH
git clone git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

## 🎯 Quick Commands Summary

```bash
# On local machine - push to GitHub:
git add -A && git commit -m "Update" && git push

# On VPS - pull updates and restart:
cd /root/ultra-bot
git pull
sudo systemctl restart ultra-bot

# Monitor bot:
sudo systemctl status ultra-bot
tail -f logs/bot.log
htop  # Check resource usage

# Check if bot is running:
ps aux | grep python3 | grep ultra

# Emergency stop:
sudo systemctl stop ultra-bot
pkill -f ultra_launcher
```

## ✅ Verification Checklist

- [ ] Code pushed to GitHub private repo
- [ ] VPS can access GitHub repo
- [ ] All dependencies installed
- [ ] API keys configured in env.arbitrage
- [ ] Bot tested in paper mode
- [ ] Bot running in live mode
- [ ] Telegram notifications working
- [ ] System service configured for auto-restart

## 📱 Monitor from Telegram

Your admin chat (5329503447) will receive:
- Startup confirmation
- Heartbeat every 30 minutes
- All trade executions
- Error notifications
- Performance reports

---

**Your bot will now trade ALL pairs, ALL timeframes, on ALL exchanges, 24/7!** 🚀