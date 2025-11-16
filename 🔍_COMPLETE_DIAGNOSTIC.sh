#!/bin/bash
#
# 🔍 COMPLETE DIAGNOSTIC - Check EVERYTHING
#
# This checks:
# 1. Bot status
# 2. All systems loaded
# 3. Errors/warnings
# 4. Exchange connections
# 5. Balance detection
# 6. Signal generation
# 7. Trade execution
# 8. Evolution activity
# 9. Silent failures
#

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🔍 COMPLETE SYSTEM DIAGNOSTIC"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

LOG_FILE="apex_live.log"

# Check if log exists
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    echo "Bot may not be running or using different log file"
    echo ""
    echo "Available logs:"
    ls -lth *.log 2>/dev/null | head -5
    exit 1
fi

echo "📋 Analyzing: $LOG_FILE"
echo "📊 Log size: $(du -h $LOG_FILE | cut -f1)"
echo "⏰ Last updated: $(stat -c %y $LOG_FILE | cut -d'.' -f1)"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  BOT PROCESS STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if pgrep -f "COMPLETE_ULTIMATE_ORCHESTRATOR" > /dev/null; then
    echo "✅ Bot is RUNNING"
    ps aux | grep COMPLETE_ULTIMATE_ORCHESTRATOR | grep -v grep
else
    echo "❌ Bot is NOT RUNNING"
    exit 1
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  SYSTEM INITIALIZATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Core Systems:"
grep "SYSTEMS INITIALIZED" $LOG_FILE | tail -1 || echo "⚠️  No initialization message found"

echo ""
echo "Intelligence Systems:"
grep -E "AI.*Service|Balance.*Manager|Autonomous.*Coordinator|Ultimate.*Intelligence" $LOG_FILE | grep "initialized" | tail -10

echo ""
echo "Evolution:"
EVOLUTION_COUNT=$(grep -c "Spawned.*Evolution" $LOG_FILE)
echo "Models spawned: $EVOLUTION_COUNT"
grep "Evolution systems initialized" $LOG_FILE | tail -1 || echo "Checking..."

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  ERRORS & WARNINGS CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ERROR_COUNT=$(grep -c "ERROR" $LOG_FILE)
WARNING_COUNT=$(grep -c "WARNING" $LOG_FILE)
CRITICAL_COUNT=$(grep -c "CRITICAL\|FAILED" $LOG_FILE)

echo "Total errors: $ERROR_COUNT"
echo "Total warnings: $WARNING_COUNT"
echo "Critical issues: $CRITICAL_COUNT"

if [ $ERROR_COUNT -gt 0 ] || [ $CRITICAL_COUNT -gt 0 ]; then
    echo ""
    echo "⚠️  Recent errors (last 10):"
    grep -E "ERROR|CRITICAL" $LOG_FILE | tail -10
fi

if [ $WARNING_COUNT -gt 0 ]; then
    echo ""
    echo "⚠️  Recent warnings (last 5):"
    grep "WARNING" $LOG_FILE | tail -5
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  EXCHANGE CONNECTIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Exchanges initialized:"
grep "exchanges initialized" $LOG_FILE | tail -5

echo ""
echo "Exchange status:"
grep -E "binance.*initialized|bybit.*initialized|gateio.*initialized" $LOG_FILE | tail -10

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  BALANCE DETECTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Balance checks:"
grep -i "balance\|Balance" $LOG_FILE | grep -v "Rebalance" | tail -15

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  SIGNAL GENERATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SIGNAL_COUNT=$(grep -c "Published.*signals" $LOG_FILE)
echo "Total signals published: $SIGNAL_COUNT"

echo ""
echo "Recent signals:"
grep "Published.*signals\|Signal.*confidence" $LOG_FILE | tail -10

echo ""
echo "Signal types:"
grep -E "FX signal|ARBITRAGE signal|SCALP signal|Decision:" $LOG_FILE | tail -10

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  TRADE EXECUTION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TRADE_COUNT=$(grep -c "Trade executed\|TRADE.*SUCCESS" $LOG_FILE)
WIN_COUNT=$(grep -c "WIN" $LOG_FILE)
LOSS_COUNT=$(grep -c "LOSS" $LOG_FILE)

echo "Total trades: $TRADE_COUNT"
echo "Wins: $WIN_COUNT"
echo "Losses: $LOSS_COUNT"

if [ $TRADE_COUNT -gt 0 ]; then
    WIN_RATE=$(echo "scale=1; $WIN_COUNT * 100 / $TRADE_COUNT" | bc 2>/dev/null || echo "N/A")
    echo "Win rate: ${WIN_RATE}%"
    
    echo ""
    echo "Recent trades:"
    grep -E "Trade executed|WIN|LOSS" $LOG_FILE | tail -10
