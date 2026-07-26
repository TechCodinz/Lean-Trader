#!/usr/bin/env python3
"""
Compare working orchestrator vs current one
"""

print("🔍 Comparing orchestrators...")
print()

# Check which orchestrator files exist
import os

orchestrators = {
    'EXECUTION_ORCHESTRATOR.py': 'Working (grew $50→$808)',
    'COMPLETE_ULTIMATE_ORCHESTRATOR.py': 'Current (losing money)'
}

for file, desc in orchestrators.items():
    if os.path.exists(file):
        print(f"[OK] {file} - {desc}")
        
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check key settings
        print(f"   Checking {file}...")
        
        # Position sizing
        if 'min_position_usd' in content:
            import re
            min_pos = re.search(r'min_position_usd\s*=\s*([\d.]+)', content)
            if min_pos:
                print(f"     min_position_usd: ${min_pos.group(1)}")
        
        # Take profit / Stop loss
        if 'pnl_pct > 0.02' in content:
            print(f"     Take profit: +2% [OK]")
        elif 'pnl_pct > 0.01' in content:
            print(f"     Take profit: +1% ")
        
        if 'pnl_pct < -0.01' in content:
            print(f"     Stop loss: -1% [OK]")
        elif 'pnl_pct < -0.03' in content:
            print(f"     Stop loss: -3% ")
        
        # Confidence threshold
        if 'min_confidence = 0.50' in content or 'min_confidence=0.50' in content:
            print(f"     Confidence: 0.50 [OK]")
        elif 'min_confidence = 0.65' in content or 'min_confidence=0.65' in content:
            print(f"     Confidence: 0.65 ")
        
        # Position limits
        if 'max_open_positions = 999999' in content:
            print(f"     Max positions: Unlimited [OK]")
        elif 'max_open_positions =' in content:
            import re
            max_pos = re.search(r'max_open_positions\s*=\s*(\d+)', content)
            if max_pos:
                print(f"     Max positions: {max_pos.group(1)}")
        
        print()
    else:
        print(f"[X] {file} - NOT FOUND")

