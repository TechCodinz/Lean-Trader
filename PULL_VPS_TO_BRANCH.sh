#!/bin/bash
# Pull VPS bot content into a new branch in workspace
# This lets the agent see your REAL working bot and enhance it properly

set -e  # Exit on error

echo "==============================================================================="
echo "📥 PULLING VPS BOT TO NEW BRANCH - Smart Integration Approach"
echo "==============================================================================="
echo ""

# Configuration - YOU NEED TO SET THESE
VPS_IP="${1:-YOUR_VPS_IP}"  # Pass as first argument or edit here
VPS_USER="${2:-root}"        # Pass as second argument or edit here
VPS_BOT_PATH="${3:-~/trading_bot}"  # Pass as third argument or edit here

if [ "$VPS_IP" = "YOUR_VPS_IP" ]; then
    echo "❌ ERROR: Please provide VPS IP address!"
    echo ""
    echo "Usage: bash PULL_VPS_TO_BRANCH.sh <VPS_IP> [VPS_USER] [VPS_BOT_PATH]"
    echo ""
    echo "Example:"
    echo "  bash PULL_VPS_TO_BRANCH.sh 75.119.149.117"
    echo "  bash PULL_VPS_TO_BRANCH.sh 75.119.149.117 root ~/trading_bot"
    echo ""
    exit 1
fi

echo "📋 Configuration:"
echo "   VPS IP: $VPS_IP"
echo "   VPS User: $VPS_USER"
echo "   VPS Bot Path: $VPS_BOT_PATH"
echo ""

# Create branch name with timestamp
BRANCH_NAME="vps-bot-$(date +%Y%m%d-%H%M%S)"
TEMP_DIR="/tmp/vps_bot_pull_$$"

echo "📌 New branch will be: $BRANCH_NAME"
echo ""

# Step 1: Create temporary directory
echo "1️⃣ Creating temporary directory..."
mkdir -p "$TEMP_DIR"
echo "   ✅ Created: $TEMP_DIR"
echo ""

# Step 2: Pull VPS git info first (to see what branch they're on)
echo "2️⃣ Checking VPS git status..."
echo "==============================================================================="
ssh $VPS_USER@$VPS_IP "cd $VPS_BOT_PATH && git branch 2>/dev/null || echo 'Not a git repo'" > "$TEMP_DIR/vps_branch.txt"
ssh $VPS_USER@$VPS_IP "cd $VPS_BOT_PATH && git log --oneline -10 2>/dev/null || echo 'No git history'" > "$TEMP_DIR/vps_commits.txt"
ssh $VPS_USER@$VPS_IP "cd $VPS_BOT_PATH && git status 2>/dev/null || echo 'No git status'" > "$TEMP_DIR/vps_status.txt"

echo "📄 VPS Current Branch:"
cat "$TEMP_DIR/vps_branch.txt"
echo ""
echo "📄 VPS Recent Commits:"
cat "$TEMP_DIR/vps_commits.txt"
echo ""

# Step 3: Pull ALL Python files
echo "3️⃣ Pulling ALL Python files from VPS..."
echo "==============================================================================="
ssh $VPS_USER@$VPS_IP "cd $VPS_BOT_PATH && find . -maxdepth 1 -name '*.py' -type f" | while read file; do
    filename=$(basename "$file")
    echo "   📥 Downloading: $filename"
    scp -q $VPS_USER@$VPS_IP:$VPS_BOT_PATH/"$filename" "$TEMP_DIR/" 2>/dev/null || echo "      ⚠️  Failed to download $filename"
done
echo ""

# Step 4: Pull configuration files
echo "4️⃣ Pulling configuration files..."
echo "==============================================================================="
scp -q $VPS_USER@$VPS_IP:$VPS_BOT_PATH/.env "$TEMP_DIR/VPS.env" 2>/dev/null && echo "   ✅ .env downloaded" || echo "   ⚠️  No .env file"
scp -q $VPS_USER@$VPS_IP:$VPS_BOT_PATH/requirements*.txt "$TEMP_DIR/" 2>/dev/null && echo "   ✅ requirements.txt downloaded" || echo "   ⚠️  No requirements.txt"
scp -q $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*.json "$TEMP_DIR/" 2>/dev/null && echo "   ✅ JSON config files downloaded" || echo "   ⚠️  No JSON files"
echo ""

