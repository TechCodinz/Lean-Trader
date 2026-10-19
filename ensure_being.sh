#!/bin/bash
# ensure_being.sh - LeanTrader recovery watchdog (host cron, every 5 min).
# Starts ONLY the beings that are missing; never bounces a healthy one.
# The full being: zoo, continuous, swarm, governor, sentinel, scanner,
# nervous_system (which itself supervises the 12-service fleet).
C=leantrader-2025-testnet

# Signing relay first - every being's money path runs through it.
/root/start_relay.sh > /dev/null 2>&1 || true

RUNNING=$(docker exec $C python3 -c "
import os
out=[]
for pid in os.listdir('/proc'):
    if pid.isdigit():
        try:
            cl=open(f'/proc/{pid}/cmdline','rb').read().decode(errors='ignore')
            out.append(cl)
        except Exception: pass
print('\n'.join(out))
" 2>/dev/null) || exit 0   # container down: boot path (systemd/start_being) owns that

TOK=$(grep "^TELEGRAM_BOT_TOKEN=" /root/Lean-Trader/.env | cut -d'=' -f2)
CID=$(grep "^TELEGRAM_CHAT_ID=" /root/Lean-Trader/.env | cut -d'=' -f2)
RELAY="TESTNET_RELAY=http://172.17.0.1:18099"
TG="TELEGRAM_BOT_TOKEN=$TOK TELEGRAM_CHAT_ID=$CID"

start_missing() {
  local name="$1" log="$2" envs="$3"
  if ! grep -q "/app/$name" <<< "$RUNNING"; then
    echo "$(date -u +%F\ %T) starting missing $name"
    docker exec $C bash -c "$envs setsid python3 -u /app/$name > /tmp/$log 2>&1 < /dev/null &"
  fi
}

start_missing zoo_paper_trader.py zoo_paper.log "TRADING_MODE=testnet $RELAY $TG"
start_missing continuous_service.py continuous.log "$RELAY $TG"
start_missing swarm_service.py swarm.log "$RELAY $TG"
start_missing governor_service.py governor.log "$RELAY $TG"
start_missing bus_bridge_service.py bus_bridge.log "$RELAY $TG"
start_missing discovery_service.py discovery.log ""
start_missing sentinel_service.py sentinel.log "$TG"
start_missing multiplatform_scanner_service.py scanner.log "$TG"
start_missing nervous_system.py nervous.log ""
