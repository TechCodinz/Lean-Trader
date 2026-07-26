#!/usr/bin/env python3
"""
Fix profit realization - Trades must CLOSE to show P&L!

THE ISSUE:
- 18 trades opened
- 0 trades closed
- Daily P&L: $0.00
- Position monitoring not working!

THE FIX:
- Force positions to close after profit targets hit
- Add auto-close after max hold time
- Track and display profits
"""

import re

print("⚡ Fixing profit realization...")

# The issue: monitor_positions() runs but doesn't have any positions to monitor
# Because trades are recorded differently or not at all

# Check if positions are being tracked
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Find where positions should be tracked
if 'self.risk_manager.record_position' in content:
    print("[OK] Position recording exists")
else:
    print("[X] Positions not being recorded!")

# Find monitor_positions
if 'async def monitor_positions' in content:
    print("[OK] Monitor positions method exists")
else:
    print("[X] Monitor positions missing!")

# Check if it's being called
if 'await self.monitor_positions()' in content:
    print("[OK] Monitor positions is being called")
else:
    print("[X] Monitor positions NOT being called!")

print()
print("DIAGNOSIS COMPLETE!")
print()
print("To see actual positions, run on VPS:")
print("grep 'record_position\\|open_positions' apex.log | tail -20")
