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
STATE_ROOT="/opt/leantrader/runtime/leantrader-2025-state"
WORKSPACE_STATE="$STATE_ROOT/workspace"

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
echo "=== RESTORE EXACT 2025 BRAIN BEFORE OVERLAYS ==="
git -C "$LEGACY" reset --hard "$ANCHOR"
git -C "$LEGACY" clean -fd
mkdir -p "$WORKSPACE_STATE"
chmod 700 "$STATE_ROOT" "$WORKSPACE_STATE"
git -C "$LEGACY" status --short
echo "legacy_head=$(git -C "$LEGACY" rev-parse HEAD)"
echo "legacy_date=$(git -C "$LEGACY" show -s --format=%cI HEAD)"

# Keep the 2025 controller/queues/scouts/scalper/decision/evolution logic.
# Overlay only the already-proven authenticated execution plumbing so the
# historical brain does not fall back to simulated trades or synthetic closes.
rsync -a --delete "$SOURCE/src/leantrader/" "$LEGACY/src/leantrader/"
cp "$SOURCE/EXECUTION_ORCHESTRATOR.py" "$LEGACY/EXECUTION_ORCHESTRATOR.py"

# Modern authenticated execution requires these two top-level reconciliation
# modules. They do not replace the October-2025 brain; they only preserve
# authenticated ACK -> fill -> position -> close -> realized-net semantics.
for dep in rpb_fill_reconciliation.py rpb_position_lifecycle.py; do
    if [ ! -f "$SOURCE/$dep" ]; then
        echo "Missing authenticated execution dependency: $SOURCE/$dep"
        exit 1
    fi
    cp "$SOURCE/$dep" "$LEGACY/$dep"
done

cp "$SOURCE/ops/legacy_2025_real_intelligence_bridge.py" "$LEGACY/LEGACY_2025_REAL_INTELLIGENCE_BRIDGE.py"

# Apply compatibility overlays only; the October-2025 signal/decision strategy stays intact.
python3 - "$LEGACY" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

# 1. The 2025 base initializer created RealProfitBot with its default live mode.
# Propagate the orchestrator-selected mode instead. It remains an available
# historical component but is NOT an independent execution owner.
p = root / "COMPLETE_UNIFIED_ORCHESTRATOR.py"
s = p.read_text()
s = s.replace(
    "self.trading_engines['real_profit'] = RealProfitBot()",
    "self.trading_engines['real_profit'] = RealProfitBot(mode=self.mode)",
)
if "self.trading_engines['real_profit'] = RealProfitBot(mode=self.mode)" not in s:
    raise SystemExit("failed to mode-wire historical RealProfitBot")
p.write_text(s)

# 2. Repair the historical swarm handoff: the old decision loop called a
# method that did not exist and, when a result existed, blended confidence even
# when directions disagreed. The real-evidence bridge supplies the method.
p = root / "COMPLETE_UNIFIED_ORCHESTRATOR.py"
s = p.read_text()
s = s.replace(
    "swarm_decision = await self.swarm.collective_decision()",
    "swarm_decision = await self.swarm.collective_decision(signal)",
)
old = """                        # Boost confidence if swarm agrees
                        if swarm_decision:
                            swarm_conf = swarm_decision.get('confidence', 0.0)
                            if swarm_conf > 0:
                                signal_confidence = min(0.95, (signal_confidence + swarm_conf) / 2)"""
new = """                        # Swarm may strengthen the specialist only when its
                        # real-market direction agrees. Opposing/hold consensus
                        # is informative but does not globally veto the specialist.
                        if swarm_decision:
                            swarm_conf = float(swarm_decision.get('confidence', 0.0) or 0.0)
                            swarm_action = str(swarm_decision.get('action', 'hold')).lower()
                            specialist_action = str(signal_side or 'hold').lower()
                            if (
                                swarm_decision.get('real_market_data') is True
                                and swarm_conf > 0
                                and swarm_action == specialist_action
                            ):
                                signal_confidence = min(
                                    0.99,
                                    max(float(signal_confidence or 0.0), swarm_conf),
                                )"""
if old in s:
    s = s.replace(old, new)
if "collective_decision(signal)" not in s:
    raise SystemExit("failed to connect swarm to the current decision signal")
p.write_text(s)

