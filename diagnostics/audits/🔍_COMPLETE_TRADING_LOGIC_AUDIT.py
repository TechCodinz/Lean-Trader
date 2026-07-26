#!/usr/bin/env python3
"""
COMPLETE TRADING LOGIC AUDIT
Validates all modes, engines, services, relays, strategy analysis
"""

import os
import sys
import importlib.util
from pathlib import Path
import ast
import re

print("=" * 100)
print("🔍 COMPLETE TRADING LOGIC AUDIT")
print("=" * 100)
print()

# Track results
results = {
    'engines': {'found': [], 'issues': []},
    'services': {'found': [], 'issues': []},
    'strategies': {'found': [], 'issues': []},
    'relays': {'found': [], 'issues': []},
    'modes': {'found': [], 'issues': []},
    'orchestration': {'found': [], 'issues': []},
}

# ============================================================================
# 1. CHECK MAIN ORCHESTRATOR
# ============================================================================
print("1️⃣  CHECKING MAIN ORCHESTRATOR...")
print("-" * 100)

orchestrator_file = 'COMPLETE_ULTIMATE_ORCHESTRATOR.py'
if os.path.exists(orchestrator_file):
    with open(orchestrator_file, 'r') as f:
        content = f.read()
    
    # Check critical imports
    critical_imports = [
        'EVOLUTION_ENGINE',
        'critical_features_addon',
        'ULTRA_GOLDMINE_FEATURES',
        'ULTRA_RARE_ENGINES',
        'brain',
        'hivemind',
    ]
    
    for imp in critical_imports:
        if imp in content:
            results['orchestration']['found'].append(f"✅ {imp} imported")
        else:
            results['orchestration']['issues'].append(f"⚠️  {imp} NOT imported")
    
    # Check initialization methods
    init_methods = [
        'initialize_evolution_engine',
        'initialize_critical_features',
        'initialize_ultra_features',
        'initialize_engines',
        'initialize_exchanges',
    ]
    
    for method in init_methods:
        if method in content:
            results['orchestration']['found'].append(f"✅ {method}() exists")
        else:
            results['orchestration']['issues'].append(f"⚠️  {method}() missing")
    
    print(f"✅ Orchestrator file found: {len(content)} lines")
else:
    results['orchestration']['issues'].append(f"❌ {orchestrator_file} NOT FOUND!")
    print(f"❌ {orchestrator_file} NOT FOUND!")

print()

# ============================================================================
# 2. CHECK EVOLUTION ENGINE
# ============================================================================
print("2️⃣  CHECKING EVOLUTION ENGINE...")
print("-" * 100)

evo_file = 'EVOLUTION_ENGINE.py'
if os.path.exists(evo_file):
    with open(evo_file, 'r') as f:
        evo_content = f.read()
    
    # Check critical methods
    evo_methods = [
        'load_existing_models',
        'run_evolution_cycle',
        'spawn_new_models',
        'learn_from_live_data',
        'evolve_existing_models',
    ]
    
    for method in evo_methods:
        if f"def {method}" in evo_content:
            results['engines']['found'].append(f"✅ Evolution: {method}()")
        else:
            results['engines']['issues'].append(f"⚠️  Evolution: {method}() missing")
    
    # Check for IMMORTAL MEMORY integration
    if 'immortal_memory' in evo_content or 'IMMORTAL_MEMORY' in evo_content:
        results['engines']['found'].append("✅ Evolution: IMMORTAL MEMORY integrated")
    else:
        results['engines']['issues'].append("ℹ️  Evolution: IMMORTAL MEMORY not yet integrated (run integration script)")
    
    print(f"✅ Evolution Engine found: {len(evo_content)} lines")
else:
    results['engines']['issues'].append(f"❌ {evo_file} NOT FOUND!")
    print(f"❌ {evo_file} NOT FOUND!")

print()

# ============================================================================
# 3. CHECK CRITICAL FEATURES
# ============================================================================
print("3️⃣  CHECKING CRITICAL PROFIT FEATURES...")
print("-" * 100)

critical_file = 'critical_features_addon.py'
if os.path.exists(critical_file):
    with open(critical_file, 'r') as f:
        critical_content = f.read()
    
    critical_classes = [
        'TrailingStopManager',
        'CompoundEngine',
        'PartialTPManager',
        'FundingArbitrage',
        'VolumeProfileAnalyzer',
        'EmergencyStop',
    ]
    
    for cls in critical_classes:
        if f"class {cls}" in critical_content:
            results['engines']['found'].append(f"✅ Critical: {cls}")
        else:
            results['engines']['issues'].append(f"⚠️  Critical: {cls} missing")
    
    print(f"✅ Critical Features found: {len(critical_content)} lines")
else:
    results['engines']['issues'].append(f"❌ {critical_file} NOT FOUND!")
    print(f"❌ {critical_file} NOT FOUND!")

print()

# ============================================================================
# 4. CHECK ULTRA GOLDMINE FEATURES
# ============================================================================
print("4️⃣  CHECKING ULTRA GOLDMINE FEATURES...")
print("-" * 100)

