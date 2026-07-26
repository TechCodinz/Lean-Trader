#!/usr/bin/env python3
"""
Comprehensive diagnosis: Why trades not happening
"""

import re
from collections import defaultdict

print("🔍 DIAGNOSING: Why trades not happening...")
print()

with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
    log = f.read()

# 1. Check if bot is generating signals
print("1️⃣ SIGNAL GENERATION:")
print("-" * 70)

signals = re.findall(r'signal|Decision|confidence.*[0-9]', log, re.IGNORECASE)
if signals:
    print(f"   [OK] Found {len(signals)} signal mentions")
    # Show recent signals
    signal_lines = [line for line in log.split('\n') if 'signal' in line.lower() or 'decision' in line.lower()][-10:]
    for line in signal_lines[-5:]:
        print(f"   {line[:100]}")
else:
    print("   [X] NO SIGNALS FOUND - Bot not generating trading signals!")

print()

# 2. Check if trades are being executed
print("2️⃣ TRADE EXECUTION:")
print("-" * 70)

executions = re.findall(r'Trade executed|execute_signal|execute_trade|ORDER.*placed', log, re.IGNORECASE)
if executions:
    print(f"   [OK] Found {len(executions)} execution attempts")
    # Show recent executions
    exec_lines = [line for line in log.split('\n') if any(x in line.lower() for x in ['trade executed', 'execute', 'order'])]
    for line in exec_lines[-5:]:
        print(f"   {line[:100]}")
else:
    print("   [X] NO TRADE EXECUTIONS - Trades not being placed!")

print()

# 3. Check for position monitoring
print("3️⃣ POSITION MONITORING:")
print("-" * 70)

monitoring = re.findall(r'Monitoring.*position|monitor_positions|Checking.*position', log, re.IGNORECASE)
if monitoring:
    print(f"   [OK] Found {len(monitoring)} monitoring activities")
    # Show recent monitoring
    monitor_lines = [line for line in log.split('\n') if 'monitor' in line.lower() or 'checking.*position' in line.lower()][-5:]
    for line in monitor_lines:
        print(f"   {line[:100]}")
else:
    print("   [X] NO MONITORING ACTIVITY - Positions not being checked!")

print()

# 4. Check for position closes
print("4️⃣ POSITION CLOSES:")
print("-" * 70)

closes = re.findall(r'POSITION CLOSED|Take profit|Stop loss|close_position', log, re.IGNORECASE)
if closes:
    print(f"   [OK] Found {len(closes)} position closes")
    # Show recent closes
    close_lines = [line for line in log.split('\n') if any(x in line.lower() for x in ['position closed', 'take profit', 'stop loss'])][-5:]
    for line in close_lines:
        print(f"   {line[:100]}")
else:
    print("   [X] NO POSITION CLOSES - Positions not closing!")

print()

# 5. Check for errors blocking execution
print("5️⃣ ERRORS BLOCKING EXECUTION:")
print("-" * 70)

errors = re.findall(r'ERROR.*execution|ERROR.*trade|ERROR.*signal|Insufficient balance|Order.*failed', log, re.IGNORECASE)
if errors:
    print(f"     Found {len(errors)} execution-related errors")
    # Show recent errors
    error_lines = [line for line in log.split('\n') if 'error' in line.lower() and any(x in line.lower() for x in ['execution', 'trade', 'signal', 'balance', 'order'])]
    for line in error_lines[-10:]:
        print(f"   {line[:100]}")
else:
    print("   [OK] No execution errors found")

print()

# 6. Check balance history
print("6️⃣ BALANCE HISTORY:")
print("-" * 70)

balances = re.findall(r'Balance[:\s]*\$?([\d.]+)|balance[:\s]*\$?([\d.]+)', log, re.IGNORECASE)
if balances:
    balance_vals = []
    for b in balances:
        val = b[0] or b[1]
        if val and val.replace('.', '').isdigit():
            balance_vals.append(float(val))
    
    if balance_vals:
        print(f"   Started: ${balance_vals[0]:.2f}")
        print(f"   Current: ${balance_vals[-1]:.2f}")
        print(f"   Change: ${balance_vals[-1] - balance_vals[0]:.2f}")
        if balance_vals[-1] < balance_vals[0]:
            print(f"   [X] Balance DECREASING - Money being lost!")
        elif balance_vals[-1] == balance_vals[0]:
            print(f"     Balance UNCHANGED - No profits being made")
        else:
            print(f"   [OK] Balance INCREASING - Profits being made!")
else:
    print("     No balance information found")

print()

# 7. Check if execution loop is running
print("7️⃣ EXECUTION LOOP STATUS:")
print("-" * 70)

if 'EXECUTION LOOP STARTED' in log or 'execution.*loop' in log.lower():
    print("   [OK] Execution loop started")
else:
    print("   [X] Execution loop may not be running!")

if 'run_execution_loop' in log.lower():
    print("   [OK] run_execution_loop() is being called")
else:
    print("   [X] run_execution_loop() may not be called")

print()

# 8. Check for open positions
print("8️⃣ OPEN POSITIONS:")
print("-" * 70)

open_pos = re.findall(r'open.*position|position.*open|Monitoring.*\d+.*position', log, re.IGNORECASE)
if open_pos:
    print(f"   Found {len(open_pos)} mentions of open positions")
    # Show recent
    for line in [l for l in log.split('\n') if 'open.*position' in l.lower() or 'monitoring.*position' in l.lower()][-5:]:
        print(f"   {line[:100]}")
else:
    print("     No open positions mentioned - May have no positions or not tracking them")

print()
print("=" * 70)
print("💡 DIAGNOSIS SUMMARY")
print("=" * 70)
print()
print("If NO SIGNALS: Bot not generating trading opportunities")
print("If NO EXECUTIONS: Signals generated but not being executed")
print("If NO MONITORING: Positions opened but not being checked")
print("If NO CLOSES: Positions opened but never closed (money locked)")
print("If BALANCE DECREASING: Trades losing money or fees eating balance")
print()

