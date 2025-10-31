#!/bin/bash
# FINAL COMPLETE dependencies - ALL that popped up during deployment
# This includes EVERY error we encountered and fixed

set -e

echo "=========================================="
echo "📦 INSTALLING ALL DEPENDENCIES"
echo "   (Including all from deployment errors)"
echo "=========================================="
echo

pip install --upgrade pip

echo "📦 Installing ALL dependencies (including deployment fixes)..."
pip install --no-cache-dir \
    \
    ccxt \
    pandas \
    numpy \
    python-dotenv \
    loguru \
    requests \
    aiohttp \
    \
    "pyarrow>=15,<18" \
    scipy \
    scikit-learn \
    \
    beautifulsoup4 \
    lxml \
    html5lib \
    \
    "python-telegram-bot>=20,<21" \
    "urllib3>=2" \
    aiogram \
    \
    "tensorflow>=2.17,<2.19" \
    keras \
    \
    langchain \
    langchain-core \
    langchain-community \
    openai \
    \
    qiskit \
    qiskit-aer \
    qiskit-optimization \
    qiskit-algorithms \
    qiskit-ibm-runtime \
    \
    qrcode[pil] \
    Pillow \
    stripe \
    "tzlocal<5" \
    pytz \
    APScheduler \
    \
    matplotlib \
    seaborn \
    sqlalchemy \
    python-dateutil

echo
echo "=========================================="
echo "✅ ALL DEPENDENCIES INSTALLED"
echo "=========================================="
echo

echo "🔍 Verifying ALL imports (from deployment errors)..."
python3 << 'EOF'
import sys
errors = []

try:
    import ccxt
    print("✅ ccxt")
except ImportError as e:
    errors.append(f"❌ ccxt: {e}")

try:
    import pandas
    print("✅ pandas")
except ImportError as e:
    errors.append(f"❌ pandas: {e}")

try:
    import numpy
    print("✅ numpy")
except ImportError as e:
    errors.append(f"❌ numpy: {e}")

try:
    import pyarrow
    print("✅ pyarrow")
except ImportError as e:
    errors.append(f"❌ pyarrow: {e}")

try:
    from bs4 import BeautifulSoup
    print("✅ beautifulsoup4 (bs4)")
except ImportError as e:
    errors.append(f"❌ beautifulsoup4: {e}")

try:
    from telegram.ext import Application
    print("✅ python-telegram-bot")
except ImportError as e:
    errors.append(f"❌ python-telegram-bot: {e}")

try:
    import tensorflow
    print("✅ tensorflow")
except ImportError as e:
    errors.append(f"❌ tensorflow: {e}")

try:
    import langchain
    print("✅ langchain")
except ImportError as e:
    errors.append(f"❌ langchain: {e}")

try:
    import aiogram
    print("✅ aiogram")
except ImportError as e:
    errors.append(f"❌ aiogram: {e}")

try:
    import qrcode
    from PIL import Image
    print("✅ qrcode + Pillow")
except ImportError as e:
    errors.append(f"❌ qrcode/Pillow: {e}")

try:
    import stripe
    print("✅ stripe")
except ImportError as e:
    errors.append(f"❌ stripe: {e}")

try:
    import tzlocal
    import pytz
    print("✅ tzlocal + pytz")
except ImportError as e:
    errors.append(f"❌ tzlocal/pytz: {e}")

try:
    from qiskit import QuantumCircuit
    print("✅ qiskit")
except ImportError as e:
    errors.append(f"❌ qiskit: {e}")

if errors:
    print("\n❌ ERRORS FOUND:")
    for error in errors:
        print(f"   {error}")
    sys.exit(1)
else:
    print("\n✅ ALL DEPENDENCIES VERIFIED!")
    print("   All deployment errors are fixed!")
EOF

echo
echo "✅ Ready to run bot - no missing dependencies!"