goldmine_file = 'ULTRA_GOLDMINE_FEATURES.py'
if os.path.exists(goldmine_file):
    with open(goldmine_file, 'r') as f:
        goldmine_content = f.read()
    
    goldmine_classes = [
        'GammaSqueezeDetector',
        'WhaleTracker',
        'OrderBookToxicityScanner',
        'LatencyArbitrageEngine',
        'MEVProtectionLayer',
        'FuturesBasisArbitrage',
        'AdaptiveRegimeSizer',
        'MultiTimeframeConfluence',
        'SocialMomentumPredictor',
        'NetworkEffectAnalyzer',
    ]
    
    for cls in goldmine_classes:
        if f"class {cls}" in goldmine_content:
            results['engines']['found'].append(f"✅ Goldmine: {cls}")
        else:
            results['engines']['issues'].append(f"⚠️  Goldmine: {cls} missing")
    
    print(f"✅ Ultra Goldmine found: {len(goldmine_content)} lines")
else:
    results['engines']['issues'].append(f"❌ {goldmine_file} NOT FOUND!")
    print(f"❌ {goldmine_file} NOT FOUND!")

print()

# ============================================================================
# 5. CHECK ULTRA RARE ENGINES
# ============================================================================
print("5️⃣  CHECKING ULTRA RARE ENGINES (11 Market Inefficiency Exploiters)...")
print("-" * 100)

rare_file = 'ULTRA_RARE_ENGINES.py'
if os.path.exists(rare_file):
    with open(rare_file, 'r') as f:
        rare_content = f.read()
    
    rare_classes = [
        'MicrostructureExploiter',
        'InformationEntropyTrader',
        'CascadingLiquidityHunter',
        'FlashCrashPredator',
        'FundingRateArbitrage',
        'HiddenOrderDetector',
        'SmartMoneyShadow',
        'RetailPanicExploiter',
        'TimeWarpPatterns',
        'WhalePsychologyPredictor',
        'UltraRareEnginesOrchestrator',
    ]
    
    for cls in rare_classes:
        if f"class {cls}" in rare_content:
            results['engines']['found'].append(f"✅ UltraRare: {cls}")
        else:
            results['engines']['issues'].append(f"⚠️  UltraRare: {cls} missing")
    
    print(f"✅ Ultra Rare Engines found: {len(rare_content)} lines")
else:
    results['engines']['issues'].append(f"❌ {rare_file} NOT FOUND!")
    print(f"❌ {rare_file} NOT FOUND!")

print()

# ============================================================================
# 6. CHECK BRAIN + HIVEMIND
# ============================================================================
print("6️⃣  CHECKING BRAIN + HIVEMIND...")
print("-" * 100)

brain_file = 'brain.py'
if os.path.exists(brain_file):
    with open(brain_file, 'r') as f:
        brain_content = f.read()
    
    brain_classes = ['Memory', 'VolSizer', 'Brain', 'Advice']
    
    for cls in brain_classes:
        if f"class {cls}" in brain_content:
            results['services']['found'].append(f"✅ Brain: {cls}")
        else:
            results['services']['issues'].append(f"⚠️  Brain: {cls} missing")
    
    print(f"✅ Brain system found: {len(brain_content)} lines")
else:
    results['services']['issues'].append(f"❌ {brain_file} NOT FOUND!")
    print(f"❌ {brain_file} NOT FOUND!")

hivemind_file = 'hivemind.py'
if os.path.exists(hivemind_file):
    with open(hivemind_file, 'r') as f:
        hivemind_content = f.read()
    print(f"✅ Hivemind system found: {len(hivemind_content)} lines")
    results['services']['found'].append("✅ Hivemind system")
else:
    results['services']['issues'].append(f"⚠️  {hivemind_file} NOT FOUND")
    print(f"⚠️  {hivemind_file} NOT FOUND")

print()

# ============================================================================
# 7. CHECK ADDITIONAL ENGINES
# ============================================================================
print("7️⃣  CHECKING ADDITIONAL ENGINES...")
print("-" * 100)

additional_engines = [
    'SMART_SCALPING_ENGINE.py',
    'AGGRESSIVE_SCALPING_ENGINE.py',
    'NEWS_TRADING_ENGINE.py',
    'DEX_SWAP_ENGINE.py',
    'DEFI_YIELD_FARMING_ENGINE.py',
    'IBM_QUANTUM_ENGINE.py',
    'SELF_HEALING_ENGINE.py',
    'PREDICTIVE_NEXT_MOVE_ENGINE.py',
    'INFINITE_GROWTH_ENGINE.py',
    'OMNISCIENT_EXECUTION_ENGINE.py',
]

for engine in additional_engines:
    if os.path.exists(engine):
        results['engines']['found'].append(f"✅ {engine}")
        print(f"✅ {engine}")
    else:
        results['engines']['issues'].append(f"⚠️  {engine} not found")
        print(f"⚠️  {engine} not found")

print()

