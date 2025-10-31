# 📋 Install All Dependencies in New Venv

## 🚀 Quick Install (Recommended):

```bash
cd ~/bot || cd /root/bot

# 1. Create new venv
python3 -m venv .venv

# 2. Activate venv
source .venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install all dependencies (use the script)
bash 📦_COMPLETE_DEPENDENCIES.sh

# OR use requirements.txt
pip install --no-cache-dir -r requirements.txt
```

---

## 📦 Alternative: One-Line Install

```bash
cd ~/bot && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install --no-cache-dir ccxt pandas numpy python-dotenv loguru "pyarrow>=15,<18" scipy scikit-learn beautifulsoup4 lxml html5lib requests "python-telegram-bot>=20,<21" "urllib3>=2" aiogram "tensorflow>=2.17,<2.19" keras langchain langchain-core langchain-community openai qiskit qiskit-aer qiskit-optimization qiskit-algorithms qiskit-ibm-runtime qrcode[pil] stripe "tzlocal<5" pytz APScheduler matplotlib seaborn
```

---

## ✅ Verify Installation:

```bash
# Test all critical imports
python3 -c "
import ccxt
import pandas
import numpy
import qiskit
import tensorflow
import langchain
import telegram
import bs4
print('✅ All core dependencies installed!')
"
```

---

## 📋 What's Included:

- ✅ **Trading**: ccxt (all exchanges)
- ✅ **Data**: pandas, numpy, pyarrow
- ✅ **ML**: tensorflow, scikit-learn, scipy
- ✅ **LLM**: langchain, openai
- ✅ **Quantum**: qiskit (all modules)
- ✅ **Telegram**: python-telegram-bot, aiogram
- ✅ **Web**: beautifulsoup4, requests
- ✅ **Utils**: qrcode, stripe, pytz, APScheduler

**All dependencies from our session are included!**
