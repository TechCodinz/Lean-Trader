# 🎯 Pull VPS Bot to NEW Branch

## Quick Command (Copy & Paste)

This creates a **brand new branch** with timestamp: `vps-pull-20251028-HHMMSS`

```bash
REPO_PATH="$HOME/workspace" && \
VPS_PATH="/root/trading_bot" && \
NEW_BRANCH="vps-pull-$(date +%Y%m%d-%H%M%S)" && \
cd "$REPO_PATH" && \
git fetch origin && \
git checkout main && \
git pull origin main && \
git checkout -b "$NEW_BRANCH" && \
echo "✅ Created NEW branch: $NEW_BRANCH" && \
rsync -avz --delete \
  --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='*.log' --exclude='venv' --exclude='node_modules' \
  root@75.119.149.117:"$VPS_PATH/" ./ && \
git add -A && \
git commit -m "VPS bot snapshot - $(date)" && \
git push -u origin "$NEW_BRANCH" && \
echo "" && \
echo "✅ DONE! NEW BRANCH: $NEW_BRANCH"
```

---

## What This Does:

1. ✅ **Creates NEW branch**: `vps-pull-YYYYMMDD-HHMMSS` (unique timestamp)
2. ✅ **Pulls from VPS**: `/root/trading_bot/` (or whatever you set)
3. ✅ **Commits everything**: All VPS files
4. ✅ **Pushes to GitHub**: So I can access it
5. ✅ **Shows branch name**: At the end

---

## Update Paths First:

Change these two lines at the top:

```bash
REPO_PATH="$HOME/workspace"      # ← Your actual workspace location
VPS_PATH="/root/trading_bot"     # ← Where bot is on VPS
```

---

## After Running:

You'll see:
```
✅ DONE! NEW BRANCH: vps-pull-20251028-105432
```

Then tell me:
> **"Branch: vps-pull-20251028-105432"**

---

## I'll Then:

```bash
git fetch origin
git checkout vps-pull-20251028-105432
```

And analyze:
- What's different between VPS and workspace
- What files are on VPS but not here
- Which orchestrator is actually running
- Configuration differences
- What's making it work on VPS

---

## Don't Know VPS Path?

Find it:
```bash
ssh root@75.119.149.117 "find /root /home -name '*.py' -path '*trading*' | head -10"
```

Or check what's running:
```bash
ssh root@75.119.149.117 "ps aux | grep python"
```

---

**Ready!** Just copy-paste the command and give me the new branch name 🚀