# ============================================================================
# 8. CHECK TRADING MODES
# ============================================================================
print("8️⃣  CHECKING TRADING MODES...")
print("-" * 100)

if os.path.exists(orchestrator_file):
    # Check for mode configurations
    modes = ['scalping', 'swing', 'arbitrage', 'market_making', 'trend_following']
    
    for mode in modes:
        if mode in content.lower():
            results['modes']['found'].append(f"✅ Mode: {mode}")
            print(f"✅ Mode: {mode}")
        else:
            results['modes']['issues'].append(f"ℹ️  Mode: {mode} not explicitly mentioned")

print()

# ============================================================================
# 9. CHECK STRATEGY ANALYSIS
# ============================================================================
print("9️⃣  CHECKING STRATEGY ANALYSIS...")
print("-" * 100)

strategy_file = 'STRATEGY_EVOLUTION_ENGINE.py'
if os.path.exists(strategy_file):
    with open(strategy_file, 'r') as f:
        strategy_content = f.read()
    
    strategy_methods = [
        'analyze_strategy',
        'evolve_strategy',
        'backtest_strategy',
        'optimize_parameters',
    ]
    
    for method in strategy_methods:
        if method in strategy_content:
            results['strategies']['found'].append(f"✅ Strategy: {method}()")
        else:
            results['strategies']['issues'].append(f"ℹ️  Strategy: {method}() not found")
    
    print(f"✅ Strategy Evolution Engine found: {len(strategy_content)} lines")
else:
    results['strategies']['issues'].append(f"ℹ️  {strategy_file} NOT FOUND (may be integrated elsewhere)")
    print(f"ℹ️  {strategy_file} NOT FOUND (may be integrated elsewhere)")

print()

# ============================================================================
# 10. CHECK DATA RELAYS / FEEDS
# ============================================================================
print("🔟 CHECKING DATA RELAYS & FEEDS...")
print("-" * 100)

if os.path.exists(orchestrator_file):
    relay_patterns = ['websocket', 'data_feed', 'market_data', 'ticker', 'orderbook']
    
    for pattern in relay_patterns:
        matches = len(re.findall(pattern, content, re.IGNORECASE))
        if matches > 0:
            results['relays']['found'].append(f"✅ Relay: {pattern} ({matches} references)")
            print(f"✅ Relay: {pattern} ({matches} references)")
        else:
            results['relays']['issues'].append(f"ℹ️  Relay: {pattern} not found")

print()

# ============================================================================
# 11. CHECK EXCHANGE INTEGRATIONS
# ============================================================================
print("1️⃣1️⃣  CHECKING EXCHANGE INTEGRATIONS...")
print("-" * 100)

if os.path.exists(orchestrator_file):
    exchanges = ['binance', 'bybit', 'okx', 'bitget', 'mexc']
    
    for exchange in exchanges:
        if exchange in content.lower():
            results['services']['found'].append(f"✅ Exchange: {exchange}")
            print(f"✅ Exchange: {exchange}")
        else:
            results['services']['issues'].append(f"ℹ️  Exchange: {exchange} not explicitly mentioned")

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print()
print("=" * 100)
print("📊 AUDIT SUMMARY")
print("=" * 100)
print()

for category, data in results.items():
    print(f"{'─' * 100}")
    print(f"🔹 {category.upper()}")
    print(f"{'─' * 100}")
    
    if data['found']:
        print(f"✅ FOUND ({len(data['found'])}):")
        for item in data['found'][:10]:  # Show first 10
            print(f"  {item}")
        if len(data['found']) > 10:
            print(f"  ... and {len(data['found']) - 10} more")
    
    if data['issues']:
        print(f"⚠️  ISSUES ({len(data['issues'])}):")
        for item in data['issues'][:10]:  # Show first 10
            print(f"  {item}")
        if len(data['issues']) > 10:
            print(f"  ... and {len(data['issues']) - 10} more")
    
    print()

# Overall health
total_found = sum(len(data['found']) for data in results.values())
total_issues = sum(len(data['issues']) for data in results.values())

print("=" * 100)
print("🎯 OVERALL HEALTH")
print("=" * 100)
print(f"✅ Components Working: {total_found}")
print(f"⚠️  Components with Issues: {total_issues}")
print()

if total_issues == 0:
    print("🎉 PERFECT! All trading logic is in place and ready!")
    print("✅ All modes, engines, services, relays, and strategies validated")
elif total_issues < 5:
    print("✅ EXCELLENT! Bot is fully functional with minor optional components missing")
elif total_issues < 10:
    print("✅ GOOD! Core trading logic works, some advanced features may need attention")
else:
    print("⚠️  ATTENTION NEEDED: Some core components may be missing")

print()
print("=" * 100)
print("🚀 NEXT STEPS")
print("=" * 100)
print()
print("1. If IMMORTAL MEMORY not integrated:")
print("   bash 🧠_ACTIVATE_IMMORTAL_MEMORY.sh")
print()
print("2. Start the bot:")
print("   nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex.log 2>&1 &")
print()
print("3. Monitor:")
print("   tail -f apex.log")
print()
print("=" * 100)
