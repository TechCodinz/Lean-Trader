#!/bin/bash
# Simple version - just provide VPS IP and it does everything

echo "==============================================================================="
echo "📥 SIMPLE VPS PULL - One Command Solution"
echo "==============================================================================="
echo ""

# Get VPS IP from user
if [ -z "$1" ]; then
    echo "Please provide your VPS IP address:"
    read VPS_IP
else
    VPS_IP="$1"
fi

if [ -z "$VPS_IP" ]; then
    echo "❌ ERROR: VPS IP required!"
    exit 1
fi

echo "🔗 Connecting to: $VPS_IP"
echo ""

# Run the full pull
bash PULL_VPS_TO_BRANCH.sh "$VPS_IP" root ~/trading_bot

echo ""
echo "==============================================================================="
echo "✅ DONE! Your VPS bot is now in a new branch."
echo "==============================================================================="
echo ""
echo "Check these files:"
echo "  - VPS_STATUS_REPORT.md (complete VPS status)"
echo "  - VPS_INTEGRATION_ANALYSIS.md (what to do next)"
echo "  - VPS_*.py (your actual running code)"
echo ""
