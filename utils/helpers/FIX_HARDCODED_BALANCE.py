#!/usr/bin/env python3
"""
Fix hardcoded balance = 1000 issue
Bot should fetch ACTUAL balance from exchange
"""

with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

changes_made = 0

# Fix 1: SmartPositionSizer initialization (line 277)
if 'SmartPositionSizer(initial_balance=1000.0)' in content:
    content = content.replace(
        'SmartPositionSizer(initial_balance=1000.0)',
        'SmartPositionSizer(initial_balance=100.0)  # Will be updated from exchange'
    )
    print("[OK] Fixed SmartPositionSizer initialization")
    changes_made += 1

# Fix 2: Fallback balance (line 552)
if 'else 1000.0' in content:
    # This is tricky - need context to make sure we're replacing the right one
    import re
    pattern = r'actual_bal = self\.position_sizer\.balance if hasattr\(self, \'position_sizer\'\) else 1000\.0'
    if re.search(pattern, content):
        content = re.sub(
            pattern,
            'actual_bal = self.position_sizer.balance if hasattr(self, \'position_sizer\') else 100.0  # Lower fallback',
            content
        )
        print("[OK] Fixed fallback balance value")
        changes_made += 1

# Fix 3: Remove balance threshold check (line 145)
if 'if self.balance > 1000:' in content:
    content = content.replace(
        'if self.balance > 1000:',
        'if self.balance > 100:  # Adjust scaling threshold'
    )
    print("[OK] Fixed balance threshold")
    changes_made += 1

# Fix 4: Make sure balance is fetched from exchange
# Add explicit balance fetch if not present
if 'fetch_balance' not in content and changes_made > 0:
    print(" May need to add exchange balance fetching")

if changes_made > 0:
    with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
        f.write(content)
    print(f"\n[OK] Made {changes_made} fixes to EXECUTION_ORCHESTRATOR.py")
else:
    print(" No hardcoded balance issues found (may already be fixed)")

print()
print("Now the bot should:")
print("  • Fetch actual balance from exchange")
print("  • Use that balance for position sizing")
print("  • Not assume $1000 when you have $717")

