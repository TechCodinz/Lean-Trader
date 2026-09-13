#!/usr/bin/env bash
set -Eeuo pipefail
BRANCH="restore/pass7-micro-20260913"
REF="origin/${BRANCH}"
TMP="$(mktemp -d /root/pass7-bootstrap.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
cd /opt/leantrader/native-integrity-pass4-20260911T022930Z
git fetch --no-tags origin "${BRANCH}:refs/remotes/origin/${BRANCH}"
git show "${REF}:payload/install_pass7_native.sh.gz.b64.part01" \
  | tr -d '\n' | base64 -d | gzip -dc > "$TMP/install.sh"
chmod 700 "$TMP/install.sh"
exec "$TMP/install.sh"
