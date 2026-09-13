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
python3 - "$TMP/install.sh" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text()
marker='refusing recursive redeployment from a Pass 7 wrapper'
if marker not in s:
    old='  say "Existing Pass 7 source found but runtime is not ready; continuing bounded redeployment."\n'
    new='''  CURRENT_IMAGE_REF="$(docker inspect -f '{{.Config.Image}}' "$CONTAINER" 2>/dev/null || true)"\n  CURRENT_HAS_PASS7_STATE_MOUNT="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination \\"/var/lib/leantrader-pass7\\"}}yes{{end}}{{end}}' "$CONTAINER" 2>/dev/null || true)"\n  if [[ "$CURRENT_IMAGE_REF" == "leantrader-native-testnet:${HEAD_SHA:0:12}" || "$CURRENT_HAS_PASS7_STATE_MOUNT" == "yes" ]]; then\n    fail "existing Pass 7 runtime is not ready; refusing recursive redeployment from a Pass 7 wrapper"\n  fi\n  say "Pass 7 source exists and canonical container is the Pass 6 rollback; retrying bounded deployment."\n'''
    if old not in s:
        raise SystemExit('unexpected installer revision; safeguard target not found')
    p.write_text(s.replace(old,new))
PY
bash -n "$TMP/install.sh"
chmod 700 "$TMP/install.sh"
exec "$TMP/install.sh"
