#!/bin/bash
# Start bot with Revolutionary Engines and verify everything

echo "🚀 Starting bot with REVOLUTIONARY ENGINES..."
echo ""

# Clear old log
> apex.log

# Start bot
nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex.log 2>&1 &
BOT_PID=$!

echo "✅ Bot started (PID: $BOT_PID)"
echo ""
echo "⏳ Waiting 15 seconds for initialization..."
sleep 15

echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "📊 CHECKING REVOLUTIONARY ENGINES"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

# Check if revolutionary engines loaded
REVOLUTIONARY=$(tail -500 apex.log | grep -c "REVOLUTIONARY ENGINES LOADED")
MASTER=$(tail -500 apex.log | grep -c "REVOLUTIONARY MASTER")
ANTI_CLOCKWISE=$(tail -500 apex.log | grep -c "Anti-Clockwise")
QUANTUM=$(tail -500 apex.log | grep -c "Quantum")
FRACTAL=$(tail -500 apex.log | grep -c "Fractal")
DIMENSIONAL=$(tail -500 apex.log | grep -c "10D")
DNA=$(tail -500 apex.log | grep -c "DNA")

echo ""
echo "🌀 Revolutionary Engines Status:"
if [ $REVOLUTIONARY -gt 0 ]; then
    echo "   ✅ REVOLUTIONARY ENGINES LOADED"
else
    echo "   ❌ Revolutionary engines not found"
fi

if [ $MASTER -gt 0 ]; then
    echo "   ✅ REVOLUTIONARY MASTER initialized"
else
    echo "   ❌ Revolutionary master not found"
fi

if [ $ANTI_CLOCKWISE -gt 0 ]; then
    echo "   ✅ Anti-Clockwise engine ready"
fi

if [ $QUANTUM -gt 0 ]; then
    echo "   ✅ Quantum Time-Reversal ready"
fi

if [ $FRACTAL -gt 0 ]; then
    echo "   ✅ Fractal Recursion ready"
fi

if [ $DIMENSIONAL -gt 0 ]; then
    echo "   ✅ 10D Hyperspace ready"
fi

if [ $DNA -gt 0 ]; then
    echo "   ✅ Market DNA ready"
fi

echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "📊 CHECKING ALL SCANNING ENGINES"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

MOON_SPOTTER=$(tail -500 apex.log | grep -c "MicroMoonSpotter STARTED")
ULTRA_MOON=$(tail -500 apex.log | grep -c "UltraMoonSystem STARTED")
DYNAMIC_SCANNER=$(tail -500 apex.log | grep -c "DynamicMarketScanner STARTED")
MULTI_PLATFORM=$(tail -500 apex.log | grep -c "MultiPlatformScanner STARTED")
ARBITRAGE=$(tail -500 apex.log | grep -c "CrossExchangeArbitrage")

echo ""
echo "🔍 Scanning Engines Status:"
[ $MOON_SPOTTER -gt 0 ] && echo "   ✅ MicroMoonSpotter STARTED" || echo "   ❌ MicroMoonSpotter not started"
[ $ULTRA_MOON -gt 0 ] && echo "   ✅ UltraMoonSystem STARTED" || echo "   ❌ UltraMoonSystem not started"
[ $DYNAMIC_SCANNER -gt 0 ] && echo "   ✅ DynamicMarketScanner STARTED" || echo "   ❌ DynamicMarketScanner not started"
[ $MULTI_PLATFORM -gt 0 ] && echo "   ✅ MultiPlatformScanner STARTED" || echo "   ❌ MultiPlatformScanner not started"
[ $ARBITRAGE -gt 0 ] && echo "   ✅ CrossExchangeArbitrage ready" || echo "   ❌ CrossExchangeArbitrage not found"

echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "📊 CHECKING EXCHANGES"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

EXCHANGES=$(tail -500 apex.log | grep "exchanges active" | tail -1)
if [ ! -z "$EXCHANGES" ]; then
    echo ""
    echo "   $EXCHANGES"
else
    echo ""
    echo "   ⚠️  No multi-exchange initialization found"
fi

echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "🔍 CHECKING FOR ERRORS"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'

ERRORS=$(tail -500 apex.log | grep -i "error\|exception\|failed\|traceback" | wc -l)
if [ $ERRORS -eq 0 ]; then
    echo ""
    echo "   ✅ No errors detected!"
else
    echo ""
    echo "   ⚠️  Found $ERRORS error/warning lines (checking details...)"
    echo ""
    tail -500 apex.log | grep -i "error\|exception" | grep -v "DEBUG" | tail -5
fi

echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo "📋 QUICK SUMMARY"
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
echo ""
echo "Bot PID: $BOT_PID"
echo "Status: $(ps -p $BOT_PID > /dev/null && echo '✅ RUNNING' || echo '❌ STOPPED')"
echo ""
echo "To monitor live:"
echo "   tail -f apex.log | grep -E '🌀|REVOLUTIONARY|signal|BUY|SELL'"
echo ""
echo "To see full initialization:"
echo "   tail -500 apex.log | grep -E 'REVOLUTIONARY|Anti-Clockwise|Quantum|Fractal|10D|DNA'"
echo ""
echo "To check scanner output (wait 2-3 minutes):"
echo "   tail -300 apex.log | grep -E 'Scanning|Found|discovered|pairs|Active'"
echo ""
echo "=" | awk '{s=sprintf("%80s",""); gsub(/ /,"=",$0); print}'
