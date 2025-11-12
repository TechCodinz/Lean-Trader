#!/usr/bin/env python3
"""
Add debug logging to execution loop to see why it's not processing signals
"""

import re

print("🔧 Adding debug logging to EXECUTION_ORCHESTRATOR.py...")

with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Find and enhance the loop
old_loop = '''        while self.execution_enabled:
            try:
                # Reset daily stats if new day
                self.risk_manager.reset_daily_stats()
                
                # Check for decisions in alert queue
                if not self.data_hub.alert_queue.empty():'''

new_loop = '''        while self.execution_enabled:
            try:
                logger.info("🔄 EXEC LOOP: Iteration starting...")
                
                # Reset daily stats if new day
                self.risk_manager.reset_daily_stats()
                
                # Check for decisions in alert queue
                logger.debug(f"   Checking alert_queue...")
                if not self.data_hub.alert_queue.empty():
                    logger.info("   📥 Alert queue has decision!")'''

if old_loop in content:
    content = content.replace(old_loop, new_loop)
    print("✅ Added loop iteration logging")
else:
    print("⚠️  Loop pattern not found, trying alternative...")

# Add signal checking logs
old_signals = '''                # ACTIVELY CHECK HUB FOR NEW SIGNALS (don't just wait for alert queue!)
                signals = self.data_hub.get_signals(limit=20)'''

new_signals = '''                # ACTIVELY CHECK HUB FOR NEW SIGNALS (don't just wait for alert queue!)
                signals = self.data_hub.get_signals(limit=20)
                logger.info(f"   📊 Data hub returned {len(signals)} signals")'''

if old_signals in content:
    content = content.replace(old_signals, new_signals)
    print("✅ Added signal checking logging")

# Add signal processing logs  
old_process = '''                for signal in signals:
                    # Only execute high-confidence scalper signals
                    source = signal.get('source', '')
                    strategy = signal.get('strategy', '')
                    confidence = signal.get('confidence', 0)'''

new_process = '''                for signal in signals:
                    logger.debug(f"      Checking signal: {signal.get('symbol', 'Unknown')}")
                    
                    # Only execute high-confidence scalper signals
                    source = signal.get('source', '')
                    strategy = signal.get('strategy', '')
                    confidence = signal.get('confidence', 0)'''

if old_process in content:
    content = content.replace(old_process, new_process)
    print("✅ Added signal processing logging")

# Write back
with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.write(content)

print("✅ Debug logging added!")
print("\nNow restart bot to see detailed execution logs:")
print("  pkill -f RUN_BOT && nohup python3 RUN_BOT.py > apex.log 2>&1 &")
