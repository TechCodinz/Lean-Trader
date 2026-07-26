
# Read file
with open('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

# Remove any lines with position_cleanup initialization that might be in wrong place
new_lines = []
for i, line in enumerate(lines):
    # Skip the problematic line
    if 'self.position_cleanup = AutomaticPositionCleanup' in line:
        print(f"Removing line {i+1}: {line.strip()}")
        continue
    new_lines.append(line)

# Write back
with open('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.writelines(new_lines)

print("[OK] Removed problematic code")
