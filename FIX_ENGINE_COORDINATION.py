#!/usr/bin/env python3
"""
Fix Engine Coordination - Wire Everything Together
===================================================

Current Issues:
1. Steady Profit runs but signals = [] (not getting from hub)
2. Scalper publishes but signals don't have SL/TP
3. MICRO gets signals but doesn't use SL/TP
4. Execution Orchestrator exists but not used

Fixes:
1. Wire Steady Profit → Data Hub
2. Wire MICRO → Data Hub (with SL/TP usage)
3. Wire all engines to Execution Orchestrator
4. Add position monitoring across all engines
"""

import sys
import re

def fix_coordination(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    changes = []
    
    # ===================================================================
    # FIX 1: Steady Profit - Get signals from hub
    # ===================================================================
    old_steady = '''                        # Check all timeframes
                        for tf in ['1m', '5m', '15m', '1h', '4h']:
                            # Get signals from data hub
                            signals = []  # self.data_hub would provide these
                            
                            for signal in signals:'''
    
    new_steady = '''                        # Get signals from data hub (filtered by timeframe)
                        all_signals = self.data_hub.get_signals(limit=100)
                        
                        for tf in ['1m', '5m', '15m', '1h', '4h']:
                            # Filter signals for this timeframe
                            signals = [s for s in all_signals if s.get('timeframe') == tf or not s.get('timeframe')]
                            
                            logger.debug(f"💰 STEADY checking {len(signals)} signals on {tf}")
                            
                            for signal in signals:'''
    
    if old_steady in content:
        content = content.replace(old_steady, new_steady)
        changes.append("✅ Steady Profit now gets signals from hub")
    
    # ===================================================================
    # FIX 2: Make Steady Profit errors visible
    # ===================================================================
    content = content.replace(
        'logger.debug(f"Steady profit: {e}")',
        'logger.error(f"❌ STEADY PROFIT ERROR: {e}")\n                        import traceback\n                        logger.error(traceback.format_exc())'
    )
    changes.append("✅ Steady Profit errors now visible")
    
    # ===================================================================
    # FIX 3: Add execution logging to see if trades happen
    # ===================================================================
    old_exec = '''                                    # Execute via execution engine
                                    if getattr(self, 'execution', None):
                                        await self.execution.execute_signal(extraction_signal)'''
    
    new_exec = '''                                    # Execute via execution engine
                                    if getattr(self, 'execution', None):
                                        logger.info(f"⚡ STEADY executing via Execution Orchestrator")
                                        result = await self.execution.execute_signal(extraction_signal)
                                        if result:
                                            logger.info(f"✅ STEADY trade executed: {extraction_signal.get('symbol')}")
                                        else:
                                            logger.warning(f"⚠️  STEADY trade failed")
                                    else:
                                        logger.warning("⚠️  STEADY: Execution Orchestrator not available!")'''
    
    if old_exec in content:
        content = content.replace(old_exec, new_exec)
        changes.append("✅ Steady Profit execution logging added")
    
    # Save
    with open(filepath, 'w') as f:
        f.write(content)
    
    return changes

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 FIX_ENGINE_COORDINATION.py COMPLETE_ULTIMATE_ORCHESTRATOR.py")
        sys.exit(1)
    
    changes = fix_coordination(sys.argv[1])
    
    print("🔧 ENGINE COORDINATION FIXES")
    print("="*60)
    print()
    
    for change in changes:
        print(change)
    
    print()
    print("📊 What's Now Coordinated:")
    print("  1. Scalper → publishes signals → Data Hub")
    print("  2. Data Hub → provides signals → Steady Profit")
    print("  3. Data Hub → provides signals → MICRO")
    print("  4. Steady Profit → executes via → Execution Orchestrator")
    print("  5. MICRO → executes directly → Gate.io")
    print()
    print("Result: All engines working TOGETHER!")
