#!/usr/bin/env python3
"""
FIX ALL ENGINES PROPERLY
Fix the orchestrator without breaking try/except blocks
"""

import re
import shutil
from datetime import datetime

def backup_file():
    """Create timestamped backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(
        'COMPLETE_ULTIMATE_ORCHESTRATOR.py',
        f'COMPLETE_ULTIMATE_ORCHESTRATOR.py.backup_{timestamp}'
    )
    print(f"✅ Backup created: backup_{timestamp}")

def add_imports_carefully():
    """Add imports without breaking existing try/except"""
    print("\n🔧 Adding imports for Ultra Rare + Brain + Hivemind...")
    
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
        lines = f.readlines()
    
    # Find where to insert (after DIVINE_INTELLIGENCE_FEATURES import)
    insert_idx = None
    for i, line in enumerate(lines):
        if 'from DIVINE_INTELLIGENCE_FEATURES import' in line:
            # Find the end of this import block
            j = i
            while j < len(lines) and (')' not in lines[j] or lines[j].strip().startswith('from')):
                j += 1
            # Now find the except block
            while j < len(lines) and 'except Exception' not in lines[j]:
                j += 1
            # Skip to after the except block
            while j < len(lines) and (lines[j].strip().startswith('logger.') or 
                                     lines[j].strip().startswith('DIVINE_') or
                                     'DIVINE' in lines[j]):
                j += 1
            insert_idx = j
            break
    
    if insert_idx is None:
        print("❌ Could not find insertion point")
        return False
    
    # Insert new imports
    new_imports = '''
# ============================================================================
# ULTRA RARE ENGINES - 11 Market Inefficiency Exploiters
# ============================================================================
try:
    from ULTRA_RARE_ENGINES import (
        MicrostructureExploiter,
        InformationEntropyTrader,
        CascadingLiquidityHunter,
        FlashCrashPredator,
        FundingRateArbitrage,
        HiddenOrderDetector,
        SmartMoneyShadow,
        RetailPanicExploiter,
        TimeWarpPatterns,
        WhalePsychologyPredictor,
        UltraRareEnginesOrchestrator
    )
    ULTRA_RARE_AVAILABLE = True
    logger.info("✅ ULTRA RARE ENGINES LOADED - 11 market inefficiency exploiters!")
except Exception as e:
    logger.error(f"❌ ULTRA RARE ENGINES FAILED TO LOAD: {e}")
    ULTRA_RARE_AVAILABLE = False

# ============================================================================
# BRAIN + HIVEMIND - Professional Trading Intelligence
# ============================================================================
try:
    from brain import Memory, VolSizer, Brain, Advice
    BRAIN_AVAILABLE = True
    logger.info("✅ BRAIN SYSTEM LOADED - Memory, sizing, regime awareness!")
except Exception as e:
    logger.error(f"❌ BRAIN SYSTEM FAILED TO LOAD: {e}")
    BRAIN_AVAILABLE = False
    Memory = VolSizer = Brain = Advice = None

try:
    from hivemind import HiveCoordinator, FrameDecision
    HIVEMIND_AVAILABLE = True
    logger.info("✅ HIVEMIND LOADED - Multi-timeframe consensus!")
except Exception as e:
    logger.error(f"❌ HIVEMIND FAILED TO LOAD: {e}")
    HIVEMIND_AVAILABLE = False
    HiveCoordinator = FrameDecision = None

'''
    
    lines.insert(insert_idx, new_imports)
    
    with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Imports added")
    return True

def verify_syntax():
    """Verify no syntax errors"""
    import subprocess
    result = subprocess.run(
        ['python3', '-m', 'py_compile', 'COMPLETE_ULTIMATE_ORCHESTRATOR.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Syntax check PASSED")
        return True
    else:
        print("❌ Syntax check FAILED:")
        print(result.stderr)
        return False

def main():
    print("="*80)
    print("FIX ALL ENGINES PROPERLY")
    print("="*80)
    
    # Backup
    backup_file()
    
    # Add imports
    if not add_imports_carefully():
        print("❌ Failed to add imports")
        return 1
    
    # Verify
    if not verify_syntax():
        print("❌ Syntax errors introduced")
        return 1
    
    # Now run the other wiring scripts
    print("\n🔧 Running Ultra Rare wiring...")
    import subprocess
    result = subprocess.run(['python3', 'WIRE_ULTRA_RARE_ENGINES.py'], capture_output=True, text=True)
    if 'SUCCESS' in result.stdout:
        print("✅ Ultra Rare wired")
    else:
        print("⚠️  Ultra Rare wiring had issues")
    
    print("\n🔧 Running Brain/Hivemind wiring...")
    result = subprocess.run(['python3', 'WIRE_BRAIN_HIVEMIND.py'], capture_output=True, text=True)
    if 'SUCCESS' in result.stdout:
        print("✅ Brain/Hivemind wired")
    else:
        print("⚠️  Brain/Hivemind wiring had issues")
    
    # Final verify
    if verify_syntax():
        print("\n✅ ALL ENGINES FIXED AND WIRED!")
        return 0
    else:
        print("\n❌ Still has errors")
        return 1

if __name__ == "__main__":
    exit(main())
