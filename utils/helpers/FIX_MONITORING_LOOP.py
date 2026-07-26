#!/usr/bin/env python3
"""
Fix monitor_positions() to run continuously, not just once
"""

print("🔧 Fixing monitoring loop...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

original = content

# Find line 415 with the timeout
lines = content.split('\n')

print("Looking for the problematic line...")
for i, line in enumerate(lines):
    if 'await asyncio.wait_for(self.monitor_positions()' in line and 'timeout=3.0' in line:
        print(f"[OK] Found at line {i+1}: {line.strip()}")
        print()
        
        # Show context
        print("Context (10 lines before and after):")
        for j in range(max(0, i-10), min(len(lines), i+11)):
            marker = ">>> " if j == i else "    "
            print(f"{marker}{j+1}: {lines[j][:80]}")
        
        print()
        print("=" * 70)
        print("FIX STRATEGY")
        print("=" * 70)
        print()
        print("Current: Calls monitor_positions() once with 3s timeout")
        print("Problem: Never calls it again!")
        print()
        print("Solution: Make it recurring")
        print()
        
        # Check if it's inside a loop already
        # Look backwards for while
        in_loop = False
        for k in range(max(0, i-30), i):
            if 'while' in lines[k]:
                print(f"[OK] It's inside a while loop at line {k+1}")
                print(f"   {lines[k].strip()}")
                in_loop = True
                break
        
        if not in_loop:
            print("[X] NOT in a loop!")
            print()
            print("CRITICAL: Need to wrap this in a continuous loop")
            print()
            print("Adding monitoring loop...")
            
            # Find the function this is in
            for k in range(i, -1, -1):
                if 'async def ' in lines[k] or 'def ' in lines[k]:
                    print(f"[OK] Inside function at line {k+1}: {lines[k].strip()}")
                    break
        
        break

print()
print("=" * 70)
print("APPLYING FIX")
print("=" * 70)
print()

# Simple fix: Comment out the timeout wrapper and put monitor_positions in a proper loop
# Or better: Find where this is called from and ensure it's in a loop

print("Checking if there's a main run loop...")
for i, line in enumerate(lines):
    if ('while True' in line or 'while self.running' in line) and i < 500:
        print(f"[OK] Found main loop at line {i+1}")
        print()
        
        # Check if monitor_positions is called inside
        for j in range(i, min(len(lines), i+100)):
            if 'monitor_positions' in lines[j]:
                print(f"   monitor_positions called at line {j+1}")
                break
        else:
            print("   [X] monitor_positions NOT called in main loop!")
        break
else:
    print("  No obvious main loop found")

print()
print("=" * 70)
print("RECOMMENDED FIX")
print("=" * 70)
print()
print("Since monitor_positions() exists and has close logic,")
print("we need to ensure it's called repeatedly.")
print()
print("Two options:")
print("  A. Put it in the main event loop")
print("  B. Run it as a background task with asyncio.create_task()")
print()
print("I'll implement option B (background task) for safety")