# Step 5: Pull recent logs (last 200 lines)
echo "5️⃣ Pulling recent bot logs..."
echo "==============================================================================="
ssh $VPS_USER@$VPS_IP "tail -200 $VPS_BOT_PATH/bot.log 2>/dev/null || tail -200 ~/bot.log 2>/dev/null || echo 'No log file found'" > "$TEMP_DIR/VPS_bot.log"
echo "   ✅ Logs saved to VPS_bot.log"
echo ""

# Step 6: Get running process info
echo "6️⃣ Capturing running process information..."
echo "==============================================================================="
ssh $VPS_USER@$VPS_IP "ps aux | grep python | grep -v grep" > "$TEMP_DIR/VPS_running_processes.txt"
ssh $VPS_USER@$VPS_IP "screen -ls 2>&1" > "$TEMP_DIR/VPS_screen_sessions.txt"
echo "   ✅ Process info captured"
echo ""

# Step 7: Get directory structure
echo "7️⃣ Getting VPS directory structure..."
echo "==============================================================================="
ssh $VPS_USER@$VPS_IP "cd $VPS_BOT_PATH && ls -lah" > "$TEMP_DIR/VPS_directory_structure.txt"
echo "   ✅ Directory structure captured"
echo ""

# Step 8: Create comprehensive status file
echo "8️⃣ Creating VPS status report..."
echo "==============================================================================="
cat > "$TEMP_DIR/VPS_STATUS_REPORT.md" << EOF
# VPS BOT STATUS REPORT
**Pulled:** $(date)
**VPS IP:** $VPS_IP
**VPS Path:** $VPS_BOT_PATH

