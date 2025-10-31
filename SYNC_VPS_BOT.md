# 🔄 Sync VPS Bot - Quick Guide

## Quick Command

Run this single command to pull the bot, create a new branch, and verify sync:

```bash
cd /workspace && bash 🔄_SYNC_AND_CREATE_BRANCH.sh
```

---

## What It Does

1. **Fetches all remote branches** - Gets latest from GitHub
2. **Stashes local changes** - Safely saves any uncommitted work
3. **Pulls latest from current branch** - Updates your workspace
4. **Creates new branch** - Makes a timestamped branch: `cursor/sync-from-vps-YYYYMMDD-HHMMSS`
5. **Syncs with micro-fix-local** - Merges VPS branch if it exists
6. **Verifies sync** - Checks commits, files, and imports
7. **Tests critical files** - Ensures all important files are present

---

## Manual Sync Commands

If you prefer to do it manually:

### 1. Fetch and Create Branch
```bash
cd /workspace

# Fetch all remote branches
git fetch origin --all --prune

# Create new branch with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
git checkout -b "cursor/sync-from-vps-${TIMESTAMP}"

# Pull latest from current branch
git pull origin cursor/continue-bot-trading-improvements-4f37
```

### 2. Sync with VPS Branch (micro-fix-local)
```bash
# If micro-fix-local exists on remote
git fetch origin micro-fix-local:micro-fix-local

# Merge it into your new branch
git merge micro-fix-local
```

### 3. Verify Sync
```bash
# Check status
git status

# Check commits ahead/behind
git log --oneline -10

# Verify critical files
ls -la COMPLETE_PROFIT_SYSTEM.py EXECUTION_ORCHESTRATOR.py RUN_BOT.py

# Test imports
python3 -c "from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem; print('✅ OK')"
```

---

## Verify Everything is in Sync

### Check Branch Status
```bash
# Current branch
git branch --show-current

# All branches
git branch -a

# Remote tracking
git branch -vv
```

### Check for Differences
```bash
# See what's different from remote
git diff origin/your-branch-name

# See commit history
git log --oneline --graph --all -20

# Check file differences
git diff --name-status HEAD origin/your-branch-name
```

### Verify Critical Files
```bash
# Check if critical files exist
test -f COMPLETE_PROFIT_SYSTEM.py && echo "✅ COMPLETE_PROFIT_SYSTEM.py" || echo "❌ Missing"
test -f EXECUTION_ORCHESTRATOR.py && echo "✅ EXECUTION_ORCHESTRATOR.py" || echo "❌ Missing"
test -f RUN_BOT.py && echo "✅ RUN_BOT.py" || echo "❌ Missing"
test -f .env && echo "✅ .env" || echo "❌ Missing"
```

### Test Imports
```bash
# Quick import test
python3 << EOF
try:
    from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem
    from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
EOF
```

---

## Push Your New Branch

After syncing and verifying:

```bash
# Push new branch to remote
git push origin cursor/sync-from-vps-YYYYMMDD-HHMMSS

# Or push and set upstream
git push -u origin cursor/sync-from-vps-YYYYMMDD-HHMMSS
```

---

## Troubleshooting

### Merge Conflicts
If you see merge conflicts:
```bash
# See conflicts
git status

# Resolve conflicts manually
# Edit conflicted files, then:
git add .
git commit -m "Resolved merge conflicts"
```

### Missing Remote Branch
If `micro-fix-local` doesn't exist:
```bash
# Check available remote branches
git branch -r

# Pull from the branch you need
git pull origin <branch-name>
```

### Stuck Changes
If you need to reset:
```bash
# Discard local changes (careful!)
git reset --hard origin/your-branch-name

# Or restore from stash
git stash pop
```

---

## Quick Verification Command

One-liner to verify everything:
```bash
cd /workspace && \
echo "📍 Branch: $(git branch --show-current)" && \
echo "🔄 Status: $(git status --short | wc -l) files changed" && \
python3 -c "from COMPLETE_PROFIT_SYSTEM import CompleteProfitSystem; print('✅ Imports OK')" 2>&1 | tail -1
```

---

## Summary

**Use the script:**
```bash
bash 🔄_SYNC_AND_CREATE_BRANCH.sh
```

**Or manually:**
1. `git fetch origin --all`
2. `git checkout -b cursor/sync-from-vps-$(date +%Y%m%d-%H%M%S)`
3. `git pull origin micro-fix-local` (if exists)
4. `git status` (verify)
5. `git push origin <new-branch-name>` (when ready)

That's it! 🚀