# 2. Remove only the standalone RPB task from CompleteUltimateOrchestrator.
# Smart Scalper -> DataHub -> UnifiedDecisionEngine -> ExecutionOrchestrator
# remains the order-producing path.
p = root / "COMPLETE_ULTIMATE_ORCHESTRATOR.py"
s = p.read_text()
start_marker = "        # START REAL PROFIT BOT - 35 Pairs Trading!"
end_marker = "        # START DYNAMIC MARKET SCANNER - Auto-discover trending pairs!"
start = s.find(start_marker)
end = s.find(end_marker, start) if start >= 0 else -1
if start >= 0 and end > start:
    replacement = (
        "        # REAL_PROFIT_BOT remains available as a historical component,\n"
        "        # but unified 2025 orchestration owns execution.\n"
        "        if hasattr(self, 'real_profit_bot') and self.real_profit_bot:\n"
        "            logger.info(\"✅ 💰 REAL PROFIT BOT PRESENT - unified controller owns execution\")\n\n"
    )
    s = s[:start] + replacement + s[end:]

if "asyncio.to_thread(self.real_profit_bot.run)" in s:
    raise SystemExit("standalone RealProfitBot execution loop still present")

# Use one SmartScalpingEngine instance across base and advanced orchestration,
# preserving its learned session performance instead of duplicating state.
s = s.replace(
    """            self.smart_scalping = SmartScalpingEngine(
                ultra_core=ultra_core_instance,
                risk_engine=self.risk_engine
            )""",
    """            self.smart_scalping = (
                self.trading_engines.get('smart_scalping')
                if hasattr(self, 'trading_engines')
                else None
            ) or SmartScalpingEngine(
                ultra_core=ultra_core_instance,
                risk_engine=self.risk_engine
            )""",
)

# Modern authenticated ExecutionOrchestrator reports realized_net_profit.
s = s.replace(
    "exec_stats['total_profit']",
    "exec_stats.get('realized_net_profit', exec_stats.get('total_profit', 0.0))",
)
s = s.replace(
    "exec_stats.get('total_profit', 0)",
    "exec_stats.get('realized_net_profit', exec_stats.get('total_profit', 0.0))",
)

# The two historical intelligence managers return dictionaries; preview them
# as dictionaries instead of slicing them like lists. Logging only.
old = """                                for sig in goldmine_signals[:2]:  # Log first 2
                                    logger.info(f"💎 GOLDMINE: {symbol} - {sig.get('feature', 'Unknown')}: {sig.get('signal', 'N/A')}")"""
new = """                                if isinstance(goldmine_signals, dict):
                                    preview = list(goldmine_signals.items())[:2]
                                    for feature_name, sig in preview:
                                        logger.info(f"💎 GOLDMINE: {symbol} - {feature_name}: {sig}")
                                else:
                                    for sig in list(goldmine_signals)[:2]:
                                        logger.info(f"💎 GOLDMINE: {symbol} - {sig}")"""
s = s.replace(old, new)

old = """                            for sig in divine_signals[:3]:  # Log first 3
                                logger.info(f"🔮 DIVINE: {sig.get('feature', 'Unknown')} - {sig.get('insight', 'N/A')}")"""
new = """                            if isinstance(divine_signals, dict):
                                for feature_name, sig in list(divine_signals.items())[:3]:
                                    logger.info(f"🔮 DIVINE: {feature_name} - {sig}")
                            else:
                                for sig in list(divine_signals)[:3]:
                                    logger.info(f"🔮 DIVINE: {sig}")"""
s = s.replace(old, new)
p.write_text(s)

# 3. Match the actual 2025 PrivateTxClient constructor. With no DEX sender or
# private key configured it correctly remains unavailable/monitoring-only.
p = root / "DEX_ORCHESTRATOR.py"
if p.exists():
    s = p.read_text()
    old = """                self.private_client = PrivateTxClient(
                    endpoint="https://rpc.flashbots.net",
                    api_key=""  # Set from env
                )"""
    if old in s:
        s = s.replace(old, "                self.private_client = PrivateTxClient(sender=None)")
    p.write_text(s)

# 4. Historical auxiliary bots carried direct credential constants. They are
# not execution owners in the restored topology. Make them environment/public
# data clients so only the universal ExecutionOrchestrator owns private orders.
p = root / "REAL_PROFIT_BOT.py"
if p.exists():
    s = p.read_text()
    if "import os\n" not in s.split("class REAL_PROFIT_BOT", 1)[0]:
        s = s.replace("import requests\n", "import requests\nimport os\n", 1)

    s = re.sub(
        r'self\.telegram_bot_token\s*=\s*"[^"]*"',
        'self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")',
        s,
    )
    s = re.sub(
        r'self\.admin_chat_id\s*=\s*"[^"]*"',
        'self.admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")',
        s,
    )
    s = re.sub(
        r"'apiKey':\s*os\.getenv\('BYBIT_API_KEY',\s*'[^']*'\)",
        "'apiKey': os.getenv('BYBIT_API_KEY', '')",
        s,
    )
    s = re.sub(
        r"'secret':\s*os\.getenv\('BYBIT_SECRET',\s*'[^']*'\)",
        "'secret': os.getenv('BYBIT_SECRET', '')",
        s,
    )
    s = re.sub(
        r"'apiKey':\s*'[^']*',\s*\n\s*'secret':\s*'[^']*',\s*\n\s*'sandbox': False",
        "'apiKey': os.getenv('GATEIO_LIVE_API_KEY', os.getenv('GATE_API_KEY', '')),\n"
        "                'secret': os.getenv('GATEIO_LIVE_SECRET', os.getenv('GATE_SECRET', '')),\n"
        "                'sandbox': False",
        s,
        count=1,
    )
    s = s.replace(
        'print("💰 TRADING EXCHANGE: Gate.io (REAL INCOME GENERATION)")',
        'print(f"💰 TRADING EXCHANGE: {\'Bybit Testnet\' if self.mode == \'testnet\' else \'Gate.io Live\'}")',
    )
    p.write_text(s)

