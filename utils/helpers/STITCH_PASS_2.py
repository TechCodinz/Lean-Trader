import os
import shutil

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VAULT_SUBFOLDER = os.path.join(ROOT_DIR, "_BACKUP_VAULT_BEFORE_STITCH", "Lean-Trader-continue-from-micro-fix")

# The Army to Restore (From Subfolder to Root)
RESTORE_LIST = [
    "EXECUTION_ORCHESTRATOR.py",          # 148KB version (vs 86KB in vault root)
    "HYBRID_INTELLIGENCE_COORDINATOR.py", # Only in subfolder
    "EXCHANGE_SPAWN_MANAGER.py",          # Only in subfolder
    "CROSS_VENUE_CAPITAL_MANAGER.py",
    "PROFIT_OPTIMIZATION_ENGINE.py",
    "MARKET_DATA_INTELLIGENCE.py",        # Critical for data
    "INTELLIGENT_EXCHANGE_ROUTER.py",     # Critical for routing
    "strategies",                         # Directory
    "utils",                              # Directory
    "config",                             # Directory
    "requirements.txt",                   # Missing in root
    "nobel_ai_models.py",                 # Likely needed
    "divine_intelligence_core.py"         # Likely needed
]

def log(msg):
    print(f"[STITCHER_PASS_2] {msg}")

def perform_stitch_2():
    log("Initiating Phase 3: reuniting the Army...")
    
    restored_count = 0
    
    for item in RESTORE_LIST:
        src = os.path.join(VAULT_SUBFOLDER, item)
        dst = os.path.join(ROOT_DIR, item)
        
        if os.path.exists(src):
            try:
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    log(f"[OK] Restored Directory: {item}")
                else:
                    shutil.copy2(src, dst)
                    log(f"[OK] Restored File: {item}")
                restored_count += 1
            except Exception as e:
                log(f"[X] Failed to restore {item}: {e}")
        else:
            log(f" Missing Source in Subfolder: {item}")
            
    log(f"Stitch Pass 2 Complete. Restored {restored_count} components.")

if __name__ == "__main__":
    perform_stitch_2()
