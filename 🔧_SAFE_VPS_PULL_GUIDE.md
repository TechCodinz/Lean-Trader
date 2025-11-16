# 🔧 SAFE VPS PULL GUIDE - NO DATA LOSS!

**⚠️ IMPORTANT: NEVER use `git reset --hard` - it wipes the venv!**

---

## 📋 STEP 1: Check VPS Status (Run on VPS)

```bash
# Navigate to bot directory
cd ~/apex_bot

# Check current branch
git branch

# Check current status
git status

# See last 3 commits
git log --oneline -3

# Check for uncommitted changes
git diff --stat
```

**📝 Note the outputs above before proceeding!**

---

## 🔍 STEP 2: Identify Current Branch

The VPS bot is likely on one of these branches:
- `main`
- `master`  
- `cursor/fix-and-enhance-autonomous-trading-systems-6f74` (our new branch)
- Other custom branch

**⚠️ DO NOT PROCEED until you know the branch name!**

---

## 💾 STEP 3: Backup Current State (SAFETY FIRST!)

```bash
cd ~/apex_bot

# Create backup of current state
git stash push -m "Backup before pull $(date +%Y%m%d_%H%M%S)"

# OR if you have uncommitted changes you want to keep:
git add -A
git commit -m "VPS state backup before pull"

# Verify backup
git stash list
# OR
git log --oneline -1
```

---

## 🔄 STEP 4: Safe Pull Options

### Option A: If on SAME branch as workspace

```bash
cd ~/apex_bot

# Check your branch
git branch

# If it shows: cursor/fix-and-enhance-autonomous-trading-systems-6f74
# Then safely pull:
git pull origin cursor/fix-and-enhance-autonomous-trading-systems-6f74

# Check what was updated
git log --oneline -10
```

### Option B: If on DIFFERENT branch (e.g., main or master)

```bash
cd ~/apex_bot

# Fetch all branches first
git fetch --all

# Check available branches
git branch -a

# Option B1: Merge our fixes into your current branch
git merge origin/cursor/fix-and-enhance-autonomous-trading-systems-6f74

# Option B2: Switch to our branch (if you want all our features)
git checkout -b cursor/fix-and-enhance-autonomous-trading-systems-6f74 origin/cursor/fix-and-enhance-autonomous-trading-systems-6f74
```

### Option C: If you have merge conflicts

```bash
cd ~/apex_bot

# Pull with rebase (safer than reset)
git pull --rebase origin cursor/fix-and-enhance-autonomous-trading-systems-6f74

# If conflicts occur:
# 1. Edit the conflicted files
# 2. git add <file>
# 3. git rebase --continue

# OR abort if too complex:
git rebase --abort
```

---

## 🧪 STEP 5: Verify Everything Still Works

```bash
cd ~/apex_bot

# Check Python/venv still intact
source apex_venv/bin/activate
python3 --version

# Check new files exist
ls -la AI_CONSULTATION_SERVICE.py
ls -la INTELLIGENT_BALANCE_MANAGER.py
ls -la ULTIMATE_AUTONOMOUS_INTELLIGENCE.py

# Test integration
python3 COMPLETE_INTEGRATION_TEST.py

# Check .env still exists
ls -la systems/.env
```

---

## 🚀 STEP 6: Restart Bot with New Features

```bash
cd ~/apex_bot
source apex_venv/bin/activate

# Option 1: Easy start
bash ⚡_START_BOT_NOW.sh

# Option 2: Manual start
cd systems
python3 RUN_BOT.py --testnet
```

---

## 🤖 STEP 7: Configure Multiple AI Providers (Optional)

Add to `systems/.env`:

```bash
# Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-your_key_here

# GPT-4 (OpenAI)  
OPENAI_API_KEY=sk-your_openai_key_here

# Grok (xAI)
GROK_API_KEY=your_grok_key_here
GROK_ENDPOINT=https://api.x.ai/v1/chat/completions

# Raiziom (Your personal AI)
RAIZIOM_API_KEY=your_raiziom_key_here
RAIZIOM_ENDPOINT=https://your-raiziom-endpoint.com/api/chat

# Custom AI
CUSTOM_AI_API_KEY=your_custom_key
CUSTOM_AI_ENDPOINT=https://your-custom-ai.com/api

# Auto-select best available (default)
AI_PROVIDER=auto

# OR force specific provider
# AI_PROVIDER=claude
# AI_PROVIDER=gpt4
# AI_PROVIDER=grok
# AI_PROVIDER=raiziom
```

Bot will automatically use the best available AI provider!

---

## 🆘 IF SOMETHING GOES WRONG

### Rollback to Previous State

```bash
cd ~/apex_bot

# If you used git stash:
git stash pop

# If you made a commit:
git log --oneline -5
# Find your backup commit hash
git reset --soft <commit_hash>

# If you need to go back completely:
git reflog  # Find where you were
git checkout <commit_hash>
```

### Restore venv if damaged

```bash
cd ~/apex_bot

# Check if venv is damaged
source apex_venv/bin/activate

# If it fails, DON'T recreate! Fix it:
python3 -m venv --upgrade apex_venv
source apex_venv/bin/activate
pip install -r requirements.txt
```

---

## ✅ SAFE COMMANDS SUMMARY

**✅ SAFE:**
- `git pull origin <branch>`
- `git pull --rebase`
- `git merge origin/<branch>`
- `git stash`
- `git fetch --all`
- `git checkout -b <new_branch>`

**❌ DANGEROUS:**
- `git reset --hard` ← **NEVER USE! Wipes venv!**
- `git clean -fdx` ← **Deletes untracked files!**
- `rm -rf apex_venv` ← **Destroys months of work!**

---

## 📞 WHAT TO TELL ME

After running STEP 1, tell me:

1. **Current branch:** `git branch` output
2. **Last commits:** `git log --oneline -3` output
3. **Any changes:** `git status` output

Then I'll give you the EXACT safe commands for your situation!

---

## 🎯 NEW FEATURES YOU'LL GET

After pulling:
- ✅ AI Consultation Service (Claude, GPT-4, Grok, Raiziom support!)
- ✅ Intelligent Balance Manager (NO more insufficient balance!)
- ✅ Ultimate Autonomous Intelligence (1-20 dynamic trades!)
- ✅ Autonomous Master Coordinator (all systems work together!)

All tested and working! 🎉
