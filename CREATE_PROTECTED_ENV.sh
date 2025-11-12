#!/bin/bash
##############################################################################
# CREATE PROTECTED .ENV - Won't get wiped!
##############################################################################

# 1. Remove read-only if set
chmod 644 .env 2>/dev/null

# 2. Create complete .env
cat > .env << 'EOF'
# Telegram
TELEGRAM_BOT_TOKEN=8291641352:AAFTGq-hIY_iS47aMOoGXrBDFlR_B3nCupg
VIP_CHANNEL_ID=-1002983007302
FREE_CHANNEL_ID=-1002930953007
TELEGRAM_FREE_CHANNEL=-1002930953007

# TESTNET MODE
TRADING_MODE=testnet
BYBIT_TESTNET=true
ENABLE_LIVE=false

# Bybit TESTNET
BYBIT_TESTNET_API_KEY=N8BMgWdfisCtkvfZk8
BYBIT_TESTNET_API_SECRET=BIu7c65FQnDsd6kBmctU7gK9bBbzY15vi8oe

# Bybit LIVE
BYBIT_API_KEY=mMHs7rDC72TvHs4oQG
BYBIT_API_SECRET=NwTa6UOgczdmZI2Kn2WBcFfh5r6VkVGnvGEI

# Gate.io
GATE_API_KEY=a0508d8aadf3bcb76e16f4373e1f3a76
GATE_API_SECRET=451770a07dbede1b87bb92f5ce98e24029d2fe91e0053be2ec41771c953113f9

# AI APIs - ADD YOUR KEYS HERE!
ANTHROPIC_API_KEY=sk-ant-your-claude-key-here
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-gemini-key-here
GROK_API_KEY=your-grok-key-here
XAI_API_KEY=your-xai-key-here

# AI Settings
AI_BUDGET_DAILY=10.0
AI_RATE_LIMIT_PER_MIN=20
AI_DEBATE_ROUNDS=3

# Trading Limits
MAX_POSITION_SIZE=10
MAX_DAILY_TRADES=999999
MAX_OPEN_POSITIONS=999999
MIN_CONFIDENCE=0.65
EOF

# 3. Make it READ-ONLY (protected from overwrites!)
chmod 444 .env

echo "✅ .env created with ALL keys!"
echo "✅ Protected (read-only)!"
echo ""
echo "To add your AI keys:"
echo "chmod 644 .env"
echo "nano .env"
echo "# Add your keys, then:"
echo "chmod 444 .env"
