#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE="/opt/leantrader/rpb-unified-20260917"
LEGACY="/opt/leantrader/leantrader-2025-c7f9327"
ANCHOR="c7f9327b44cbeedd91046dcdaed57e55ea360db3"
CURRENT_RPB="leantrader-rpb-testnet"
LEGACY_IMAGE="leantrader-2025-runtime:local"

cd "$SOURCE"

echo "=== LEANTRADER 2025 DEPENDENCY BOOTSTRAP ONLY ==="
echo "No container will be stopped and no trading runtime will be started."

git fetch --no-tags origin

if [ ! -d "$LEGACY/.git" ] && [ ! -f "$LEGACY/.git" ]; then
  rm -rf "$LEGACY"
  git worktree add --detach "$LEGACY" "$ANCHOR"
fi

if [ "$(git -C "$LEGACY" rev-parse HEAD)" != "$ANCHOR" ]; then
  echo "Wrong historical worktree HEAD; refusing bootstrap."
  exit 1
fi

echo "historical_head=$(git -C "$LEGACY" rev-parse HEAD)"
echo "historical_date=$(git -C "$LEGACY" show -s --format=%cI HEAD)"

BASE_IMAGE="$(docker inspect "$CURRENT_RPB" --format '{{.Config.Image}}')"
echo "base_image=$BASE_IMAGE"

cat > /tmp/Dockerfile.leantrader-2025-deps <<EOF
FROM $BASE_IMAGE
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc g++ libgomp1 libgl1 libglib2.0-0 \
      libxml2 libxslt1.1 libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --upgrade pip setuptools wheel

# Core dependencies and the exact classes of packages encountered during the
# previous LeanTrader import-smoke/restoration work.
RUN pip install --no-cache-dir --prefer-binary \
      pytest pytest-asyncio pytest-cov pytest-mock black flake8 mypy \
      numpy pandas scipy scikit-learn joblib \
      ccxt PyYAML aiohttp psutil python-dotenv redis web3 \
      requests httpx beautifulsoup4 lxml feedparser \
      fastapi uvicorn sqlalchemy prometheus-client

# 2025 intelligence/model stack, including the Tensor/Keras layer the old
# Evolution Engine imported at startup.
RUN pip install --no-cache-dir --prefer-binary \
      tensorflow keras torch transformers \
      xgboost lightgbm catboost yfinance python-binance \
      websocket-client websockets eth-account eth-utils \
      matplotlib seaborn plotly \
      nltk textblob vaderSentiment \
      "langchain==0.3.27" langchain-community \
      anthropic openai \
      python-telegram-bot aiogram \
      stripe qrcode \
      pytz python-dateutil networkx \
      cryptography bcrypt schedule loguru toml \
      optuna statsmodels \
      tweepy praw discord.py celery \
      qiskit qiskit-aer qiskit-ibm-runtime

# Additional 2025 specialist-engine dependencies.  These are separated so any
# platform-specific wheel problem is obvious in the build output.
RUN pip install --no-cache-dir --prefer-binary TA-Lib ta

RUN pip check
EOF

echo
echo "=== BUILDING FULL 2025 DEPENDENCY IMAGE ==="
docker build -t "$LEGACY_IMAGE" -f /tmp/Dockerfile.leantrader-2025-deps /tmp

echo
echo "=== DEPENDENCY IMPORT MATRIX ==="
docker run --rm "$LEGACY_IMAGE" python - <<'PY'
import importlib
import sys

modules = [
    "pytest", "numpy", "pandas", "scipy", "sklearn", "ccxt",
    "yaml", "aiohttp", "psutil", "dotenv", "redis", "web3",
    "bs4", "lxml", "feedparser", "tensorflow", "keras", "torch",
    "transformers", "xgboost", "lightgbm", "catboost", "joblib",
    "yfinance", "websocket", "websockets", "requests", "httpx",
    "eth_account", "eth_utils", "matplotlib", "seaborn", "plotly",
    "nltk", "textblob", "vaderSentiment",
    "langchain", "langchain_community", "anthropic", "openai",
    "telegram", "aiogram", "fastapi", "uvicorn", "sqlalchemy",
    "stripe", "qrcode", "pytz", "dateutil", "networkx",
    "cryptography", "bcrypt", "schedule", "loguru", "toml",
    "optuna", "statsmodels", "prometheus_client",
    "tweepy", "praw", "discord", "celery",
    "qiskit", "qiskit_aer", "qiskit_ibm_runtime",
    "talib", "ta",
]
failed = []
for name in modules:
    try:
        importlib.import_module(name)
        print(f"IMPORT_OK {name}")
    except Exception as exc:
        failed.append((name, type(exc).__name__, str(exc)[:240]))
        print(f"IMPORT_FAIL {name} {type(exc).__name__}: {str(exc)[:240]}")

if failed:
    print("\nDEPENDENCY_MATRIX_FAILED")
    for row in failed:
        print(row)
    sys.exit(1)

print("\nLEGACY_2025_DEPENDENCIES_OK")
PY

echo
echo "=== PYTEST / TENSOR / KERAS PROOF ==="
docker run --rm "$LEGACY_IMAGE" python - <<'PY'
import pytest
import tensorflow as tf
import keras
print("PYTEST_OK", pytest.__version__)
print("TENSORFLOW_OK", tf.__version__)
print("KERAS_OK", keras.__version__)
PY

echo
echo "=== COMPILE EXACT OCTOBER-2025 SOURCE TREE ==="
docker run --rm \
  -v "$LEGACY:/app:ro" \
  -w /app \
  "$LEGACY_IMAGE" \
  python -m compileall -q .
echo "LEGACY_2025_COMPILE_OK"

echo
echo "=== EXACT 2025 ORCHESTRATOR IMPORT SMOKE ==="
docker run --rm \
  -v "$LEGACY:/app:ro" \
  -w /app \
  "$LEGACY_IMAGE" \
  python -c 'from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator; print("LEGACY_2025_IMPORT_OK")'

echo
echo "=== BOOTSTRAP COMPLETE ==="
echo "No trading cutover was performed."
echo "Image ready: $LEGACY_IMAGE"
