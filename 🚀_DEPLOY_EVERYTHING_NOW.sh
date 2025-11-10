#!/bin/bash
# Complete deployment script with verification

echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "🚀 DEPLOYING BOT WITH REVOLUTIONARY ENGINES + FOREX TRADING"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo ""

# 1. Stop old bot
echo "1️⃣ Stopping old bot..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR
sleep 2
echo "   ✅ Old bot stopped"
echo ""

# 2. Clear log
echo "2️⃣ Clearing old logs..."
> apex.log
echo "   ✅ Log cleared"
echo ""

# 3. Start new bot
echo "3️⃣ Starting bot with all new features..."
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex.log 2>&1 &
BOT_PID=$!
echo "   ✅ Bot started (PID: $BOT_PID)"
echo ""

# 4. Wait for initialization
echo "4️⃣ Waiting 20 seconds for full initialization..."
sleep 20
echo ""

# 5. Verify revolutionary engines
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "🌀 REVOLUTIONARY ENGINES STATUS"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

REV_LOADED=$(tail -500 apex.log | grep -c "REVOLUTIONARY ENGINES LOADED")
REV_MASTER=$(tail -500 apex.log | grep -c "REVOLUTIONARY MASTER")

if [ $REV_LOADED -gt 0 ]; then
    echo "✅ Revolutionary Engines LOADED"
    tail -500 apex.log | grep "REVOLUTIONARY ENGINES LOADED" | head -1
fi

if [ $REV_MASTER -gt 0 ]; then
    echo ""
    echo "✅ Revolutionary Master ACTIVE"
    tail -500 apex.log | grep -A 10 "REVOLUTIONARY MASTER" | head -11
fi

# 6. Verify forex trading
echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "💱 FOREX TRADING STATUS"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

FOREX_LOADED=$(tail -500 apex.log | grep -c "ULTRA FOREX MASTER")
FOREX_DATAHUB=$(tail -500 apex.log | grep -c "Connected to DataHub")
FOREX_EXEC=$(tail -500 apex.log | grep -c "ExecutionOrchestrator for REAL")

if [ $FOREX_LOADED -gt 0 ]; then
    echo "✅ Forex Master LOADED"
    tail -500 apex.log | grep "ULTRA FOREX MASTER" | head -1
fi

if [ $FOREX_DATAHUB -gt 0 ]; then
    echo "✅ Connected to DataHub"
fi

if [ $FOREX_EXEC -gt 0 ]; then
    echo "✅ Connected to ExecutionOrchestrator"
    echo "   → REAL forex trading enabled!"
fi

# 7. Verify exchanges
echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "🌐 MULTI-EXCHANGE STATUS"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

EXCHANGES=$(tail -500 apex.log | grep "exchanges active" | tail -1)
if [ ! -z "$EXCHANGES" ]; then
    echo "$EXCHANGES"
fi

# 8. Verify scanners
echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "🔍 SCANNING ENGINES STATUS"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

tail -500 apex.log | grep "STARTED" | grep -E "Moon|Scanner|Arbitrage|Platform" | head -10

# 9. Check for errors
echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "🔍 ERROR CHECK"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

CRITICAL_ERRORS=$(tail -500 apex.log | grep -i "traceback\|critical\|fatal" | wc -l)
if [ $CRITICAL_ERRORS -eq 0 ]; then
    echo "✅ No critical errors!"
else
    echo "⚠️  Found $CRITICAL_ERRORS critical errors:"
    tail -500 apex.log | grep -i "traceback\|critical\|fatal" | tail -5
fi

# 10. Summary
echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "📊 DEPLOYMENT SUMMARY"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo ""
echo "Bot PID: $BOT_PID"
echo "Status: $(ps -p $BOT_PID > /dev/null && echo '✅ RUNNING' || echo '❌ STOPPED')"
echo ""
echo "Revolutionary Engines: $([ $REV_MASTER -gt 0 ] && echo '✅ ACTIVE' || echo '❌ NOT FOUND')"
echo "Forex Trading: $([ $FOREX_EXEC -gt 0 ] && echo '✅ ACTIVE (REAL)' || echo '⚠️  CHECK LOGS')"
echo "Multi-Exchange: $([ ! -z "$EXCHANGES" ] && echo '✅ ACTIVE' || echo '⚠️  CHECK LOGS')"
echo ""

# 11. Live monitoring commands
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "📺 LIVE MONITORING COMMANDS"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo ""
echo "Watch forex trading:"
echo "  tail -f apex.log | grep -E '💱|FOREX|XAU|EUR|GBP|Published.*REAL'"
echo ""
echo "Watch revolutionary engines:"
echo "  tail -f apex.log | grep -E '🌀|REVOLUTIONARY|Anti-Clockwise|Quantum'"
echo ""
echo "Watch all signals:"
echo "  tail -f apex.log | grep -E 'BUY|SELL|signal|confidence'"
echo ""
echo "Watch everything important:"
echo "  tail -f apex.log | grep -E '💱|🌀|🔍|✅|⚠️|BUY|SELL'"
echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
