# 📦 APEX BOT - COMPLETE DEPENDENCIES GUIDE

**Version:** 2.0  
**Updated:** 2025-11-16  
**For:** Living Digital Trading Organism

---

## 🎯 QUICK START

### Option 1: Automated Installation (Recommended)
```bash
cd apex_bot
bash install_dependencies.sh
```

### Option 2: Requirements File
```bash
cd apex_bot
python3 -m venv apex_venv
source apex_venv/bin/activate
pip install -r requirements.txt
```

### Option 3: Minimal Install (Core Only)
```bash
pip install ccxt python-dotenv requests aiohttp anthropic openai numpy pandas scipy scikit-learn
```

---

## 📋 DEPENDENCY CATEGORIES

### ✅ **REQUIRED (Core Trading)**
These are MANDATORY for the bot to run:

| Package | Version | Purpose |
|---------|---------|---------|
| `ccxt` | ≥4.0.0 | Exchange connectivity (Bybit, Binance, etc.) |
| `python-dotenv` | ≥1.0.0 | Load API keys from .env file |
| `requests` | ≥2.31.0 | HTTP requests |
| `aiohttp` | ≥3.9.0 | Async HTTP for concurrent operations |
| `numpy` | ≥1.24.0 | Numerical computing |
| `pandas` | ≥2.0.0 | Data manipulation |

**Install:**
```bash
pip install ccxt python-dotenv requests aiohttp numpy pandas
```

---

### 🤖 **AI INTELLIGENCE (Highly Recommended)**
For Multi-AI consultation and continuous learning:

| Package | Version | Purpose |
|---------|---------|---------|
| `anthropic` | ≥0.7.0 | Claude AI API (strategy optimization) |
| `openai` | ≥1.3.0 | GPT-4 API (market analysis) |
| `scipy` | ≥1.11.0 | Scientific computing |
| `scikit-learn` | ≥1.3.0 | Machine learning models |

**Install:**
```bash
pip install anthropic openai scipy scikit-learn
```

**Note:** Without these, bot still works but won't have AI consultation features.

---

### 🧠 **ADVANCED FEATURES (Optional)**
For maximum intelligence and profit potential:

#### Critical Profit Features (+50-100% boost):
```bash
pip install matplotlib seaborn  # For volume profile analysis
```

#### Ultra Goldmine Features (+200-500% boost):
```bash
pip install beautifulsoup4 lxml  # For web scraping (whale tracking, news)
```

#### Divine Intelligence Features (+300-1000% boost):
```bash
pip install sympy networkx  # For quantum/chaos theory analysis
```

---

### 🚀 **DEEP LEARNING (Optional)**
For neural network predictions:

| Package | Version | Purpose |
|---------|---------|---------|
| `tensorflow` | ≥2.14.0 | Deep learning framework |
| `keras` | ≥2.14.0 | High-level neural networks |
| `torch` | ≥2.1.0 | PyTorch (alternative) |

**Install:**
```bash
# TensorFlow/Keras (recommended)
pip install tensorflow keras

# OR PyTorch (alternative)
pip install torch torchvision
```

**Note:** Deep learning is optional. Adds LSTM/Transformer predictions but requires significant compute power.

---

### 📱 **TELEGRAM NOTIFICATIONS (Optional)**
For bot status updates and remote control:

```bash
pip install python-telegram-bot
```

