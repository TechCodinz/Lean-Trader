#!/bin/bash
# Stop all bot processes

echo "🛑 Stopping bot processes..."

# Kill by process name
pkill -9 -f RUN_BOT.py
pkill -9 -f COMPLETE_ULTIMATE_ORCHESTRATOR
pkill -9 -f python3.*RUN_BOT
pkill -9 -f python.*RUN_BOT

# Kill by PID file if it exists
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Killing PID: $PID"
        kill -9 $PID 2>/dev/null
        rm -f bot.pid
    fi
fi

# Check if any processes are still running
if pgrep -f "RUN_BOT\|COMPLETE_ULTIMATE_ORCHESTRATOR" > /dev/null; then
    echo "⚠️  Some processes still running. Force killing..."
    pkill -9 -f "RUN_BOT\|COMPLETE_ULTIMATE_ORCHESTRATOR"
    sleep 1
fi

# Verify stopped
if ! pgrep -f "RUN_BOT\|COMPLETE_ULTIMATE_ORCHESTRATOR" > /dev/null; then
    echo "✅ Bot stopped successfully"
else
    echo "❌ Some processes may still be running:"
    ps aux | grep -E "RUN_BOT|COMPLETE_ULTIMATE_ORCHESTRATOR" | grep -v grep
fi
