#!/usr/bin/env bash
set -euo pipefail
cd "/home/ubuntu/trading_bot" 2>/dev/null || cd /workspace
export ENABLE_TELEGRAM=0
# Optional: restrict real profit engine unless you explicitly enable it
export ENABLE_REAL_PROFIT_ENGINE=0
# Stop old process
pkill -9 -f RUN_BOT.py || true
sleep 2
# Start fresh in testnet mode
nohup python3 -u RUN_BOT.py --testnet --auto-confirm > bot.log 2>&1 &
PID=
echo "Bot PID: "
sleep 5
# Show recent status lines
( tail -n +1 -f bot.log & ) | sed -n '1,120p';
