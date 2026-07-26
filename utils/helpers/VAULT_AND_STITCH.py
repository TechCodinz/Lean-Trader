import os
import shutil
import time

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VAULT_NAME = "_BACKUP_VAULT_BEFORE_STITCH"
VAULT_PATH = os.path.join(ROOT_DIR, VAULT_NAME)

# The "Golden" Map - Source Logic -> Destination
# Source is relative to the Vault (after moving)
# We move everything to Vault first, then copy out.
GOLDEN_MAP = {
    # The Supreme Commander (Root Version was 365KB vs Subfolder 351KB)
    "COMPLETE_ULTIMATE_ORCHESTRATOR.py": "COMPLETE_ULTIMATE_ORCHESTRATOR.py",
    
    # The Execution Engine (Root Version was patched by us)
    "INTELLIGENT_EXECUTION_ENGINE.py": "INTELLIGENT_EXECUTION_ENGINE.py",
    
    # Intelligence Coordinator (Root Version)
    "HYBRID_INTELLIGENCE_COORDINATOR.py": "HYBRID_INTELLIGENCE_COORDINATOR.py",
    
    # Evolution Engine (Subfolder Version was 89KB vs Root 71KB)
    os.path.join("Lean-Trader-continue-from-micro-fix", "EVOLUTION_ENGINE.py"): "EVOLUTION_ENGINE.py",
    
    # Swarm/Consciousness (Subfolder versions were more complete/recent in scan)
    os.path.join("Lean-Trader-continue-from-micro-fix", "AI_COLLECTIVE_CONSCIOUSNESS.py"): "AI_COLLECTIVE_CONSCIOUSNESS.py",
    os.path.join("Lean-Trader-continue-from-micro-fix", "SUPREME_CONSCIOUSNESS_CORE.py"): "SUPREME_CONSCIOUSNESS_CORE.py",
    os.path.join("Lean-Trader-continue-from-micro-fix", "SENTIENT_TRADING_BRAIN.py"): "SENTIENT_TRADING_BRAIN.py",
    os.path.join("Lean-Trader-continue-from-micro-fix", "hivemind.py"): "hivemind.py",
    
    # Critical Configs/Utils (Assuming Root is valid for these, if not we check subfolder)
    ".env": ".env",
    "requirements.txt": "requirements.txt",
}

def log(msg):
    print(f"[STITCHER] {msg}")

def perform_vaulting():
    log("Initiating Phase 1: Vaulting...")
    
    if not os.path.exists(VAULT_PATH):
        os.makedirs(VAULT_PATH)
        log(f"Created Vault: {VAULT_PATH}")
    
    # Move everything to Vault (except the vault itself and this script)
    for item in os.listdir(ROOT_DIR):
        if item == VAULT_NAME or item == "VAULT_AND_STITCH.py":
            continue
            
        src = os.path.join(ROOT_DIR, item)
        dst = os.path.join(VAULT_PATH, item)
        
        try:
            shutil.move(src, dst)
        except Exception as e:
            log(f"Failed to move {item}: {e}")
            
    log("Vaulting Complete. Root is clean (except script & vault).")

def perform_surgical_extraction():
    log("Initiating Phase 2: Surgical Extraction...")
    
    restored_count = 0
    
    for vault_rel_path, root_name in GOLDEN_MAP.items():
        src = os.path.join(VAULT_PATH, vault_rel_path)
        dst = os.path.join(ROOT_DIR, root_name)
        
        if os.path.exists(src):
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                log(f"[OK] Restored Golden Engine: {root_name} (from {vault_rel_path})")
                restored_count += 1
            except Exception as e:
                log(f"[X] Failed to restore {root_name}: {e}")
        else:
            log(f" Missing Golden Source: {vault_rel_path}")
            
    log(f"Extraction Complete. Restored {restored_count} Golden Engines.")

if __name__ == "__main__":
    perform_vaulting()
    perform_surgical_extraction()
    log("Operation Successful. The 'Ant Colony' is now consolidated.")
