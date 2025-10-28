# 🎯 Pull VPS Bot to GitHub - SIMPLE

## What You Need to Do:

### Step 1: Copy This Command

```bash
# Update these first:
REPO_PATH="/path/to/your/workspace"  # Your actual workspace location
VPS_PATH="/root/trading_bot"          # Where bot is on VPS

# Then run this:
cd "$REPO_PATH" && \
git checkout main && \
git pull && \
git checkout -b "vps-working-$(date +%Y%m%d-%H%M)" && \
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='*.log' \
  root@75.119.149.117:"$VPS_PATH/" ./ && \
git add -A && \
git commit -m "Pull current VPS bot - $(date)" && \
git push -u origin "vps-working-$(date +%Y%m%d-%H%M)" && \
echo "✅ DONE! Branch: vps-working-$(date +%Y%m%d-%H%M)"
```

### Step 2: Tell Me the Branch Name

After it pushes, tell me:
> "Pull branch: vps-working-20251028-XXXX"

### Step 3: I'll Pull and Analyze

I'll:
1. `git fetch origin`
2. `git checkout your-branch-name`
3. Compare VPS vs workspace code
4. Tell you exactly what's different

---

## Don't Know VPS Path?

Find it first:

```bash
ssh root@75.119.149.117 "ps aux | grep python | grep -E '(orchestrator|bot)' | head -5"
```

Or:

```bash
ssh root@75.119.149.117 "find /root /home -name 'COMPLETE_ULTIMATE_ORCHESTRATOR.py' 2>/dev/null"
```

---

## Quick Version (If You Know Paths)

```bash
cd ~/workspace && \
git checkout -b vps-live-now && \
rsync -avz root@75.119.149.117:/root/trading_bot/ ./ && \
git add -A && git commit -m "VPS bot" && \
git push -u origin vps-live-now
```

Then tell me: **"Pull branch: vps-live-now"**
