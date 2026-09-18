#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE="/opt/leantrader/rpb-unified-20260917"
LEGACY="/opt/leantrader/leantrader-2025-c7f9327"
ANCHOR="c7f9327b44cbeedd91046dcdaed57e55ea360db3"
CURRENT_RPB="leantrader-rpb-testnet"
CURRENT_INTEL="leantrader-intelligence-only"
LEGACY_CONTAINER="leantrader-2025-testnet"
ENV_FILE="/opt/leantrader/leantrader-2025-testnet.env"
LEGACY_IMAGE="leantrader-2025-runtime:local"

cd "$SOURCE"

echo "=== 2025 LEANTRADER RESTORE ==="
echo "anchor=$ANCHOR"
echo "source=$SOURCE"
echo "runtime=$LEGACY"

git fetch --no-tags origin

if [ ! -d "$LEGACY/.git" ] && [ ! -f "$LEGACY/.git" ]; then
  rm -rf "$LEGACY"
  git worktree add --detach "$LEGACY" "$ANCHOR"
fi

if [ "$(git -C "$LEGACY" rev-parse HEAD)" != "$ANCHOR" ]; then
  echo "Refusing to use a non-2025 runtime worktree."
  exit 1
fi

echo
echo "=== PRESERVE EXACT 2025 BRAIN ==="
git -C "$LEGACY" status --short
echo "legacy_head=$(git -C "$LEGACY" rev-parse HEAD)"
echo "legacy_date=$(git -C "$LEGACY" show -s --format=%cI HEAD)"

# Keep the 2025 controller/queues/scouts/scalper/decision/evolution logic.
# Overlay only the already-proven authenticated execution plumbing so the
# historical brain does not fall back to simulated trades or synthetic closes.
rsync -a --delete "$SOURCE/src/leantrader/" "$LEGACY/src/leantrader/"
cp "$SOURCE/EXECUTION_ORCHESTRATOR.py" "$LEGACY/EXECUTION_ORCHESTRATOR.py"

# Avoid a second independent order owner. RPB remains instantiated/available
# to the historical system, but the unified 2025 controller owns execution.
python3 - "$LEGACY/COMPLETE_ULTIMATE_ORCHESTRATOR.py" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text()
old = """        # START REAL PROFIT BOT - 35 Pairs Trading!
        if hasattr(self, 'real_profit_bot') and self.real_profit_bot:
            # Wrap sync run() in async
            async def run_real_profit_loop():
                await asyncio.to_thread(self.real_profit_bot.run)

            tasks.append(asyncio.create_task(run_real_profit_loop()))
            logger.info("✅ 💰 REAL PROFIT BOT STARTED - Trading 35 pairs!")
"""
new = """        # REAL_PROFIT_BOT remains part of the historical system, but it is
        # not launched as an independent order owner here. Signals and
        # decisions execute through the unified ExecutionOrchestrator.
        if hasattr(self, 'real_profit_bot') and self.real_profit_bot:
            logger.info("✅ 💰 REAL PROFIT BOT PRESENT - unified controller owns execution")
"""
if old in s:
    s = s.replace(old, new)
p.write_text(s)
PY

echo
echo "=== BUILD TESTNET ENV WITHOUT REUSING TRACKED 2025 SECRETS ==="
: > "$ENV_FILE"

docker inspect "$CURRENT_RPB"   --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null   | grep -E '^(BYBIT_|EXECUTION_|ACCOUNT_|TELEGRAM_|NEWS|CRYPTOPANIC|OPENAI_|ANTHROPIC_|HUGGINGFACE_|QISKIT_|ETHERSCAN_|COINGECKO_|CRYPTOCOMPARE_)'   >> "$ENV_FILE" || true

cat >> "$ENV_FILE" <<'EOF'
TRADING_MODE=testnet
EXECUTION_MODE=testnet
USE_TESTNET=true
ENABLE_LIVE=false
GATEIO_MODE=testnet
PYTHONUNBUFFERED=1
EOF

chmod 600 "$ENV_FILE"

for key in ANTHROPIC_API_KEY OPENAI_API_KEY HUGGINGFACE_TOKEN QISKIT_IBM_TOKEN; do
  if grep -q "^\${key}=." "$ENV_FILE"; then
    echo "$key=SET"
  else
    echo "$key=UNSET"
  fi
done

BASE_IMAGE="$(docker inspect "$CURRENT_RPB" --format '{{.Config.Image}}')"
echo "base_runtime_image=$BASE_IMAGE"

# Historical RUN_BOT.py loads /app/.env itself.  Replace only this detached
# 2025 worktree's tracked .env with the currently authenticated Testnet
# environment so stale 2025 secrets/mode values cannot override Docker env.
cp "$ENV_FILE" "$LEGACY/.env"
chmod 600 "$LEGACY/.env"

