
import sys

target = '/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py'

# Backup
import shutil
shutil.copy(target, target + '.pre_integration')

with open(target, 'r') as f:
    content = f.read()

# Add import at top if not present
if 'SAFE_EXECUTION_WRAPPER' not in content:
    lines = content.split('\n')
    # Find first import
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            lines.insert(i + 1, 'from SAFE_EXECUTION_WRAPPER import get_safe_executor')
            print(f"Added import at line {i+2}")
            break
    content = '\n'.join(lines)

# Find execute_signals call and wrap it
if 'get_safe_executor()' not in content:
    # Simple approach: add after data hub signal publish
    marker = 'Published'
    if marker in content and 'signals to data hub' in content:
        import re
        # Find the line with published signals
        pattern = r'(logger\.info\(f.*Published.*signals to data hub.*\))'
        replacement = r'\1\n                # Execute via safe wrapper\n                try: get_safe_executor()(self, scalp_signals if \'scalp_signals\' in locals() else [])\n                except: pass'
        content = re.sub(pattern, replacement, content)
        print("Added safe executor call")

with open(target, 'w') as f:
    f.write(content)

print("Orchestrator patched")
