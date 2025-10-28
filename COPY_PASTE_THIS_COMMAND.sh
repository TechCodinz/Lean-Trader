#!/bin/bash
# COPY AND PASTE THIS ENTIRE BLOCK INTO YOUR TERMINAL
# (Run on your local machine where you can SSH to VPS)

set -e

# Configuration
VPS_IP="75.119.149.117"
VPS_USER="root"
VPS_BOT_PATH="/root/trading_bot"  # Change if different
LOCAL_REPO_PATH="$HOME/workspace"  # Change to your actual workspace path
BRANCH_NAME="vps-current-working-$(date +%Y%m%d-%H%M)"

echo "🎯 PULLING VPS BOT TO GITHUB"
echo "=============================="
echo ""
echo "VPS: $VPS_IP"
echo "Path: $VPS_BOT_PATH"
echo "Branch: $BRANCH_NAME"
echo ""

# Navigate to your local repo
cd "$LOCAL_REPO_PATH" || {
    echo "❌ Error: Cannot find workspace at $LOCAL_REPO_PATH"
    echo "Please update LOCAL_REPO_PATH in the script"
    exit 1
}

# Fetch latest
git fetch origin

# Create new branch from main
git checkout main
git pull origin main
git checkout -b "$BRANCH_NAME"

# Pull files from VPS (preserving structure)
echo "📥 Pulling from VPS..."
rsync -avz --progress \
    --delete \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='*.log.*' \
    --exclude='venv/' \
    --exclude='env/' \
    --exclude='node_modules/' \
    --exclude='.env.bak*' \
    "$VPS_USER@$VPS_IP:$VPS_BOT_PATH/" \
    ./

# Add all changes
echo ""
echo "💾 Committing changes..."
git add -A

# Commit
git commit -m "feat: Pull current working bot from VPS

VPS IP: $VPS_IP
VPS Path: $VPS_BOT_PATH
Date: $(date)
Branch: $BRANCH_NAME

This is the CURRENT working bot from production VPS.
Contains latest modifications and working configuration.
" || {
    echo "⚠️  No changes detected - VPS matches current code"
    exit 0
}

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
git push -u origin "$BRANCH_NAME"

echo ""
echo "✅ SUCCESS!"
echo "=============================="
echo ""
echo "🌿 Branch: $BRANCH_NAME"
echo "📍 GitHub: https://github.com/TechCodinz/Lean-Trader/tree/$BRANCH_NAME"
echo ""
echo "Now tell the Cursor agent:"
echo "  \"Pull branch: $BRANCH_NAME\""
echo ""