# Package markers that were part of the later import-smoke repairs.  They do
# not change trading logic; they make restored packages importable when the
# corresponding directories exist.
for pkgdir in "$LEGACY/src/leantrader/agents" "$LEGACY/src/leantrader/production"; do
  if [ -d "$pkgdir" ]; then
    touch "$pkgdir/__init__.py"
  fi
done

echo
echo "=== BUILD COMPLETE 2025 COMPATIBILITY IMAGE ==="
cat > /tmp/Dockerfile.leantrader-2025 <<EOF
FROM $BASE_IMAGE
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc g++ libgomp1 libgl1 libglib2.0-0 libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --upgrade pip setuptools wheel

# Packages already encountered during LeanTrader restoration/import-smoke work.
RUN pip install --no-cache-dir --prefer-binary \
      pytest pytest-asyncio pytest-cov pytest-mock \
      numpy pandas scipy scikit-learn joblib numba tiktoken python-multipart \
      ccxt PyYAML aiohttp psutil python-dotenv redis web3 requests httpx \
      beautifulsoup4 lxml feedparser

# October-2025 active intelligence/runtime stack: Tensor/Keras, model arsenal,
# exchange/data clients, NLP, external-AI clients, orchestration and utilities.
RUN pip install --no-cache-dir --prefer-binary \
      tensorflow keras torch transformers \
      xgboost lightgbm catboost yfinance python-binance \
      websocket-client websockets eth-account eth-utils \
      matplotlib seaborn plotly \
      nltk textblob vaderSentiment \
      "langchain==0.3.27" langchain-community anthropic openai \
      python-telegram-bot aiogram \
      fastapi uvicorn sqlalchemy \
      stripe qrcode \
      pytz python-dateutil networkx \
      cryptography bcrypt schedule loguru toml \
      optuna statsmodels prometheus-client \
      tweepy praw discord.py celery \
      qiskit qiskit-aer qiskit-ibm-runtime

# Technical-analysis libraries used by several 2025 specialist engines.
RUN pip install --no-cache-dir --prefer-binary TA-Lib ta || true

RUN pip check
EOF

docker build -t "$LEGACY_IMAGE" -f /tmp/Dockerfile.leantrader-2025 /tmp

echo
echo "=== COMPLETE DEPENDENCY IMPORT MATRIX ==="
docker run --rm "$LEGACY_IMAGE" python - <<'PY'
import importlib
import sys

modules = [
    # previously repaired/core validation
    "pytest", "numpy", "pandas", "scipy", "sklearn", "numba", "tiktoken", "multipart", "ccxt",
    "yaml", "aiohttp", "psutil", "dotenv", "redis", "web3",
    # 2025 runtime imports
    "bs4", "lxml", "feedparser", "tensorflow", "keras", "torch",
    "transformers", "xgboost", "lightgbm", "catboost", "joblib",
    "yfinance", "websocket", "websockets", "requests", "httpx",
    "eth_account", "eth_utils", "matplotlib", "seaborn", "plotly",
    "nltk", "textblob", "vaderSentiment", "langchain",
    "langchain_community", "anthropic", "openai", "telegram", "aiogram",
    "fastapi", "uvicorn", "sqlalchemy", "stripe", "qrcode", "pytz",
    "dateutil", "networkx", "cryptography", "bcrypt", "schedule",
    "loguru", "toml", "optuna", "statsmodels", "prometheus_client",
    "tweepy", "praw", "discord", "celery", "qiskit",
    "qiskit_aer", "qiskit_ibm_runtime",
]
failed = []
for name in modules:
    try:
        importlib.import_module(name)
        print(f"IMPORT_OK {name}")
    except Exception as exc:
        failed.append((name, type(exc).__name__, str(exc)[:240]))
        print(f"IMPORT_FAIL {name} {type(exc).__name__}: {str(exc)[:240]}")

# TA-Lib is historically used by specialist/older engines. Require it when the
# wheel installed successfully; report separately if the platform cannot load
# it, before any trading cutover.
for name in ("talib", "ta"):
    try:
        importlib.import_module(name)
        print(f"IMPORT_OK {name}")
    except Exception as exc:
        failed.append((name, type(exc).__name__, str(exc)[:240]))
        print(f"IMPORT_FAIL {name} {type(exc).__name__}: {str(exc)[:240]}")

if failed:
    print("DEPENDENCY_MATRIX_FAILED", failed)
    sys.exit(1)
print("LEGACY_2025_DEPENDENCIES_OK")
PY

echo
echo "=== APPLY NON-STRATEGY 2025 SOURCE REPAIRS ==="
# These are parser/import repairs only. They do not alter trading thresholds,
# signals, sizing, execution mode, or strategy behavior.
python3 - "$LEGACY" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])

# Historical test_api_connections.py was already listed in the 2025 repair
# scripts as a syntax-error file. Repair only object naming + typing imports.
p = root / "test_api_connections.py"
if p.exists():
    s = p.read_text()
    if "from typing import Dict, Any" not in s:
        s = s.replace("import sys\n", "import sys\nfrom typing import Dict, Any\n", 1)
    s = s.replace("self.ExchangeManager() = ExchangeManager()", "self.exchange_manager = ExchangeManager()")
    s = s.replace("self.ExchangeManager()", "self.exchange_manager")
    p.write_text(s)