else
    echo ""
    echo "ℹ️  No trades yet - Bot analyzing for perfect opportunities"
    echo ""
    echo "Checking decision making:"
    grep -i "Decision:" $LOG_FILE | tail -5 || echo "No decisions logged yet"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  EVOLUTION ENGINE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

EVOLUTION_CYCLES=$(grep -c "Evolution Cycle" $LOG_FILE)
echo "Evolution cycles completed: $EVOLUTION_CYCLES"

echo ""
echo "Latest evolution activity:"
grep "Evolving\|Evolution cycle.*completed" $LOG_FILE | tail -15

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  SILENT FAILURES CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Checking for silent failures..."
echo ""

# Check for traceback (Python errors)
TRACEBACK_COUNT=$(grep -c "Traceback" $LOG_FILE)
if [ $TRACEBACK_COUNT -gt 0 ]; then
    echo "⚠️  Found $TRACEBACK_COUNT tracebacks (errors):"
    grep -A 10 "Traceback" $LOG_FILE | tail -30
else
    echo "✅ No tracebacks found"
fi

echo ""

# Check for failed imports
IMPORT_ERRORS=$(grep -c "ModuleNotFoundError\|ImportError" $LOG_FILE)
if [ $IMPORT_ERRORS -gt 0 ]; then
    echo "⚠️  Import errors found: $IMPORT_ERRORS"
    grep "ModuleNotFoundError\|ImportError" $LOG_FILE | tail -10
else
    echo "✅ No import errors"
fi

echo ""

# Check for failed connections
CONNECTION_ERRORS=$(grep -c "Connection.*failed\|Connection.*refused\|timeout" $LOG_FILE)
if [ $CONNECTION_ERRORS -gt 0 ]; then
    echo "⚠️  Connection issues: $CONNECTION_ERRORS"
    grep -i "connection.*failed\|refused\|timeout" $LOG_FILE | tail -10
else
    echo "✅ No connection errors"
fi

echo ""

# Check for insufficient balance errors
BALANCE_ERRORS=$(grep -c "insufficient.*balance\|Balance too low" $LOG_FILE)
if [ $BALANCE_ERRORS -gt 0 ]; then
    echo "⚠️  Balance errors: $BALANCE_ERRORS"
    grep -i "insufficient.*balance\|Balance too low" $LOG_FILE | tail -5
else
    echo "✅ No balance errors"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔟 AI CONSULTATION STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "AI systems:"
grep -E "AI.*initialized|AI.*available|Gemini.*initialized" $LOG_FILE | tail -10

echo ""
echo "AI consultations:"
AI_CONSULT_COUNT=$(grep -c "Consulting.*AI\|AI.*found" $LOG_FILE)
echo "Total AI consultations: $AI_CONSULT_COUNT"

if [ $AI_CONSULT_COUNT -gt 0 ]; then
    grep "Consulting.*AI\|AI.*found" $LOG_FILE | tail -5
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣1️⃣  LIVE ACTIVITY (Last 2 Minutes)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get timestamp from 2 minutes ago
TWO_MIN_AGO=$(date -d '2 minutes ago' '+%Y-%m-%d %H:%M' 2>/dev/null || date -v-2M '+%Y-%m-%d %H:%M' 2>/dev/null)

echo "Activity since $TWO_MIN_AGO:"
echo ""

# Show recent activity
tail -100 $LOG_FILE | grep -E "✅|🔄|🔧|💱|🎯" | tail -20

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣2️⃣  PERFORMANCE SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get latest cycle stats
echo "Latest cycle stats:"
grep "Complete cycle" $LOG_FILE | tail -1

echo ""
echo "System health:"
grep "All engines healthy\|Harmony.*complete" $LOG_FILE | tail -3

echo ""

# ═══════════════════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIAGNOSTIC SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
if [ $ERROR_COUNT -eq 0 ] && [ $CRITICAL_COUNT -eq 0 ]; then
    echo "✅ NO CRITICAL ISSUES FOUND"
    echo "✅ All systems operational"
    echo "✅ Bot is healthy and running"
else
    echo "⚠️  Found $ERROR_COUNT errors, $CRITICAL_COUNT critical issues"
    echo "Review errors above for details"
fi

echo ""
echo "Current status:"
echo "  • Systems: Running"
echo "  • Evolution: Active ($EVOLUTION_CYCLES cycles)"
echo "  • Signals: Generated ($SIGNAL_COUNT)"
echo "  • Trades: $TRADE_COUNT (Wins: $WIN_COUNT, Losses: $LOSS_COUNT)"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Diagnostic complete! Check above for any issues."
echo "═══════════════════════════════════════════════════════════════════════════════"
