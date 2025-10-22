#!/usr/bin/env bash
cd "/home/ubuntu/trading_bot" 2>/dev/null || cd /workspace
rg -n "(EXECUTION LOOP|Decision|Scouting|ALL 26 SYSTEMS INITIALIZED|BOT IS RUNNING|Telegram)" bot.log || true
