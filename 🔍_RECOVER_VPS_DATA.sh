#!/bin/bash
# Recover learned data (2k+ evolution) from VPS

echo "=========================================="
echo "🔍 RECOVERING LEARNED DATA FROM VPS"
echo "=========================================="
echo
echo "⚠️  IMPORTANT: Learned data (evolution, patterns, models) is stored"
echo "   in data/, models/, runtime/ directories - NOT in git!"
echo
echo "📍 Check if VPS still has the learned data:"
echo

# Commands to run ON VPS to check for learned data
cat << 'EOF'
# Run these commands ON YOUR VPS:

cd ~/bot || cd /root/bot

echo "📁 Checking for learned data directories..."
ls -la | grep -E "^d.*data|^d.*models|^d.*runtime"

echo
echo "📊 Checking for evolution databases..."
find . -name "*evolution*.db" -o -name "*.db" | head -20

echo
echo "📈 Checking evolution count in databases..."
for db in $(find . -name "*evolution*.db" 2>/dev/null); do
    echo "  Checking: $db"
    sqlite3 "$db" "SELECT COUNT(*) FROM model_evolution;" 2>/dev/null || echo "    No model_evolution table"
done

echo
echo "💾 Size of data directories:"
du -sh data/ models/ runtime/ 2>/dev/null || echo "  Directories not found"

echo
echo "📋 Files in data/ (learned patterns):"
ls -lh data/ 2>/dev/null | head -20 || echo "  No data/ directory"

echo
echo "📋 Files in models/ (learned weights):"
ls -lh models/ 2>/dev/null | head -20 || echo "  No models/ directory"

EOF

echo
echo "=========================================="
echo "💾 TO BACKUP LEARNED DATA FROM VPS:"
echo "=========================================="
echo
cat << 'EOF'
# On VPS, create backup:
cd ~/bot || cd /root/bot
tar -czf learned_data_backup_$(date +%Y%m%d).tar.gz \
    data/ models/ runtime/ \
    *.db \
    --exclude='__pycache__' \
    --exclude='*.pyc'

# Then download to local (if needed):
# scp user@vps:~/bot/learned_data_backup_*.tar.gz ./
EOF

echo
echo "=========================================="
echo "🔄 TO RESTORE LEARNED DATA:"
echo "=========================================="
echo
cat << 'EOF'
# Extract backup:
cd ~/bot || cd /root/bot
tar -xzf learned_data_backup_YYYYMMDD.tar.gz

# Or copy from old venv if it still exists:
# cp -r /path/to/old/venv/data ./data
# cp -r /path/to/old/venv/models ./models
# cp -r /path/to/old/venv/runtime ./runtime
EOF

echo