p = root / "enhanced_trading_bot.py"
if p.exists():
    s = p.read_text()
    # This historical helper remains intelligence/public-data only. Private
    # placement belongs to ExecutionOrchestrator.
    block_start = s.find("        # Bybit configuration with REAL trading enabled")
    block_end = s.find("        # Telegram configuration", block_start)
    if block_start >= 0 and block_end > block_start:
        replacement = (
            "        # Public Bybit market-data client; private execution is centralized.\n"
            "        self.bybit = ccxt.bybit({'enableRateLimit': True})\n\n"
        )
        s = s[:block_start] + replacement + s[block_end:]

    s = s.replace(
        "            exchanges_to_init = ['binance', 'okx', 'coinbase', 'kucoin', 'gateio', 'huobi']",
        "            exchanges_to_init = ['binance', 'okx', 'coinbase', 'kucoin', 'gateio', 'huobi']\n"
        "            exchange_aliases = {'gateio': 'gate', 'huobi': 'htx'}",
    )
    s = s.replace(
        "                    exchange_class = getattr(ccxt, exchange_name)",
        "                    exchange_class = getattr(ccxt, exchange_aliases.get(exchange_name, exchange_name))",
    )
    p.write_text(s)

# 5. Install the evidence bridge before the historical orchestrator imports.
# This keeps the 2025 classes/topology but replaces placeholder/RNG market
# evidence with real public Bybit observations.
p = root / "RUN_BOT.py"
s = p.read_text()
needle = "# Import orchestrator\nprint(\"📦 Loading trading systems...\")"
replacement = (
    "# Install October-2025 real-evidence compatibility bridge\n"
    "from LEGACY_2025_REAL_INTELLIGENCE_BRIDGE import install as _install_real_intelligence\n"
    "_install_real_intelligence()\n\n"
    "# Import orchestrator\n"
    "print(\"📦 Loading trading systems...\")"
)
if "_install_real_intelligence()" not in s:
    if needle not in s:
        raise SystemExit("failed to locate RUN_BOT orchestrator import marker")
    s = s.replace(needle, replacement, 1)
p.write_text(s)

# 6. Keep the 2025 Dynamic Market Scanner alive from public market data even
# when no private arbitrage credentials are configured.
p = root / "COMPLETE_ULTIMATE_ORCHESTRATOR.py"
s = p.read_text()
old = """        else:
            logger.warning("⚠️  Need at least 1 exchange for market scanning")
            self.market_scanner = None"""
new = """        else:
            try:
                import ccxt.async_support as ccxt_async
                public_bybit = ccxt_async.bybit({'enableRateLimit': True})
                self.market_scanner = DynamicMarketScanner({'bybit': public_bybit}, self.data_hub)
                self.advanced_orchestrators['market_scanner'] = self.market_scanner
                logger.info("✅ 🔍 DYNAMIC MARKET SCANNER WIRED - public Bybit market data")
            except Exception as e:
                logger.warning(f"⚠️  Public market scanner unavailable: {e}")
                self.market_scanner = None"""
if old in s:
    s = s.replace(old, new)
p.write_text(s)

print("LEGACY_2025_RUNTIME_COMPAT_OVERLAYS_OK")
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
EVOLUTION_DB_PATH=/workspace/evolution_engine.db
DYNAMIC_SCAN_SECONDS=60
EXECUTION_FILL_RECONCILE_SECONDS=6
PYTHONUNBUFFERED=1
EOF

chmod 600 "$ENV_FILE"

echo
echo "=== MIRROR CURRENT TESTNET SECRET AUTHORITY ==="
SECRET_MOUNT_ARGS=()
SECRET_ROOT="$STATE_ROOT/secrets"
rm -rf "$SECRET_ROOT"
mkdir -p "$SECRET_ROOT"
chmod 700 "$SECRET_ROOT"

