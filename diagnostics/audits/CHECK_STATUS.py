#!/usr/bin/env python3
"""
Comprehensive status check
Verify all fixes are in place
"""

import subprocess
import re

print("="*70)
print("🔍 COMPREHENSIVE STATUS CHECK")
print("="*70)
print()

# ============================================
# 1. CHECK IF BOT IS RUNNING
# ============================================
print("1️⃣ Bot Process Status:")
print("-" * 70)

result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
if 'COMPLETE_ULTIMATE_ORCHESTRATOR' in result.stdout:
    print("✅ Bot is RUNNING")
    
    # Get process info
    for line in result.stdout.split('\n'):
        if 'COMPLETE_ULTIMATE_ORCHESTRATOR' in line:
            parts = line.split()
            if len(parts) >= 10:
                cpu = parts[2]
                mem = parts[3]
                time = parts[9]
                print(f"   CPU: {cpu}% | Memory: {mem}% | Runtime: {time}")
else:
    print("❌ Bot is NOT running!")
    print("   Need to restart it")

print()

# ============================================
# 2. VERIFY FIXES ARE IN CODE
# ============================================
print("2️⃣ Verifying Fixes in Code:")
print("-" * 70)

# Check toxic symbols blacklist
try:
    with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
        content = f.read()
    
    if 'TOXIC_SYMBOLS' in content:
        print("✅ Toxic symbols blacklist: IN CODE")
        if 'is_toxic_symbol' in content:
            print("✅ Toxic symbol check function: IN CODE")
    else:
        print("❌ Toxic symbols blacklist: MISSING")
except:
    print("❌ Could not check INTELLIGENT_EXECUTION_ENGINE.py")

# Check position sizing
try:
    with open('EXECUTION_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    if 'base_pct = 0.05' in content:
        print("✅ Safe 5% position sizing: IN CODE")
    else:
        print("⚠️ Position sizing: May still be complex")
except:
    print("❌ Could not check EXECUTION_ORCHESTRATOR.py")

print()

# ============================================
# 3. CHECK LOG OUTPUT
# ============================================
print("3️⃣ Recent Log Activity:")
print("-" * 70)

try:
    with open('bot.log', 'r', errors='ignore') as f:
        logs = f.read()
    
    # Get last 50 lines
    log_lines = logs.split('\n')[-50:]
    
    # Check for key indicators
    has_balance = any('Got exchange balance' in line for line in log_lines)
    has_trades = any('POSITION CLOSED' in line or 'EXECUTING' in line for line in log_lines)
    has_signals = any('signal' in line.lower() for line in log_lines)
    has_errors = any('ERROR' in line or 'Traceback' in line for line in log_lines)
    
    print(f"Balance checks: {'✅ YES' if has_balance else '❌ NO'}")
    print(f"Trade activity: {'✅ YES' if has_trades else '❌ NO'}")
    print(f"Signal detection: {'✅ YES' if has_signals else '❌ NO'}")
    print(f"Errors present: {'⚠️ YES' if has_errors else '✅ NO'}")
    
    # Show last 5 meaningful lines
    print()
    print("Last 5 meaningful log lines:")
    count = 0
    for line in reversed(log_lines):
        if line.strip() and not line.startswith('2025') and count < 5:
            continue
        if line.strip() and count < 5:
            print(f"  {line[:120]}")
            count += 1
    
except Exception as e:
    print(f"❌ Could not read logs: {e}")

print()

# ============================================
# 4. CURRENT BALANCE
# ============================================
print("4️⃣ Current Balance:")
print("-" * 70)

try:
    result = subprocess.run(
        ['grep', '-a', 'Got exchange balance', 'bot.log'],
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        balances = re.findall(r'\$([0-9.]+)', result.stdout)
        if balances:
            current = float(balances[-1])
            print(f"Balance: ${current:.2f}")
            
            if current < 10:
                print()
                print("⚠️ CRITICAL: Balance too low!")
                print(f"   Current: ${current:.2f}")
                print(f"   Minimum for effective trading: $20+")
                print()
                print("With 5% position sizing:")
                print(f"   ${current:.2f} × 5% = ${current * 0.05:.2f} per trade")
                print(f"   Minimum trade size: $5")
                print()
                print("Recommendation: Add $50-100 fresh capital")
        else:
            print("⚠️ No balance data found")
    else:
        print("⚠️ No balance checks in logs yet")
        
except Exception as e:
    print(f"Error: {e}")

print()

# ============================================
# 5. RECOMMENDATIONS
# ============================================
print("="*70)
print("💡 RECOMMENDATIONS")
print("="*70)
print()

try:
    # Determine bot state
    bot_running = 'COMPLETE_ULTIMATE_ORCHESTRATOR' in subprocess.run(
        ['ps', 'aux'], capture_output=True, text=True
    ).stdout
    
    with open('bot.log', 'r', errors='ignore') as f:
        recent_logs = f.read().split('\n')[-100:]
    
    has_recent_activity = any('2025-11-21 1' in line for line in recent_logs)
    
    if not bot_running:
        print("🚨 ACTION NEEDED: Bot is not running!")
        print()
        print("   Start bot with:")
        print("   nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > bot.log 2>&1 &")
    
    elif not has_recent_activity:
        print("⚠️ Bot running but no recent activity")
        print()
        print("   Options:")
        print("   1. Wait 5 more minutes (may be initializing)")
        print("   2. Check for errors: tail -50 bot.log")
        print("   3. Restart if needed")
    
    else:
        print("✅ Bot appears to be running")
        print()
        print("Next steps:")
        print("   1. Monitor for 30 minutes")
        print("   2. Verify toxic symbols are blocked")
        print("   3. Verify safe position sizing is used")
        print("   4. Check if balance is growing")
        print()
        print("If all checks pass:")
        print("   → Add $50-100 fresh testnet capital")
        print("   → Let it rebuild with protections")
        print("   → Monitor closely for first few hours")

except Exception as e:
    print(f"Could not determine status: {e}")

print()
print("="*70)

