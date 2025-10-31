#!/bin/bash
# COMPLETE dependency installation - Nothing missing!
# Run this in your new venv

set -e

echo "=========================================="
echo "📦 INSTALLING ALL DEPENDENCIES"
echo "=========================================="
echo

# Upgrade pip first
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install all at once
echo
echo "📦 Installing all dependencies..."
pip install --no-cache-dir \
    ccxt \
    pandas \
    numpy \
    python-dotenv \
    loguru \
    requests \
    aiohttp \
    "pyarrow>=15,<18" \
    scipy \
    scikit-learn \
    beautifulsoup4 \
    lxml \
    html5lib \
    "python-telegram-bot>=20,<21" \
    "urllib3>=2" \
    aiogram \
    "tensorflow>=2.17,<2.19" \
    keras \
    langchain \
    langchain-core \
    langchain-community \
    openai \
    qiskit \
    qiskit-aer \
    qiskit-optimization \
    qiskit-algorithms \
    qiskit-ibm-runtime \
    qrcode[pil] \
    stripe \
    "tzlocal<5" \
    pytz \
    APScheduler \
    matplotlib \
    seaborn

echo
echo "=========================================="
echo "✅ ALL DEPENDENCIES INSTALLED"
echo "=========================================="
echo

# Verify critical imports
echo "🔍 Verifying installation..."
python3 -c "
try:
    import ccxt
    import pandas
    import numpy
    import qiskit
    import tensorflow
    import langchain
    import telegram
    import bs4
    print('✅ All critical dependencies verified!')
except ImportError as e:
    print(f'❌ Missing: {e}')
    exit(1)
"

echo
echo "✅ Ready to run bot!"
