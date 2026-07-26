#!/usr/bin/env python3
"""
Robust fix for position sizing - ensures $5 minimum
"""

print("🔧 Applying robust position sizing fix...")
print()

with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

fixed = False
for i, line in enumerate(lines):
    # Fix min_size for balance < 100
    if 'min_size, max_size = 3.0, 20.0' in line and 'balance < 100' in lines[i-1] if i > 0 else False:
        lines[i] = '                min_size, max_size = 5.0, 20.0  # FIXED: $5 minimum (Bybit requirement)\n'
        print(f"   [OK] Fixed line {i+1}: min_size 3.0 → 5.0")
        fixed = True
    
    # Add absolute $5 minimum check after final_size calculation
    if 'final_size = max(min_size, min(final_size, max_size))' in line:
        # Insert check after this line
        check_lines = [
            '            \n',
            '            # CRITICAL: Ensure absolute $5 minimum (Bybit requirement)\n',
            '            if final_size < 5.0 and balance >= 5.0:\n',
            '                # Scale up to meet minimum (use up to 30% of balance if needed)\n',
            '                final_size = min(5.0, balance * 0.30)\n',
            '                logger.info(f"     Scaled up to meet $5 minimum: ${final_size:.2f}")\n',
            '            final_size = max(5.0, final_size)  # Final safety check\n'
        ]
        # Insert after current line
        lines.insert(i+1, ''.join(check_lines))
        print(f"   [OK] Added absolute $5 minimum check after line {i+1}")
        fixed = True
        break  # Only insert once

if fixed:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print()
    print("=" * 70)
    print("[OK] POSITION SIZING FIXED")
    print("=" * 70)
else:
    print("     Could not find position sizing code to fix")
    print("   Showing current state:")
    for i, line in enumerate(lines[620:635], start=621):
        if 'min_size' in line or 'final_size' in line:
            print(f"   Line {i}: {line.rstrip()}")

print()

# Also check PROFIT_MONITORING_SYSTEM
print("2️⃣ Checking PROFIT_MONITORING_SYSTEM thresholds...")

try:
    with open('PROFIT_MONITORING_SYSTEM.py', 'r', encoding='utf-8', errors='ignore') as f:
        profit_content = f.read()
    
    # Find take_profit and stop_loss values
    import re
    
    tp_match = re.search(r'take_profit[^=]*=\s*([\d.]+)', profit_content)
    sl_match = re.search(r'stop_loss[^=]*=\s*([\d.]+)', profit_content)
    
    if tp_match:
        tp_val = float(tp_match.group(1))
        if tp_val < 0.02:
            print(f"     Take profit too low: {tp_val:.4f} (should be 0.02 = 2%)")
        else:
            print(f"   [OK] Take profit: {tp_val:.4f} ({tp_val*100:.1f}%)")
    
    if sl_match:
        sl_val = float(sl_match.group(1))
        if sl_val > 0.01:
            print(f"     Stop loss too high: {sl_val:.4f} (should be 0.01 = 1%)")
        else:
            print(f"   [OK] Stop loss: {sl_val:.4f} ({sl_val*100:.1f}%)")
    
    if not tp_match and not sl_match:
        print("   ℹ️  Take profit/stop loss not found in expected format")
        print("   → May be using EXECUTION_ORCHESTRATOR thresholds instead")
        
except Exception as e:
    print(f"     Error checking PROFIT_MONITORING_SYSTEM: {e}")

print()

# Verify EXECUTION_ORCHESTRATOR thresholds
print("3️⃣ Verifying EXECUTION_ORCHESTRATOR thresholds...")

try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r', encoding='utf-8', errors='ignore') as f:
        exec_content = f.read()
    
    if 'elif pnl_pct > 0.02:' in exec_content:
        print("   [OK] Take profit: +2%")
    elif 'elif pnl_pct > 0.01:' in exec_content:
        print("     Take profit: +1% (should be +2%)")
    else:
        print("   ℹ️  Take profit threshold not found")
    
    if 'if pnl_pct < -0.01:' in exec_content:
        print("   [OK] Stop loss: -1%")
    elif 'if pnl_pct < -0.03:' in exec_content:
        print("     Stop loss: -3% (should be -1%)")
    else:
        print("   ℹ️  Stop loss threshold not found")
        
except Exception as e:
    print(f"     Error checking EXECUTION_ORCHESTRATOR: {e}")

print()
print("=" * 70)
print("[OK] VERIFICATION COMPLETE")
print("=" * 70)

