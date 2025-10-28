#!/bin/bash
# Quick command to pull VPS bot - will try common paths

VPS_IP="75.119.149.117"
VPS_USER="root"

echo "🔍 Finding bot on VPS..."
echo ""

# Try common paths
PATHS=(
    "/root/trading_bot"
    "/home/root/trading_bot"
    "/root/trading-bot"
    "/home/ubuntu/trading_bot"
    "/opt/trading_bot"
)

echo "Testing SSH connection..."
ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_IP" "echo '✅ SSH Connected'" || {
    echo "❌ Cannot connect to VPS"
    echo "Please check:"
    echo "  - VPS IP: $VPS_IP"
    echo "  - SSH key or password"
    exit 1
}

echo ""
echo "🔍 Searching for bot directory on VPS..."
for path in "${PATHS[@]}"; do
    if ssh "$VPS_USER@$VPS_IP" "[ -d '$path' ]" 2>/dev/null; then
        echo "✅ Found bot at: $path"
        VPS_PATH="$path"
        break
    fi
done

if [ -z "$VPS_PATH" ]; then
    echo ""
    echo "❌ Bot not found in common locations"
    echo "Checking all directories..."
    ssh "$VPS_USER@$VPS_IP" "find /root /home /opt -maxdepth 3 -name '*.py' -path '*trading*' -o -name 'COMPLETE_ULTIMATE_ORCHESTRATOR.py' 2>/dev/null | head -20"
    echo ""
    echo "Please update VPS_PATH in the script with the correct path"
    exit 1
fi

echo ""
echo "🎯 Bot found! Pulling from: $VPS_PATH"
echo ""

# Now run the full pull script with the found path
sed -i "s|VPS_PATH=\".*\"|VPS_PATH=\"$VPS_PATH\"|" /workspace/PULL_VPS_BOT.sh
bash /workspace/PULL_VPS_BOT.sh
