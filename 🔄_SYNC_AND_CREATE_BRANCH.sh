#!/bin/bash
#
# 🔄 SYNC BOT AND CREATE NEW BRANCH
# Pulls latest from remote, creates new branch, verifies sync
#

set -e  # Exit on error

echo "=" | tr -d '\n' | head -c 80
echo ""
echo "🔄 SYNCING BOT AND CREATING NEW BRANCH"
echo "=" | tr -d '\n' | head -c 80
echo ""
echo ""

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"
echo ""

# Step 1: Fetch all remote branches
echo "📥 Step 1: Fetching all remote branches..."
git fetch origin --all --prune
echo "✅ Fetched all remote branches"
echo ""

# Step 2: Show available branches
echo "📋 Available remote branches:"
git branch -r | grep -E "(micro-fix-local|main|master|continue)" | head -5
echo ""

# Step 3: Stash any local changes (if any)
echo "💾 Step 2: Stashing local changes (if any)..."
if ! git diff-index --quiet HEAD --; then
    git stash push -m "Auto-stash before sync $(date +%Y%m%d-%H%M%S)"
    echo "✅ Stashed local changes"
else
    echo "✅ No local changes to stash"
fi
echo ""

# Step 4: Get latest from current branch
echo "🔄 Step 3: Pulling latest from current branch..."
git pull origin "$CURRENT_BRANCH" || echo "⚠️  Could not pull from $CURRENT_BRANCH (might not exist on remote)"
echo ""

# Step 5: Create new branch with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
NEW_BRANCH="cursor/sync-from-vps-${TIMESTAMP}"

echo "🌿 Step 4: Creating new branch: $NEW_BRANCH"
git checkout -b "$NEW_BRANCH"
echo "✅ Created and switched to branch: $NEW_BRANCH"
echo ""

# Step 6: Try to sync with micro-fix-local (VPS branch) if it exists
if git show-ref --verify --quiet refs/remotes/origin/micro-fix-local; then
    echo "🔄 Step 5: Syncing with micro-fix-local (VPS branch)..."
    git fetch origin micro-fix-local:micro-fix-local
    echo "✅ Fetched micro-fix-local branch"
    
    # Merge micro-fix-local into new branch
    if git merge --no-edit micro-fix-local 2>/dev/null; then
        echo "✅ Merged micro-fix-local into $NEW_BRANCH"
    else
        echo "⚠️  Merge conflicts detected - manual resolution needed"
        echo "   Run: git status to see conflicts"
    fi
    echo ""
else
    echo "⚠️  micro-fix-local branch not found on remote"
    echo ""
fi

# Step 7: Verify sync status
echo "🔍 Step 6: Verifying sync status..."
echo ""
echo "📊 Branch Status:"
echo "   Current branch: $(git branch --show-current)"
echo "   Remote tracking: $(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo 'not set')"
echo ""

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Uncommitted changes detected:"
    git status --short
    echo ""
fi

# Check commits ahead/behind
COMMITS_AHEAD=$(git rev-list --count HEAD ^origin/"$NEW_BRANCH" 2>/dev/null || echo "0")
COMMITS_BEHIND=$(git rev-list --count origin/"$NEW_BRANCH" ^HEAD 2>/dev/null || echo "0")

if [ "$COMMITS_AHEAD" -gt 0 ] || [ "$COMMITS_BEHIND" -gt 0 ]; then
    echo "📈 Commits ahead: $COMMITS_AHEAD"
    echo "📉 Commits behind: $COMMITS_BEHIND"
else
    echo "✅ Branch is in sync with remote"
fi
echo ""

# Step 8: Show file differences (if any)
echo "📁 Step 7: Checking for file changes..."
CHANGED_FILES=$(git diff --name-only HEAD origin/"$NEW_BRANCH" 2>/dev/null | wc -l)
if [ "$CHANGED_FILES" -gt 0 ]; then
    echo "📝 Changed files detected:"
    git diff --name-status HEAD origin/"$NEW_BRANCH" 2>/dev/null | head -10
else
    echo "✅ No file differences detected"
fi
echo ""

# Step 9: Verify critical files exist
echo "✅ Step 8: Verifying critical files..."
CRITICAL_FILES=(
    "COMPLETE_PROFIT_SYSTEM.py"
    "EXECUTION_ORCHESTRATOR.py"
    "COMPLETE_ULTIMATE_ORCHESTRATOR.py"
    "RUN_BOT.py"
    ".env"
)

ALL_FILES_OK=true
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (MISSING)"
        ALL_FILES_OK=false
    fi
done

if [ "$ALL_FILES_OK" = true ]; then
    echo ""
    echo "✅ All critical files present"
else
    echo ""
    echo "⚠️  Some critical files are missing"
fi
echo ""

# Step 10: Test imports (quick check)
echo "🧪 Step 9: Testing imports..."
if python3 -c "from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem; print('✅ COMPLETE_PROFIT_SYSTEM')" 2>/dev/null; then
    echo "   ✅ COMPLETE_PROFIT_SYSTEM imports OK"
else
    echo "   ⚠️  COMPLETE_PROFIT_SYSTEM import failed"
fi

if python3 -c "from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator; print('✅ EXECUTION_ORCHESTRATOR')" 2>/dev/null; then
    echo "   ✅ EXECUTION_ORCHESTRATOR imports OK"
else
    echo "   ⚠️  EXECUTION_ORCHESTRATOR import failed"
fi
echo ""

# Summary
echo "=" | tr -d '\n' | head -c 80
echo ""
echo "🎉 SYNC COMPLETE!"
echo "=" | tr -d '\n' | head -c 80
echo ""
echo ""
echo "📌 Summary:"
echo "   Old branch: $CURRENT_BRANCH"
echo "   New branch: $NEW_BRANCH"
echo "   Status: $(git status --short | wc -l) files changed"
echo ""
echo "📝 Next steps:"
echo "   1. Review changes: git diff"
echo "   2. Commit changes: git add . && git commit -m 'message'"
echo "   3. Push branch: git push origin $NEW_BRANCH"
echo ""
echo "🔍 To see changes:"
echo "   git log --oneline -10"
echo "   git diff HEAD~5"
echo ""
echo "✅ All done! Your bot is synced and ready."
echo ""
