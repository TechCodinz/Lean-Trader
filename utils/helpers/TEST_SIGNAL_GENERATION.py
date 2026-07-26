#!/usr/bin/env python3
"""
Test signal generation to see what symbols are analyzed
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

print("🔍 Testing signal generation...")
print()

try:
    # Try to import and test the collective consensus
    from COLLECTIVE_CONSENSUS_ENGINE import CollectiveConsensusEngine
    
    print("[OK] Imported CollectiveConsensusEngine")
    
    # Create instance
    consensus = CollectiveConsensusEngine()
    print(f"[OK] Created instance")
    print(f"   min_confidence: {getattr(consensus, 'min_confidence', 'NOT SET')}")
    print(f"   min_agreement: {getattr(consensus, 'min_agreement', 'NOT SET')}")
    
    # Check what symbols it would analyze
    if hasattr(consensus, 'get_tradeable_symbols'):
        symbols = consensus.get_tradeable_symbols()
        print(f"[OK] Tradeable symbols: {len(symbols)}")
        print(f"   {symbols[:20]}")  # First 20
    elif hasattr(consensus, 'symbols'):
        print(f"[OK] Symbols: {consensus.symbols[:20]}")
    else:
        print("  No symbol list found in consensus engine")
    
except ImportError as e:
    print(f"[X] Could not import CollectiveConsensusEngine: {e}")
except Exception as e:
    print(f"  Error testing consensus: {e}")

print()

# Try execution orchestrator
try:
    from EXECUTION_ORCHESTRATOR import ExecutionOrchestrator
    
    print("[OK] Imported ExecutionOrchestrator")
    
    # Check what it has configured
    import inspect
    source = inspect.getsource(ExecutionOrchestrator.__init__)
    
    # Look for symbol configuration
    if 'symbols' in source.lower() or 'pairs' in source.lower():
        print("[OK] Found symbol configuration in ExecutionOrchestrator.__init__")
        for line in source.split('\n'):
            if 'symbol' in line.lower() or 'pair' in line.lower():
                print(f"   {line.strip()}")
    
except ImportError as e:
    print(f"[X] Could not import ExecutionOrchestrator: {e}")
except Exception as e:
    print(f"  Error: {e}")

