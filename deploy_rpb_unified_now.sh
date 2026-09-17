#!/usr/bin/env bash
set -Eeuo pipefail

BRANCH="${RPB_BRANCH:-restore/rpb-unified-20260917}"
SOURCE_REPO="${LEANTRADER_SOURCE_REPO:-/opt/leantrader/native-integrity-pass4-20260911T022930Z}"
REMOTE="${LEANTRADER_REMOTE:-lean-trader}"
TMP="/tmp/deploy_rpb_unified_testnet_v2.$$.sh"

[[ -d "$SOURCE_REPO/.git" || -f "$SOURCE_REPO/.git" ]] || {
  echo "ERROR: canonical Lean-Trader repo missing: $SOURCE_REPO" >&2
  exit 2
}

cd "$SOURCE_REPO"
CANONICAL_URL="$(git remote get-url "$REMOTE" 2>/dev/null || true)"
[[ -n "$CANONICAL_URL" ]] || {
  echo "ERROR: canonical Lean-Trader remote '$REMOTE' is not configured in $SOURCE_REPO" >&2
  exit 3
}

# Prove the requested branch exists on the canonical Lean-Trader remote before
# doing anything to the running VPS architecture.
git ls-remote --exit-code --heads "$REMOTE" "refs/heads/$BRANCH" >/dev/null || {
  echo "ERROR: branch '$BRANCH' is not visible through remote '$REMOTE'" >&2
  exit 4
}

git fetch --no-tags "$REMOTE" "$BRANCH:refs/remotes/$REMOTE/$BRANCH"
git show "$REMOTE/$BRANCH:deploy_rpb_unified_testnet_v2.sh" > "$TMP"
chmod 700 "$TMP"

# The inner handoff script predates the VPS remote split and still names
# 'origin'. Do not mutate the preserved worktree's git config: override only
# the URL seen by child git commands for this process, so 'origin' resolves to
# the canonical Lean-Trader remote rather than the legacy LeanTrader-Bot repo.
export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0=remote.origin.url
export GIT_CONFIG_VALUE_0="$CANONICAL_URL"

# docker exec needs stdin attached for the final read-only Python authority
# probe. Keep this compatibility repair at the launcher boundary.
sed -i 's/docker exec "\$RPB_CONTAINER" python -/docker exec -i "\$RPB_CONTAINER" python -/' "$TMP"

exec bash "$TMP"
