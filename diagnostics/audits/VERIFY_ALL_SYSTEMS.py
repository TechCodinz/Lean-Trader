#!/usr/bin/env python3
"""
CRITICAL DIAGNOSTIC: Are all 205+ engines actually WORKING?

This checks:
1. Which systems are initialized
2. Which systems are being CALLED during trading
3. Whether collective consensus is active
4. Whether systems are learning/adapting
5. Which engines are DORMANT (initialized but never used)
"""

import re
from collections import defaultdict

print("="*80)
print("🔍 COMPREHENSIVE SYSTEM HEALTH CHECK")
print("="*80)
print()

# ============================================================================
# 1. CHECK WHICH ENGINES ARE INITIALIZED
# ============================================================================
print("1️⃣ CHECKING WHICH ENGINES ARE INITIALIZED")
print("-" * 80)

try:
    with open('bot.log', 'r', errors='ignore') as f:
        logs = f.read()
    
    initialized_systems = []
    
    # Look for initialization messages
    init_patterns = [
        r'✅.*LOADED',
        r'✅.*initialized',
        r'✅.*ready',
        r'Initializing.*Engine',
        r'Loading.*system'
    ]
    
    for pattern in init_patterns:
        matches = re.findall(pattern, logs, re.IGNORECASE)
        initialized_systems.extend(matches)
    
    print(f"Found {len(initialized_systems)} initialization messages:")
    for i, sys in enumerate(initialized_systems[:20], 1):  # Show first 20
        print(f"   {i}. {sys}")
    
    if len(initialized_systems) > 20:
        print(f"   ... and {len(initialized_systems) - 20} more")
    
    print()

except Exception as e:
    print(f"❌ Error reading logs: {e}")
    print()

# ============================================================================
# 2. CHECK IF COLLECTIVE CONSENSUS IS ACTIVE
# ============================================================================
print("2️⃣ CHECKING COLLECTIVE CONSENSUS ACTIVITY")
print("-" * 80)

try:
    # Search for collective consensus messages
    collective_patterns = [
        r'collective.*consensus',
        r'swarm.*intelligence',
        r'collective.*scrutiny',
        r'APPROVED|REJECTED',
        r'ensemble.*vote',
        r'consensus.*threshold'
    ]
    
    collective_activity = 0
    collective_messages = []
    
    for pattern in collective_patterns:
        matches = re.findall(f'.*{pattern}.*', logs, re.IGNORECASE)
        collective_activity += len(matches)
        collective_messages.extend(matches[:5])  # Sample
    
    if collective_activity > 0:
        print(f"✅ Collective consensus IS active: {collective_activity} messages found")
        print()
        print("Sample messages:")
        for msg in collective_messages[:10]:
            print(f"   {msg[:120]}")
    else:
        print("❌ NO collective consensus activity found!")
        print("   🚨 This means trades are NOT being validated by the swarm!")
        print("   🚨 Engines are initialized but NOT consulting each other!")
    
    print()

except Exception as e:
    print(f"Error: {e}")
    print()

# ============================================================================
# 3. CHECK WHICH ENGINES ARE CALLED DURING TRADES
# ============================================================================
print("3️⃣ CHECKING WHICH ENGINES ARE ACTUALLY USED IN TRADING")
print("-" * 80)

try:
    # Look for engine activity during trade execution
    engine_calls = defaultdict(int)
    
    engine_patterns = {
        'Adaptive Confidence': r'adaptive.*confidence|adjust.*threshold',
        'Predictive Engine': r'predictive.*engine|prediction.*made',
        'Quantum System': r'quantum.*analysis|quantum.*signal',
        'Fractal Analysis': r'fractal.*detected|fractal.*pattern',
        'Order Book Imbalance': r'order.*book.*imbalance',
        'Liquidity Detection': r'liquidity.*detected|liquidity.*analysis',
        'Volume Profile': r'volume.*profile|volume.*analysis',
        'Smart Money': r'smart.*money|institutional.*flow',
        'Hidden Orders': r'hidden.*order|iceberg.*detected',
        'Market Regime': r'regime.*change|market.*regime',
        'Volatility Clustering': r'volatility.*cluster',
        'Correlation Matrix': r'correlation.*analyzed',
    }
    
    for engine_name, pattern in engine_patterns.items():
        matches = re.findall(pattern, logs, re.IGNORECASE)
        engine_calls[engine_name] = len(matches)
    
    print("Engine call frequency:")
    active_engines = 0
    dormant_engines = 0
    
    for engine, count in sorted(engine_calls.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"   ✅ {engine:30s}: {count:4d} calls")
            active_engines += 1
        else:
            print(f"   ❌ {engine:30s}: {count:4d} calls (DORMANT!)")
            dormant_engines += 1
    
    print()
    print(f"Summary: {active_engines} active, {dormant_engines} dormant")
    
    if dormant_engines > active_engines:
        print()
        print("🚨 WARNING: Most engines are DORMANT!")
        print("   Initialized but never called during trading!")
    
    print()

