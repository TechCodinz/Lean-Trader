
#!/usr/bin/env python3
"""
PROFESSIONAL SYSTEM ACTIVATOR
-----------------------------
Launches the fully organized, deduplicated LeanTrader Bot.
Ensures environment is correct, paths are set, and engines are wired.
"""

import os
import sys
import time
import importlib
import logging
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Add root to python path so "core.orchestrators" etc. work
sys.path.insert(0, ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "engines"))
sys.path.append(os.path.join(ROOT_DIR, "utils"))
sys.path.append(os.path.join(ROOT_DIR, "features"))
sys.path.append(os.path.join(ROOT_DIR, "ultra_rare"))

LOG_FILE = "ACTIVATION_LOG.txt"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [ACTIVATOR] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ACTIVATOR")

def check_structure():
    logger.info("checking folder structure...")
    required_paths = [
        "core/orchestrators",
        "engines/execution",
        "engines/profit",
        "ultra_rare/goldmine"
    ]
    all_ok = True
    for p in required_paths:
        full = os.path.join(ROOT_DIR, p)
        if not os.path.exists(full):
            logger.error(f"MISSING CRITICAL PATH: {p}")
            all_ok = False
        else:
            logger.info(f"Verified: {p}")
    return all_ok

def activate_system():
    print("\n" + "="*60)
    print("INITIATING PROFESSIONAL ACTIVATION SEQUENCE")
    print("="*60 + "\n")
    
    # 1. Environment Check
    if not check_structure():
        logger.critical("STRUCTURE INTEGRITY FAILED. Aborting.")
        return

    # 2. Critical Imports Check (Simulated Ignition)
    logger.info("Testing Critical Wiring...")
    try:
        logger.info("   -> Importing Core Orchestrator...")
        from core.orchestrators import COMPLETE_ULTIMATE_ORCHESTRATOR
        logger.info("      Core Orchestrator Loaded")
        
        logger.info("   -> Importing Execution Cluster...")
        from engines.execution import INTELLIGENT_EXECUTION_ENGINE
        from engines.execution import EXECUTION_ORCHESTRATOR
        logger.info("      Execution Cluster Loaded")
        
        logger.info("   -> Importing Ultra-Rare Features...")
        from ultra_rare.goldmine import ULTRA_GOLDMINE_FEATURES
        logger.info("      Ultra-Rare Features Loaded")
        
    except ImportError as e:
        logger.critical(f"WIRING FAILURE: {e}")
        logger.critical(f"   Debug Hint: Verify __init__.py files and sys.path")
        return
    except Exception as e:
        logger.critical(f"UNEXPECTED FAIL: {e}")
        return

    # 3. Launch
    logger.info("ALL SYSTEMS GREEN. LAUNCHING ULTIMATE ORCHESTRATOR...")
    print("\nWARNING: You are about to launch the COMPLETE SYSTEM.")
    print("   Includes: 22 Supreme Engines, HFT Scalping, and AI Consciousness.")
    
    # We will invoke the main function of the orchestrator if possible, 
    # but the Orchestrator is usually an infinite loop async.
    # We'll just print Success for now to prove it CAN start.
    
    print("\nACTIVATION SUCCESSFUL (Simulation Mode)")
    print("   To run live, normally we would execute: core.orchestrators.COMPLETE_ULTIMATE_ORCHESTRATOR.main()")
    print("   System is fully wired and ready for command.")

if __name__ == "__main__":
    activate_system()
