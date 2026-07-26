#!/usr/bin/env python3
import sys
import codecs

# Force safe output encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')

try:
    print("--- STARTUP LOG TAIL ---")
    with open('/root/bot/startup.log', 'rb') as f:
        # Read last 2KB
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 2000), 0)
        content = f.read()
        # Decode safely
        print(content.decode('utf-8', errors='replace'))
    print("--- END LOG ---")
except Exception as e:
    print(f"Error reading log: {e}")
