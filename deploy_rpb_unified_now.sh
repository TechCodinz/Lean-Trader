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

# Prove the requested branch exists on the real Lean-Trader remote before
# touching any running container or execution authority.
git ls-remote --exit-code --heads "$REMOTE" "refs/heads/$BRANCH" >/dev/null || {
  echo "ERROR: branch '$BRANCH' is not visible through remote '$REMOTE'" >&2
  exit 4
}

# Use a dedicated canonical clone so the handoff script's historical 'origin'
# reference can never resolve to the legacy LeanTrader-Bot repository. The
# preserved archaeology worktree and its remotes are left unchanged.
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

# docker exec needs stdin attached for the final read-only authority probe.
sed -i 's/docker exec "\$RPB_CONTAINER" python -/docker exec -i "\$RPB_CONTAINER" python -/' "$TMP"

export LEANTRADER_SOURCE_REPO="$CANONICAL_REPO"
exec bash "$TMP"
