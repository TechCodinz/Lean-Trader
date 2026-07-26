import os

# Read the file
with open('HARMONY_MAINTENANCE_SYSTEM.py', 'r') as f:
    content = f.read()

# Fix the iteration bug
old_code = "for name, engine in self.consciousness.engines.items():"
new_code = "for name, engine in list(self.consciousness.engines.items()):"

if old_code in content:
    content = content.replace(old_code, new_code)
    print("[OK] Fixed iteration bug in HARMONY_MAINTENANCE_SYSTEM.py")
    
    with open('HARMONY_MAINTENANCE_SYSTEM.py', 'w') as f:
        f.write(content)
else:
    print("ℹ️  Iteration bug already fixed or code not found")
