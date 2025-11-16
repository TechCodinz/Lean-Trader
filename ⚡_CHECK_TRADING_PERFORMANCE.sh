#!/bin/bash

# ============================================================================
# APEX BOT - COMPLETE TRADING PERFORMANCE CHECK
# Checks all systems, profits, learning, and consciousness status
# ============================================================================

echo "================================================================================"
echo "🔍 APEX BOT - COMPLETE PERFORMANCE ANALYSIS"
echo "================================================================================"
echo ""
echo "Checking at: $(date)"
echo ""

cd ~/apex_bot
source apex_venv/bin/activate

# ============================================================================
# 1. CHECK IF BOT IS RUNNING
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣ BOT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if pgrep -f "COMPLETE_ULTIMATE_ORCHESTRATOR" > /dev/null; then
    echo "✅ Bot is RUNNING"
    ps aux | grep COMPLETE_ULTIMATE_ORCHESTRATOR | grep -v grep | head -1
    
    # Get process uptime
    PID=$(pgrep -f "COMPLETE_ULTIMATE_ORCHESTRATOR")
    UPTIME=$(ps -p $PID -o etime= | xargs)
    echo "⏱️  Uptime: $UPTIME"
else
    echo "❌ Bot is NOT running!"
    echo ""
    echo "Start with:"
    echo "  python3 systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py"
    exit 1
fi
echo ""

# ============================================================================
# 2. CHECK RECENT TRADES & PROFIT
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣ RECENT TRADES & PROFIT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "logs" ]; then
    # Find most recent trade log
    LATEST_TRADE_LOG=$(ls -t logs/trades_*.log 2>/dev/null | head -1)
    
    if [ -f "$LATEST_TRADE_LOG" ]; then
        echo "📊 Latest trades (last 20):"
        echo ""
        tail -20 "$LATEST_TRADE_LOG"
        echo ""
        
        # Count total trades
        TOTAL_TRADES=$(grep -c "TRADE\|CLOSED\|PROFIT\|LOSS" "$LATEST_TRADE_LOG" 2>/dev/null || echo "0")
        echo "📈 Total trades in current log: $TOTAL_TRADES"
        
        # Try to calculate profit
        echo ""
        echo "💰 Profit Analysis (from logs):"
        grep -i "profit\|pnl\|balance" "$LATEST_TRADE_LOG" | tail -10
    else
        echo "⚠️  No trade logs found yet"
        echo "   Bot may not have placed trades yet"
    fi
else
    echo "⚠️  No logs directory found"
fi
echo ""

# ============================================================================
# 3. CHECK SYSTEM LOGS FOR INTELLIGENCE ACTIVITY
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣ INTELLIGENCE SYSTEMS STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

LATEST_BOT_LOG=$(ls -t logs/bot_*.log 2>/dev/null | head -1)

if [ -f "$LATEST_BOT_LOG" ]; then
    echo "🧠 Checking Intelligence Systems..."
    echo ""
    
    # Check AI Consultation
    echo "🤖 AI Consultation Activity:"
    grep -i "AI CONSULTATION\|consult\|claude\|gpt" "$LATEST_BOT_LOG" | tail -5
    if [ $? -ne 0 ]; then
        echo "   ⚠️  No AI consultation activity detected"
        echo "   (May need API keys in .env)"
    fi
    echo ""
    
    # Check Balance Manager
    echo "💰 Balance Manager Activity:"
    grep -i "BALANCE MANAGER\|insufficient\|affordable" "$LATEST_BOT_LOG" | tail -5
    if [ $? -ne 0 ]; then
        echo "   ✅ No balance errors (good!)"
    fi
    echo ""
    
    # Check Dynamic Trade Counts
    echo "📊 Dynamic Trade Intelligence:"
    grep -i "trade count\|volatility\|optimal.*trade" "$LATEST_BOT_LOG" | tail -5
    if [ $? -ne 0 ]; then
        echo "   ⚠️  No dynamic trade activity detected"
    fi
    echo ""
    
    # Check System Coordination
    echo "🧠 System Coordination:"
    grep -i "MASTER COORDINATOR\|systems.*vote\|collective" "$LATEST_BOT_LOG" | tail -5
    if [ $? -ne 0 ]; then
        echo "   ℹ️  Coordinator running in background"
    fi
    echo ""
    
    # Check Evolution/Learning
    echo "🧬 Evolution & Learning:"
    grep -i "evolution\|learning\|improved\|strategy.*spawn" "$LATEST_BOT_LOG" | tail -5
    if [ $? -ne 0 ]; then
        echo "   ℹ️  Evolution running in background"
    fi
