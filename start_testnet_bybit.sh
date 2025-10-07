#!/usr/bin/env bash
set -euo pipefail

SESSION="ultra_testnet"
if tmux has-session -t "$SESSION" 2>/dev/null; then
	tmux kill-session -t "$SESSION"
fi

export EXCHANGE_ID=bybit
export BYBIT_TESTNET=true
export ENABLE_LIVE=true
export ALLOW_LIVE=true
export LIVE_CONFIRM=YES
# Testnet notional per order (demo)
export LIVE_ORDER_USD=${LIVE_ORDER_USD:-50}
export DAILY_MAX_LOSS=${DAILY_MAX_LOSS:-100}
export CIRCUIT_BREAKER_ENABLED=true
export SESSION_MIN_WEIGHT=${SESSION_MIN_WEIGHT:-0.80}
export LIVE_SYMBOLS=${LIVE_SYMBOLS:-"BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT"}
# Provide testnet keys via environment before running
: "${BYBIT_API_KEY:?Set BYBIT_API_KEY}"
: "${BYBIT_API_SECRET:?Set BYBIT_API_SECRET}"

export TELEGRAM_ENABLED=true
: "${TELEGRAM_BOT_TOKEN:?Set TELEGRAM_BOT_TOKEN}"
: "${TELEGRAM_CHAT_ID:?Set TELEGRAM_CHAT_ID}"

# Create session
tmux new-session -d -s "$SESSION" -n testnet

# Pane 1: live daemon (testnet)
cmd1="python3 -u tools/run_bot_daemon.py 2>&1 | tee -a reports/testnet_daemon.log"
tmux send-keys -t "$SESSION":0.0 "$cmd1" C-m

# Pane 2: supervisor (learning) optional
tmux split-window -h -t "$SESSION":0
cmd2="ENABLE_LEARNING=true LEARNING_EXCHANGE=binance python3 -u -m tools.supervisor 2>&1 | tee -a runtime/logs/testnet_supervisor.log"
tmux send-keys -t "$SESSION":0.1 "$cmd2" C-m

echo "Started tmux session '$SESSION'. Attach with: tmux attach -t $SESSION"