#!/bin/bash

echo "================================================================================"
echo "🔍 COMPARE VPS vs BRANCH (continue-from-micro-fix)"
echo "================================================================================"
echo ""

# Fetch latest
echo "📥 Fetching latest branch info..."
git fetch origin continue-from-micro-fix 2>/dev/null
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  COMMIT COMPARISON"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Your VPS (last 5 commits):"
git log --oneline -5
echo ""

echo "Branch remote (last 5 commits):"
git log --oneline -5 origin/continue-from-micro-fix
echo ""

BEHIND=$(git rev-list --count HEAD..origin/continue-from-micro-fix 2>/dev/null || echo "0")
AHEAD=$(git rev-list --count origin/continue-from-micro-fix..HEAD 2>/dev/null || echo "0")

echo "Status:"
if [ "$BEHIND" -gt 0 ]; then
    echo "  📥 You are $BEHIND commits BEHIND the branch"
    echo "     (Branch has new changes you don't have)"
fi
if [ "$AHEAD" -gt 0 ]; then
    echo "  📤 You are $AHEAD commits AHEAD of the branch"
    echo "     (You have local changes not in branch)"
fi
if [ "$BEHIND" -eq 0 ] && [ "$AHEAD" -eq 0 ]; then
    echo "  ✅ You are up to date with the branch"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  FILE DIFFERENCES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Files modified on VPS (not in branch):"
git status -s
echo ""

echo "Files different between VPS and branch:"
git diff --name-status origin/continue-from-micro-fix
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  NEW FILES ON BRANCH (You'll get these when you pull)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Files that exist on branch but not on VPS
git diff --name-only --diff-filter=A origin/continue-from-micro-fix

if [ $? -eq 0 ]; then
    echo ""
    echo "🆕 These are NEW optimization files you'll get:"
    git diff --name-only --diff-filter=A origin/continue-from-micro-fix | grep -E "WEBSOCKET|SMART|SIGNAL|DYNAMIC|OPTIMIZATION"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  DETAILED DIFF FOR KEY FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check key files
for file in EVOLUTION_ENGINE.py COMPLETE_ULTIMATE_ORCHESTRATOR.py IMMORTAL_MEMORY_SYSTEM.py; do
    echo "Checking: $file"
    
    if [ -f "$file" ]; then
        # Check if file differs from branch
        if git diff --quiet origin/continue-from-micro-fix -- "$file" 2>/dev/null; then
            echo "  ✅ Same as branch"
        else
            echo "  ⚠️  DIFFERENT from branch!"
            echo "     Lines changed: $(git diff origin/continue-from-micro-fix -- "$file" | grep -c '^[+-]' || echo '0')"
        fi
    else
        echo "  ❌ File not found on VPS"
        
        # Check if it exists on branch
        if git cat-file -e origin/continue-from-micro-fix:"$file" 2>/dev/null; then
            echo "     (But exists on branch - you'll get it when you pull)"
        fi
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  WHAT WILL HAPPEN WHEN YOU PULL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if pull will cause conflicts
git merge-tree $(git merge-base HEAD origin/continue-from-micro-fix) HEAD origin/continue-from-micro-fix > /tmp/merge-preview.txt 2>&1

if grep -q "<<<<<<" /tmp/merge-preview.txt; then
    echo "⚠️  WARNING: Pull may cause CONFLICTS!"
    echo "   Files that will conflict:"
    grep -B5 "<<<<<<" /tmp/merge-preview.txt | grep "^+++ " | cut -d'/' -f2-
    echo ""
    echo "   RECOMMENDATION: Backup first, then resolve conflicts manually"
else
    echo "✅ Pull should be clean (no conflicts expected)"
    echo ""
    echo "Files that will be updated:"
    git diff --name-only origin/continue-from-micro-fix | head -10
    
    if [ $(git diff --name-only origin/continue-from-micro-fix | wc -l) -gt 10 ]; then
        echo "   ... and $(expr $(git diff --name-only origin/continue-from-micro-fix | wc -l) - 10) more"
    fi
fi
echo ""

echo "================================================================================"
echo "📊 SUMMARY"
echo "================================================================================"
echo ""
echo "Current Branch: $(git branch --show-current)"
echo "Commits Behind: $BEHIND"
echo "Commits Ahead: $AHEAD"
echo "Modified Files: $(git status -s | grep "^ M" | wc -l)"
echo "Untracked Files: $(git status -s | grep "^??" | wc -l)"
echo ""

if [ "$BEHIND" -gt 0 ] || [ $(git status -s | wc -l) -gt 0 ]; then
    echo "🚨 RECOMMENDATION:"
    echo "   1. Run backup script first:"
    echo "      bash 💾_BACKUP_VPS_BEFORE_PULL.sh"
    echo ""
    echo "   2. Review the backup, especially:"
    echo "      - VPS_STATE.txt"
    echo "      - vps_changes.patch"
    echo ""
    echo "   3. Then safely pull:"
    echo "      git pull origin continue-from-micro-fix"
else
    echo "✅ You're up to date! Safe to use current setup."
fi
echo ""
echo "================================================================================"
