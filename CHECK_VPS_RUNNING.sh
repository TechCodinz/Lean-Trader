#!/bin/bash
# Check what's ACTUALLY running on VPS

VPS_IP="75.119.149.117"
VPS_USER="root"

echo "🔍 CHECKING WHAT'S RUNNING ON VPS"
echo "===================================="
echo ""

echo "1️⃣  Python processes running:"
echo "------------------------------------"
ssh "$VPS_USER@$VPS_IP" "ps aux | grep python | grep -v grep | grep -v sshd"

echo ""
echo "2️⃣  Looking for MICRO WALLET:"
echo "------------------------------------"
ssh "$VPS_USER@$VPS_IP" "ps aux | grep -i micro | grep -v grep"

echo ""
echo "3️⃣  Looking for orchestrators:"
echo "------------------------------------"
ssh "$VPS_USER@$VPS_IP" "ps aux | grep -i orchestrator | grep -v grep"

echo ""
echo "4️⃣  Screen/tmux sessions:"
echo "------------------------------------"
ssh "$VPS_USER@$VPS_IP" "screen -ls 2>&1 || echo 'No screen sessions'"
ssh "$VPS_USER@$VPS_IP" "tmux ls 2>&1 || echo 'No tmux sessions'"

echo ""
echo "5️⃣  Finding bot directory:"
echo "------------------------------------"
ssh "$VPS_USER@$VPS_IP" "find /root /home -name 'MICRO_WALLET_GROWER.py' -o -name 'COMPLETE_ULTIMATE_ORCHESTRATOR.py' 2>/dev/null | head -5"

echo ""
echo "6️⃣  Recent Python files (last modified):"
echo "------------------------------------"
ssh "$VPS_USER@$VPS_IP" "find /root -name '*.py' -type f -mmin -120 2>/dev/null | head -10"

echo ""
echo "7️⃣  Check logs for MICRO WALLET:"
echo "------------------------------------"
ssh "$VPS_USER@$VPS_IP" "find /root -name '*.log' -type f -mmin -60 2>/dev/null | xargs grep -l 'MICRO' 2>/dev/null | head -5"

echo ""
echo "8️⃣  Check for running bots in common locations:"
echo "------------------------------------"
ssh "$VPS_USER@$VPS_IP" "ls -la /root/trading_bot/*.py 2>/dev/null | grep -E '(MICRO|ORCHESTRATOR|RUN)' | head -10"

echo ""
echo "===================================="
echo "✅ Done checking VPS"
echo ""
