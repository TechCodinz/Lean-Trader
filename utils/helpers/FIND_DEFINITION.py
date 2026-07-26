#!/usr/bin/env python3
"""
Robust search for definition
"""
import os

print("=== SEARCHING ===")
target = "def get_recent_signals"

for root, dirs, files in os.walk("/root/bot"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if target in line:
                            print(f"FOUND in {path}:{i+1}")
                            print(line.strip())
            except Exception as e:
                pass
