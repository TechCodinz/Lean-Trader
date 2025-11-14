# Find what times out during startup
import re

with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

print("Searching for async operations that might timeout...")
print()

for i, line in enumerate(lines, 1):
    # Find await calls
    if 'await' in line and any(x in line for x in ['fetch', 'load_markets', 'watch', 'universal']):
        print(f"Line {i}: {line.strip()}")

print("\nSearching for loops that might hang...")
for i, line in enumerate(lines, 1):
    if 'while True' in line or 'for' in line and 'fetch' in lines[min(i+5, len(lines))]:
        print(f"Line {i}: {line.strip()}")
        for j in range(5):
            if i+j < len(lines):
                print(f"  {i+j}: {lines[i+j-1].strip()}")