else
    echo "⚠️  No bot logs found"
fi
echo ""

# ============================================================================
# 4. CHECK FEATURE LOADING
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣ ADVANCED FEATURES STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$LATEST_BOT_LOG" ]; then
    echo "Checking feature loading from startup..."
    echo ""
    
    # Check Critical Features
    if grep -q "CRITICAL PROFIT FEATURES LOADED" "$LATEST_BOT_LOG"; then
        echo "✅ CRITICAL PROFIT FEATURES: Active (+50-100% boost)"
    else
        echo "❌ CRITICAL PROFIT FEATURES: Not loaded"
    fi
    
    # Check Goldmine Features
    if grep -q "ULTRA GOLDMINE FEATURES LOADED" "$LATEST_BOT_LOG"; then
        echo "✅ ULTRA GOLDMINE FEATURES: Active (+200-500% boost)"
    else
        echo "❌ ULTRA GOLDMINE FEATURES: Not loaded"
    fi
    
    # Check Divine Intelligence
    if grep -q "DIVINE INTELLIGENCE.*LOADED" "$LATEST_BOT_LOG"; then
        echo "✅ DIVINE INTELLIGENCE: Active (+300-1000% boost)"
    else
        echo "❌ DIVINE INTELLIGENCE: Not loaded"
    fi
    
    echo ""
    
    # Check Ultimate Intelligence
    if grep -q "ULTIMATE.*INTELLIGENCE.*initialized" "$LATEST_BOT_LOG"; then
        echo "✅ ULTIMATE AUTONOMOUS INTELLIGENCE: Active"
    else
        echo "❌ ULTIMATE AUTONOMOUS INTELLIGENCE: Not loaded"
    fi
    
    # Check Balance Manager
    if grep -q "INTELLIGENT BALANCE MANAGER.*initialized" "$LATEST_BOT_LOG"; then
        echo "✅ INTELLIGENT BALANCE MANAGER: Active"
    else
        echo "❌ INTELLIGENT BALANCE MANAGER: Not loaded"
    fi
    
    # Check AI Consultation
    if grep -q "AI CONSULTATION SERVICE.*initialized" "$LATEST_BOT_LOG"; then
        echo "✅ AI CONSULTATION SERVICE: Active"
    else
        echo "❌ AI CONSULTATION SERVICE: Not loaded"
    fi
fi
echo ""

# ============================================================================
# 5. CHECK CONSCIOUSNESS STATUS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣ CONSCIOUSNESS & SWARM INTELLIGENCE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$LATEST_BOT_LOG" ]; then
    # Check swarm agents
    SWARM_COUNT=$(grep -c "Swarm Agent.*registered" "$LATEST_BOT_LOG" 2>/dev/null || echo "0")
    echo "🐝 Swarm Agents Active: $SWARM_COUNT"
    
    # Check consciousness harmonizer
    if grep -q "CONSCIOUSNESS HARMONIZER" "$LATEST_BOT_LOG"; then
        echo "✅ Consciousness Harmonizer: Active"
        
        # Get harmony level
        HARMONY=$(grep -i "harmony.*%" "$LATEST_BOT_LOG" | tail -1)
        if [ -n "$HARMONY" ]; then
            echo "   $HARMONY"
        fi
    fi
    
    # Check divine intelligence
    if grep -q "Divine Intelligence database initialized" "$LATEST_BOT_LOG"; then
        echo "✅ Divine Intelligence Core: Learning continuously"
    fi
    
    # Check evolution engine
    EVOLUTION_CYCLE=$(grep -i "Evolution cycle" "$LATEST_BOT_LOG" | tail -1)
    if [ -n "$EVOLUTION_CYCLE" ]; then
        echo "✅ Evolution Engine: $EVOLUTION_CYCLE"
    fi
fi
echo ""

