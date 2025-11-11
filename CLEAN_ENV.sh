#!/bin/bash
cd ~/apex_bot

echo "=========================================="
echo "🔧 CLEANING .env FILE"
echo "=========================================="
echo ""

echo "1️⃣ Backing up current .env..."
cp .env .env.backup.$(date +%s)
echo "   ✅ Backup created"
echo ""

echo "2️⃣ Current Bybit entries:"
grep -i "BYBIT" .env
echo ""

echo "3️⃣ Correct format needed:"
echo ""
echo "# Bybit Testnet (only 2 lines needed!)"
echo "BYBIT_TESTNET_API_KEY=your_key_here"
echo "BYBIT_TESTNET_SECRET=your_secret_here"
echo ""

echo "=========================================="
echo "⚠️  MANUAL FIX REQUIRED"
echo "=========================================="
echo ""
echo "Run this command:"
echo ""
echo "nano .env"
echo ""
echo "Then:"
echo "1. Find all lines starting with BYBIT"
echo "2. DELETE all of them"
echo "3. Add only these 2 lines:"
echo ""
echo "   BYBIT_TESTNET_API_KEY=paste_your_key_here"
echo "   BYBIT_TESTNET_SECRET=paste_your_secret_here"
echo ""
echo "4. Save: Ctrl+O, Enter, Ctrl+X"
echo ""
echo "=========================================="
echo "✅ After fixing, run:"
echo "=========================================="
echo ""
echo "bash FIX_BYBIT_TESTNET.sh"
echo ""
