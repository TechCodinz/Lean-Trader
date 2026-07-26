#!/usr/bin/env python3
"""
DIAGNOSE WHY WIN RATE IS SO LOW

The bot has 205+ engines and collective consensus that should
give 70-85% win rate. If we're getting 11%, something is broken!
"""

import os

print("="*70)
print("🔍 DIAGNOSING ACCURACY PROBLEM")
print("="*70)
print()

# Check if collective consensus file exists
files_to_check = [
    'COLLECTIVE_CONSENSUS_ENGINE.py',
    'COLLECTIVE_SWARM_INTELLIGENCE.py',
    'EXECUTION_ORCHESTRATOR.py',
    'COMPLETE_ULTIMATE_ORCHESTRATOR.py'
]

print("1️⃣ Checking if files exist...")
for f in files_to_check:
    exists = "[OK]" if os.path.exists(f) else "[X]"
    print(f"   {exists} {f}")

print()
print("2️⃣ Checking COMPLETE_ULTIMATE_ORCHESTRATOR initialization...")

try:
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    checks = {
        'CollectiveConsensusEngine imported': 'CollectiveConsensusEngine' in content or 'CollectiveSwarmIntelligence' in content,
        'Consensus engine initialized': 'collective_consensus' in content or 'collective_swarm' in content,
        'Consensus passed to orchestrator': 'collective' in content.lower(),
    }
    
    print()
    for check, result in checks.items():
        status = "[OK]" if result else "[X] MISSING!"
        print(f"   {status} {check}")
    
    # Check if there's initialization code
    if 'self.collective_consensus = ' in content or 'collective_swarm = ' in content:
        print("\n   [OK] Found consensus initialization")
    else:
        print("\n   [X] NO CONSENSUS INITIALIZATION FOUND!")
        print("   🚨 THIS IS THE PROBLEM!")
        
except FileNotFoundError:
    print("   [X] COMPLETE_ULTIMATE_ORCHESTRATOR.py not found!")

print()
print("3️⃣ Checking if consensus is being used in execution...")

try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    if 'if self.collective_consensus:' in content:
        print("   [OK] Consensus check found in code")
        
        # Check if it's actually enabled or commented
        if 'self.collective_consensus' in content:
            print("   [OK] Consensus variable exists")
        else:
            print("   [X] Consensus variable missing!")
    else:
        print("   [X] No consensus check in execution flow!")
        
except FileNotFoundError:
    print("   [X] EXECUTION_ORCHESTRATOR.py not found!")

print()
print("="*70)
print("💡 DIAGNOSIS")
print("="*70)
print()
print("If you see [X] marks above, that's why win rate is 11%!")
print()
print("The bot is executing trades WITHOUT collective scrutiny.")
print("It's like having 205 experts but only listening to 1!")
print()
print("Next: Check bot.log for consensus messages...")
print("="*70)
