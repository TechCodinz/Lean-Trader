# 🎯 Commands to Pull Working Bot from VPS

## Quick Start (Recommended)

Just run this one command:

```bash
bash /workspace/QUICK_VPS_PULL.sh
```

This will:
1. ✅ Auto-detect where the bot is on VPS
2. ✅ Create a new branch with timestamp
3. ✅ Pull all VPS files to workspace
4. ✅ Commit everything so you can compare

---

## Manual Pull (If Quick Start Fails)

### Step 1: Find the bot on VPS

```bash
ssh root@75.119.149.117 "find /root /home -name 'COMPLETE_ULTIMATE_ORCHESTRATOR.py' 2>/dev/null"
```

### Step 2: Pull files

Once you know the path (e.g., `/root/trading_bot`), run:

```bash
# Create new branch
cd /workspace
git checkout -b vps-live-bot-$(date +%Y%m%d-%H%M)

# Pull files from VPS
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    root@75.119.149.117:/root/trading_bot/ \
    /workspace/

# Commit the VPS snapshot
git add -A
git commit -m "feat: Pull live working bot from VPS"
```

---

## Alternative: Use Existing VPS Snapshot

There's already a VPS snapshot branch from Oct 28:

```bash
cd /workspace
git checkout -b analyze-vps-bot origin/vps-working-snapshot-20251028-0402
```

---

## After Pulling

Compare workspace vs VPS code:

```bash
# See what's different
git diff main HEAD

# See which files changed
git diff main HEAD --name-only

# Compare specific file
git diff main HEAD -- COMPLETE_ULTIMATE_ORCHESTRATOR.py
```

---

## VPS Info

- **IP**: 75.119.149.117
- **User**: root
- **Likely Paths**:
  - `/root/trading_bot`
  - `/home/root/trading_bot`
  - `/opt/trading_bot`

---

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH
ssh root@75.119.149.117 "echo 'Connection OK'"

# If permission denied, check SSH key
ssh -v root@75.119.149.117
```

### Can't Find Bot

```bash
# Search for bot files
ssh root@75.119.149.117 "find / -name 'COMPLETE_ULTIMATE_ORCHESTRATOR.py' 2>/dev/null"

# List running Python processes
ssh root@75.119.149.117 "ps aux | grep python"

# Check screen/tmux sessions
ssh root@75.119.149.117 "screen -ls"
```

---

## What to Look For After Pull

1. **Which orchestrator is running?**
   - COMPLETE_ULTIMATE_ORCHESTRATOR.py
   - MICRO_WALLET_GROWER.py
   - RUN_BOT.py

2. **What's different?**
   - Compare imports
   - Check which engines are initialized
   - Look for configuration differences

3. **Environment variables**
   - Compare .env files
   - Check API keys
   - Verify exchange settings

---

**Ready?** Run: `bash /workspace/QUICK_VPS_PULL.sh`
