#!/bin/bash
# Pull working bot from VPS to workspace for analysis

set -e

VPS_IP="75.119.149.117"
VPS_USER="root"
VPS_PATH="/root/trading_bot"  # Common path for root user
BRANCH_NAME="vps-live-bot-$(date +%Y%m%d-%H%M)"

echo "🎯 PULLING LIVE BOT FROM VPS TO WORKSPACE"
echo "=========================================="
echo ""
echo "📍 VPS: $VPS_IP"
echo "👤 User: $VPS_USER"
echo "📁 VPS Path: $VPS_PATH"
echo "🌿 New Branch: $BRANCH_NAME"
echo ""

# Step 1: Create new branch
echo "🌿 Creating new branch: $BRANCH_NAME"
cd /workspace
git checkout -b "$BRANCH_NAME"

# Step 2: Create temp directory for VPS files
echo "📁 Creating temp directory..."
TEMP_DIR="/tmp/vps_bot_pull_$(date +%s)"
mkdir -p "$TEMP_DIR"

# Step 3: Pull files from VPS using rsync
echo "📥 Pulling files from VPS..."
echo ""
echo "⚠️  You may be prompted for SSH password or key..."
echo ""

# Option 1: Try rsync first (faster, preserves timestamps)
if command -v rsync &> /dev/null; then
    echo "Using rsync..."
    rsync -avz --progress \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.log' \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='.env.bak*' \
        "$VPS_USER@$VPS_IP:$VPS_PATH/" \
        "$TEMP_DIR/"
else
    # Option 2: Fallback to scp
    echo "Using scp..."
    scp -r "$VPS_USER@$VPS_IP:$VPS_PATH/*" "$TEMP_DIR/"
fi

# Step 4: Copy VPS files to workspace (excluding git)
echo ""
echo "📋 Copying VPS files to workspace..."
rsync -av --delete \
    --exclude='.git' \
    --exclude='.gitignore' \
    "$TEMP_DIR/" \
    /workspace/

# Step 5: Show what changed
echo ""
echo "📊 Changes detected:"
git status

# Step 6: Add all changes
echo ""
echo "➕ Adding all VPS files to git..."
git add -A

# Step 7: Commit
echo ""
echo "💾 Committing VPS snapshot..."
git commit -m "feat: Pull live working bot from VPS

VPS IP: $VPS_IP
VPS Path: $VPS_PATH
Date: $(date)

This is the actual working bot pulled from production VPS.
Use this to understand what's really running vs workspace code.
" || echo "⚠️  No changes to commit"

# Step 8: Show summary
echo ""
echo "✅ COMPLETE!"
echo "=========================================="
echo ""
echo "🌿 Branch: $BRANCH_NAME"
echo "📁 VPS files are now in workspace"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff main..$BRANCH_NAME"
echo "  2. Compare files to understand VPS setup"
echo "  3. Identify what's working on VPS"
echo ""
echo "To switch back: git checkout main"
echo ""

# Cleanup
rm -rf "$TEMP_DIR"

# Show branch info
git log --oneline -5
