#!/usr/bin/env python3
"""
SIMPLIFIED ORCHESTRATOR STARTER
Loads the orchestrator with full error reporting
"""
import sys
import traceback

print("=" * 70)
print("STARTING COMPLETE ULTIMATE ORCHESTRATOR")
print("=" * 70)

try:
    print("\n[1/3] Importing orchestrator...")
    from COMPLETE_ULTIMATE_ORCHESTRATOR import CompleteUltimateOrchestrator, main
    print("[OK] Import successful!")
    
    print("\n[2/3] Starting async event loop...")
    import asyncio
    
    print("\n[3/3] Running main()...")
    asyncio.run(main())
    
except ImportError as e:
    print(f"\n[X] IMPORT ERROR: {e}")
    print("\nMissing module. Traceback:")
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"\n[X] RUNTIME ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
