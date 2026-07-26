#!/usr/bin/env python3
"""
Fix profit monitoring to actually close positions
"""

print("🔧 Fixing profit monitoring system...")
print()

with open('PROFIT_MONITORING_SYSTEM.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Check what's in the file
lines = content.split('\n')

print(f"File has {len(lines)} lines")
print()

# Find key settings
found_settings = False

for i, line in enumerate(lines[:200]):  # Check first 200 lines
    if 'take_profit' in line.lower() or 'stop_loss' in line.lower():
        print(f"Line {i+1}: {line.strip()}")
        found_settings = True

if not found_settings:
    print("  No take_profit or stop_loss settings found in first 200 lines!")
    print()
    print("Checking if this is an empty/template file...")
    
    # Check if file has actual logic
    if 'def monitor' in content or 'def check' in content:
        print("[OK] File has monitoring methods")
    else:
        print("[X] File might be empty or broken!")

print()
print("=" * 70)
print("CHECKING __init__ METHOD")
print("=" * 70)
print()

# Find __init__ method
for i, line in enumerate(lines):
    if 'def __init__' in line:
        print(f"Found __init__ at line {i+1}")
        print()
        print("Next 30 lines:")
        for j in range(i, min(len(lines), i+30)):
            if lines[j].strip():
                print(f"  {j+1}: {lines[j][:80]}")
        break

