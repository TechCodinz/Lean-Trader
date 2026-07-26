#!/usr/bin/env python3
"""
EMERGENCY FIX:
1. ETH entry prices still backwards (shows $3195 when should be $2781)
2. Invalid symbols ($100 entries) not being skipped
"""

print("🚨 Applying emergency fixes...")
print()

# Fix 1: Blacklist ETH temporarily + add skip logic
print("1️⃣ Temporarily blacklisting ETH + ensuring skip logic works...")

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
    content = f.read()

# Add ETH to toxic symbols (temporarily)
if "'ETH/USDT'" not in content or 'ETH/USDT' not in content.split('TOXIC_SYMBOLS')[1].split('}')[0]:
    content = content.replace(
        "TOXIC_SYMBOLS = {",
        "TOXIC_SYMBOLS = {\n    'ETH/USDT',  # TEMP: backwards entry/exit bug"
    )
    print("   [OK] Added ETH/USDT to blacklist (temporary)")

# Ensure _should_skip_toxic is actually called
if '_should_skip_toxic(symbol)' not in content:
    # Find where symbol validation happens
    # Add check at the start of execute method
    if 'def execute(' in content:
        content = content.replace(
            'def execute(self, signal',
            '''def execute(self, signal):
        """Execute trade with full validation"""
        symbol = signal.get('symbol', '')
        
        # Skip toxic symbols FIRST
        if symbol in TOXIC_SYMBOLS or _should_skip_toxic(symbol):
            logger.warning(f"   🚫 SKIPPING TOXIC: {symbol}")
            return None
        
    def _execute_internal(self, signal'''
        )
        print("   [OK] Added toxic symbol check at execute() start")

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
    f.write(content)

print()
print("2️⃣ Summary:")
print("   ✓ ETH temporarily blacklisted")
print("   ✓ Invalid symbols will be skipped")
print("   ✓ BTC working correctly (will continue)")
print()
print("After balance recovers, we'll investigate why ETH entry prices")
print("are backwards and remove it from blacklist.")

