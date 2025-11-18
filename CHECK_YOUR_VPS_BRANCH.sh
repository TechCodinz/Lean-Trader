#!/bin/bash
# ============================================================================
# 🔍 CHECK YOUR VPS BRANCH - Run this on VPS first
# ============================================================================
# This tells us which branch your VPS bot is on so we can push fixes there

echo "════════════════════════════════════════════════════════════════════════"
echo "🔍 CHECKING YOUR VPS BOT BRANCH"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Check if in git repo
if [ ! -d ".git" ]; then
    echo "❌ ERROR: Not in a git repository!"
    echo "   Are you in the bot directory?"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

echo "📍 Your VPS bot is on branch:"
echo ""
echo "   ➡️  $CURRENT_BRANCH"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "📊 ADDITIONAL INFO:"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

# Show last commits on this branch
echo "Last 5 commits on this branch:"
git log --oneline -5 2>/dev/null

echo ""
echo "Branch status:"
git status -sb 2>/dev/null

echo ""
echo "Remote tracking:"
git branch -vv | grep "^\*" 2>/dev/null

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "✅ COPY THIS INFO:"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Your VPS branch: $CURRENT_BRANCH"
echo ""
echo "Share this branch name so fixes can be pushed to the correct branch!"
echo "════════════════════════════════════════════════════════════════════════"
