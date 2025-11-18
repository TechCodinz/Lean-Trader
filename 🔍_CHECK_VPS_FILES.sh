#!/bin/bash

################################################################################
# 🔍 DIAGNOSTIC - CHECK WHICH FILES ARE ON VPS
################################################################################

echo "================================================================================"
echo "🔍 CHECKING VPS FILES - DIAGNOSTIC REPORT"
echo "================================================================================"
echo ""

cd ~/bot || cd ~/apex_bot || { echo "❌ Bot directory not found!"; exit 1; }

echo "📍 Current directory: $(pwd)"
echo ""

# Check git status
echo "================================================================================"
echo "📊 GIT STATUS"
echo "================================================================================"
git status
echo ""

# Check which branch
echo "📍 Current branch: $(git branch --show-current)"
echo "📍 Remote branch: $(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo 'not tracking')"
echo ""

# Check last commit
echo "📍 Last commit:"
git log -1 --oneline
echo ""

# Check if files exist in git
echo "================================================================================"
echo "🔍 CHECKING FILES IN GIT REPO"
echo "================================================================================"
echo ""

FILES=(
    "BOOTSTRAP_PROFIT_TRACKER.py"
    "ULTRA_GOLDMINE_FEATURES.py"
    "ULTRASONIC_INTEGRATION_COMPLETE.py"
    "ULTRASONIC_RARE_STRATEGIES.py"
    "DIVINE_INTELLIGENCE_FEATURES.py"
    "DIVINE_HARMONY_CALIBRATOR.py"
    "SUPREME_CONSCIOUSNESS_CORE.py"
    "SUPREME_ACTIVATION_SYSTEM.py"
    "UNIVERSAL_AI_ORCHESTRATOR.py"
)

echo "Checking if files are tracked in git..."
echo ""

for file in "${FILES[@]}"; do
    if git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
        echo "✅ $file - IN GIT"
    else
        echo "❌ $file - NOT IN GIT"
    fi
done

echo ""
echo "================================================================================"
echo "🔍 CHECKING FILES ON FILESYSTEM"
echo "================================================================================"
echo ""

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(ls -lh "$file" | awk '{print $5}')
        echo "✅ $file - EXISTS ($SIZE)"
    else
        echo "❌ $file - MISSING"
    fi
done

echo ""
echo "================================================================================"
echo "🔍 CHECKING REMOTE (GITHUB)"
echo "================================================================================"
echo ""

echo "Fetching remote info..."
git fetch origin continue-from-micro-fix --dry-run 2>&1 | head -5

echo ""
echo "Files in remote branch:"
for file in "${FILES[@]}"; do
    if git ls-tree -r origin/continue-from-micro-fix --name-only | grep -q "^${file}$"; then
        echo "✅ $file - IN REMOTE"
    else
        echo "❌ $file - NOT IN REMOTE"
    fi
done

echo ""
echo "================================================================================"
echo "📊 SUMMARY"
echo "================================================================================"
echo ""

# Count files
IN_GIT=$(for f in "${FILES[@]}"; do git ls-files --error-unmatch "$f" 2>/dev/null; done | wc -l)
ON_DISK=$(for f in "${FILES[@]}"; do [ -f "$f" ] && echo "$f"; done | wc -l)
IN_REMOTE=$(for f in "${FILES[@]}"; do git ls-tree -r origin/continue-from-micro-fix --name-only | grep -q "^${f}$" && echo "$f"; done | wc -l)

echo "Files in local git: $IN_GIT / ${#FILES[@]}"
echo "Files on disk: $ON_DISK / ${#FILES[@]}"
echo "Files in remote: $IN_REMOTE / ${#FILES[@]}"

echo ""

if [ $IN_REMOTE -eq ${#FILES[@]} ]; then
    echo "✅ ALL FILES ARE IN REMOTE!"
    echo "   Solution: git pull origin continue-from-micro-fix"
elif [ $IN_GIT -eq ${#FILES[@]} ]; then
    echo "✅ ALL FILES ARE IN LOCAL GIT!"
    echo "   Just need to check them out to disk"
else
    echo "⚠️  SOME FILES ARE MISSING FROM REPO!"
    echo "   They need to be added and pushed"
fi

echo ""
echo "================================================================================"
echo "🔧 RECOMMENDED ACTIONS"
echo "================================================================================"
echo ""

if [ $IN_REMOTE -gt $ON_DISK ]; then
    echo "📥 PULL FILES FROM REMOTE:"
    echo "   git pull origin continue-from-micro-fix"
    echo ""
fi

if [ $ON_DISK -lt ${#FILES[@]} ] && [ $IN_GIT -gt $ON_DISK ]; then
    echo "🔄 RESET TO MATCH GIT:"
    echo "   git reset --hard HEAD"
    echo ""
fi

if [ $IN_GIT -lt ${#FILES[@]} ]; then
    echo "⚠️  FILES MISSING FROM GIT:"
    for file in "${FILES[@]}"; do
        if ! git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
            echo "   - $file"
        fi
    done
    echo ""
    echo "   These files need to be added to the repo first!"
fi

echo "================================================================================"
