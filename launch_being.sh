#!/bin/bash
set -e
[ ! -f /run/secrets/bybit_testnet_api_key ] && exit 1
supervise() { while true; do $2 >> $3 2>&1; sleep 5; done & }
supervise RUN_BOT "python3 -u /app/RUN_BOT.py --testnet" /tmp/run_bot.log
sleep 5
supervise PIPE "python3 -u /app/wire_scanner_extractor.py" /tmp/scanner_extractor.log
sleep 5
supervise SPOT "python3 -u /app/spot_closer.py" /tmp/spot_closer.log
supervise POSMGR "python3 -u /app/position_manager.py" /tmp/position_manager.log
wait
