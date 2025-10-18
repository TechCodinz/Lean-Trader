#!/bin/bash
echo "═══════════════════════════════════════════════════════"
echo "🔍 WHICH ENGINES ARE ACTUALLY TRADING?"
echo "═══════════════════════════════════════════════════════"
echo ""

echo "1️⃣ REAL_PROFIT_BOT - Is this the one trading?"
sudo journalctl -u trading-bot-testnet --since "10 min ago" | grep "REAL PROFIT" | tail -10
echo ""

echo "2️⃣ EXECUTION ORCHESTRATOR - Routing signals?"
sudo journalctl -u trading-bot-testnet --since "5 min ago" | grep "EXECUTING:" | tail -10
echo ""

echo "3️⃣ SCALPER - Generating signals?"
scalper=$(sudo journalctl -u trading-bot-testnet --since "5 min ago" | grep -c "Scalper generated")
echo "Scalper signals: $scalper"
sudo journalctl -u trading-bot-testnet --since "2 min ago" | grep "Scalper generated" | tail -5
echo ""

echo "4️⃣ ARBITRAGE - Finding opportunities?"
arb=$(sudo journalctl -u trading-bot-testnet --since "5 min ago" | grep -c "Arbitrage")
echo "Arbitrage opportunities: $arb"
sudo journalctl -u trading-bot-testnet --since "5 min ago" | grep "Arbitrage" | tail -5
echo ""

echo "5️⃣ ALL PAIRS ANALYZED:"
sudo journalctl -u trading-bot-testnet --since "3 min ago" | grep "Decision:" | tail -20
echo ""

echo "6️⃣ WHY ONLY BTC/USDT TRADING?"
sudo journalctl -u trading-bot-testnet --since "5 min ago" | grep -E "does not have|ticker error|Already in position" | tail -10