# Historical tools/market_data_ultra.py contains a multiline f-string that is
# invalid Python. Preserve the same URL/values and only repair the parser form.
p = root / "tools" / "market_data_ultra.py"
if p.exists():
    s = p.read_text()
    old = '''                f"https://cryptopanic.com/api/v1/posts/?auth_token={
                    self.api_keys.get(
                        'cryptopanic', '')}&currencies={symbol}",'''
    new = '''                f"https://cryptopanic.com/api/v1/posts/?auth_token={self.api_keys.get('cryptopanic', '')}&currencies={symbol}",'''
    if old in s:
        s = s.replace(old, new)
    p.write_text(s)

# Package markers restored during the later module-repair work.
for pkgdir in (root / "src" / "leantrader" / "agents", root / "src" / "leantrader" / "production"):
    if pkgdir.is_dir():
        (pkgdir / "__init__.py").touch()

print("LEGACY_2025_SOURCE_REPAIRS_APPLIED")
PY

echo
echo "=== SOURCE SYNTAX CHECK — NO PYC WRITES ==="
docker run --rm -i \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  python - <<'PY'
from pathlib import Path
import sys

root = Path("/legacy")
bad = []
checked = 0
skip_parts = {".git", "__pycache__", ".venv", "venv", "runtime", "node_modules"}

for p in sorted(root.rglob("*.py")):
    if any(part in skip_parts for part in p.parts):
        continue
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
        compile(src, str(p.relative_to(root)), "exec", dont_inherit=True)
        checked += 1
    except SyntaxError as exc:
        bad.append((str(p.relative_to(root)), exc.lineno, exc.msg))
    except Exception as exc:
        bad.append((str(p.relative_to(root)), None, f"{type(exc).__name__}: {exc}"))

print("SYNTAX_CHECKED", checked)
if bad:
    print("SYNTAX_ERRORS", len(bad))
    for row in bad:
        print(row)
    sys.exit(1)
print("LEGACY_2025_SOURCE_SYNTAX_OK")
PY

echo
echo "=== IMPORT SMOKE TEST — NO TRADING ==="
docker run --rm \
  --name leantrader-2025-import-smoke \
  --env-file "$ENV_FILE" \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  sh -lc 'cp -a /legacy /tmp/leantrader-2025 && cd /tmp/leantrader-2025 && python -c '"'"'from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator; print("LEGACY_2025_IMPORT_OK")'"'"''

echo
echo "=== CUTOVER TO 2025 CONTROLLER ==="
docker rm -f "$LEGACY_CONTAINER" >/dev/null 2>&1 || true
docker stop "$CURRENT_RPB" >/dev/null 2>&1 || true

docker run -d   --name "$LEGACY_CONTAINER"   --restart unless-stopped   --env-file "$ENV_FILE"   -v "$LEGACY:/app"   -w /app   "$LEGACY_IMAGE"   python RUN_BOT.py --testnet >/dev/null

sleep 25

if ! docker ps --format '{{.Names}}' | grep -qx "$LEGACY_CONTAINER"; then
  echo "2025 runtime exited during startup. Restoring previous RPB."
  docker logs --tail 220 "$LEGACY_CONTAINER" 2>&1 || true
  docker start "$CURRENT_RPB" >/dev/null 2>&1 || true
  exit 1
fi

docker stop "$CURRENT_INTEL" >/dev/null 2>&1 || true

echo
echo "=== 2025 RUNTIME STATUS ==="
docker ps --filter "name=$LEGACY_CONTAINER"   --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'

echo
echo "=== ENGINE START EVIDENCE ==="
docker logs --since 3m "$LEGACY_CONTAINER" 2>&1   | grep -E 'Decision loop started|EXECUTION LOOP STARTED|SMART SCALPING LOOP STARTED|Scalper generated|Published .* signals|Decision:|EXECUTING:|SUBMITTING|ORDER ACKNOWLEDGED|Trade executed|Evolution|Sentient|Swarm|Learning loop started|Scouting loop started|ERROR|Traceback'   | tail -n 240 || true

echo
echo "=== CONTAINER MODE EVIDENCE ==="
docker exec "$LEGACY_CONTAINER" python - <<'PY'
import os
print({
    "TRADING_MODE": os.getenv("TRADING_MODE"),
    "EXECUTION_MODE": os.getenv("EXECUTION_MODE"),
    "USE_TESTNET": os.getenv("USE_TESTNET"),
    "ENABLE_LIVE": os.getenv("ENABLE_LIVE"),
    "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
    "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
    "HUGGINGFACE_TOKEN": bool(os.getenv("HUGGINGFACE_TOKEN")),
})
PY

echo
echo "2025 controller is now the active Testnet runtime."
