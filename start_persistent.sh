#!/usr/bin/env bash
set -euo pipefail

SESSION="ultra_live"
# Kill existing session if any
if tmux has-session -t "$SESSION" 2>/dev/null; then
	tmux kill-session -t "$SESSION"
fi

# Common environment (edit to taste)
export EXCHANGE_ID=gateio
export ENABLE_LIVE=true
export ALLOW_LIVE=true
export LIVE_CONFIRM=YES
export LIVE_ORDER_USD=${LIVE_ORDER_USD:-6}
export DAILY_MAX_LOSS=${DAILY_MAX_LOSS:-2}
export CIRCUIT_BREAKER_ENABLED=true
export SESSION_MIN_WEIGHT=${SESSION_MIN_WEIGHT:-0.85}
export LIVE_SYMBOLS=${LIVE_SYMBOLS:-"BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT,DOGE/USDT"}
# Per-symbol hard caps
export MAX_ORDER_SIZE_BTC=${MAX_ORDER_SIZE_BTC:-0.00005}
export MAX_ORDER_SIZE_ETH=${MAX_ORDER_SIZE_ETH:-0.001}
export MAX_ORDER_SIZE_SOL=${MAX_ORDER_SIZE_SOL:-0.05}
# Gate keys
export GATEIO_API_KEY=${GATEIO_API_KEY:?missing}
export GATEIO_API_SECRET=${GATEIO_API_SECRET:?missing}
# Telegram
export TELEGRAM_ENABLED=true
export TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:?missing}
export TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:?missing}
export TG_ADMIN_CHAT_ID=${TG_ADMIN_CHAT_ID:-}
export TG_FREE_CHAT_ID=${TG_FREE_CHAT_ID:-}
export TG_VIP_CHAT_ID=${TG_VIP_CHAT_ID:-}
# Learning
export ENABLE_LEARNING=true
export LEARNING_EXCHANGE=${LEARNING_EXCHANGE:-binance}

# Create session
tmux new-session -d -s "$SESSION" -n live

# Pane 1: live daemon
cmd1="python3 -u tools/run_bot_daemon.py 2>&1 | tee -a reports/daemon_console.log"
tmux send-keys -t "$SESSION":0.0 "$cmd1" C-m

# Pane 2: supervisor (learning + publishers)
tmux split-window -h -t "$SESSION":0
cmd2="python3 -u -m tools.supervisor 2>&1 | tee -a runtime/logs/supervisor_console.log"
tmux send-keys -t "$SESSION":0.1 "$cmd2" C-m

# Optional pane 3: periodic scanner signals (publish)
tmux split-window -v -t "$SESSION":0.1
cmd3="SCAN_TF=5m TOP_N=7 SCAN_LIMIT=250 python3 -u signals_scanner.py --publish --repeat 300 2>&1 | tee -a runtime/logs/scanner_console.log"
tmux send-keys -t "$SESSION":0.2 "$cmd3" C-m

# Attach hint
echo "Started tmux session '$SESSION'. Attach with: tmux attach -t $SESSION"