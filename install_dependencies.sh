#!/bin/bash

# ============================================================================
# APEX BOT - AUTOMATED DEPENDENCY INSTALLER
# Installs ALL dependencies for the Living Digital Trading Organism
# ============================================================================

set -e  # Exit on error

echo "================================================================================"
echo "🚀 APEX BOT - DEPENDENCY INSTALLER"
echo "================================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python $REQUIRED_VERSION or higher required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
echo ""

# Check if venv exists
if [ ! -d "apex_venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv apex_venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi
echo ""

# Activate venv
echo "🔌 Activating virtual environment..."
source apex_venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✅ Pip upgraded${NC}"
echo ""

echo "================================================================================"
echo "📦 INSTALLING DEPENDENCIES (This may take 5-15 minutes)..."
echo "================================================================================"
echo ""

# Function to install package with error handling
install_package() {
    local package=$1
    local description=$2
    echo "📦 Installing $description..."
    if pip install "$package" --no-warn-script-location; then
        echo -e "${GREEN}✅ $description installed${NC}"
    else
        echo -e "${RED}❌ Failed to install $description${NC}"
        echo -e "${YELLOW}⚠️  Continuing with other packages...${NC}"
    fi
    echo ""
}

# Install in stages to handle dependencies properly

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 1: CORE DEPENDENCIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "ccxt>=4.0.0" "CCXT (Exchange Connectivity)"
install_package "python-dotenv>=1.0.0" "Python Dotenv (Environment Variables)"
install_package "requests>=2.31.0" "Requests (HTTP)"
install_package "aiohttp>=3.9.0" "AioHTTP (Async HTTP)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 2: AI APIs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "anthropic>=0.7.0" "Anthropic (Claude AI)"
install_package "openai>=1.3.0" "OpenAI (GPT-4)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 3: DATA SCIENCE & ML"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "numpy>=1.24.0" "NumPy (Numerical Computing)"
install_package "pandas>=2.0.0" "Pandas (Data Analysis)"
install_package "scipy>=1.11.0" "SciPy (Scientific Computing)"
install_package "scikit-learn>=1.3.0" "Scikit-learn (Machine Learning)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 4: DEEP LEARNING (Optional - may take 10+ minutes)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Install TensorFlow/Keras? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    install_package "tensorflow>=2.14.0" "TensorFlow (Deep Learning)"
    install_package "keras>=2.14.0" "Keras (Neural Networks)"
else
    echo -e "${YELLOW}⚠️  Skipping TensorFlow/Keras${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 5: VISUALIZATION & ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "matplotlib>=3.7.0" "Matplotlib (Plotting)"
install_package "seaborn>=0.12.0" "Seaborn (Statistical Visualization)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 6: ADVANCED MATH & NETWORKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "sympy>=1.12" "SymPy (Symbolic Math)"
install_package "networkx>=3.1" "NetworkX (Graph Analysis)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 7: WEB SCRAPING & DATA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "beautifulsoup4>=4.12.0" "BeautifulSoup (Web Scraping)"
install_package "lxml>=4.9.0" "LXML (XML/HTML Parsing)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 8: DATABASE & STORAGE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "sqlalchemy>=2.0.0" "SQLAlchemy (SQL Toolkit)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 9: TELEGRAM (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Install Telegram bot support? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    install_package "python-telegram-bot>=20.6" "Telegram Bot"
else
    echo -e "${YELLOW}⚠️  Skipping Telegram bot${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 10: QUANTUM COMPUTING (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Install Qiskit (IBM Quantum)? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    install_package "qiskit>=0.45.0" "Qiskit (Quantum Computing)"
else
    echo -e "${YELLOW}⚠️  Skipping Qiskit${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 11: WEB3/BLOCKCHAIN (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Install Web3 (for DEX trading)? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    install_package "web3>=6.11.0" "Web3 (Ethereum)"
    install_package "eth-account>=0.10.0" "Ethereum Account Management"
else
    echo -e "${YELLOW}⚠️  Skipping Web3${NC}"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 12: UTILITIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "pyyaml>=6.0.0" "PyYAML"
install_package "python-dateutil>=2.8.0" "Python Dateutil"
install_package "pytz>=2023.3" "PyTZ (Timezones)"
install_package "colorama>=0.4.6" "Colorama (Colored Output)"
install_package "ujson>=5.8.0" "UltraJSON (Fast JSON)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stage 13: SECURITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
install_package "cryptography>=41.0.0" "Cryptography"

echo ""
echo "================================================================================"
echo "🎉 INSTALLATION COMPLETE!"
echo "================================================================================"
echo ""

# Verify critical imports
echo "🔍 Verifying critical imports..."
python3 << 'PYEOF'
import sys

packages = [
    ('ccxt', 'Exchange Connectivity'),
    ('dotenv', 'Environment Variables'),
    ('requests', 'HTTP Requests'),
    ('aiohttp', 'Async HTTP'),
    ('numpy', 'NumPy'),
    ('pandas', 'Pandas'),
    ('scipy', 'SciPy'),
    ('sklearn', 'Scikit-learn'),
]

all_good = True
for package, name in packages:
    try:
        __import__(package)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} - FAILED")
        all_good = False

if all_good:
    print("\n✅ All critical packages verified!")
else:
    print("\n⚠️  Some packages failed to import")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo -e "${GREEN}✅ APEX BOT IS READY TO RUN!${NC}"
    echo "================================================================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure your .env file with API keys:"
    echo "   nano .env"
    echo ""
    echo "2. Start the organism:"
    echo "   python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py"
    echo ""
    echo "3. Or use the autonomous awakening:"
    echo "   python3 AUTONOMOUS_AWAKENING.py"
    echo ""
    echo "================================================================================"
else
    echo ""
    echo "================================================================================"
    echo -e "${RED}❌ INSTALLATION HAD ERRORS${NC}"
    echo "================================================================================"
    echo ""
    echo "Please check errors above and:"
    echo "1. Try installing failed packages individually"
    echo "2. Or run: pip install -r requirements.txt"
    echo ""
fi
