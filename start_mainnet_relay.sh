#!/bin/bash
# Start the MAINNET relay if healthy/not running. Refuses without keys.
if curl -s --max-time 3 http://172.17.0.1:18098/health | grep -q '"ok": true'; then
  echo "mainnet relay already healthy"; exit 0
fi
if [ ! -f /root/secrets/bybit_mainnet_api_key ] || [ ! -f /root/secrets/bybit_mainnet_api_secret ]; then
  echo "mainnet keys not present - relay NOT started"; exit 1
fi
pkill -f mainnet_relay.py 2>/dev/null; sleep 1
setsid python3 -u /root/mainnet_relay.py > /root/mainnet_relay.log 2>&1 < /dev/null &
sleep 2
curl -s --max-time 3 http://172.17.0.1:18098/health && echo " <- mainnet relay up"
