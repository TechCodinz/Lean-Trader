#!/bin/bash
# Deploy Complete Ultimate Orchestrator to VPS

echo "🚀 DEPLOYING COMPLETE ULTIMATE ORCHESTRATOR TO VPS"
echo "=================================================="

# Stop any running bot
echo "🛑 Stopping current bot..."
pkill -f RUN_BOT.py || true
sleep 2

# Test the integration
echo "🧪 Testing integration..."
python3 test_integration.py

if [ $? -eq 0 ]; then
    echo "✅ Integration test passed!"
    
    # Start the bot
    echo "🚀 Starting bot with complete integration..."
    nohup python3 RUN_BOT.py --testnet --auto-confirm > bot.log 2>&1 &
    
    # Wait a moment
    sleep 5
    
    # Check if bot is running
    if ps aux | grep RUN_BOT.py | grep -v grep > /dev/null; then
        echo "✅ Bot is running successfully!"
        echo "📊 Bot process:"
        ps aux | grep RUN_BOT.py | grep -v grep
        
        echo "🔍 Recent logs:"
        tail -20 bot.log | grep -E "(ULTRA|QUANTUM|SWARM|FLUID|ARBITRAGE|SCALPING|MOON|ML|TRADE|BOT|UNIFIED|WIRING|INITIALIZING)"
        
        echo ""
        echo "🎉 DEPLOYMENT COMPLETE!"
        echo "   Bot is running with all systems integrated"
        echo "   Monitor with: tail -f bot.log"
        echo "   Stop with: pkill -f RUN_BOT.py"
    else
        echo "❌ Bot failed to start!"
        echo "📋 Error logs:"
        tail -20 bot.log
    fi
else
    echo "❌ Integration test failed!"
    echo "📋 Check the errors above"
fi