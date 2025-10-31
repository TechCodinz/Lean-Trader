#!/bin/bash
# Quick check if learned data survived venv deletion

echo "=========================================="
echo "🔍 CHECKING IF LEARNED DATA SURVIVED"
echo "=========================================="
echo

cd ~/bot || cd /root/bot || cd /workspace || pwd

echo "1️⃣  Checking evolution database..."
if [ -f evolution_engine.db ]; then
    echo "  ✅ evolution_engine.db EXISTS"
    echo "  📊 Evolution count:"
    sqlite3 evolution_engine.db "SELECT COUNT(*) FROM model_evolution;" 2>/dev/null || echo "    (table may be empty or not created yet)"
else
    echo "  ❌ evolution_engine.db NOT FOUND"
fi

echo
echo "2️⃣  Checking data directory..."
if [ -d data ]; then
    echo "  ✅ data/ EXISTS"
    echo "  📁 Files in data/:"
    ls -lh data/ | head -10
    echo "  💾 Size: $(du -sh data/ | cut -f1)"
else
    echo "  ❌ data/ NOT FOUND"
fi

echo
echo "3️⃣  Checking models directory..."
if [ -d models ]; then
    echo "  ✅ models/ EXISTS"
    echo "  💾 Size: $(du -sh models/ | cut -f1)"
    ls -lh models/ | head -5
else
    echo "  ⚠️  models/ NOT FOUND (may be empty, that's OK)"
fi

echo
echo "4️⃣  Checking runtime directory..."
if [ -d runtime ]; then
    echo "  ✅ runtime/ EXISTS"
    echo "  💾 Size: $(du -sh runtime/ | cut -f1)"
else
    echo "  ⚠️  runtime/ NOT FOUND (may be empty, that's OK)"
fi

echo
echo "5️⃣  Checking all .db files..."
for db in *.db; do
    if [ -f "$db" ]; then
        echo "  ✅ $db ($(du -sh "$db" | cut -f1))"
    fi
done

echo
echo "=========================================="
echo "📊 SUMMARY:"
echo "=========================================="

if [ -f evolution_engine.db ] && [ -d data ]; then
    echo "✅ YOUR LEARNED DATA SURVIVED VENV DELETION!"
    echo "   → Evolution database exists"
    echo "   → Data directory exists"
    echo "   → Just reinstall Python packages (venv)"
    echo
    echo "💡 To restore:"
    echo "   1. git checkout correct branch"
    echo "   2. python3 -m venv .venv"
    echo "   3. source .venv/bin/activate"
    echo "   4. pip install [dependencies]"
    echo "   5. python3 RUN_BOT.py --live"
    echo "   → Bot will load your learned data automatically!"
else
    echo "❌ LEARNED DATA NOT FOUND"
    echo "   → May have been stored inside venv (unusual)"
    echo "   → Or bot hasn't run yet (data gets created on first run)"
fi

echo