## Current Branch:
\`\`\`
$(cat "$TEMP_DIR/vps_branch.txt")
\`\`\`

## Recent Commits:
\`\`\`
$(cat "$TEMP_DIR/vps_commits.txt")
\`\`\`

## Git Status:
\`\`\`
$(cat "$TEMP_DIR/vps_status.txt")
\`\`\`

## Running Processes:
\`\`\`
$(cat "$TEMP_DIR/VPS_running_processes.txt")
\`\`\`

## Screen Sessions:
\`\`\`
$(cat "$TEMP_DIR/VPS_screen_sessions.txt")
\`\`\`

## Directory Structure:
\`\`\`
$(cat "$TEMP_DIR/VPS_directory_structure.txt")
\`\`\`

## Python Files Found:
\`\`\`
$(cd "$TEMP_DIR" && ls -1 *.py 2>/dev/null || echo "No Python files")
\`\`\`

## Configuration Files:
\`\`\`
$(cd "$TEMP_DIR" && ls -1 *.env *.json *.txt 2>/dev/null | grep -v VPS_ || echo "No config files")
\`\`\`

## Recent Log Activity (Last 50 lines):
\`\`\`
$(tail -50 "$TEMP_DIR/VPS_bot.log")
\`\`\`
EOF
echo "   ✅ Status report created"
echo ""

# Step 9: Count what we pulled
echo "9️⃣ Summary of pulled files..."
echo "==============================================================================="
PY_COUNT=$(find "$TEMP_DIR" -name "*.py" | wc -l)
echo "   📊 Python files: $PY_COUNT"
echo "   📊 Config files: $(find "$TEMP_DIR" -name "*.env" -o -name "*.json" -o -name "requirements*.txt" | wc -l)"
echo "   📊 Log files: $(find "$TEMP_DIR" -name "*.log" | wc -l)"
echo ""

if [ $PY_COUNT -eq 0 ]; then
    echo "❌ ERROR: No Python files found! Check VPS connection."
    echo ""
    echo "Debug info:"
    echo "   SSH command used: ssh $VPS_USER@$VPS_IP"
    echo "   SCP command used: scp $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*.py"
    echo ""
    echo "Try running manually:"
    echo "   ssh $VPS_USER@$VPS_IP 'ls $VPS_BOT_PATH/*.py'"
    exit 1
fi

# Step 10: Create new branch and import files
echo "🔀 Creating new branch: $BRANCH_NAME"
echo "==============================================================================="

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "⚠️  Not in a git repository. Creating new branch anyway..."
    git init
    git add .
    git commit -m "Initial workspace state" 2>/dev/null || true
fi

# Create new branch
git checkout -b "$BRANCH_NAME" 2>/dev/null || {
    echo "⚠️  Branch might already exist, using existing"
    git checkout "$BRANCH_NAME"
}
echo "   ✅ Branch created and checked out"
echo ""

# Step 11: Copy VPS files to workspace
echo "📂 Copying VPS files to workspace..."
echo "==============================================================================="

# Copy Python files (prefix with VPS_ to avoid conflicts)
for file in "$TEMP_DIR"/*.py; do
    if [ -f "$file" ]; then
        basename=$(basename "$file")
        cp "$file" "./VPS_$basename"
        echo "   ✅ Copied: VPS_$basename"
    fi
done

# Copy config files
[ -f "$TEMP_DIR/VPS.env" ] && cp "$TEMP_DIR/VPS.env" ./ && echo "   ✅ Copied: VPS.env"
cp "$TEMP_DIR"/*.txt "$TEMP_DIR"/*.json . 2>/dev/null || true
cp "$TEMP_DIR/VPS_STATUS_REPORT.md" ./ 2>/dev/null || true
echo ""

# Step 12: Create analysis file
echo "📝 Creating VPS analysis file..."
echo "==============================================================================="
cat > VPS_INTEGRATION_ANALYSIS.md << EOF
# VPS BOT INTEGRATION ANALYSIS

**Status:** Ready for agent analysis
**Branch:** $BRANCH_NAME
**Files Pulled:** $PY_COUNT Python files + configs

---

## 🎯 WHAT TO DO NEXT:

### For Agent:
1. ✅ Analyze VPS_STATUS_REPORT.md to understand current setup
2. ✅ Check VPS_*.py files to see actual running code
3. ✅ Review VPS_bot.log to see recent activity
4. ✅ Identify which files are main orchestrators
5. ✅ Determine which engines are actually active
6. ✅ Create enhancements that integrate with THIS code
7. ✅ Test enhancements in this branch
8. ✅ Create deployment script for VPS

### Key Files to Check:
- **VPS_STATUS_REPORT.md** - Complete VPS status
- **VPS.env** - Current configuration
- **VPS_bot.log** - Recent activity
- **VPS_running_processes.txt** - What's actually running
- **VPS_*ORCHESTRATOR*.py** - Main bot files
- **VPS_*PROFIT*.py** - Profit engines
- **VPS_*SCALP*.py** - Scalping engines

---

## 📊 VPS SNAPSHOT:

$(cat VPS_STATUS_REPORT.md)

---

## 🔄 NEXT STEPS:

Once agent analyzes this branch:
1. Agent will identify what's working
2. Agent will create targeted enhancements
3. Agent will test in this branch
4. Agent will provide deployment script
5. Deploy to VPS with one command

---

**All VPS files are now in this branch for analysis!**
EOF
echo "   ✅ Created: VPS_INTEGRATION_ANALYSIS.md"
echo ""

# Step 13: Git commit
echo "💾 Committing VPS snapshot to branch..."
echo "==============================================================================="
git add .
git commit -m "VPS bot snapshot from $VPS_IP - $(date)" 2>/dev/null || echo "   ⚠️  Nothing new to commit"
echo ""

# Step 14: Cleanup
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"
echo "   ✅ Cleanup complete"
echo ""

# Step 15: Final summary
echo "==============================================================================="
echo "✅ VPS BOT SUCCESSFULLY PULLED TO BRANCH"
echo "==============================================================================="
echo ""
echo "📌 Branch: $BRANCH_NAME"
echo "📊 Files pulled: $PY_COUNT Python files + configs"
echo ""
echo "📁 Key files in workspace:"
ls -1 VPS_* | head -10
echo ""
echo "==============================================================================="
echo "🎯 NEXT STEPS:"
echo "==============================================================================="
echo ""
echo "1. ✅ Check VPS_STATUS_REPORT.md to see complete VPS state"
echo "2. ✅ Review VPS_*.py files to see your actual code"
echo "3. ✅ Check VPS_bot.log to see recent activity"
echo "4. ✅ Agent will now analyze and create targeted enhancements"
echo "5. ✅ Deploy back to VPS with one command"
echo ""
echo "📖 Read: VPS_INTEGRATION_ANALYSIS.md for detailed info"
echo ""
echo "==============================================================================="
echo "🤖 AGENT: You can now analyze the VPS bot directly in this branch!"
echo "==============================================================================="
