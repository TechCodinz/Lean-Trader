#!/usr/bin/env bash
#
# ⚡ FINAL CLEAN DEPLOYMENT ⚡
# ONE script that fixes everything
# Tested in workspace, ready for VPS
#

set -e

echo "=" | tr -d '\n' | head -c 80; echo
echo "⚡ FINAL CLEAN DEPLOYMENT - ALL APEX ENHANCEMENTS ⚡"
echo "=" | tr -d '\n' | head -c 80; echo
echo ""

cd ~/bot || { echo "❌ ~/bot not found"; exit 1; }

# BACKUP EVERYTHING
echo "📦 Creating backup..."
BACKUP="backup_final_clean_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP"
cp *.py "$BACKUP/" 2>/dev/null || true
cp .env "$BACKUP/" 2>/dev/null || true
echo "✅ Full backup: $BACKUP"
echo ""

# RESTORE CLEAN EXECUTION_ORCHESTRATOR (from git if available)
echo "🔧 Restoring clean EXECUTION_ORCHESTRATOR.py..."
if git show HEAD:EXECUTION_ORCHESTRATOR.py > EXECUTION_ORCHESTRATOR.py 2>/dev/null; then
    echo "✅ Restored from git"
else
    # Use oldest backup (most likely clean)
    OLDEST=$(ls -t backup_*/EXECUTION_ORCHESTRATOR.py 2>/dev/null | tail -1)
    if [ -n "$OLDEST" ]; then
        cp "$OLDEST" EXECUTION_ORCHESTRATOR.py
        echo "✅ Restored from backup: $(dirname $OLDEST)"
    else
        echo "⚠️ No clean version found - will work with current"
    fi
fi

# Test syntax
python3 -m py_compile EXECUTION_ORCHESTRATOR.py 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ EXECUTION_ORCHESTRATOR still broken - using fallback"
    
    # Create minimal working executor
    cat > EXECUTION_ORCHESTRATOR.py << 'MINIMAL_EXEC'
#!/usr/bin/env python3
"""Minimal working executor"""
import asyncio
import logging

logger = logging.getLogger(__name__)

class ExecutionOrchestrator:
    def __init__(self, exchange, initial_balance=0):
        self.exchange = exchange
        self.balance = initial_balance
        logger.info("⚡ Execution Orchestrator initialized")
    
    async def execute_trade(self, signal):
        """Minimal executor that works"""
        try:
            symbol = signal.get('symbol', 'UNKNOWN')
            side = signal.get('side', 'buy').lower()
            
            # Get balance
            bal = await asyncio.to_thread(self.exchange.fetch_balance)
            usdt = bal.get('USDT', {}).get('free', 0)
            
            if usdt < 3.0:
                logger.warning(f"Balance too low: ${usdt:.2f}")
                return None
            
            # Safe position: 30%
            position = usdt * 0.30
            position = max(3.0, min(position, usdt * 0.95))
            
            # Get price and quantity
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            price = ticker['last']
            quantity = position / price
            
            logger.info(f"⚡ EXECUTING: {side.upper()} {quantity:.6f} {symbol} (${position:.2f})")
            
            order = await asyncio.to_thread(
                self.exchange.create_market_order,
                symbol, side, quantity
            )
            
            logger.info(f"✅ EXECUTED: {order.get('id')}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Execution failed: {e}")
            return None

__all__ = ['ExecutionOrchestrator']
MINIMAL_EXEC
    
    echo "✅ Created minimal working executor"
fi

echo ""

# CREATE AUTO-ADAPTIVE APEX (clean version)
echo "⚡ Creating Auto-Adaptive APEX..."
cat > AUTO_ADAPTIVE_APEX.py << 'APEX_CLEAN'
#!/usr/bin/env python3
"""⚡ AUTO-ADAPTIVE APEX - Auto-adjusts to balance"""
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AutoAdaptiveApex:
    def __init__(self, exchange):
        self.exchange = exchange
        self.current_balance = 0.0
        self.starting_balance = 0.0
        self.current_tier = None
        
        self.tiers = {
            'nano': {'min': 0, 'max': 5, 'risk': 0.95, 'target': 0.025},
            'micro': {'min': 5, 'max': 50, 'risk': 0.90, 'target': 0.020},
            'small': {'min': 50, 'max': 200, 'risk': 0.80, 'target': 0.015},
            'medium': {'min': 200, 'max': 1000, 'risk': 0.70, 'target': 0.012},
            'large': {'min': 1000, 'max': float('inf'), 'risk': 0.60, 'target': 0.010}
        }
        
        logger.info("⚡ AUTO-ADAPTIVE APEX loaded - Balance-aware trading!")
    
    async def get_balance(self):
        try:
            bal = await asyncio.to_thread(self.exchange.fetch_balance)
            usdt = bal.get('USDT', {}).get('total', 0.0)
            
            if self.starting_balance == 0:
                self.starting_balance = usdt
                logger.info(f"💰 Starting balance: ${usdt:.2f}")
            
            self.current_balance = usdt
            return usdt
        except:
            return self.current_balance
    
    def get_tier(self, balance):
        for name, cfg in self.tiers.items():
            if cfg['min'] <= balance < cfg['max']:
                if self.current_tier != name:
                    if self.current_tier:
                        logger.info(f"🎉 TIER: {self.current_tier.upper()} → {name.upper()} (${balance:.2f})")
                    self.current_tier = name
                return name, cfg
        return 'large', self.tiers['large']
    
    async def optimize(self, signal: Dict) -> Optional[Dict]:
        balance = await self.get_balance()
        
        if balance < 3.0:
            return None
        
        tier_name, tier = self.get_tier(balance)
        
        if signal.get('confidence', 0) < 0.75:
            return None
        
        pos = balance * tier['risk']
        pos = max(3.0, min(pos, balance * 0.95))
        
        exp_profit = pos * tier['target']
        fees = pos * 0.004
        
        if exp_profit <= fees * 1.5:
            return None
        
        logger.info(f"✅ APEX: {signal.get('symbol')} | {tier_name.upper()} | ${pos:.2f} → ${exp_profit:.2f}")
        
        return {
            'position_size': pos,
            'target_profit_pct': tier['target'],
            'stop_loss_pct': tier['target'] * 0.6,
            'expected_profit': exp_profit
        }

apex = None

def init_auto_apex(exchange):
    global apex
    apex = AutoAdaptiveApex(exchange)
    return apex

def get_auto_apex():
    return apex

__all__ = ['AutoAdaptiveApex', 'init_auto_apex', 'get_auto_apex']
APEX_CLEAN

echo "✅ Created AUTO_ADAPTIVE_APEX.py"
echo ""

# Test compilation
echo "🧪 Testing Python syntax..."
python3 -m py_compile AUTO_ADAPTIVE_APEX.py
python3 -m py_compile EXECUTION_ORCHESTRATOR.py

if [ $? -eq 0 ]; then
    echo "✅ All files compile successfully!"
    echo ""
    
    # Restart bot
    echo "🔄 Restarting bot with clean code..."
    pkill -f "COMPLETE_ULTIMATE_ORCHESTRATOR.py" || true
    sleep 2
    
    nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
    BOT_PID=$!
    
    sleep 5
    
    if ps -p $BOT_PID > /dev/null 2>&1; then
        echo "✅ BOT IS RUNNING!"
        echo ""
        echo "📊 Recent log:"
        tail -20 bot.log
        echo ""
        echo "📈 Monitor: tail -f bot.log"
    else
        echo "❌ Bot crashed:"
        tail -50 bot.log
    fi
else
    echo "❌ Compilation failed"
fi
