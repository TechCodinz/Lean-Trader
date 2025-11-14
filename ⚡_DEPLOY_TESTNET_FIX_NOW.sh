#!/bin/bash
# ⚡ DEPLOY TESTNET MODE FIX - ROUTER NOW RESPECTS TESTNET!

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     ⚡ DEPLOYING CRITICAL TESTNET FIX ⚡                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd ~/apex_bot

echo "1️⃣  Stopping current bot..."
pkill -f RUN_BOT
sleep 3

echo "2️⃣  Pulling latest fixes..."
git pull origin cursor/continue-previous-coding-operation-8c4a

echo "3️⃣  Clearing old logs..."
> apex.log

echo "4️⃣  Starting bot with testnet fix..."
nohup python3 -u RUN_BOT.py > apex.log 2>&1 &

echo ""
echo "✅ Bot restarted with testnet mode fix!"
echo ""
echo "Waiting 60 seconds for initialization..."
sleep 60

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 🧪 TESTNET MODE VERIFICATION                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "Router initialization:"
grep "Router initialized in" apex.log | tail -1

echo ""
echo "Router filtering testnet routes:"
grep "Testnet mode: Filtered" apex.log | tail -3

echo ""
echo "Trades executed:"
grep "✅.*EXECUTED\|Order ID:" apex.log | tail -5

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    📊 MONITORING COMMANDS                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "# Watch for testnet routing:"
echo "tail -f apex.log | grep '🧪 Testnet mode'"
echo ""
echo "# Watch for successful trades:"
echo "tail -f apex.log | grep '✅.*EXECUTED'"
echo ""
echo "# Watch all router activity:"
echo "tail -f apex.log | grep 'ROUTER:'"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║            ✅ DEPLOYMENT COMPLETE - START MONITORING!          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
