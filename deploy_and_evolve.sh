#!/bin/bash

# Ultra Trading Bot - Production Deployment Script
# This starts the bot with all components and evolution capabilities

echo "======================================================================="
echo "🚀 ULTRA TRADING BOT - PRODUCTION DEPLOYMENT"
echo "======================================================================="
echo ""
echo "📋 Pre-flight checks..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi
echo "✅ Python3 available"

# Create required directories
mkdir -p logs state data backups
echo "✅ Directories ready"

# Set environment variables if not set
if [ -z "$BYBIT_API_KEY" ]; then
    echo "⚠️ BYBIT_API_KEY not set, using paper trading mode"
    export TRADING_MODE="paper"
else
    export TRADING_MODE="live"
    echo "✅ API credentials found"
fi

# Set default configuration
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export MAX_POSITION_SIZE="${MAX_POSITION_SIZE:-1000}"
export RISK_LEVEL="${RISK_LEVEL:-conservative}"
export SYMBOLS="${SYMBOLS:-BTC/USDT,ETH/USDT}"

echo ""
echo "📊 Configuration:"
echo "  Mode: $TRADING_MODE"
echo "  Log Level: $LOG_LEVEL"
echo "  Symbols: $SYMBOLS"
echo "  Risk Level: $RISK_LEVEL"
echo ""

# Create startup configuration
cat > startup_config.json << EOF
{
    "mode": "$TRADING_MODE",
    "symbols": ["BTC/USDT", "ETH/USDT"],
    "risk": {
        "max_position_size": $MAX_POSITION_SIZE,
        "stop_loss": -0.02,
        "take_profit": 0.05,
        "max_daily_loss": -0.1
    },
    "features": {
        "god_mode_enabled": true,
        "moon_spotter_enabled": true,
        "forex_master_enabled": false,
        "telegram_enabled": false,
        "ml_enabled": true,
        "evolution_enabled": true
    },
    "monitoring": {
        "health_check_interval": 60,
        "position_reconciliation_interval": 300,
        "performance_log_interval": 60
    },
    "optimization": {
        "memory_cleanup_interval": 3600,
        "state_save_interval": 60,
        "cache_ttl": 300
    }
}
EOF

echo "✅ Startup configuration created"
echo ""
echo "======================================================================="
echo "🎯 STARTING ULTRA TRADING BOT WITH FULL EVOLUTION CAPABILITIES"
echo "======================================================================="
echo ""

# Start the bot with all components
python3 ultra_launcher.py \
    --mode $TRADING_MODE \
    --config startup_config.json \
    --symbols $SYMBOLS \
    --verbose