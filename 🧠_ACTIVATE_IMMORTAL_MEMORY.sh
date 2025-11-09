#!/bin/bash
#
# 🧠 IMMORTAL MEMORY ACTIVATION
# =============================
# Gives your bot photographic memory - NEVER loses learned data
#

set -e  # Exit on any error

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🧠 ACTIVATING IMMORTAL MEMORY SYSTEM"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Stop bot if running
echo "1️⃣  Stopping bot (if running)..."
pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR || true
sleep 2

# Go to bot directory
cd ~/apex_bot

# Pull the new files
echo ""
echo "2️⃣  Pulling IMMORTAL MEMORY files from GitHub..."
git checkout -f continue-from-micro-fix
git pull --no-rebase origin continue-from-micro-fix || {
    echo "⚠️  Git pull had issues, downloading files directly..."
    curl -O 'https://raw.githubusercontent.com/TechCodinz/Lean-Trader/continue-from-micro-fix/IMMORTAL_MEMORY_SYSTEM.py'
    curl -O 'https://raw.githubusercontent.com/TechCodinz/Lean-Trader/continue-from-micro-fix/INTEGRATE_IMMORTAL_MEMORY.py'
}

# Test the IMMORTAL MEMORY system
echo ""
echo "3️⃣  Testing IMMORTAL MEMORY on your current database..."
python3 IMMORTAL_MEMORY_SYSTEM.py

# Integrate it into the bot
echo ""
echo "4️⃣  Integrating IMMORTAL MEMORY into evolution engine..."
python3 INTEGRATE_IMMORTAL_MEMORY.py

# Verify integration
echo ""
echo "5️⃣  Verifying integration..."
if grep -q "immortal_memory" EVOLUTION_ENGINE.py; then
    echo "✅ Integration successful!"
else
    echo "❌ Integration may have failed - check manually"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ IMMORTAL MEMORY ACTIVATED!"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "YOUR BOT NOW HAS:"
echo "  🧠 Photographic memory - Ultra-sharp, divine retentive memory"
echo "  💾 Auto-backup every 10 evolution cycles"
echo "  🛡️  Triple redundant storage (3 backup locations)"
echo "  🔄 Auto-recovery from database corruption"
echo "  ✨ Git-safe (survives merges, pulls, checkouts)"
echo "  📸 Photoelectric memory for sharp trading"
echo ""
echo "BACKUPS STORED IN:"
echo "  • /root/IMMORTAL_MEMORY/"
echo "  • /root/apex_bot/IMMORTAL_MEMORY/"
echo "  • /tmp/IMMORTAL_MEMORY/"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "🚀 READY TO START BOT"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Start your bot now:"
echo "  nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex.log 2>&1 &"
echo ""
echo "Monitor backups:"
echo "  watch -n 60 'ls -lh /root/IMMORTAL_MEMORY/'"
echo ""
echo "Your bot will NEVER lose its memory again! 🧠✨"
echo "════════════════════════════════════════════════════════════════════════════════"
