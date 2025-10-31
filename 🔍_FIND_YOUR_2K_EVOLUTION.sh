#!/bin/bash
# Find where your 2k+ evolution data actually is

echo "=========================================="
echo "🔍 SEARCHING FOR YOUR 2K+ EVOLUTION DATA"
echo "=========================================="
echo

cd ~/bot || cd /root/bot

echo "1️⃣  Checking ALL tables in evolution_engine.db..."
sqlite3 evolution_engine.db ".tables" 2>/dev/null
echo

echo "2️⃣  Checking ALL tables content..."
for table in $(sqlite3 evolution_engine.db ".tables" 2>/dev/null | tr ' ' '\n'); do
    count=$(sqlite3 evolution_engine.db "SELECT COUNT(*) FROM $table;" 2>/dev/null)
    echo "  📊 $table: $count rows"
done
echo

echo "3️⃣  Checking history.csv (2.5MB file - might have your data)..."
if [ -f data/history.csv ]; then
    lines=$(wc -l < data/history.csv)
    echo "  📈 history.csv: $lines lines"
    echo "  💾 Size: $(du -sh data/history.csv | cut -f1)"
    echo "  📋 First few lines:"
    head -5 data/history.csv
fi
echo

echo "4️⃣  Checking ALL .db files..."
for db in *.db; do
    if [ -f "$db" ]; then
        echo "  📊 $db:"
        for table in $(sqlite3 "$db" ".tables" 2>/dev/null | tr ' ' '\n'); do
            count=$(sqlite3 "$db" "SELECT COUNT(*) FROM $table;" 2>/dev/null)
            echo "    - $table: $count rows"
        done
        echo
    fi
done

echo "5️⃣  Checking for evolution in other locations..."
grep -r "evolution\|2000\|2k" data/*.csv data/*.json 2>/dev/null | head -5 || echo "  (not found in CSV/JSON)"

echo
echo "6️⃣  Checking pattern_memory.csv..."
if [ -f data/pattern_memory.csv ]; then
    lines=$(wc -l < data/pattern_memory.csv)
    echo "  📈 pattern_memory.csv: $lines patterns"
    head -3 data/pattern_memory.csv
fi

echo
echo "=========================================="
echo "💡 YOUR 2K+ EVOLUTION MIGHT BE:"
echo "=========================================="
echo "1. In history.csv ($(wc -l < data/history.csv 2>/dev/null || echo 0) lines)"
echo "2. In pattern_memory.csv ($(wc -l < data/pattern_memory.csv 2>/dev/null || echo 0) patterns)"
echo "3. In other .db files (check above)"
echo "4. Evolution might refer to trade count, not model evolution"
echo
