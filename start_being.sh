#!/bin/bash
# LeanTrader being: boot-time startup (relay + container + zoo trader in testnet mode)
# Installed at /root/start_being.sh, run by leantrader-being.service (or manually).

# 1) Host firewall: let the container reach the relay (bridge subnet, one port)
ufw allow from 172.17.0.0/16 to any port 18099 proto tcp >/dev/null 2>&1
iptables -C INPUT -s 172.17.0.0/16 -p tcp --dport 18099 -j ACCEPT 2>/dev/null || \
  iptables -I INPUT 1 -s 172.17.0.0/16 -p tcp --dport 18099 -j ACCEPT

# 2) Signing relay on the host (container TLS fingerprint is WAF-blocked by Bybit testnet)
if ! pgrep -f "testnet_relay.py" >/dev/null; then
  setsid python3 /root/testnet_relay.py > /root/relay.log 2>&1 < /dev/null &
fi

# 3) Container up
docker start leantrader-2025-testnet >/dev/null 2>&1
sleep 5

# 4) Trader (single instance) in testnet mode via the relay
TOK=$(grep "^TELEGRAM_BOT_TOKEN=" /root/Lean-Trader/.env | cut -d'=' -f2)
CID=$(grep "^TELEGRAM_CHAT_ID=" /root/Lean-Trader/.env | cut -d'=' -f2)
docker exec leantrader-2025-testnet python3 -c "
import os, signal
me=str(os.getpid())
for pid in os.listdir('/proc'):
    if not pid.isdigit() or pid==me: continue
    try:
        cmd=open(f'/proc/'+pid+'/cmdline').read().replace(chr(0),' ')
        if '/app/zoo_paper_trader.py' in cmd:
            os.kill(int(pid), signal.SIGKILL)
    except: pass
"
sleep 3
docker exec leantrader-2025-testnet bash -c "TRADING_MODE=testnet TESTNET_RELAY=http://172.17.0.1:18099 TELEGRAM_BOT_TOKEN='$TOK' TELEGRAM_CHAT_ID='$CID' setsid python3 -u /app/zoo_paper_trader.py > /tmp/zoo_paper.log 2>&1 < /dev/null &"

# 5) Continuous propagation service (orchestrator with real execution, own process)
docker exec leantrader-2025-testnet python3 -c "
import os, signal
me=str(os.getpid())
for pid in os.listdir('/proc'):
    if not pid.isdigit() or pid==me: continue
    try:
        cmd=open(f'/proc/'+pid+'/cmdline').read().replace(chr(0),' ')
        if '/app/continuous_service.py' in cmd:
            os.kill(int(pid), signal.SIGKILL)
    except: pass
"
sleep 2
docker exec leantrader-2025-testnet bash -c "TESTNET_RELAY=http://172.17.0.1:18099 TELEGRAM_BOT_TOKEN='$TOK' TELEGRAM_CHAT_ID='$CID' setsid python3 -u /app/continuous_service.py > /tmp/continuous.log 2>&1 < /dev/null &"
echo "LeanTrader being started $(date)"
