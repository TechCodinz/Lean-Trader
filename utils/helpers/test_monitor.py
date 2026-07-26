import sys
sys.path.insert(0, '/root/bot')

print("Simulating what monitor_positions() sees...\n")

# The issue: intelligent_engine might be None or not have active_trades_by_tf
print("Possible scenarios:")
print("1. intelligent_engine = None → finds no positions")
print("2. intelligent_engine exists but active_trades_by_tf is empty")
print("3. trades exist but status != 'open'")
print("\nLet's check line 544 condition...")

with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()
    for i in range(540, 560):
        print(f"{i+1}: {lines[i]}", end='')
