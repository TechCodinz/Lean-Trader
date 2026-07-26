#!/usr/bin/env python3
"""
Fix the indentation error by properly commenting out the entire block
"""

print("🔧 Fixing indentation error...")
print()

with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
    lines = f.readlines()

# Find lines 1440-1450 and properly comment out the hedging block
print("Removing the # we added and commenting the entire IF block...")

# First, uncomment what we just commented
for i in range(len(lines)):
    if i >= 1440 and i <= 1449:  # Lines 1441-1450
        if lines[i].startswith('# ') and ('LONG_ETH_SHORT_BTC' in lines[i] or 'LONG_BTC_SHORT_ETH' in lines[i]):
            lines[i] = lines[i][2:]  # Remove the '# ' we added

# Now properly comment out the ENTIRE if/elif block (lines 1441-1449)
# We'll replace it with a pass statement to keep the structure valid
if 'LONG_ETH_SHORT_BTC' in lines[1440]:
    # Replace lines 1441-1449 with a commented block
    lines[1440] = "            # DISABLED: Hedging strategy (forced bad ETH entries)\n"
    lines[1441] = "            # if 'LONG_ETH_SHORT_BTC' in trade_strategy:\n"
    lines[1442] = "            #     long_symbol = 'ETH/USDT'\n"
    lines[1443] = "            #     short_symbol = 'BTC/USDT'\n"
    lines[1444] = "            # elif 'LONG_BTC_SHORT_ETH' in trade_strategy:\n"
    lines[1445] = "            #     long_symbol = 'BTC/USDT'\n"
    lines[1446] = "            #     short_symbol = 'ETH/USDT'\n"
    lines[1447] = "            # else:\n"
    lines[1448] = "            #     logger.info(f\"   ⏭️  Unknown pairs trade: {trade_strategy}\")\n"
    lines[1449] = "            #     return False\n"
    
    # Add a pass or return False to handle this case
    lines.insert(1450, "            return False  # Hedging disabled\n")
    
    print("[OK] Properly commented out hedging block")
else:
    print("  Block already modified or not found at expected location")

with open('EXECUTION_ORCHESTRATOR.py', 'w') as f:
    f.writelines(lines)

print()
print("=" * 70)
print("[OK] INDENTATION FIXED!")
print("=" * 70)
print()
print("The hedging strategy that forced bad ETH entries is now disabled")

