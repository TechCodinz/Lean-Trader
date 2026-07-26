#!/usr/bin/env python3
"""
⚡ EMERGENCY FIX - Division by Zero
Patches INTELLIGENT_EXECUTION_ENGINE to handle missing prices
"""

import sys
import re

# Read the file
with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()

# Find and fix the division issue - add more robust price validation
old_code = '''            # GET ALL AVAILABLE INTELLIGENCE
            entry_price = signal.get('entry', signal.get('price', 0))
            
            # [OK] FIX: Prevent division by zero!
            if entry_price <= 0:
                logger.warning(f"     Invalid entry price ({entry_price}) for {symbol}, skipping")
                return None'''

new_code = '''            # GET ALL AVAILABLE INTELLIGENCE
            entry_price = signal.get('entry', signal.get('price', 0))
            
            # [OK] FIX: Prevent division by zero - MORE ROBUST!
            if entry_price is None or entry_price <= 0 or entry_price == 100.0:
                # Try to get price from signal data
                if 'data' in signal and isinstance(signal['data'], dict):
                    entry_price = signal['data'].get('price', 0)
                
                # Still invalid? Skip this signal
                if not entry_price or entry_price <= 0 or entry_price == 100.0:
                    logger.warning(f"     Invalid/missing entry price for {symbol}, skipping")
                    return None'''

if old_code in content:
    content = content.replace(old_code, new_code)
    
    # Write back
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
        f.write(content)
    
    print("[OK] Fixed division by zero issue!")
else:
    print("  Code already updated or pattern not found")
    
print("Done!")
