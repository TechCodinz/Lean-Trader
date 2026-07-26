
import os
import shutil
import glob

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
BACKUP_DIR = os.path.join(ROOT_DIR, "_DUPLICATES_BACKUP")
VAULT_DIR = os.path.join(ROOT_DIR, "_BACKUP_VAULT_BEFORE_STITCH")

# Critical Files Map (Filename -> Destination Folder relative to ROOT)
CRITICAL_MAP = {
    "COMPLETE_ULTIMATE_ORCHESTRATOR.py": "core/orchestrators",
    "INTELLIGENT_EXECUTION_ENGINE.py": "engines/execution",
    "HYBRID_INTELLIGENCE_COORDINATOR.py": "core/coordinators",
    "AI_COLLECTIVE_CONSCIOUSNESS.py": "ai/intelligence",
    "EVOLUTION_ENGINE.py": "engines/evolution",
    "COMPLETE_PROFIT_SYSTEM.py": "engines/profit",
    "COLLECTIVE_CONSENSUS_ENGINE.py": "ai/intelligence",
    "ENRICHED_SIGNAL_SYSTEM.py": "ai/intelligence",
    "CONSCIOUSNESS_HARMONIZER.py": "ai/intelligence",
    "ULTRA_GOLDMINE_FEATURES.py": "ultra_rare/goldmine",
    "ULTRA_RARE_ENGINES.py": "ultra_rare/goldmine",
    "EXECUTION_SAFETY_SYSTEM.py": "safety/risk",
    "CAPITAL_DEADLOCK_PREVENTION.py": "safety/deadlock",
    "COMPOUND_LOOP_PROOF_SYSTEM.py": "safety/validation",
    "EVENT_BASED_PROFIT_TRACER.py": "engines/profit",
    "ADAPTIVE_ENGINE_HARDENING.py": "safety/risk",
    "MARKET_DATA_INTELLIGENCE.py": "data/intelligence",
    "INTELLIGENT_EXCHANGE_ROUTER.py": "engines/routing",
    "BYBIT_EXECUTION_BRIDGE.py": "engines/routing",
    "EXECUTION_ORCHESTRATOR.py": "engines/execution"
}

def log(msg):
    print(f"[RESTORE] {msg}")

def find_best_copy(filename):
    """Find the best copy in backups (Duplicate Backup first, then Vault)"""
    # 1. Check Duplicates Backup
    p1 = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(p1):
        return p1
        
    # 2. Check Vault (recursive)
    # This is slow, so we try specific known paths if possible, or limited glob
    # But usually Vault has deep structure.
    # Let's try quick walk
    for root, dirs, files in os.walk(VAULT_DIR):
        if filename in files:
            return os.path.join(root, filename)
            
    return None

def restore_criticals():
    log("RESTORING CRITICAL ENGINES TO PROFESSIONAL STRUCTURE")
    
    restored = 0
    
    for filename, folder in CRITICAL_MAP.items():
        dest_dir = os.path.join(ROOT_DIR, folder)
        dest_path = os.path.join(dest_dir, filename)
        
        # Ensure destination folder exists
        os.makedirs(dest_dir, exist_ok=True)
        
        # Check if already there
        if os.path.exists(dest_path):
            log(f"[OK] Already exists: {filename} in {folder}")
            continue
            
        # Find copy
        src = find_best_copy(filename)
        
        if src:
            try:
                shutil.copy2(src, dest_path)
                log(f"[RESTORED] Restored: {filename} -> {folder}")
                restored += 1
            except Exception as e:
                log(f"[ERROR] Error restoring {filename}: {e}")
        else:
            log(f"[MISSING] MISSING: Could not find backup for {filename}")
            
    log(f"RESTORATION COMPLETE. Restored {restored} critical engines.")

if __name__ == "__main__":
    restore_criticals()
