#!/usr/bin/env bash
set -Eeuo pipefail

BRANCH="${RPB_BRANCH:-restore/rpb-unified-20260917}"
ARCHAEOLOGY_REPO="${LEANTRADER_ARCHAEOLOGY_REPO:-/opt/leantrader/native-integrity-pass4-20260911T022930Z}"
REMOTE="${LEANTRADER_REMOTE:-lean-trader}"
CANONICAL_REPO="${LEANTRADER_CANONICAL_REPO:-/opt/leantrader/canonical-lean-trader}"
TMP="/tmp/deploy_rpb_unified_testnet_v2.$$.sh"

[[ -d "$ARCHAEOLOGY_REPO/.git" || -f "$ARCHAEOLOGY_REPO/.git" ]] || {
  echo "ERROR: archaeology repo missing: $ARCHAEOLOGY_REPO" >&2
  exit 2
}

cd "$ARCHAEOLOGY_REPO"
CANONICAL_URL="$(git remote get-url "$REMOTE" 2>/dev/null || true)"
[[ -n "$CANONICAL_URL" ]] || {
  echo "ERROR: canonical Lean-Trader remote '$REMOTE' is not configured in $ARCHAEOLOGY_REPO" >&2
  exit 3
}

git ls-remote --exit-code --heads "$REMOTE" "refs/heads/$BRANCH" >/dev/null || {
  echo "ERROR: branch '$BRANCH' is not visible through remote '$REMOTE'" >&2
  exit 4
}

if [[ -e "$CANONICAL_REPO" && ! -e "$CANONICAL_REPO/.git" ]]; then
  echo "ERROR: canonical repo path exists but is not a git repository: $CANONICAL_REPO" >&2
  exit 5
fi

if [[ ! -e "$CANONICAL_REPO/.git" ]]; then
  git clone --no-checkout "$CANONICAL_URL" "$CANONICAL_REPO"
else
  git -C "$CANONICAL_REPO" remote set-url origin "$CANONICAL_URL"
fi

git -C "$CANONICAL_REPO" fetch --no-tags origin \
  "$BRANCH:refs/remotes/origin/$BRANCH"

git -C "$CANONICAL_REPO" show \
  "origin/$BRANCH:deploy_rpb_unified_testnet_v2.sh" > "$TMP"
chmod 700 "$TMP"

python3 - "$TMP" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8")

needle = "  -e PYTHONPATH=/workspace \\\n"
replacement = (
    "  -e PYTHONPATH=/workspace \\\n"
    "  -e PYTHONDONTWRITEBYTECODE=1 \\\n"
    "  -e PYTHONPYCACHEPREFIX=/tmp/rpb-pycache \\\n"
)
if needle not in text:
    raise SystemExit("ERROR: expected PYTHONPATH marker missing from handoff script")
text = text.replace(needle, replacement)

old_compile = '''  python -m py_compile \\
    REAL_PROFIT_BOT.py \\
    rpb_position_lifecycle.py \\
    rpb_intelligence.py \\
    rpb_scalping.py \\
    rpb_alpha_risk.py \\
    rpb_production_bridge.py \\
    rpb_adopt_positions.py \\
    rpb_telegram.py \\
    verify_rpb_unified.py
'''
new_compile = '''  python - <<"PYCOMPILE"
from pathlib import Path
files = [
    "REAL_PROFIT_BOT.py",
    "rpb_position_lifecycle.py",
    "rpb_intelligence.py",
    "rpb_scalping.py",
    "rpb_alpha_risk.py",
    "rpb_production_bridge.py",
    "rpb_adopt_positions.py",
    "rpb_adoption_history.py",
    "rpb_adopt_positions_windowed.py",
    "rpb_telegram.py",
    "verify_rpb_unified.py",
]
for name in files:
    source = Path(name).read_text(encoding="utf-8")
    compile(source, name, "exec")
print("RPB_SOURCE_COMPILE=PASS")
PYCOMPILE
'''
if old_compile not in text:
    raise SystemExit("ERROR: expected py_compile block missing from handoff script")
text = text.replace(old_compile, new_compile, 1)
text = text.replace(
    "python -m pytest -q \\\n",
    "python -m pytest -q -p no:cacheprovider \\\n",
    1,
)
text = text.replace(
    "      test_rpb_scalping_real_indicators.py\n",
    "      test_rpb_scalping_real_indicators.py \\\n      test_rpb_adoption_history.py\n",
    1,
)

# Use the windowed authenticated-history wrapper for both the dry-run and the
# final idempotent apply. The wrapper changes only the read-only history fetch;
# all conservative ambiguity, inventory and cost-basis checks remain in the
# original adoption utility.
text = text.replace("python rpb_adopt_positions.py \\\n", "python rpb_adopt_positions_windowed.py \\\n")

