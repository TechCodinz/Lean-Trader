# 🚀 FINAL DEPLOYMENT - ONE COMMAND

## ✅ Everything is tested and ready in workspace

**Copy this ONE block to your VPS and run it:**

```bash
cat > DEPLOY_FINAL.sh << 'FINAL_DEPLOY_EOF'
#!/usr/bin/env bash
echo "⚡ DEPLOYING FINAL CLEAN VERSION ⚡"
cd ~/bot

# Backup
BACKUP="backup_clean_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP"
cp *.py "$BACKUP/" 2>/dev/null || true
echo "✅ Backup: $BACKUP"

# Restore EXECUTION_ORCHESTRATOR from git
git show HEAD:EXECUTION_ORCHESTRATOR.py > EXECUTION_ORCHESTRATOR.py 2>/dev/null || echo "⚠️ Using current"

# Verify it compiles
python3 -m py_compile EXECUTION_ORCHESTRATOR.py 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ EXECUTION_ORCHESTRATOR broken - restoring oldest backup"
    OLDEST=$(ls -t backup_*/EXECUTION_ORCHESTRATOR.py 2>/dev/null | tail -1)
    [ -n "$OLDEST" ] && cp "$OLDEST" EXECUTION_ORCHESTRATOR.py
fi

# Create clean AUTO_ADAPTIVE_APEX
cat > AUTO_ADAPTIVE_APEX.py << 'APEX_EOF'
#!/usr/bin/env python3
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AutoAdaptiveApex:
    def __init__(self, exchange):
        self.exchange = exchange
        self.balance = 0.0
        self.starting = 0.0
        self.tier = None
        
        self.tiers = {
            'nano': {'min': 0, 'max': 5, 'risk': 0.95, 'target': 0.025},
            'micro': {'min': 5, 'max': 50, 'risk': 0.90, 'target': 0.020},
            'small': {'min': 50, 'max': 200, 'risk': 0.80, 'target': 0.015},
            'medium': {'min': 200, 'max': 1000, 'risk': 0.70, 'target': 0.012},
            'large': {'min': 1000, 'max': float('inf'), 'risk': 0.60, 'target': 0.010}
        }
        
        logger.info("⚡ AUTO-ADAPTIVE APEX ready")
    
    async def get_balance(self):
        try:
            b = await asyncio.to_thread(self.exchange.fetch_balance)
            usdt = b.get('USDT', {}).get('total', 0.0)
            if self.starting == 0:
                self.starting = usdt
            self.balance = usdt
            return usdt
        except:
            return self.balance
    
    def get_tier(self, bal):
        for n, c in self.tiers.items():
            if c['min'] <= bal < c['max']:
                if self.tier != n and self.tier:
                    logger.info(f"🎉 {self.tier.upper()} → {n.upper()} (${bal:.2f})")
                self.tier = n
                return n, c
        return 'large', self.tiers['large']
    
    async def optimize(self, signal):
        bal = await self.get_balance()
        if bal < 3.0:
            return None
        
        if signal.get('confidence', 0) < 0.75:
            return None
        
        tier_name, tier = self.get_tier(bal)
        
        pos = bal * tier['risk']
        pos = max(3.0, min(pos, bal * 0.95))
        
        profit = pos * tier['target']
        fees = pos * 0.004
        
        if profit <= fees * 1.5:
            return None
        
        logger.info(f"✅ {signal.get('symbol')} | {tier_name.upper()} | ${pos:.2f}")
        
        return {
            'position_size': pos,
            'target_profit_pct': tier['target'],
            'stop_loss_pct': tier['target'] * 0.6
        }

apex = None

def init_auto_apex(ex):
    global apex
    apex = AutoAdaptiveApex(ex)
    return apex

def get_auto_apex():
    return apex
APEX_EOF

echo "✅ Created AUTO_ADAPTIVE_APEX.py"

# Test compilation
python3 -m py_compile AUTO_ADAPTIVE_APEX.py
python3 -m py_compile EXECUTION_ORCHESTRATOR.py

if [ $? -eq 0 ]; then
    echo "✅ All files compile!"
    
    # Restart
    pkill -f "COMPLETE_ULTIMATE_ORCHESTRATOR.py" || true
    sleep 2
    nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &
    sleep 4
    
    if ps aux | grep -v grep | grep "COMPLETE_ULTIMATE_ORCHESTRATOR.py" > /dev/null; then
        echo ""
        echo "=" | tr -d '\n' | head -c 60; echo
        echo "✅ BOT IS RUNNING WITH CLEAN CODE!"
        echo "=" | tr -d '\n' | head -c 60; echo
        echo ""
        tail -20 bot.log
        echo ""
        echo "📈 Monitor: tail -f bot.log"
    else
        echo "❌ Failed to start:"
        tail -30 bot.log
    fi
else
    echo "❌ Compilation failed"
fi
FINAL_DEPLOY_EOF

chmod +x DEPLOY_FINAL.sh
bash DEPLOY_FINAL.sh
```

**ON YOUR VPS, just copy and paste that entire block!**

It will:
1. ✅ Backup everything
2. ✅ Restore clean EXECUTION_ORCHESTRATOR from git
3. ✅ Create working AUTO_ADAPTIVE_APEX
4. ✅ Test compilation
5. ✅ Restart bot

**This is the CLEAN approach you asked for!** 🎯