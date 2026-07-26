
print("=== DIAGNOSING TELEGRAM ERROR (Lines 4690-4720) ===")
try:
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[4690:4720]):
            print(f"{4690+i}: {line}", end='')
except Exception as e:
    print(f"Error reading orchestrator: {e}")

print("\n=== DIAGNOSING EXECUTION ERROR (Searching execute_trade) ===")
try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if 'def execute_trade' in line:
                print(f"{i+1}: {line}", end='')
                # Print next 20 lines
                for j in range(1, 25):
                    if i+j < len(lines):
                        print(f"{i+1+j}: {lines[i+j]}", end='')
                break
except Exception as e:
    print(f"Error reading execution engine: {e}")
