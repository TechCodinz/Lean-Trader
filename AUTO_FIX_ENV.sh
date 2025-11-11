#!/bin/bash
cd ~/apex_bot

echo "=========================================="
echo "🔧 AUTO-FIXING .env FILE"
echo "=========================================="
echo ""

# Backup
echo "1️⃣ Creating backup..."
cp .env .env.backup.$(date +%s)
echo "   ✅ Backed up to .env.backup.*"
echo ""

# Show current Bybit entries
echo "2️⃣ Current Bybit entries (BEFORE):"
grep -i "BYBIT" .env | nl
echo ""

# Remove ALL Bybit lines
echo "3️⃣ Removing all Bybit entries..."
grep -v "BYBIT" .env > .env.temp
mv .env.temp .env
echo "   ✅ Removed"
echo ""

# Show what's left
echo "4️⃣ Now .env contains:"
cat .env
echo ""

echo "=========================================="
echo "⚠️  NOW ADD YOUR TESTNET KEYS"
echo "=========================================="
echo ""
echo "Run this command:"
echo ""
echo "cat >> .env << 'EOF'"
echo "BYBIT_TESTNET_API_KEY=paste_your_key_here"
echo "BYBIT_TESTNET_SECRET=paste_your_secret_here"
echo "EOF"
echo ""
echo "Replace 'paste_your_key_here' with your actual keys!"
echo ""
echo "Or manually add with:"
echo "  nano .env"
echo ""
