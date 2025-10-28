#!/bin/bash
# RUN THIS ON YOUR LOCAL MACHINE (not in Cursor)

VPS_IP="75.119.149.117"
VPS_USER="root"
WORKSPACE="/workspace"

echo "🎯 PULLING CURRENT VPS BOT TO NEW BRANCH"
echo "=========================================="
echo ""
echo "This will:"
echo "  1. Find bot on VPS"
echo "  2. Pull all files"
echo "  3. Create new branch with current VPS state"
echo ""
read -p "Press ENTER to continue..."

# Step 1: Find bot on VPS
echo ""
echo "🔍 Finding bot location on VPS..."
VPS_PATH=$(ssh "$VPS_USER@$VPS_IP" "find /root /home -maxdepth 3 -name 'COMPLETE_ULTIMATE_ORCHESTRATOR.py' 2>/dev/null | head -1 | xargs dirname" 2>/dev/null)

if [ -z "$VPS_PATH" ]; then
    echo "❌ Could not find bot automatically"
    echo ""
    echo "Common paths to try:"
    ssh "$VPS_USER@$VPS_IP" "ls -la /root/trading_bot/ 2>/dev/null || ls -la /root/trading-bot/ 2>/dev/null || echo 'Not found in common paths'"
    echo ""
    read -p "Enter VPS bot path (e.g., /root/trading_bot): " VPS_PATH
fi

echo "✅ Bot path: $VPS_PATH"

# Step 2: Create new branch
echo ""
echo "🌿 Creating new branch..."
cd "$WORKSPACE"
BRANCH_NAME="vps-current-live-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BRANCH_NAME"

# Step 3: Pull files from VPS
echo ""
echo "📥 Pulling files from VPS..."
rsync -avz --progress \
    --exclude='.git/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='*.log.*' \
    --exclude='venv/' \
    --exclude='node_modules/' \
    "$VPS_USER@$VPS_IP:$VPS_PATH/" \
    "$WORKSPACE/"

# Step 4: Commit
echo ""
echo "💾 Committing VPS snapshot..."
git add -A
git commit -m "feat: Pull current live VPS bot

VPS: $VPS_IP
Path: $VPS_PATH
Date: $(date)
Branch: $BRANCH_NAME

This is the CURRENT working bot from VPS (more recent than previous snapshots).
" || echo "No changes detected"

# Step 5: Show summary
echo ""
echo "✅ COMPLETE!"
echo "=========================================="
echo ""
echo "🌿 Branch: $BRANCH_NAME"
echo "📁 Files pulled from: $VPS_PATH"
echo ""
echo "Next: Push to GitHub so Cursor can access it:"
echo "  git push -u origin $BRANCH_NAME"
echo ""
