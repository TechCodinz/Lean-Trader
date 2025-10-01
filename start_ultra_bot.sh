#!/bin/bash

# Ultra Trading Bot - Intelligent Startup Script
# Automatically selects the best available launcher based on dependencies

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    ULTRA TRADING BOT - STARTUP SYSTEM                       ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a Python module is installed
check_module() {
    python3 -c "import $1" 2>/dev/null
    return $?
}

# Function to print status
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
    fi
}

echo "🔍 Checking system requirements..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} Python3 installed (version $PYTHON_VERSION)"
else
    echo -e "${RED}✗${NC} Python3 not found!"
    exit 1
fi

# Check for required modules
echo ""
echo "📦 Checking dependencies..."

CCXT_AVAILABLE=0
PANDAS_AVAILABLE=0
NUMPY_AVAILABLE=0
SKLEARN_AVAILABLE=0

if check_module ccxt; then
    CCXT_AVAILABLE=1
fi
print_status "ccxt (Exchange connectivity)" $((1-CCXT_AVAILABLE))

if check_module pandas; then
    PANDAS_AVAILABLE=1
fi
print_status "pandas (Data analysis)" $((1-PANDAS_AVAILABLE))

if check_module numpy; then
    NUMPY_AVAILABLE=1
fi
print_status "numpy (Numerical computations)" $((1-NUMPY_AVAILABLE))

if check_module sklearn; then
    SKLEARN_AVAILABLE=1
fi
print_status "scikit-learn (Machine learning)" $((1-SKLEARN_AVAILABLE))

# Determine which launcher to use
echo ""
echo "🚀 Selecting appropriate launcher..."

LAUNCHER=""
MODE="paper"  # Default to paper trading for safety

# Check if production bot can run
if [ -f "production_trading_bot.py" ] && [ $CCXT_AVAILABLE -eq 1 ] && [ $PANDAS_AVAILABLE -eq 1 ] && [ $NUMPY_AVAILABLE -eq 1 ]; then
    echo -e "${GREEN}✓${NC} Production trading bot available (full features)"
    LAUNCHER="production_trading_bot.py"
    
# Check if fixed launcher can run
elif [ -f "ultra_launcher_fixed.py" ] && [ $CCXT_AVAILABLE -eq 1 ]; then
    echo -e "${YELLOW}⚠${NC} Using fixed launcher (limited features)"
    LAUNCHER="ultra_launcher_fixed.py"
    
# Use standalone version (always works)
elif [ -f "ultra_launcher_standalone.py" ]; then
    echo -e "${YELLOW}⚠${NC} Using standalone launcher (simulation only, no external dependencies)"
    LAUNCHER="ultra_launcher_standalone.py"
else
    echo -e "${RED}✗${NC} No suitable launcher found!"
    exit 1
fi

# Parse command line arguments
SYMBOLS="BTC/USDT ETH/USDT SOL/USDT"
RISK="0.02"
CONFIDENCE="65"
CAPITAL="10000"

while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --symbols)
            SYMBOLS="$2"
            shift 2
            ;;
        --risk)
            RISK="$2"
            shift 2
            ;;
        --confidence)
            CONFIDENCE="$2"
            shift 2
            ;;
        --capital)
            CAPITAL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --mode MODE          Trading mode: paper, backtest, live (default: paper)"
            echo "  --symbols SYMBOLS    Space-separated symbols (default: BTC/USDT ETH/USDT SOL/USDT)"
            echo "  --risk RISK          Risk per trade 0-1 (default: 0.02 = 2%)"
            echo "  --confidence CONF    Min confidence 0-100 (default: 65%)"
            echo "  --capital AMOUNT     Initial capital (default: 10000)"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Safety check for live mode
if [ "$MODE" = "live" ]; then
    echo ""
    echo -e "${RED}⚠️  WARNING: LIVE TRADING MODE SELECTED ⚠️${NC}"
    echo "This will execute REAL trades with REAL money!"
    echo -n "Are you absolutely sure? Type 'YES' to confirm: "
    read CONFIRM
    if [ "$CONFIRM" != "YES" ]; then
        echo "Live trading cancelled. Switching to paper mode."
        MODE="paper"
    fi
fi

# Create logs directory
mkdir -p logs

# Display configuration
echo ""
echo "📋 Configuration:"
echo "  • Launcher: $LAUNCHER"
echo "  • Mode: $MODE"
echo "  • Symbols: $SYMBOLS"
echo "  • Risk per trade: ${RISK} ($(echo "$RISK * 100" | bc)%)"
echo "  • Min confidence: ${CONFIDENCE}%"
echo "  • Initial capital: \$$CAPITAL"
echo ""

# Start the bot
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                          STARTING TRADING BOT"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Build command based on launcher type
if [ "$LAUNCHER" = "production_trading_bot.py" ]; then
    # Production bot uses environment variables
    export TRADING_MODE="$MODE"
    export TRADING_ENABLED="true"
    export MAX_POSITION_SIZE="$(echo "$RISK * 100" | bc)"
    export MIN_CONFIDENCE="$CONFIDENCE"
    
    python3 "$LAUNCHER"
    
elif [ "$LAUNCHER" = "ultra_launcher_fixed.py" ]; then
    # Fixed launcher with arguments
    python3 "$LAUNCHER" \
        --mode "$MODE" \
        --symbols $SYMBOLS \
        --risk "$RISK" \
        --confidence "$CONFIDENCE"
        
elif [ "$LAUNCHER" = "ultra_launcher_standalone.py" ]; then
    # Standalone launcher with arguments
    python3 "$LAUNCHER" \
        --symbols $SYMBOLS \
        --capital "$CAPITAL" \
        --risk "$RISK" \
        --confidence "$CONFIDENCE" \
        --interval 5
fi

echo ""
echo "Bot stopped."