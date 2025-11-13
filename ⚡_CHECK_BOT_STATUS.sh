#!/bin/bash
echo "=== BOT STATUS CHECK ==="
echo ""
echo "Bot running: $(ps aux | grep RUN_BOT | grep -v grep | wc -l)"
echo ""
echo "Latest logs:"
tail -30 /root/apex_bot/apex.log
echo ""
echo "Execution loop:"
grep "🔄 EXEC LOOP" /root/apex_bot/apex.log | tail -3
echo ""
echo "Price fetching:"
grep "💰 Fetching" /root/apex_bot/apex.log | tail -5
echo ""
echo "Trades:"
grep "Order ID" /root/apex_bot/apex.log | tail -5
