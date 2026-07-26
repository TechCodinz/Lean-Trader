#!/usr/bin/env python3
"""
COMPREHENSIVE ENGINE AUDIT
Verifies ALL engines are properly initialized and working
"""

import sys
import re
from pathlib import Path

print("\n" + "="*80)
print("🔍 COMPREHENSIVE ENGINE AUDIT")
print("="*80 + "\n")

# ============================================================================
# PART 1: COUNT ALL AVAILABLE ENGINES IN CODEBASE
# ============================================================================

print("📦 PART 1: SCANNING CODEBASE FOR ALL ENGINES...\n")

engines_in_code = []

# Scan all Python files
for py_file in Path('.').glob('*.py'):
    if py_file.name.startswith('_'):
        continue
    
    try:
        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Find class definitions
        classes = re.findall(r'class\s+(\w+(?:Engine|Orchestrator|System|Manager|Coordinator|Bot)).*?:', content)
        for cls in classes:
            engines_in_code.append((py_file.name, cls))
    except:
        pass

print(f"✅ FOUND {len(engines_in_code)} ENGINE CLASSES IN CODEBASE:\n")
for i, (file, cls) in enumerate(sorted(set(engines_in_code)), 1):
    print(f"   {i:3}. {cls:40} ({file})")

# ============================================================================
# PART 2: CHECK WHAT'S IMPORTED IN MAIN ORCHESTRATOR
# ============================================================================

print(f"\n{'='*80}")
print("📥 PART 2: CHECKING IMPORTS IN COMPLETE_ULTIMATE_ORCHESTRATOR.py...\n")

try:
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        content = f.read()
    
    imports = re.findall(r'from\s+(\S+)\s+import\s+([^\n]+)', content)
    
    imported_engines = set()
    for module, items in imports:
        items = items.replace('(', '').replace(')', '').strip()
        for item in items.split(','):
            item = item.strip()
            if any(keyword in item for keyword in ['Engine', 'Orchestrator', 'System', 'Manager', 'Coordinator', 'Bot']):
                imported_engines.add(item)
    
    print(f"✅ IMPORTED {len(imported_engines)} ENGINES/SYSTEMS:\n")
    for i, eng in enumerate(sorted(imported_engines), 1):
        print(f"   {i:3}. {eng}")
        
except Exception as e:
    print(f"❌ Error reading orchestrator: {e}")
    imported_engines = set()

# ============================================================================
# PART 3: CHECK WHAT'S ACTUALLY INITIALIZED IN LOG
# ============================================================================

print(f"\n{'='*80}")
print("🚀 PART 3: CHECKING WHAT'S INITIALIZED IN apex_bot.log...\n")

try:
    with open('apex_bot.log', 'r') as f:
        log_content = f.read()
    
    # Count different types of initializations
    initialized = {
        'WIRED': len(re.findall(r'WIRED', log_content)),
        'STARTED': len(re.findall(r'STARTED', log_content)),
        'initialized': len(re.findall(r'initialized', log_content)),
        'ACTIVE': len(re.findall(r'ACTIVE', log_content)),
        'LOADED': len(re.findall(r'LOADED', log_content)),
        'ONLINE': len(re.findall(r'ONLINE', log_content)),
    }
    
    print("Initialization counts:")
    for key, count in initialized.items():
        print(f"   {key:15}: {count}")
    
    # Find specific engine names
    print("\n📊 SPECIFIC ENGINES FOUND IN LOG:\n")
    
    engine_patterns = [
        'CRITICAL PROFIT',
        'ULTRA GOLDMINE', 
        'ULTRA RARE',
        'DIVINE INTELLIGENCE',
        'BRAIN SYSTEM',
        'HIVEMIND',
        'EXECUTION',
        'TELEGRAM',
        'QUANTUM',
        'DEX',
        'NEWS',
        'HEDGE FUND',
        'SCALPING',
        'ARBITRAGE',
        'MONEY PRINTER',
        'AUTO PROFIT',
        'FOREX',
        'MOON SPOTTER',
        'SWARM',
        'EVOLUTION',
        'ML PIPELINE',
        'REVOLUTIONARY AI',
        'SENTIENT',
        'PERSISTENCE',
        'ONLINE LEARNER',
        'ADAPTIVE CONFIDENCE',
        'SITUATION AWARENESS',
        'MICRO TRADING',
        'CONTINUOUS'
    ]
    
    found_in_log = []
    for pattern in engine_patterns:
        matches = re.findall(f'.*{pattern}.*(?:WIRED|STARTED|initialized|ACTIVE|LOADED)', log_content, re.IGNORECASE)
        if matches:
            found_in_log.append((pattern, len(matches)))
            print(f"   ✅ {pattern:30}: {len(matches)} instance(s)")
    
    print(f"\n✅ TOTAL UNIQUE ENGINE TYPES IN LOG: {len(found_in_log)}")
    
except FileNotFoundError:
    print("❌ apex_bot.log not found - bot may not be running")
except Exception as e:
    print(f"❌ Error reading log: {e}")

# ============================================================================
# PART 4: COMPARISON & RECOMMENDATIONS
# ============================================================================

print(f"\n{'='*80}")
print("📊 PART 4: ANALYSIS & RECOMMENDATIONS\n")

print(f"   Classes in codebase:     {len(engines_in_code)}")
print(f"   Imported in orchestrator: {len(imported_engines)}")

try:
    print(f"   Running in bot log:       {len(found_in_log)}")
    
    if len(found_in_log) < len(imported_engines):
        missing = len(imported_engines) - len(found_in_log)
        print(f"\n⚠️  WARNING: {missing} engines imported but not initialized!")
        print(f"   This could mean:")
        print(f"   1. Bot is still starting up")
        print(f"   2. Some engines failed to initialize")
        print(f"   3. Initialization logged differently")
except:
    pass

print(f"\n{'='*80}")
print("✅ AUDIT COMPLETE")
print("="*80 + "\n")