declare -A SECRET_DEST_SEEN=()

add_secret_mount() {
  local spec="$1"
  local dest="$2"
  [ -n "$dest" ] || return 0
  if [ -z "${SECRET_DEST_SEEN[$dest]:-}" ]; then
    SECRET_MOUNT_ARGS+=(--mount "$spec")
    SECRET_DEST_SEEN["$dest"]=1
  fi
}

# First reuse ordinary bind/volume mounts when Docker exposes them.
while IFS='|' read -r mtype source name dest; do
  [ -n "$dest" ] || continue
  case "$dest" in
    /run/secrets/*)
      if [ "$mtype" = "bind" ] && [ -n "$source" ] && [ -e "$source" ]; then
        add_secret_mount "type=bind,src=$source,dst=$dest,readonly" "$dest"
      elif [ "$mtype" = "volume" ] && [ -n "$name" ]; then
        add_secret_mount "type=volume,src=$name,dst=$dest,readonly" "$dest"
      fi
      ;;
  esac
done < <(
  docker inspect "$CURRENT_RPB" \
    --format '{{range .Mounts}}{{printf "%s|%s|%s|%s\n" .Type .Source .Name .Destination}}{{end}}'
)

# Some Compose/runtime setups create credential files inside the container
# instead of exposing them as .Mounts. Reuse only paths already configured by
# the healthy authenticated RPB, copy them without printing contents, and mount
# them read-only at the exact same path in the restored runtime.
while IFS='=' read -r env_key secret_path; do
  [ -n "$env_key" ] || continue
  [ -n "$secret_path" ] || continue
  case "$env_key" in
    BYBIT_*_FILE|CCXT_*_FILE)
      if docker exec "$CURRENT_RPB" sh -c 'test -r "$1"' sh "$secret_path" >/dev/null 2>&1; then
        safe_name="$(printf '%s' "$env_key" | tr '[:upper:]' '[:lower:]')"
        host_copy="$SECRET_ROOT/$safe_name"
        docker cp "$CURRENT_RPB:$secret_path" "$host_copy" >/dev/null
        chmod 600 "$host_copy"
        add_secret_mount "type=bind,src=$host_copy,dst=$secret_path,readonly" "$secret_path"
        echo "$env_key=READY_FROM_CURRENT_RPB"
      fi
      ;;
  esac
done < <(
  docker inspect "$CURRENT_RPB" \
    --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep -E '^(BYBIT|CCXT)_[A-Z0-9_]*_FILE=' || true
)

if [ "${#SECRET_MOUNT_ARGS[@]}" -gt 0 ]; then
  echo "Testnet credential files mirrored without exposing secret values."
else
  echo "No file-based credentials mirrored; authenticated preflight will test direct env credentials."
fi

echo
echo "=== CURRENT RPB AUTHORITY PROOF — READ ONLY ==="
docker exec -i "$CURRENT_RPB" python - <<'PY' || true
try:
    from src.leantrader.execution.router import execution_status
    row = execution_status(mode="testnet", exchange_id="bybit")
    print({
        "execution_mode": row.get("execution_mode"),
        "authority": row.get("authority"),
        "exchange": row.get("exchange"),
        "authenticated": bool(row.get("authenticated")),
    })
except Exception as exc:
    print({"current_rpb_status_probe": type(exc).__name__})
PY

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
echo "=== REQUIRE PRE-VERIFIED 2025 COMPATIBILITY IMAGE ==="
if ! docker image inspect "$LEGACY_IMAGE" >/dev/null 2>&1; then
  echo "Missing $LEGACY_IMAGE. Run ops/bootstrap_2025_runtime_dependencies.sh first."
  exit 1
fi
docker run --rm "$LEGACY_IMAGE" pip check
echo "LEGACY_2025_IMAGE_READY"

echo
echo "=== COMPLETE DEPENDENCY IMPORT MATRIX ==="
docker run --rm -i "$LEGACY_IMAGE" python - <<'PY'
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

# The October-2025 auto-fix pass accidentally inserted a typing import
# inside two function bodies. Restore the syntax without changing behavior.
p = root / "run_live_meme.py"
if p.exists():
    s = p.read_text()
    s = s.replace(
        "    from utils import load_config\nfrom typing import Callable\n\n    cfg =",
        "    from utils import load_config\n\n    cfg =",
    )
    p.write_text(s)

p = root / "run_unified.py"
if p.exists():
    s = p.read_text()
    s = s.replace(
        "    try:\n        import os\nfrom typing import Callable\n\n        run_daemons =",
        "    try:\n        import os\n\n        run_daemons =",
    )
    # The 2025 static/ruff reports show trader_core as an expected import for
    # run_unified.py; restore that import if the broken auto-fix removed it.
    if "from trader_core import TraderCore" not in s:
        s = s.replace(
            "import argparse\n",
            "import argparse\n\nfrom trader_core import TraderCore\n",
            1,
        )
    p.write_text(s)

# Package markers restored during the later module-repair work.
for pkgdir in (root / "src" / "leantrader" / "agents", root / "src" / "leantrader" / "production"):
    if pkgdir.is_dir():
        (pkgdir / "__init__.py").touch()

print("LEGACY_2025_SOURCE_REPAIRS_APPLIED")
PY

echo

# FIX_RPB_OS_SCOPE_20260918
# Historical REAL_PROFIT_BOT has an indented `import os` inside a function.
# Python therefore treats `os` as local throughout that function, breaking
# earlier os.getenv(...) calls. Keep os module-level only.
python3 - "$LEGACY/REAL_PROFIT_BOT.py" <<'PYFIX_RPB_OS'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
src = path.read_text()

original_trailing_newline = src.endswith("\n")
lines = src.splitlines()

out = []
removed = []

for lineno, line in enumerate(lines, 1):
    stripped = line.strip()
    indent = len(line) - len(line.lstrip())

    if indent > 0 and re.fullmatch(
        r'import\s+os(?:\s+as\s+os)?',
        stripped
    ):
        removed.append(lineno)
        continue

    out.append(line)

src = "\n".join(out)

if not re.search(r'(?m)^import\s+os(?:\s|$)', src):
    src = "import os\n" + src

if original_trailing_newline:
    src += "\n"

compile(src, str(path), "exec")
path.write_text(src)

remaining_local_os = [
    lineno
    for lineno, line in enumerate(src.splitlines(), 1)
    if line[:1].isspace()
    and re.fullmatch(
        r'import\s+os(?:\s+as\s+os)?',
        line.strip()
    )
]

if remaining_local_os:
    raise SystemExit(
        "LOCAL_IMPORT_OS_REMAINS: "
        + ",".join(map(str, remaining_local_os))
    )

print(
    "REAL_PROFIT_BOT_OS_SCOPE_FIXED",
    "removed_lines=" + (
        ",".join(map(str, removed)) if removed else "none"
    )
)
PYFIX_RPB_OS



# FIX_EVOLUTION_MODEL_JSON_20260918
# The historical model dict stores spawn_time as datetime.now(). SQLite can
# retain the timestamp, but json.dumps(model) cannot serialize datetime.
# Convert unsupported objects to their ISO representation only for the JSON
# evidence blob; do not alter model generation/performance logic.
python3 - "$LEGACY/EVOLUTION_ENGINE.py" <<'PYFIX_EVO_JSON'
from pathlib import Path
import sys

p = Path(sys.argv[1])
src = p.read_text()

old = "json.dumps(model),"

new = (
    "json.dumps("
    "model, "
    "default=lambda obj: "
    "obj.isoformat() "
    "if hasattr(obj, 'isoformat') "
    "else str(obj)"
    "),"
)

count = src.count(old)

if count == 0:
    if "default=lambda obj:" in src:
        print("EVOLUTION_MODEL_JSON_ALREADY_FIXED")
    else:
        raise SystemExit(
            "ABORT: json.dumps(model) registration target not found"
        )
else:
    if count != 1:
        raise SystemExit(
            f"ABORT: expected one json.dumps(model), found {count}"
        )

    src = src.replace(
        old,
        new,
        1,
    )

    compile(
        src,
        str(p),
        "exec",
    )

    p.write_text(src)

    print("EVOLUTION_MODEL_JSON_FIXED")
PYFIX_EVO_JSON

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
  sh -lc 'cp -a /legacy /tmp/leantrader-2025 && cd /tmp/leantrader-2025 && python -c '"'"'from LEGACY_2025_REAL_INTELLIGENCE_BRIDGE import install; install(); from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator; print("LEGACY_2025_IMPORT_OK")'"'"''

echo
echo "=== FULL 2025 INITIALIZE + WIRE SMOKE — NO LOOPS / NO ORDERS ==="
docker run --rm -i \
  --name leantrader-2025-wire-smoke \
  --env-file "$ENV_FILE" \
  "${SECRET_MOUNT_ARGS[@]}" \
  -v "$WORKSPACE_STATE:/workspace" \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  sh -lc 'cp -a /legacy /tmp/leantrader-2025 && cd /tmp/leantrader-2025 && python -' <<'PY'
import asyncio
from LEGACY_2025_REAL_INTELLIGENCE_BRIDGE import install
install()

from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator

async def check():
    bot = CompleteUltimateOrchestrator(mode="testnet")
    await bot.initialize_all_systems()
    await bot.wire_all_systems()

    base = set(getattr(bot, "orchestrators", {}) or {})
    advanced = set(getattr(bot, "advanced_orchestrators", {}) or {})

    required_base = {"learning", "scouting", "decision"}
    required_advanced = {"execution", "smart_scalping"}

    missing_base = sorted(required_base - base)
    missing_advanced = sorted(required_advanced - advanced)

    print("WIRE_BASE", sorted(base))
    print("WIRE_ADVANCED", sorted(advanced))
    print("SMART_SCALPING_PRESENT", bool(getattr(bot, "smart_scalping", None)))
    print("SENTIENT_BRAIN_PRESENT", bool(getattr(bot, "sentient_brain", None)))
    print("REAL_PROFIT_BOT_PRESENT", bool(getattr(bot, "real_profit_bot", None)))
    print("MARKET_SCANNER_PRESENT", bool(getattr(bot, "market_scanner", None)))

    base_scalper = (getattr(bot, "trading_engines", {}) or {}).get("smart_scalping")
    if base_scalper is not getattr(bot, "smart_scalping", None):
        raise SystemExit("DUPLICATE_SMART_SCALPER_STATE_DETECTED")
    print("SMART_SCALPER_SINGLE_INSTANCE_OK")

    swarm = (getattr(bot, "ai_systems", {}) or {}).get("swarm")
    if swarm is None or not hasattr(swarm, "collective_decision"):
        raise SystemExit("SWARM_DECISION_PATH_NOT_CONNECTED")
    swarm_probe = await swarm.collective_decision(
        {
            "symbol": "BTC/USDT",
            "side": "buy",
            "confidence": 0.5,
            "data": {"symbol": "BTC/USDT", "real_market_data": True},
        }
    )
    print("SWARM_REAL_EVIDENCE", swarm_probe)
    if swarm_probe.get("real_market_data") is not True:
        raise SystemExit("SWARM_REAL_MARKET_EVIDENCE_FAILED")
    print("SWARM_REAL_EVIDENCE_OK")

    evolution = (getattr(bot, "ai_systems", {}) or {}).get("evolution")
    if evolution is None or not hasattr(evolution, "evo_db"):
        raise SystemExit("EVOLUTION_DATABASE_NOT_CONNECTED")
    db_check = evolution.evo_db.execute("PRAGMA quick_check").fetchone()[0]
    print("EVOLUTION_DATABASE_CHECK", db_check)
    if db_check != "ok":
        raise SystemExit("EVOLUTION_DATABASE_QUICK_CHECK_FAILED")

    if not getattr(bot, "market_scanner", None):
        raise SystemExit("REAL_MARKET_SCANNER_NOT_CONNECTED")

    if missing_base or missing_advanced:
        raise SystemExit(
            f"WIRE_SMOKE_FAILED base={missing_base} advanced={missing_advanced}"
        )

    print("LEGACY_2025_WIRE_OK")

asyncio.run(check())
PY

echo
echo "=== REAL MARKET INTELLIGENCE SMOKE — READ ONLY / NO ORDERS ==="
docker run --rm -i \
  --env-file "$ENV_FILE" \
  -v "$WORKSPACE_STATE:/workspace" \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  sh -lc 'cp -a /legacy /tmp/leantrader-2025 && cd /tmp/leantrader-2025 && python -' <<'PY'
import asyncio

from LEGACY_2025_REAL_INTELLIGENCE_BRIDGE import install, smoke_real_market
install()

evidence = smoke_real_market()
print("REAL_MARKET_PUBLIC_EVIDENCE", evidence)

from SMART_SCALPING_ENGINE import SmartScalpingEngine

async def verify_scalper():
    engine = SmartScalpingEngine(None, None)
    count = await engine.analyze_all_timeframes("BTC/USDT")
    details = engine.mtf_analyzer.get_confluence_details("BTC/USDT")
    frames = details.get("timeframes") or {}
    real_frames = sum(
        1
        for row in frames.values()
        if isinstance(row, dict)
        and isinstance(row.get("indicators"), dict)
        and row["indicators"].get("real_market_data") is True
    )
    print("REAL_SMART_SCALPER_TIMEFRAMES", count)
    print("REAL_SMART_SCALPER_EVIDENCE_FRAMES", real_frames)
    if count < 3 or real_frames < 3:
        raise SystemExit("REAL_SMART_SCALPER_DATA_FAILED")
    print("REAL_SMART_SCALPER_OK")

asyncio.run(verify_scalper())

from EVOLUTION_ENGINE import ULTIMATE_EVOLUTION_ENGINE
probe = ULTIMATE_EVOLUTION_ENGINE.__new__(ULTIMATE_EVOLUTION_ENGINE)
probe.active_engines = {"scalper_engine": {"pairs": ["BTC/USDT", "ETH/USDT"]}}
probe.data_hub = None
signals = probe.generate_scalping_signals()
print("EVOLUTION_REAL_SCALPER_SIGNAL_COUNT", len(signals))
if any(not row.get("real_market_data") for row in signals):
    raise SystemExit("EVOLUTION_SCALPER_SYNTHETIC_SIGNAL_DETECTED")
print("EVOLUTION_REAL_MARKET_PATH_OK")

# Known historical signal-producing placeholders must now be real or inert.
import HEDGE_FUND_ARSENAL as hedge
import ultra_swarm_consciousness as swarm
import ultra_arbitrage_engine as ultra_arb

if hedge.StatisticalArbitrage.find_pairs_trades.__name__ != "_real_statistical_arbitrage":
    raise SystemExit("HEDGE_FUND_SYNTHETIC_RATIO_STILL_ACTIVE")
if swarm.SwarmAgent._get_market_data.__name__ != "_real_swarm_market_data":
    raise SystemExit("SWARM_SYNTHETIC_MARKET_DATA_STILL_ACTIVE")
if swarm.SwarmConsciousness._execute_testnet_trade.__name__ != "_no_simulated_swarm_trade":
    raise SystemExit("SWARM_SIMULATED_EXECUTION_STILL_ACTIVE")
if ultra_arb.UltraArbitrageEngine._simulate_arbitrage_execution.__name__ != "_no_simulated_arbitrage_execution":
    raise SystemExit("ULTRA_ARB_SIMULATED_EXECUTION_STILL_ACTIVE")
print("KNOWN_SYNTHETIC_EXECUTION_SOURCES_NEUTRALIZED")
PY

echo
echo "=== AUTHENTICATED BYBIT TESTNET PREFLIGHT — READ ONLY ==="
docker run --rm -i \
  --env-file "$ENV_FILE" \
  "${SECRET_MOUNT_ARGS[@]}" \
  -v "$LEGACY:/legacy:ro" \
  "$LEGACY_IMAGE" \
  sh -lc 'cp -a /legacy /tmp/leantrader-2025 && cd /tmp/leantrader-2025 && python -' <<'PY'
from src.leantrader.execution.router import execution_status, route_balance

status = execution_status(mode="testnet", exchange_id="bybit")
safe = {
    "execution_mode": status.get("execution_mode"),
    "authority": status.get("authority"),
    "backend": status.get("backend"),
    "exchange": status.get("exchange"),
    "authenticated": bool(status.get("authenticated")),
}
print("EXECUTION_STATUS", safe)

if (
    safe["execution_mode"] != "testnet"
    or safe["authority"] != "testnet"
    or safe["exchange"] != "bybit"
    or safe["authenticated"] is not True
):
    raise SystemExit("AUTHENTICATED_TESTNET_PREFLIGHT_FAILED")

balance = route_balance(mode="testnet", exchange_id="bybit") or {}
free = ((balance.get("free") or {}).get("USDT"))
if free is None:
    free = ((balance.get("USDT") or {}).get("free"))
if free is None:
    raise SystemExit("AUTHENTICATED_TESTNET_BALANCE_UNAVAILABLE")

print("AUTHENTICATED_TESTNET_FREE_USDT", round(float(free), 8))

from src.leantrader.execution.broker_ccxt import BrokerCCXT
public = BrokerCCXT(execution_mode="paper", exchange_id="bybit")
ticker = public.fetch_ticker("BTC/USDT") or {}
last = float(ticker.get("last") or ticker.get("close") or 0.0)
candles = public.fetch_ohlcv("BTC/USDT", timeframe="1m", limit=30) or []
if last <= 0.0 or len(candles) < 20:
    raise SystemExit("PRODUCTION_PUBLIC_MARKET_DATA_UNAVAILABLE")
print("PRODUCTION_PUBLIC_BTC_LAST", round(last, 8))
print("PRODUCTION_PUBLIC_1M_CANDLES", len(candles))
print("AUTHENTICATED_TESTNET_PREFLIGHT_OK")
PY

echo
echo "=== CUTOVER TO 2025 CONTROLLER ==="
docker rm -f "$LEGACY_CONTAINER" >/dev/null 2>&1 || true
docker stop "$CURRENT_RPB" >/dev/null 2>&1 || true

docker run -d \
  --name "$LEGACY_CONTAINER" \
  --restart unless-stopped \
  --env-file "$ENV_FILE" \
  "${SECRET_MOUNT_ARGS[@]}" \
  -v "$WORKSPACE_STATE:/workspace" \
  -v "$LEGACY:/app" \
  -w /app \
  "$LEGACY_IMAGE" \
  python RUN_BOT.py --testnet >/dev/null

echo "Waiting for 2025 controller engine loops to come online..."
READY=0
for _ in $(seq 1 18); do
  sleep 10

  if ! docker ps --format '{{.Names}}' | grep -qx "$LEGACY_CONTAINER"; then
    break
  fi

  LOGS="$(docker logs --since 5m "$LEGACY_CONTAINER" 2>&1 || true)"

  if grep -q 'configured credential file does not exist' <<<"$LOGS"; then
    echo "Credential mount failure detected during 2025 startup."
    break
  fi
  if grep -q 'Evolution database error' <<<"$LOGS"; then
    echo "Evolution database failed during 2025 startup."
    break
  fi
  if grep -q "Enhanced loop error: 'total_profit'" <<<"$LOGS"; then
    echo "Historical execution-stat compatibility failure detected."
    break
  fi

  DECISION_OK=0
  EXECUTION_OK=0
  SCALPER_OK=0
  MARKET_OK=0
  BRIDGE_OK=0
  EVOLUTION_OK=0
  CRYPTO_SCALPER_OK=0

  grep -Eq 'Decision Engine wired|Decision:' <<<"$LOGS" && DECISION_OK=1 || true
  grep -Eq 'EXECUTION ORCHESTRATOR WIRED|EXECUTING:' <<<"$LOGS" && EXECUTION_OK=1 || true
  grep -Eq 'SMART SCALPING ENGINE WIRED|Scalper generated' <<<"$LOGS" && SCALPER_OK=1 || true
  grep -Eq 'REAL_MARKET_SCAN .*hub_market=[1-9][0-9]*' <<<"$LOGS" && MARKET_OK=1 || true
  grep -q 'LEGACY_2025_REAL_INTELLIGENCE_BRIDGE_INSTALLED' <<<"$LOGS" && BRIDGE_OK=1 || true
  grep -Eq 'Evolution database initialized|Evidence Evolution cycle' <<<"$LOGS" && EVOLUTION_OK=1 || true
  grep -Eq 'BTC/USDT|ETH/USDT|SOL/USDT|DOGE/USDT|XRP/USDT|ADA/USDT|BNB/USDT' <<<"$LOGS" && CRYPTO_SCALPER_OK=1 || true

  if [ "$DECISION_OK" -eq 1 ] && [ "$EXECUTION_OK" -eq 1 ] && [ "$SCALPER_OK" -eq 1 ] && [ "$MARKET_OK" -eq 1 ] && [ "$BRIDGE_OK" -eq 1 ] && [ "$EVOLUTION_OK" -eq 1 ] && [ "$CRYPTO_SCALPER_OK" -eq 1 ]; then
    READY=1
    break
  fi
done

if [ "$READY" -ne 1 ]; then
  echo "2025 controller did not reach the required engine-ready state."
  echo "Restoring previous RPB runtime."
  docker logs "$LEGACY_CONTAINER" 2>&1 || true
  docker rm -f "$LEGACY_CONTAINER" >/dev/null 2>&1 || true
  docker start "$CURRENT_RPB" >/dev/null 2>&1 || true
  exit 1
fi

# The restored 2025 controller has proven that its decision, execution and
# smart-scalping loops are online. Only now retire the old intelligence-only
# sidecar to free memory/CPU. The previous RPB remains stopped but available
# for rollback.
docker stop "$CURRENT_INTEL" >/dev/null 2>&1 || true

echo
echo "=== 2025 RUNTIME STATUS ==="
docker ps --filter "name=$LEGACY_CONTAINER"   --format 'NAME={{.Names}} STATUS={{.Status}} IMAGE={{.Image}}'

echo
echo "=== ENGINE START EVIDENCE ==="
docker logs --since 3m "$LEGACY_CONTAINER" 2>&1   | grep -E 'AUTHENTICATED_TESTNET|PRODUCTION_PUBLIC|REAL_MARKET_SCAN|REAL_SMART_SCALPER|LEGACY_2025_REAL_INTELLIGENCE|AUTHENTICATED POSITION|AUTHENTICATED POSITION SETTLED|Realized net P&L|ALL 50\+ ORCHESTRATORS RUNNING|Decision Engine wired|EXECUTION ORCHESTRATOR WIRED|SMART SCALPING ENGINE WIRED|Scalper generated|Published .* signals|Decision:|EXECUTING:|SUBMITTING|ORDER ACKNOWLEDGED|Evolution database initialized|Evidence Evolution cycle|Evolution|Sentient|Swarm|Learning Orchestrator wired|Scouting Orchestrator wired|ERROR|Traceback'   | tail -n 240 || true

echo
echo "=== CONTAINER MODE EVIDENCE ==="
docker exec -i "$LEGACY_CONTAINER" python - <<'PY'
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
