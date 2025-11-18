#!/bin/bash
# ⚡ FIXED VPS DEPLOYMENT - COPY & PASTE THIS!

cd ~/bot
git stash
git pull origin continue-from-micro-fix --no-edit
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 3
nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
sleep 5
echo "🚀 ALL ENHANCEMENTS DEPLOYED!"
echo "📊 Monitoring live logs..."
tail -f bot.log
