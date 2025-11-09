#!/bin/bash

echo "================================================================================"
echo "💾 BACKUP VPS STATE BEFORE PULLING NEW CHANGES"
echo "================================================================================"
echo ""

# Create backup directory with timestamp
BACKUP_DIR="VPS_BACKUP_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Created backup directory: $BACKUP_DIR"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  BACKING UP CORE FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Core bot files
for file in \
    COMPLETE_ULTIMATE_ORCHESTRATOR.py \
    EVOLUTION_ENGINE.py \
    IMMORTAL_MEMORY_SYSTEM.py \
    SMART_SCALPING_ENGINE.py \
    ULTRA_RARE_ENGINES.py \
    EXECUTION_ORCHESTRATOR.py \
    CENTRAL_DATA_HUB.py \
    SMART_POSITION_SIZER.py
do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "  ✅ Backed up: $file"
    else
        echo "  ⚠️  Not found: $file"
    fi
done
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  BACKING UP DATABASE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "evolution_engine.db" ]; then
    cp evolution_engine.db "$BACKUP_DIR/"
    DB_SIZE=$(du -h evolution_engine.db | cut -f1)
    DB_ROWS=$(sqlite3 evolution_engine.db "SELECT COUNT(*) FROM model_evolution;" 2>/dev/null || echo "unknown")
    DB_GEN=$(sqlite3 evolution_engine.db "SELECT MAX(generation) FROM model_evolution;" 2>/dev/null || echo "unknown")
    echo "  ✅ Backed up: evolution_engine.db"
    echo "     Size: $DB_SIZE"
    echo "     Rows: $DB_ROWS"
    echo "     Generation: $DB_GEN"
else
    echo "  ⚠️  evolution_engine.db not found"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  BACKING UP LOGS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for log in apex.log nohup.out; do
    if [ -f "$log" ]; then
        cp "$log" "$BACKUP_DIR/"
        echo "  ✅ Backed up: $log"
    fi
done
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  CHECKING GIT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Current branch: $(git branch --show-current)"
echo ""
echo "Uncommitted changes:"
git status -s > "$BACKUP_DIR/git_status.txt"
cat "$BACKUP_DIR/git_status.txt"

# Check if there are uncommitted changes
if [ -s "$BACKUP_DIR/git_status.txt" ]; then
    echo ""
    echo "⚠️  WARNING: You have uncommitted changes!"
    echo "   These will be backed up in the next step."
else
    echo ""
    echo "✅ No uncommitted changes"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  SAVING MODIFIED FILES (VPS-only changes)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get list of modified files
MODIFIED=$(git status -s | grep "^ M" | awk '{print $2}')

if [ -n "$MODIFIED" ]; then
    mkdir -p "$BACKUP_DIR/modified_files"
    echo "$MODIFIED" | while read file; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/modified_files/"
            echo "  ✅ Saved modified: $file"
        fi
    done
    
    # Create a patch of all changes
    git diff > "$BACKUP_DIR/vps_changes.patch"
    echo ""
    echo "  📝 Created patch file: vps_changes.patch"
else
    echo "  ℹ️  No modified files to save"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  CHECKING FOR UNTRACKED FILES (New files on VPS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

UNTRACKED=$(git status -s | grep "^??" | awk '{print $2}')

if [ -n "$UNTRACKED" ]; then
    mkdir -p "$BACKUP_DIR/untracked_files"
    echo "$UNTRACKED" > "$BACKUP_DIR/untracked_files_list.txt"
    
    echo "  Found untracked files:"
    echo "$UNTRACKED" | while read file; do
        # Only backup Python files and important files, skip logs/backups
        if [[ "$file" == *.py ]] || [[ "$file" == *.db ]] || [[ "$file" == *.sh ]]; then
            if [ -f "$file" ]; then
                cp "$file" "$BACKUP_DIR/untracked_files/"
                echo "    ✅ $file"
            fi
        else
            echo "    ⏭️  $file (skipped - not critical)"
        fi
    done
else
    echo "  ℹ️  No untracked files"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  CREATING STATE SNAPSHOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create a comprehensive state file
cat > "$BACKUP_DIR/VPS_STATE.txt" <<EOF
VPS BACKUP SNAPSHOT
===================
Date: $(date)
Directory: $(pwd)
Branch: $(git branch --show-current)
Last Commit: $(git log -1 --oneline)

RUNNING PROCESSES:
$(ps aux | grep -E "python|ORCHESTRATOR" | grep -v grep)

DATABASE STATUS:
$(if [ -f evolution_engine.db ]; then
    echo "Rows: $(sqlite3 evolution_engine.db 'SELECT COUNT(*) FROM model_evolution;' 2>/dev/null)"
    echo "Generation: $(sqlite3 evolution_engine.db 'SELECT MAX(generation) FROM model_evolution;' 2>/dev/null)"
else
    echo "Database not found"
fi)

GIT STATUS:
$(git status)

LAST 20 LOG LINES:
$(tail -20 apex.log 2>/dev/null || tail -20 nohup.out 2>/dev/null || echo "No logs found")
EOF

echo "  ✅ Created state snapshot: VPS_STATE.txt"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  COMPARING WITH BRANCH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Fetching latest branch info..."
git fetch origin continue-from-micro-fix 2>/dev/null

echo ""
echo "Commits on VPS:"
git log --oneline -5

echo ""
echo "Commits on branch (remote):"
git log --oneline -5 origin/continue-from-micro-fix

echo ""
echo "Differences between VPS and branch:"
git diff --name-only origin/continue-from-micro-fix > "$BACKUP_DIR/diff_files.txt"

if [ -s "$BACKUP_DIR/diff_files.txt" ]; then
    cat "$BACKUP_DIR/diff_files.txt"
    echo ""
    echo "⚠️  Your VPS has different files than the branch!"
else
    echo "✅ VPS matches branch (no differences)"
fi
echo ""

echo "================================================================================"
echo "✅ BACKUP COMPLETE!"
echo "================================================================================"
echo ""
echo "📁 Backup saved to: $BACKUP_DIR"
echo ""
echo "📋 WHAT WAS BACKED UP:"
echo "   ✅ All core Python files"
echo "   ✅ Evolution database (with row count)"
echo "   ✅ Log files"
echo "   ✅ Git status"
echo "   ✅ Modified files (VPS changes)"
echo "   ✅ Untracked files"
echo "   ✅ Complete state snapshot"
echo "   ✅ Comparison with branch"
echo ""
echo "💡 REVIEW THE BACKUP:"
echo "   ls -lh $BACKUP_DIR"
echo "   cat $BACKUP_DIR/VPS_STATE.txt"
echo "   cat $BACKUP_DIR/vps_changes.patch"
echo ""
echo "🚨 IMPORTANT: Before pulling new changes, review:"
echo "   1. $BACKUP_DIR/vps_changes.patch - Your VPS-only changes"
echo "   2. $BACKUP_DIR/diff_files.txt - Files that differ from branch"
echo "   3. $BACKUP_DIR/modified_files/ - Your modified versions"
echo ""
echo "✅ NOW SAFE TO: git pull origin continue-from-micro-fix"
echo "   (Your current state is saved in: $BACKUP_DIR)"
echo ""
echo "================================================================================"
