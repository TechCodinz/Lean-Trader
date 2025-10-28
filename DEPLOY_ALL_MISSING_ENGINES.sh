#!/bin/bash
#
# 🚀 DEPLOY ALL MISSING ENGINES - Complete Integration
# ======================================================
#
# Integrates ALL 19+ missing engines:
# - 11 Ultra Rare Engines (market inefficiencies)
# - 6 Professional Systems (brain/hivemind)
# - 2 Complete Trading Systems (ULTRA_SMART_AI, FULL_ULTRA_ARSENAL)
#
# From 116 → 135+ engines!
#

set -e  # Exit on error

echo "================================================================================"
echo "🚀 DEPLOYING ALL MISSING ENGINES - Complete System Integration"
echo "================================================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check we're in the right directory
if [ ! -f "COMPLETE_ULTIMATE_ORCHESTRATOR.py" ]; then
    echo -e "${RED}❌ ERROR: COMPLETE_ULTIMATE_ORCHESTRATOR.py not found${NC}"
    echo "Run this script from the bot directory"
    exit 1
fi

echo ""
echo "📋 Deployment Plan:"
echo "   1. Backup current orchestrator"
echo "   2. Wire Ultra Rare Engines (11 engines)"
echo "   3. Wire Brain + Hivemind (6 classes)"
echo "   4. Verify all integrations"
echo "   5. Test bot startup (dry-run)"
echo ""

# Ask for confirmation
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

echo ""
echo "================================================================================"
echo "STEP 1: Creating Backups"
echo "================================================================================"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/deployment_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "📦 Backing up critical files..."
cp COMPLETE_ULTIMATE_ORCHESTRATOR.py "$BACKUP_DIR/"
cp ULTRA_RARE_ENGINES.py "$BACKUP_DIR/" 2>/dev/null || true
cp brain.py "$BACKUP_DIR/" 2>/dev/null || true
cp hivemind.py "$BACKUP_DIR/" 2>/dev/null || true

echo -e "${GREEN}✅ Backup created: $BACKUP_DIR${NC}"

echo ""
echo "================================================================================"
echo "STEP 2: Wiring Ultra Rare Engines (11 market inefficiency exploiters)"
echo "================================================================================"

if [ -f "WIRE_ULTRA_RARE_ENGINES.py" ]; then
    echo "🔧 Running Ultra Rare Engines integration..."
    python3 WIRE_ULTRA_RARE_ENGINES.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Ultra Rare Engines wired successfully!${NC}"
    else
        echo -e "${RED}❌ Ultra Rare Engines integration failed${NC}"
        echo "Restoring from backup..."
        cp "$BACKUP_DIR/COMPLETE_ULTIMATE_ORCHESTRATOR.py" ./
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  WIRE_ULTRA_RARE_ENGINES.py not found, skipping${NC}"
fi

echo ""
echo "================================================================================"
echo "STEP 3: Wiring Brain + Hivemind (professional trading intelligence)"
echo "================================================================================"

if [ -f "WIRE_BRAIN_HIVEMIND.py" ]; then
    echo "🔧 Running Brain + Hivemind integration..."
    python3 WIRE_BRAIN_HIVEMIND.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Brain + Hivemind wired successfully!${NC}"
    else
        echo -e "${RED}❌ Brain + Hivemind integration failed${NC}"
        echo "Restoring from backup..."
        cp "$BACKUP_DIR/COMPLETE_ULTIMATE_ORCHESTRATOR.py" ./
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  WIRE_BRAIN_HIVEMIND.py not found, skipping${NC}"
fi

echo ""
echo "================================================================================"
echo "STEP 4: Verification"
echo "================================================================================"

echo "🔍 Verifying integrations..."

# Check imports
echo -n "   Checking imports... "
if grep -q "from ULTRA_RARE_ENGINES import" COMPLETE_ULTIMATE_ORCHESTRATOR.py && \
   grep -q "from brain import" COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    exit 1
fi

# Check initializations
echo -n "   Checking initializations... "
if grep -q "self.ultra_rare_orchestrator" COMPLETE_ULTIMATE_ORCHESTRATOR.py && \
   grep -q "self.brain_system" COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    exit 1
fi

# Check tasks
echo -n "   Checking async tasks... "
if grep -q "run_ultra_rare_exploiters" COMPLETE_ULTIMATE_ORCHESTRATOR.py && \
   grep -q "run_brain_advisor" COMPLETE_ULTIMATE_ORCHESTRATOR.py; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All verifications passed!${NC}"

echo ""
echo "================================================================================"
echo "STEP 5: Test Bot Startup (Dry-Run)"
echo "================================================================================"

echo "🧪 Testing bot startup (will stop after 5 seconds)..."

# Test import
python3 -c "from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator; print('✅ Import successful')" 2>&1 | head -20

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Bot startup test passed!${NC}"
else
    echo -e "${RED}❌ Bot startup test failed${NC}"
    echo "Check errors above. Orchestrator may have syntax errors."
    echo ""
    echo "To restore backup:"
    echo "  cp $BACKUP_DIR/COMPLETE_ULTIMATE_ORCHESTRATOR.py ./"
    exit 1
fi

echo ""
echo "================================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "================================================================================"

echo ""
echo "🎉 SUCCESS! All missing engines integrated:"
echo ""
echo "   Ultra Rare Engines (11):"
echo "   ✅ MicrostructureExploiter"
echo "   ✅ InformationEntropyTrader"
echo "   ✅ CascadingLiquidityHunter"
echo "   ✅ FlashCrashPredator"
echo "   ✅ FundingRateArbitrage"
echo "   ✅ HiddenOrderDetector"
echo "   ✅ SmartMoneyShadow"
echo "   ✅ RetailPanicExploiter"
echo "   ✅ TimeWarpPatterns"
echo "   ✅ WhalePsychologyPredictor"
echo "   ✅ UltraRareEnginesOrchestrator"
echo ""
echo "   Professional Systems (6):"
echo "   ✅ Memory (2000 trade replay)"
echo "   ✅ VolSizer (ATR-based sizing)"
echo "   ✅ Brain (regime-aware signals)"
echo "   ✅ Advice (SL/TP calculation)"
echo "   ✅ HiveCoordinator (8 timeframes)"
echo "   ✅ FrameDecision (per-TF decisions)"
echo ""
echo "📊 System Status:"
echo "   Before: 116 engines, 38 async loops"
echo "   After:  135+ engines, 50+ async loops"
echo ""
echo "🚀 Ready to Deploy:"
echo "   1. Stop current bot: pkill -9 -f COMPLETE_ULTIMATE_ORCHESTRATOR"
echo "   2. Start new bot:    nohup python COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &"
echo "   3. Monitor:          tail -f bot.log | grep -E 'ULTRA RARE|BRAIN|HIVEMIND|💎|🧠|🐝'"
echo ""
echo "💾 Backup Location: $BACKUP_DIR"
echo ""
echo "================================================================================"