old_tg = '''TELEGRAM_TOKEN="$(resolve_env TELEGRAM_BOT_TOKEN || true)"
TELEGRAM_ADMIN="$(resolve_env TELEGRAM_ADMIN_CHAT_ID || true)"
TELEGRAM_VIP="$(resolve_env TELEGRAM_VIP_CHAT_ID || true)"
TELEGRAM_FREE="$(resolve_env TELEGRAM_FREE_CHAT_ID || true)"
'''
new_tg = '''TELEGRAM_TOKEN="$(resolve_env TELEGRAM_BOT_TOKEN || true)"
[[ -n "$TELEGRAM_TOKEN" ]] || TELEGRAM_TOKEN="$(resolve_env TG_BOT_TOKEN || true)"
[[ -n "$TELEGRAM_TOKEN" ]] || TELEGRAM_TOKEN="$(resolve_env TELEGRAM_TOKEN || true)"

TELEGRAM_ADMIN="$(resolve_env TELEGRAM_ADMIN_CHAT_ID || true)"
[[ -n "$TELEGRAM_ADMIN" ]] || TELEGRAM_ADMIN="$(resolve_env TG_ADMIN_CHAT_ID || true)"
[[ -n "$TELEGRAM_ADMIN" ]] || TELEGRAM_ADMIN="$(resolve_env TELEGRAM_ADMIN_ID || true)"

TELEGRAM_VIP="$(resolve_env TELEGRAM_VIP_CHAT_ID || true)"
[[ -n "$TELEGRAM_VIP" ]] || TELEGRAM_VIP="$(resolve_env TG_VIP_CHAT_ID || true)"
[[ -n "$TELEGRAM_VIP" ]] || TELEGRAM_VIP="$(resolve_env TELEGRAM_VIP_CHANNEL || true)"
[[ -n "$TELEGRAM_VIP" ]] || TELEGRAM_VIP="$(resolve_env TELEGRAM_CHAT_ID || true)"

TELEGRAM_FREE="$(resolve_env TELEGRAM_FREE_CHAT_ID || true)"
[[ -n "$TELEGRAM_FREE" ]] || TELEGRAM_FREE="$(resolve_env TG_FREE_CHAT_ID || true)"
[[ -n "$TELEGRAM_FREE" ]] || TELEGRAM_FREE="$(resolve_env TELEGRAM_FREE_CHANNEL || true)"
'''
if old_tg not in text:
    raise SystemExit("ERROR: expected Telegram resolver block missing from handoff script")
text = text.replace(old_tg, new_tg, 1)

marker = '''SECRET_ARGS=()
'''
staging = r'''IMAGE_UID="$(docker run --rm --entrypoint sh "$IMAGE" -lc 'id -u' | tail -n 1)"
IMAGE_GID="$(docker run --rm --entrypoint sh "$IMAGE" -lc 'id -g' | tail -n 1)"
[[ "$IMAGE_UID" =~ ^[0-9]+$ && "$IMAGE_GID" =~ ^[0-9]+$ ]] || fail "could not resolve runtime image uid/gid"

STAGED_SECRETS="$RPB_DATA/secrets"
rm -rf "$STAGED_SECRETS"
install -d -o "$IMAGE_UID" -g "$IMAGE_GID" -m 0500 "$STAGED_SECRETS"

stage_secret_path() {
  local configured="$1" src="" base=""
  [[ -n "$configured" ]] || return 0
  base="$(basename "$configured")"
  case "$configured" in
    /run/secrets/*) src="$SECRETS/${configured#/run/secrets/}" ;;
    *) src="$configured" ;;
  esac
  [[ -f "$src" ]] || fail "configured credential file is missing on host: $base"
  install -o "$IMAGE_UID" -g "$IMAGE_GID" -m 0400 "$src" "$STAGED_SECRETS/$base"
  printf '/run/secrets/%s' "$base"
}

if [[ -n "$BYBIT_KEY_FILE" ]]; then BYBIT_KEY_FILE="$(stage_secret_path "$BYBIT_KEY_FILE")"; fi
if [[ -n "$BYBIT_SECRET_FILE" ]]; then BYBIT_SECRET_FILE="$(stage_secret_path "$BYBIT_SECRET_FILE")"; fi

chown "$IMAGE_UID:$IMAGE_GID" "$RPB_DATA"
chown -R "$IMAGE_UID:$IMAGE_GID" "$RPB_DATA/runtime" "$RPB_DATA/reports"
chmod 0750 "$RPB_DATA" "$RPB_DATA/runtime" "$RPB_DATA/reports"

echo "RUNTIME_IMAGE_UID=$IMAGE_UID"
echo "BYBIT_FILE_SECRETS_STAGED=$([[ -n "$BYBIT_KEY_FILE" && -n "$BYBIT_SECRET_FILE" ]] && echo yes || echo no)"
echo "TELEGRAM_TOKEN_RESOLVED=$([[ -n "$TELEGRAM_TOKEN" ]] && echo yes || echo no)"
echo "TELEGRAM_ADMIN_RESOLVED=$([[ -n "$TELEGRAM_ADMIN" ]] && echo yes || echo no)"
echo "TELEGRAM_PREMIUM_RESOLVED=$([[ -n "$TELEGRAM_VIP" ]] && echo yes || echo no)"
echo "TELEGRAM_FREE_RESOLVED=$([[ -n "$TELEGRAM_FREE" ]] && echo yes || echo no)"

SECRET_ARGS=()
'''
if marker not in text:
    raise SystemExit("ERROR: expected SECRET_ARGS marker missing from handoff script")
text = text.replace(marker, staging, 1)

old_mount = '-v "$SECRETS:/run/secrets:ro"'
if old_mount not in text:
    raise SystemExit("ERROR: expected secrets mount missing from handoff script")
text = text.replace(old_mount, '-v "$STAGED_SECRETS:/run/secrets:ro"')

p.write_text(text, encoding="utf-8")
PY

sed -i 's/docker exec "\$RPB_CONTAINER" python -/docker exec -i "\$RPB_CONTAINER" python -/' "$TMP"

export LEANTRADER_SOURCE_REPO="$CANONICAL_REPO"
exec bash "$TMP"
