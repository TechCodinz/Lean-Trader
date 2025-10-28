#!/bin/bash
# This creates a BRAND NEW branch with unique timestamp

set -e

# UPDATE THESE:
REPO_PATH="$HOME/workspace"                    # ← Your workspace path
VPS_PATH="/root/trading_bot"                   # ← VPS bot path
VPS_USER="root"
VPS_IP="75.119.149.117"

# Generate UNIQUE branch name
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BRANCH_NAME="vps-pull-${TIMESTAMP}"

echo "🎯 Creating NEW branch: $BRANCH_NAME"
echo ""

# Navigate to repo
cd "$REPO_PATH" || exit 1

# Fetch latest
git fetch origin

# Create NEW branch from main
git checkout main
git pull origin main
git checkout -b "$BRANCH_NAME"

echo "✅ Created new branch: $BRANCH_NAME"
echo ""
echo "📥 Pulling files from VPS..."

# Pull from VPS
rsync -avz --progress \
    --delete \
    --exclude='.git/' \
    --exclude='.gitignore' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='venv/' \
    --exclude='node_modules/' \
    "$VPS_USER@$VPS_IP:$VPS_PATH/" \
    ./

echo ""
echo "💾 Committing VPS files..."

# Commit
git add -A
git commit -m "feat: VPS bot snapshot - $TIMESTAMP

Pulled from: $VPS_IP:$VPS_PATH
Date: $(date)
Branch: $BRANCH_NAME

Fresh pull of currently working VPS bot.
"

echo ""
echo "📤 Pushing to GitHub..."

# Push new branch
git push -u origin "$BRANCH_NAME"

echo ""
echo "✅ SUCCESS!"
echo "=================================="
echo ""
echo "🌿 NEW BRANCH: $BRANCH_NAME"
echo ""
echo "📋 Tell Cursor agent:"
echo "    git fetch origin && git checkout $BRANCH_NAME"
echo ""
