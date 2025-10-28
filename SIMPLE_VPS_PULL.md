# 🎯 Pull Current VPS Bot - SIMPLE STEPS

## You Need to Run This on Your LOCAL Machine

(Cursor/this workspace doesn't have SSH access to your VPS)

---

## Option 1: One Command (Recommended)

```bash
# On your local machine:
cd /path/to/your/workspace

# Pull from VPS
rsync -avz --exclude='.git' root@75.119.149.117:/root/trading_bot/ ./

# Create new branch
git checkout -b vps-live-$(date +%Y%m%d-%H%M)

# Commit
git add -A
git commit -m "Pull current VPS bot"

# Push to GitHub so Cursor can see it
git push -u origin vps-live-$(date +%Y%m%d-%H%M)
```

---

## Option 2: Find Bot First

If you don't know where the bot is:

```bash
# Find it
ssh root@75.119.149.117 "find /root /home -name 'COMPLETE_ULTIMATE_ORCHESTRATOR.py'"

# Then pull (replace PATH)
rsync -avz root@75.119.149.117:/path/to/bot/ /path/to/workspace/
```

---

## Option 3: Download and Upload

```bash
# 1. Download from VPS to local
scp -r root@75.119.149.117:/root/trading_bot ~/vps_bot_backup

# 2. Copy to workspace
cp -r ~/vps_bot_backup/* /path/to/workspace/

# 3. Git it
cd /path/to/workspace
git checkout -b vps-current-live
git add -A
git commit -m "VPS current state"
git push -u origin vps-current-live
```

---

## After You Push

Tell me the branch name and I'll:
1. Fetch it
2. Checkout to that branch  
3. Analyze what's actually running
4. Compare to workspace code

---

## Quick Check

What's the bot path on VPS?

```bash
ssh root@75.119.149.117 "ps aux | grep python | grep -i orchestrator"
```

This shows which file is actually running.
