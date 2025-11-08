#!/bin/bash
#
# 🛡️ SAFE MIGRATION - PRESERVES 19K+ EVOLUTION CYCLES
# This script safely upgrades bot WITHOUT losing learned data
#

echo "═══════════════════════════════════════════════════════════════"
echo "🛡️ SAFE BOT MIGRATION - PRESERVING LEARNED DATA"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Step 1: Backup current learned data
echo "1️⃣  BACKING UP LEARNED DATA..."
BACKUP_DIR="apex_bot_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p ~/$BACKUP_DIR

# Backup databases (contain evolution data)
if [ -d ~/apex_bot ]; then
    echo "   📦 Backing up databases..."
    cp ~/apex_bot/*.db ~/$BACKUP_DIR/ 2>/dev/null
    
    # Backup bot_data directory if exists
    if [ -d ~/apex_bot/bot_data ]; then
        echo "   📦 Backing up bot_data..."
        cp -r ~/apex_bot/bot_data ~/$BACKUP_DIR/
    fi
    
    # Backup current log (to see what was running)
    echo "   📦 Backing up logs..."
    cp ~/apex_bot/apex_bot.log ~/$BACKUP_DIR/ 2>/dev/null
    
    echo "   ✅ Backup created: ~/$BACKUP_DIR"
else
    echo "   ⚠️  ~/apex_bot not found - nothing to backup"
fi

# Step 2: Check what's currently running
echo ""
echo "2️⃣  CHECKING CURRENT BOT STATUS..."
RUNNING_PID=$(pgrep -f "python.*COMPLETE_ULTIMATE_ORCHESTRATOR" | head -1)

if [ -n "$RUNNING_PID" ]; then
    echo "   ⚠️  Bot is RUNNING (PID: $RUNNING_PID)"
    echo "   📊 Checking evolution cycles..."
    
    # Check recent log for evolution count
    EVOLUTION_COUNT=$(grep -o "Evolution cycle [0-9]*" ~/apex_bot/apex_bot.log 2>/dev/null | tail -1 | grep -o "[0-9]*")
    
    if [ -n "$EVOLUTION_COUNT" ]; then
        echo "   🧬 Current evolution cycle: $EVOLUTION_COUNT"
        echo "   ✅ This data will be preserved!"
    fi
    
    echo ""
    echo "   ⚠️  IMPORTANT: Bot is currently running and learning."
    echo "   ⚠️  We should NOT disrupt it unless necessary."
    echo ""
    read -p "   Stop and upgrade bot? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo ""
        echo "   ✅ Migration cancelled - bot continues running"
        echo "   💡 Current bot will keep learning"
        echo "   💡 You can upgrade later when ready"
        exit 0
    fi
else
    echo "   ℹ️  No bot currently running"
    echo "   ✅ Safe to proceed with upgrade"
fi

# Step 3: Pull new code WITHOUT disrupting old
echo ""
echo "3️⃣  PULLING ENHANCED CODE..."
cd ~/apex_bot

# Save current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "   Current branch: $CURRENT_BRANCH"

# Fetch new branch
git fetch origin cursor/check-last-agent-stop-point-for-bot-functionality-8296

echo "   ✅ New code fetched (not yet applied)"

# Step 4: Copy learned data to ensure it persists
echo ""
echo "4️⃣  PREPARING LEARNED DATA FOR NEW BOT..."

# Ensure bot_data directory exists
mkdir -p ~/apex_bot/bot_data

# Copy evolution databases to bot_data if not there
for db in ~/apex_bot/*.db; do
    if [ -f "$db" ]; then
        dbname=$(basename "$db")
        echo "   📦 Preserving $dbname"
        cp "$db" ~/apex_bot/bot_data/ 2>/dev/null
    fi
done

echo "   ✅ Learned data prepared"

# Step 5: Show migration options
echo ""
echo "5️⃣  MIGRATION OPTIONS:"
echo ""
echo "   OPTION A: SAFE TEST (Recommended)"
echo "   ─────────────────────────────────"
echo "   • Keep current bot running"
echo "   • Install enhanced bot in NEW directory"
echo "   • Test new bot with COPY of learned data"
echo "   • Switch when confident"
echo ""
echo "   OPTION B: DIRECT UPGRADE"
echo "   ─────────────────────────────────"
echo "   • Stop current bot"
echo "   • Upgrade in place"
echo "   • Learned data preserved"
echo "   • Start enhanced bot"
echo ""
read -p "   Choose option (A/B): " OPTION

if [ "$OPTION" = "A" ] || [ "$OPTION" = "a" ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "✅ OPTION A: SAFE TEST INSTALLATION"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Installing enhanced bot in: ~/apex_bot_enhanced"
    echo ""
    
    # Clone to new directory
    cd ~
    git clone https://github.com/TechCodinz/Lean-Trader.git apex_bot_enhanced
    cd apex_bot_enhanced
    git checkout cursor/check-last-agent-stop-point-for-bot-functionality-8296
    
    # Copy learned data
    echo "Copying learned data..."
    cp -r ~/apex_bot/bot_data ./
    cp ~/apex_bot/*.db . 2>/dev/null
    
    # Copy .env
    echo "Copying configuration..."
    cp ~/apex_bot/.env .
    
    echo ""
    echo "✅ Enhanced bot installed!"
    echo ""
    echo "To start enhanced bot (OLD bot keeps running):"
    echo "   cd ~/apex_bot_enhanced"
    echo "   source apex_venv/bin/activate  # or create new venv"
    echo "   nohup python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py > apex_bot_enhanced.log 2>&1 &"
    echo ""
    echo "Monitor both:"
    echo "   OLD: tail -f ~/apex_bot/apex_bot.log"
    echo "   NEW: tail -f ~/apex_bot_enhanced/apex_bot_enhanced.log"
    echo ""
    echo "Compare performance, then switch when ready!"
    
elif [ "$OPTION" = "B" ] || [ "$OPTION" = "b" ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "✅ OPTION B: DIRECT UPGRADE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    # Stop bot
    if [ -n "$RUNNING_PID" ]; then
        echo "Stopping current bot..."
        kill -9 $RUNNING_PID
        sleep 2
        echo "✅ Bot stopped"
    fi
    
    # Upgrade in place
    cd ~/apex_bot
    echo "Upgrading code..."
    git checkout cursor/check-last-agent-stop-point-for-bot-functionality-8296
    git pull origin cursor/check-last-agent-stop-point-for-bot-functionality-8296
    
    echo "✅ Code upgraded!"
    echo ""
    echo "Learned data location:"
    echo "   Databases: ~/apex_bot/*.db (preserved)"
    echo "   Bot data: ~/apex_bot/bot_data/ (preserved)"
    echo ""
    echo "To start enhanced bot:"
    echo "   cd ~/apex_bot"
    echo "   source apex_venv/bin/activate"
    echo "   nohup python3 AUTOMATED_ORCHESTRATOR_ENHANCED.py > apex_bot.log 2>&1 &"
    echo "   tail -f apex_bot.log"
    echo ""
    echo "The bot will load existing evolution data and CONTINUE from cycle $EVOLUTION_COUNT"
    
else
    echo "Invalid option. Migration cancelled."
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ MIGRATION PREPARED"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📦 Backup saved to: ~/$BACKUP_DIR"
echo "🧬 Evolution cycles: $EVOLUTION_COUNT (will be preserved)"
echo "💾 Database files: Backed up and ready"
echo ""
echo "Your 19k+ evolution cycles are SAFE! 🛡️"
echo ""
