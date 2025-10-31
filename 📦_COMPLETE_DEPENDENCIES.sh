#!/bin/bash
# COMPLETE dependency installation for the trading bot
# Run this in your new venv

echo "=========================================="
echo "📦 INSTALLING ALL BOT DEPENDENCIES"
echo "=========================================="
echo

# Core trading and data
echo "1️⃣  Core trading libraries..."
pip install --no-cache-dir \
    ccxt \
    pandas \
    numpy \
    python-dotenv \
    loguru

# Data processing
echo
echo "2️⃣  Data processing..."
pip install --no-cache-dir \
    "pyarrow>=15,<18" \
    scipy \
    scikit-learn

# Web scraping
echo
echo "3️⃣  Web scraping..."
pip install --no-cache-dir \
    beautifulsoup4 \
    lxml \
    html5lib \
    requests

# Telegram
echo
echo "4️⃣  Telegram integration..."
pip install --no-cache-dir \
    "python-telegram-bot>=20,<21" \
    "urllib3>=2" \
    aiogram

# Machine Learning
echo
echo "5️⃣  Machine Learning..."
pip install --no-cache-dir \
    "tensorflow>=2.17,<2.19" \
    keras

# LangChain (LLM)
echo
echo "6️⃣  LangChain (LLM)..."
pip install --no-cache-dir \
    langchain \
    langchain-core \
    langchain-community \
    openai

# Quantum computing
echo
echo "7️⃣  Quantum computing (IBM Qiskit)..."
pip install --no-cache-dir \
    qiskit \
    qiskit-aer \
    qiskit-optimization \
    qiskit-algorithms \
    qiskit-ibm-runtime

# Utilities
echo
echo "8️⃣  Utilities..."
pip install --no-cache-dir \
    qrcode[pil] \
    stripe \
    "tzlocal<5" \
    pytz \
    APScheduler

# Additional ML/data science
echo
echo "9️⃣  Additional ML libraries..."
pip install --no-cache-dir \
    scikit-learn \
    matplotlib \
    seaborn

echo
echo "=========================================="
echo "✅ ALL DEPENDENCIES INSTALLED"
echo "=========================================="
echo
echo "💡 Verify installation:"
echo "   python3 -c 'import ccxt, pandas, numpy, qiskit, tensorflow, langchain; print(\"✅ All imports work\")'"
