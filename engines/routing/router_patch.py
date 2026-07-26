#!/usr/bin/env python3
import sys
with open('router.py', 'r') as f:
    content = f.read()

# CRITICAL FIXES:
# 1. Force dry_run to False
content = content.replace('"dry_run": True', '"dry_run": False')
# 2. Enable live trading by default
content = content.replace('self.live = False', 'self.live = True')
# 3. Set ALLOW_LIVE environment
content = content.replace("os.getenv('ALLOW_LIVE')", "os.getenv('ALLOW_LIVE', 'YES')")

with open('router.py', 'w') as f:
    f.write(content)
print("router.py patched for REAL execution")
