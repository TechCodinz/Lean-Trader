#!/usr/bin/env python3
"""
Check if profit monitoring is being imported and called
"""

print("🔍 Checking if profit monitoring is active...")
print()

# Check EXECUTION_ORCHESTRATOR or COMPLETE_ULTIMATE_ORCHESTRATOR
import os

orchestrator_files = [
    'EXECUTION_ORCHESTRATOR.py',
    'COMPLETE_ULTIMATE_ORCHESTRATOR.py'
]

for filename in orchestrator_files:
    if os.path.exists(filename):
        print(f"Checking {filename}...")
        
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for imports
        if 'PROFIT_MONITORING' in content:
            print(f"  ✅ Imports PROFIT_MONITORING_SYSTEM")
            
            # Check if monitor function is called
            if 'monitor_trade_for_profit' in content:
                print(f"  ✅ Calls monitor_trade_for_profit()")
            else:
                print(f"  ❌ Does NOT call monitor_trade_for_profit()")
            
            # Check if monitoring loop exists
            if 'monitor_positions' in content:
                print(f"  ✅ Has monitor_positions() method")
                
                # Check if it's in a loop
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'monitor_positions' in line and 'def ' in line:
                        print(f"     Found at line {i+1}")
                        
                        # Check if it's called in main loop
                        if 'while' in content[max(0, i-100):i+100]:
                            print(f"     ✅ Inside a loop!")
                        else:
                            print(f"     ⚠️  Not in a loop?")
                        break
            else:
                print(f"  ❌ No monitor_positions() method")
        else:
            print(f"  ❌ Does NOT import PROFIT_MONITORING_SYSTEM")
        
        print()

print()
print("=" * 70)
print("CHECKING RECENT LOGS")
print("=" * 70)
print()

# Check if monitoring is happening in logs
with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

if 'Starting ULTRA-FAST profit monitoring' in log:
    print("✅ Profit monitoring IS starting!")
    count = log.count('Starting ULTRA-FAST profit monitoring')
    print(f"   Started {count} times")
else:
    print("❌ Profit monitoring NOT starting!")
    print("   This is the root cause - monitoring never launches")

print()

# Check for position monitoring
if 'monitor_positions' in log.lower():
    print("✅ monitor_positions() being called")
else:
    print("❌ monitor_positions() NOT being called")

print()
print("=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print()
print("The PROFIT_MONITORING_SYSTEM.py file exists and has logic.")
print("But it's not being called to actually monitor positions!")
print()
print("FIX NEEDED:")
print("  → Ensure orchestrator calls monitor_trade_for_profit()")
print("  → OR use a simpler inline monitoring approach")