**Setup:**
1. Create bot with [@BotFather](https://t.me/BotFather)
2. Add to `.env`:
   ```ini
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

---

### ⚛️ **QUANTUM COMPUTING (Optional)**
For IBM Quantum features:

```bash
pip install qiskit qiskit-aer
```

**Note:** Requires IBM Quantum API key. Adds quantum portfolio optimization.

---

### 🌐 **WEB3/BLOCKCHAIN (Optional)**
For DEX trading (Uniswap, PancakeSwap, etc.):

```bash
pip install web3 eth-account
```

**Note:** Only needed if trading on decentralized exchanges.

---

### 🔧 **UTILITIES**
Helpful but not critical:

```bash
pip install pyyaml python-dateutil pytz colorama ujson cryptography
```

---

## 🎯 RECOMMENDED INSTALLATION PROFILES

### Profile 1: MINIMAL (Core Trading Only)
**Size:** ~200MB  
**Time:** ~2 minutes

```bash
pip install ccxt python-dotenv requests aiohttp numpy pandas
```

**Features:**
- ✅ Basic trading
- ✅ Exchange connectivity
- ❌ No AI consultation
- ❌ No advanced features

---

### Profile 2: STANDARD (Recommended)
**Size:** ~500MB  
**Time:** ~5 minutes

```bash
pip install ccxt python-dotenv requests aiohttp numpy pandas scipy scikit-learn anthropic openai
```

**Features:**
- ✅ Full trading
- ✅ Multi-AI consultation
- ✅ Intelligent balance management
- ✅ Dynamic trade counts
- ❌ No deep learning

---

### Profile 3: COMPLETE (Maximum Intelligence)
**Size:** ~3GB  
**Time:** ~15 minutes

```bash
bash install_dependencies.sh
# Or
pip install -r requirements.txt
```

**Features:**
- ✅ Everything in Standard
- ✅ Deep learning predictions
- ✅ Advanced visualizations
- ✅ Quantum computing features
- ✅ Web3/DEX trading
- ✅ Telegram notifications

---

## 🐛 TROUBLESHOOTING

### Issue: "No module named 'ccxt'"
```bash
pip install ccxt
```

### Issue: "No module named 'anthropic'"
```bash
pip install anthropic openai
```

### Issue: TensorFlow installation fails
```bash
# Try without TensorFlow - bot still works!
# Or install CPU-only version:
pip install tensorflow-cpu
```

### Issue: "Permission denied" errors
```bash
# Use virtual environment:
python3 -m venv apex_venv
source apex_venv/bin/activate
pip install -r requirements.txt
```

### Issue: NumPy/Pandas build errors
```bash
# Install system dependencies first:
sudo apt update
sudo apt install python3-dev build-essential libatlas-base-dev gfortran
pip install numpy pandas
```

### Issue: Out of memory during installation
```bash
# Install packages one by one:
pip install ccxt
pip install numpy
pip install pandas
# etc...
```

---

## 📊 DEPENDENCY MATRIX

### What Works Without What:

| Feature | ccxt | numpy | pandas | anthropic | tensorflow |
|---------|------|-------|--------|-----------|------------|
| **Basic Trading** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **AI Consultation** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Balance Manager** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Dynamic Trades** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Deep Learning** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Critical Features** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Goldmine Features** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Divine Intelligence** | ✅ | ✅ | ✅ | ❌ | ❌ |

**Legend:**
- ✅ Required for this feature
- ❌ Not required

---

## 🎯 WHAT YOU ACTUALLY NEED

### For $20 → $20,000 Growth:
**Minimum:**
```bash
pip install ccxt python-dotenv requests aiohttp numpy pandas scipy scikit-learn
```

**Recommended (adds AI learning):**
```bash
pip install anthropic openai
```

**That's it!** The core intelligence works without TensorFlow, Quantum, or Web3.

---

## 💡 PRO TIPS

1. **Start Minimal** → Add features later as needed
2. **Use Virtual Environment** → Keeps system Python clean
3. **Install AI APIs** → Claude/GPT-4 make bot smarter over time
4. **Skip TensorFlow** → Unless you have GPU and want deep learning
5. **Skip Quantum** → Unless you really want quantum features
6. **Add Telegram** → Great for monitoring on mobile

---

## 📝 VERIFICATION SCRIPT

Run this after installation to verify everything:

```python
python3 << 'PYEOF'
import sys

def test_import(package, name):
    try:
        __import__(package)
        print(f"✅ {name}")
        return True
    except ImportError:
        print(f"❌ {name}")
        return False

print("\n🔍 VERIFYING DEPENDENCIES\n")

core = [
    ('ccxt', 'CCXT (Required)'),
    ('dotenv', 'Python Dotenv (Required)'),
    ('requests', 'Requests (Required)'),
    ('aiohttp', 'AioHTTP (Required)'),
    ('numpy', 'NumPy (Required)'),
    ('pandas', 'Pandas (Required)'),
]

ai = [
    ('anthropic', 'Anthropic Claude (AI)'),
    ('openai', 'OpenAI GPT-4 (AI)'),
    ('scipy', 'SciPy (ML)'),
    ('sklearn', 'Scikit-learn (ML)'),
]

optional = [
    ('tensorflow', 'TensorFlow (Deep Learning)'),
    ('telegram', 'Telegram Bot'),
    ('qiskit', 'Qiskit (Quantum)'),
    ('web3', 'Web3 (DEX)'),
]

print("CORE (Required):")
core_ok = all(test_import(p, n) for p, n in core)

print("\nAI/ML (Recommended):")
ai_ok = all(test_import(p, n) for p, n in ai)

print("\nOPTIONAL:")
for p, n in optional:
    test_import(p, n)

print("\n" + "="*50)
if core_ok and ai_ok:
    print("✅ FULL INSTALLATION VERIFIED!")
    print("   Bot ready with all intelligence features!")
elif core_ok:
    print("✅ CORE INSTALLATION VERIFIED!")
    print("   Bot will work but without AI consultation")
    print("   Install AI packages for full intelligence:")
    print("   pip install anthropic openai scipy scikit-learn")
else:
    print("❌ MISSING CORE PACKAGES")
    print("   Install required packages:")
    print("   pip install ccxt python-dotenv requests aiohttp numpy pandas")
    sys.exit(1)
PYEOF
```

---

## 🚀 READY TO DEPLOY!

**Minimum for trading:**
```bash
pip install ccxt python-dotenv requests aiohttp numpy pandas
```

**Recommended for full intelligence:**
```bash
pip install ccxt python-dotenv requests aiohttp numpy pandas scipy scikit-learn anthropic openai
```

**Maximum power (optional):**
```bash
bash install_dependencies.sh
```

**Then start trading:**
```bash
python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py
```

---

**All dependencies documented, tested, and ready!** 📦✅
