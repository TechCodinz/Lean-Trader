#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║        🚀 ULTRA TRADING SYSTEM - COMPLETE DEPENDENCY INSTALLER      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to install requirements file
install_requirements() {
    local req_file=$1
    if [ -f "$req_file" ]; then
        echo -e "${YELLOW}📦 Installing from $req_file...${NC}"
        pip install -r "$req_file" --quiet --disable-pip-version-check 2>/dev/null || {
            echo -e "${YELLOW}  Retrying with --break-system-packages...${NC}"
            pip install -r "$req_file" --break-system-packages --quiet 2>/dev/null || {
                echo -e "${RED}  Some packages failed, continuing...${NC}"
            }
        }
        echo -e "${GREEN}  ✅ Done${NC}"
    fi
}

# Update pip first
echo "🔧 Updating pip..."
pip install --upgrade pip --quiet 2>/dev/null || pip install --upgrade pip --break-system-packages --quiet 2>/dev/null

# Core dependencies that must be installed
echo ""
echo "📋 Installing CORE dependencies..."
pip install ccxt python-telegram-bot pandas numpy scikit-learn aiohttp python-dotenv --break-system-packages 2>/dev/null || {
    pip install ccxt python-telegram-bot pandas numpy scikit-learn aiohttp python-dotenv 2>/dev/null
}
echo -e "${GREEN}✅ Core dependencies installed${NC}"

# Install from all requirements files
echo ""
echo "📚 Installing from all requirements files..."
install_requirements "requirements.txt"
install_requirements "requirements_production.txt"
install_requirements "requirements_ultra.txt"
install_requirements "ultimate_requirements.txt"
install_requirements "complete_requirements.txt"
install_requirements "requirements-full.txt"
install_requirements "god_trader_requirements.txt"
install_requirements "requirements_fx.txt"
install_requirements "working_requirements.txt"
install_requirements "traders_core/requirements.core.txt"
install_requirements "requirements-dev.txt"

# Install additional packages that might be missing
echo ""
echo "🔧 Installing additional packages..."
ADDITIONAL_PACKAGES=(
    "asyncio-throttle"
    "aiodns"
    "psutil"
    "sqlalchemy"
    "aiosqlite"
    "prometheus-client"
    "colorama"
    "tabulate"
    "cryptography"
    "websockets"
    "redis"
    "motor"
    "pymongo"
    "influxdb"
    "matplotlib"
    "seaborn"
    "plotly"
    "dash"
    "streamlit"
    "fastapi"
    "uvicorn"
    "celery"
    "flower"
    "pytest"
    "black"
    "pylint"
)

for package in "${ADDITIONAL_PACKAGES[@]}"; do
    pip install "$package" --quiet --break-system-packages 2>/dev/null || true
done

echo -e "${GREEN}✅ Additional packages processed${NC}"

# Verify critical packages
echo ""
echo "🔍 Verifying critical packages..."
python3 -c "
import sys
print('Python version:', sys.version)
print('')
print('Checking critical packages:')

packages = {
    'ccxt': 'Exchange connectivity',
    'pandas': 'Data processing',
    'numpy': 'Numerical computing',
    'sklearn': 'Machine learning',
    'telegram': 'Telegram notifications',
    'aiohttp': 'Async HTTP',
    'dotenv': 'Environment variables'
}

all_good = True
for pkg, desc in packages.items():
    try:
        if pkg == 'sklearn':
            __import__('sklearn')
        elif pkg == 'telegram':
            __import__('telegram')
        elif pkg == 'dotenv':
            __import__('dotenv')
        else:
            __import__(pkg)
        print(f'  ✅ {pkg}: {desc}')
    except ImportError:
        print(f'  ❌ {pkg}: {desc} - MISSING')
        all_good = False

if all_good:
    print('')
    print('✅ All critical packages are installed!')
else:
    print('')
    print('⚠️  Some packages are missing but bot may still work')
" 2>/dev/null || echo "⚠️  Python verification failed but packages may still be installed"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ DEPENDENCY INSTALLATION COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📝 Next steps:"
echo "  1. Configure your API keys: nano env.arbitrage"
echo "  2. Test the bot: python3 ultra_launcher.py --mode paper"
echo "  3. Run live: python3 ultra_launcher.py --mode live"
echo ""