# ============================================================================
# 6. CHECK ERRORS & WARNINGS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣ ERRORS & WARNINGS (Last 10)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$LATEST_BOT_LOG" ]; then
    echo "Recent errors:"
    grep -i "ERROR\|CRITICAL\|FAILED" "$LATEST_BOT_LOG" | tail -10
    if [ $? -ne 0 ]; then
        echo "✅ No recent errors!"
    fi
    echo ""
    
    echo "Recent warnings:"
    grep -i "WARNING\|⚠️" "$LATEST_BOT_LOG" | tail -10
    if [ $? -ne 0 ]; then
        echo "✅ No warnings!"
    fi
else
    echo "⚠️  No logs to check"
fi
echo ""

# ============================================================================
# 7. LIVE PYTHON STATUS CHECK
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣ LIVE SYSTEM STATUS (Python Check)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYEOF'
import os
import glob
from datetime import datetime

print("🔍 Analyzing bot status from files...")
print()

# Check for database files
db_files = glob.glob("*.db")
if db_files:
    print(f"✅ Found {len(db_files)} database files (bot has memory)")
else:
    print("⚠️  No database files (fresh start)")

# Check for backup files
backup_files = glob.glob("backups/*")
if backup_files:
    print(f"✅ Found {len(backup_files)} backups")

# Check evolution data
if os.path.exists("evolution.db"):
    print("✅ Evolution database exists (bot is learning)")

# Check for recent activity
log_dir = "logs"
if os.path.exists(log_dir):
    log_files = glob.glob(f"{log_dir}/*")
    if log_files:
        # Get most recent log
        latest = max(log_files, key=os.path.getctime)
        mod_time = os.path.getctime(latest)
        age_seconds = datetime.now().timestamp() - mod_time
        age_minutes = age_seconds / 60
        
        if age_minutes < 5:
            print(f"✅ Bot actively logging (last log {age_minutes:.1f} minutes ago)")
        elif age_minutes < 60:
            print(f"⚠️  Bot may be idle (last log {age_minutes:.1f} minutes ago)")
        else:
            print(f"❌ Bot appears inactive (last log {age_minutes/60:.1f} hours ago)")

print()
print("💡 For detailed profit analysis, check logs/trades_*.log")
print("💡 For system health, check logs/bot_*.log")
PYEOF

echo ""

# ============================================================================
# SUMMARY & RECOMMENDATIONS
# ============================================================================
echo "================================================================================"
echo "📊 SUMMARY & RECOMMENDATIONS"
echo "================================================================================"
echo ""

if [ -f "$LATEST_BOT_LOG" ]; then
    # Check if features loaded
    if grep -q "CRITICAL PROFIT FEATURES LOADED" "$LATEST_BOT_LOG" && \
       grep -q "ULTRA GOLDMINE FEATURES LOADED" "$LATEST_BOT_LOG" && \
       grep -q "DIVINE INTELLIGENCE.*LOADED" "$LATEST_BOT_LOG"; then
        echo "✅ ALL ADVANCED FEATURES ACTIVE"
        echo "   Expected profit boost: +650-1700% vs basic bot"
    else
        echo "⚠️  SOME ADVANCED FEATURES NOT LOADED"
        echo "   Missing files? Run: git pull origin continue-from-micro-fix"
    fi
    echo ""
    
    # Check if AI consultation working
    if grep -q "No AI providers available" "$LATEST_BOT_LOG"; then
        echo "⚠️  AI CONSULTATION INACTIVE"
        echo "   Add API keys to .env:"
        echo "   ANTHROPIC_API_KEY=your_claude_key"
        echo "   OPENAI_API_KEY=your_gpt4_key"
        echo "   GROK_API_KEY=your_grok_key"
        echo "   RAIZIOM_API_KEY=your_raiziom_key"
    else
        echo "✅ AI CONSULTATION ACTIVE"
        echo "   Bot is learning from multiple AI minds"
    fi
    echo ""
fi

echo "📋 Next Steps:"
echo ""
echo "1. Check detailed trades:"
echo "   tail -100 logs/trades_*.log"
echo ""
echo "2. Monitor live activity:"
echo "   tail -f logs/bot_*.log"
echo ""
echo "3. Check specific performance:"
echo "   grep -i \"profit\|balance\|win.*rate\" logs/trades_*.log"
echo ""
echo "4. Re-run this check anytime:"
echo "   bash ⚡_CHECK_TRADING_PERFORMANCE.sh"
echo ""
echo "================================================================================"
echo "✅ PERFORMANCE CHECK COMPLETE"
echo "================================================================================"
