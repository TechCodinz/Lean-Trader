#!/usr/bin/env python3
"""
CRITICAL FIX: Loosen overly-strict filters

Current problem:
  • 14,177 signals detected
  • Only 1,198 executed (8.5%)
  • 13,000+ rejected! (91.5%)
  
This bot is designed for HIGH-FREQUENCY trading but filters
are so strict it's barely trading at all!

Solution: Lower thresholds from 70%/80% to 60%/75%
"""

import re

print("="*70)
print("🔧 LOOSENING OVERLY-STRICT FILTERS")
print("="*70)
print()

changes_made = []

# ========================================
# 1. Lower collective consensus thresholds
# ========================================
print("1️⃣ Adjusting COLLECTIVE_CONSENSUS_ENGINE...")

try:
    with open('COLLECTIVE_CONSENSUS_ENGINE.py', 'r') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        # Lower min agreement from 70% to 60%
        if 'min_agreement' in line.lower() and ('0.7' in line or '70' in line):
            old_line = line
            if '0.7' in line:
                lines[i] = line.replace('0.7', '0.6')
            elif '70' in line and '%' in line:
                lines[i] = line.replace('70', '60')
            print(f"   Changed min_agreement: 70% → 60%")
            modified = True
            changes_made.append("Collective agreement: 70% → 60%")
        
        # Lower min confidence from 80% to 75%
        if 'min_confidence' in line.lower() and ('0.8' in line or '80' in line):
            old_line = line
            if '0.8' in line and '0.08' not in line:  # Avoid replacing 0.08
                lines[i] = line.replace('0.8', '0.75')
            elif '80' in line and '%' in line:
                lines[i] = line.replace('80', '75')
            print(f"   Changed min_confidence: 80% → 75%")
            modified = True
            changes_made.append("Collective confidence: 80% → 75%")
    
    if modified:
        with open('COLLECTIVE_CONSENSUS_ENGINE.py', 'w') as f:
            f.writelines(lines)
        print("   [OK] Thresholds lowered!")
    else:
        print("    Thresholds not found or already adjusted")

except FileNotFoundError:
    print("    File not found")
except Exception as e:
    print(f"   [X] Error: {e}")

print()

# ========================================
# 2. Adjust EXECUTION_ORCHESTRATOR min_confidence
# ========================================
print("2️⃣ Adjusting EXECUTION_ORCHESTRATOR...")

try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        # Lower min_confidence
        if 'self.min_confidence' in line and '=' in line:
            if '0.85' in line:
                lines[i] = line.replace('0.85', '0.70')
                print(f"   Changed min_confidence: 85% → 70%")
                modified = True
                changes_made.append("Execution confidence: 85% → 70%")
            elif '0.75' in line:
                lines[i] = line.replace('0.75', '0.70')
                print(f"   Changed min_confidence: 75% → 70%")
                modified = True
                changes_made.append("Execution confidence: 75% → 70%")
    
    if modified:
        with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
            f.writelines(lines)
        print("   [OK] Threshold lowered!")
    else:
        print("    Threshold not found or already adjusted")

except FileNotFoundError:
    print("    File not found")
except Exception as e:
    print(f"   [X] Error: {e}")

print()

# ========================================
# 3. Summary
# ========================================
print("="*70)
print("📊 CHANGES SUMMARY")
print("="*70)
print()

if changes_made:
    print("Changes applied:")
    for i, change in enumerate(changes_made, 1):
        print(f"   {i}. {change}")
    print()
    print("Expected impact:")
    print("   • Execution rate: 8.5% → 20-30%")
    print("   • More trades = better use of collective intelligence")
    print("   • Still validates with swarm (not random trading!)")
    print("   • Should improve win rate through volume")
else:
    print(" No changes made - files may have different structure")

print()
print("="*70)