except Exception as e:
    print(f"Error: {e}")
    print()

# ============================================================================
# 4. CHECK IF SYSTEMS ARE LEARNING/ADAPTING
# ============================================================================
print("4️⃣ CHECKING IF SYSTEMS ARE LEARNING/ADAPTING")
print("-" * 80)

try:
    learning_patterns = [
        r'learning|learned',
        r'adapt|adapted|adapting',
        r'threshold.*adjusted',
        r'confidence.*changed',
        r'model.*updated',
        r'performance.*improved'
    ]
    
    learning_activity = 0
    learning_messages = []
    
    for pattern in learning_patterns:
        matches = re.findall(f'.*{pattern}.*', logs, re.IGNORECASE)
        learning_activity += len(matches)
        learning_messages.extend(matches[:3])
    
    if learning_activity > 10:
        print(f"✅ Systems ARE learning: {learning_activity} learning events")
        print()
        print("Sample:")
        for msg in learning_messages[:5]:
            print(f"   {msg[:120]}")
    else:
        print(f"⚠️ Limited learning activity: Only {learning_activity} events")
        print("   Systems may not be adapting to market conditions")
    
    print()

except Exception as e:
    print(f"Error: {e}")
    print()

# ============================================================================
# 5. CHECK TRADE EXECUTION FLOW
# ============================================================================
print("5️⃣ ANALYZING TRADE EXECUTION FLOW")
print("-" * 80)

try:
    # Count how many trades went through what checks
    signal_count = len(re.findall(r'signal.*detected|SIGNAL', logs, re.IGNORECASE))
    validation_count = len(re.findall(r'validat|verify|check', logs, re.IGNORECASE))
    executed_count = len(re.findall(r'EXECUTING|ORDER PLACED', logs, re.IGNORECASE))
    closed_count = len(re.findall(r'POSITION CLOSED', logs, re.IGNORECASE))
    
    print(f"Signal detections:     {signal_count:4d}")
    print(f"Validations performed: {validation_count:4d}")
    print(f"Orders executed:       {executed_count:4d}")
    print(f"Positions closed:      {closed_count:4d}")
    
    print()
    
    if signal_count > 0:
        execution_rate = (executed_count / signal_count) * 100
        print(f"Execution rate: {execution_rate:.1f}% of signals become trades")
        
        if execution_rate > 80:
            print("   ⚠️  Very high execution rate!")
            print("   Filters may not be working (should reject bad signals)")
        elif execution_rate < 10:
            print("   ⚠️  Very low execution rate!")
            print("   Filters may be too strict")
        else:
            print("   ✅ Reasonable execution rate")
    
    print()

except Exception as e:
    print(f"Error: {e}")
    print()

# ============================================================================
# 6. FINAL DIAGNOSIS
# ============================================================================
print("="*80)
print("🎯 DIAGNOSIS & RECOMMENDATIONS")
print("="*80)
print()

issues_found = []

# Check collective consensus
if collective_activity == 0:
    issues_found.append("❌ CRITICAL: Collective consensus NOT running")
    issues_found.append("   → Trades executing without swarm validation")
    issues_found.append("   → Only 1 engine deciding, not 205!")

# Check dormant engines
if dormant_engines > 5:
    issues_found.append(f"❌ MAJOR: {dormant_engines} engines are DORMANT")
    issues_found.append("   → Engines initialized but never called")
    issues_found.append("   → Wasted potential!")

# Check learning
if learning_activity < 10:
    issues_found.append("⚠️ WARNING: Limited learning/adaptation")
    issues_found.append("   → Systems not improving over time")

if issues_found:
    print("ISSUES FOUND:")
    print()
    for issue in issues_found:
        print(issue)
    print()
    print("="*80)
    print("🔧 RECOMMENDED FIXES:")
    print("="*80)
    print()
    print("1. Enable collective consensus filter")
    print("   → Make sure ALL engines vote before executing")
    print()
    print("2. Activate dormant engines")
    print("   → Wire them into the execution flow")
    print()
    print("3. Enable learning/adaptation")
    print("   → Systems should learn from wins/losses")
    print()
else:
    print("✅ All systems appear to be working correctly!")
    print()
    print("If performance is still poor, the issue is:")
    print("  • Market conditions (not suitable for strategy)")
    print("  • Parameter tuning needed")
    print("  • Strategy logic flaws")

print()
print("="*80)
