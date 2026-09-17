#!/usr/bin/env bash
set -Eeuo pipefail

BRANCH="${RPB_BRANCH:-restore/rpb-unified-20260917}"
SOURCE_REPO="${LEANTRADER_SOURCE_REPO:-/opt/leantrader/native-integrity-pass4-20260911T022930Z}"
TMP="/tmp/deploy_rpb_unified_testnet_v2.$$.sh"

[[ -d "$SOURCE_REPO/.git" || -f "$SOURCE_REPO/.git" ]] || {
  echo "ERROR: canonical Lean-Trader repo missing: $SOURCE_REPO" >&2
  exit 2
}

cd "$SOURCE_REPO"
git fetch --no-tags origin "$BRANCH:refs/remotes/origin/$BRANCH"
git show "origin/$BRANCH:deploy_rpb_unified_testnet_v2.sh" > "$TMP"
chmod 700 "$TMP"

# docker exec needs stdin attached for the final read-only Python authority
# probe. Keep this one-line compatibility repair at the launcher boundary so
# an older Docker CLI cannot turn a healthy handoff into a false rollback.
sed -i 's/docker exec "\$RPB_CONTAINER" python -/docker exec -i "\$RPB_CONTAINER" python -/' "$TMP"

exec bash "$TMP"
