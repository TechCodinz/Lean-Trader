#!/bin/bash
# Compare current branch with micro-fix-local (the working one)

echo "=========================================="
echo "🔍 COMPARING BRANCHES"
echo "=========================================="
echo

CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"
echo

echo "📊 Checking micro-fix-local branch..."
if git show-ref --verify --quiet refs/heads/micro-fix-local; then
    echo "  ✅ micro-fix-local exists locally"
elif git show-ref --verify --quiet refs/remotes/origin/micro-fix-local; then
    echo "  ✅ micro-fix-local exists on remote"
    echo "  💡 Run: git checkout micro-fix-local"
else
    echo "  ❌ micro-fix-local not found"
fi

echo
echo "📝 Differences in COMPLETE_ULTIMATE_ORCHESTRATOR.py:"
if git show-ref --verify --quiet refs/heads/micro-fix-local 2>/dev/null || git show-ref --verify --quiet refs/remotes/origin/micro-fix-local 2>/dev/null; then
    echo "  Comparing imports..."
    git diff micro-fix-local...HEAD -- COMPLETE_ULTIMATE_ORCHESTRATOR.py | grep -E "^\+from|^\-from|^\+import|^\-import" | head -30
else
    echo "  Cannot compare - branch not available"
fi

echo
echo "📦 Files unique to micro-fix-local:"
if git show-ref --verify --quiet refs/heads/micro-fix-local 2>/dev/null || git show-ref --verify --quiet refs/remotes/origin/micro-fix-local 2>/dev/null; then
    git diff --name-only micro-fix-local...HEAD | head -20
else
    echo "  Cannot check - branch not available"
fi

echo
echo "=========================================="
echo "💡 TO SWITCH TO WORKING BRANCH:"
echo "=========================================="
echo "  git fetch origin micro-fix-local"
echo "  git checkout micro-fix-local"
echo "  git pull origin micro-fix-local"
echo