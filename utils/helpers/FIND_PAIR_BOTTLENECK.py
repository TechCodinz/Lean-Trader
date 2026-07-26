#!/usr/bin/env python3
"""
Find what's limiting the bot to only ETH/BTC when 6,633 pairs available
"""

import re

print("🔍 Finding pair selection bottleneck...")
print()

issues_found = []

# Check 1: Confidence threshold (we raised it to 0.65!)
print("1️⃣ Checking confidence threshold...")
with open('ADAPTIVE_CONFIDENCE_ENGINE.py', 'r') as f:
    conf = f.read()
    
thresholds = re.findall(r'min_confidence.*?=.*?([\d.]+)', conf)
if thresholds:
    for t in thresholds[:3]:
        if float(t) > 0.60:
            print(f"     HIGH threshold found: {t}")
            issues_found.append(f"Confidence threshold too high: {t}")
        else:
            print(f"   [OK] Threshold OK: {t}")

print()

# Check 2: Symbol limits in code
print("2️⃣ Checking for symbol limits in EXECUTION_ORCHESTRATOR...")
with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    exec_orch = f.read()

# Find [:N] limits
limits = re.findall(r'\[:\d+\]', exec_orch)
if limits:
    print(f"     Found {len(limits)} symbol slice limits:")
    for limit in set(limits)[:5]:
        print(f"      {limit}")
    issues_found.append(f"Symbol slicing limits: {len(limits)} found")
else:
    print("   [OK] No slice limits found")

print()

# Check 3: Hardcoded symbol lists
print("3️⃣ Checking for hardcoded symbol lists...")
hardcoded = re.findall(r"[\[\(]['\"](BTC|ETH|SOL)['\"]", exec_orch)
if len(hardcoded) > 3:
    print(f"     {len(hardcoded)} hardcoded symbol references")
    issues_found.append("Hardcoded symbol lists found")
else:
    print("   [OK] Minimal hardcoding")

print()

# Check 4: max_positions / max_trades limits
print("4️⃣ Checking position/trade limits...")
max_pos = re.findall(r'max_positions.*?=.*?(\d+)', exec_orch)
max_trades = re.findall(r'max_trades.*?=.*?(\d+)', exec_orch)

for val in max_pos[:3]:
    if int(val) < 100:
        print(f"     max_positions = {val} (too low!)")
        issues_found.append(f"max_positions too low: {val}")
    else:
        print(f"   [OK] max_positions = {val}")

for val in max_trades[:3]:
    if int(val) < 100:
        print(f"     max_trades = {val} (too low!)")
        issues_found.append(f"max_trades too low: {val}")

print()

# Check 5: COMPLETE_ULTIMATE_ORCHESTRATOR limits
print("5️⃣ Checking COMPLETE_ULTIMATE_ORCHESTRATOR...")
with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    ultimate = f.read()

ultimate_limits = re.findall(r'\[:\d+\]', ultimate)
if len(ultimate_limits) > 10:
    print(f"     {len(ultimate_limits)} slice limits in orchestrator!")
    issues_found.append(f"Ultimate orchestrator has {len(ultimate_limits)} limits")
else:
    print(f"   [OK] Only {len(ultimate_limits)} limits")

print()
print("=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print()

if issues_found:
    print("Issues limiting pair diversity:")
    for i, issue in enumerate(issues_found, 1):
        print(f"  {i}. {issue}")
    print()
    print("These are preventing the bot from trading all 6,633 pairs!")
else:
    print("No obvious limits found - may be signal quality issue")

print()
print("SOLUTION: Lower confidence + remove ALL limits")

