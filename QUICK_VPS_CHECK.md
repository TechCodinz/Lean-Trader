# 🔍 Check What's Running on VPS - QUICK

## Step 1: See What's Actually Running

```bash
# All Python processes
ssh root@75.119.149.117 "ps aux | grep python | grep -v grep"
```

Look for:
- `MICRO_WALLET_GROWER.py`
- `COMPLETE_ULTIMATE_ORCHESTRATOR.py`
- `RUN_BOT.py`

---

## Step 2: Find the Bot Directory

```bash
ssh root@75.119.149.117 "find /root /home -name 'MICRO_WALLET_GROWER.py' -o -name 'COMPLETE_ULTIMATE_ORCHESTRATOR.py' 2>/dev/null"
```

---

## Step 3: Check Screen/Tmux Sessions

```bash
# Screen
ssh root@75.119.149.117 "screen -ls"

# Tmux
ssh root@75.119.149.117 "tmux ls"
```

---

## Step 4: See What Command Started It

```bash
ssh root@75.119.149.117 "ps aux | grep python | grep -v grep | awk '{for(i=11;i<=NF;i++) printf \$i\" \"; print \"\"}'"
```

This shows the **full command line** that started each Python process.

---

## Step 5: Check Recent Logs

```bash
ssh root@75.119.149.117 "find /root -name '*.log' -type f -mmin -60 | head -5 | xargs tail -50"
```

Look for:
- MICRO WALLET mentions
- Trade execution attempts
- Errors

---

## Step 6: Pull the ACTUAL Running Bot

Once you know the path (e.g., `/root/trading_bot`), run:

```bash
REPO_PATH="$HOME/workspace" && \
VPS_PATH="/root/trading_bot" && \
NEW_BRANCH="vps-micro-fix-$(date +%Y%m%d-%H%M%S)" && \
cd "$REPO_PATH" && \
git checkout main && \
git pull && \
git checkout -b "$NEW_BRANCH" && \
rsync -avz --delete \
  --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='*.log' \
  root@75.119.149.117:"$VPS_PATH/" ./ && \
git add -A && \
git commit -m "VPS bot - MICRO WALLET not executing trades" && \
git push -u origin "$NEW_BRANCH" && \
echo "" && \
echo "✅ Branch: $NEW_BRANCH"
```

---

## MICRO WALLET Issue Checklist:

When you pull the code, I'll check:
- ✅ Is MICRO_WALLET_GROWER.py being imported?
- ✅ Is it initialized in the orchestrator?
- ✅ Is the execution loop actually running?
- ✅ Are there API key issues?
- ✅ Is it checking conditions correctly?
- ✅ Are trades being generated but not executed?
- ✅ Or is it not generating signals at all?

---

## Quick Diagnosis Commands:

```bash
# Is MICRO WALLET code on VPS?
ssh root@75.119.149.117 "ls -la /root/trading_bot/MICRO_WALLET_GROWER.py"

# Check if it's imported in orchestrator
ssh root@75.119.149.117 "grep -n 'MICRO_WALLET' /root/trading_bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py"

# Check recent MICRO activity in logs
ssh root@75.119.149.117 "grep -i 'micro' /root/trading_bot/*.log | tail -50"
```

---

**Start with Step 1** - check what's running, then we'll pull the right code! 🚀
