import os
import shutil

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VAULT_SUBFOLDER = os.path.join(ROOT_DIR, "_BACKUP_VAULT_BEFORE_STITCH", "Lean-Trader-continue-from-micro-fix")

# The Final Missing Pieces Part 2 (From Vault Subfolder to Root)
RESTORE_LIST = [
    "critical_features_addon.py",
    "ULTRA_GOLDMINE_FEATURES.py"
]

def log(msg):
    print(f"[STITCHER_PASS_4] {msg}")

def perform_stitch_4():
    log("Initiating Phase 5: Recovering Hidden Addons...")
    
    restored_count = 0
    
    for item in RESTORE_LIST:
        src = os.path.join(VAULT_SUBFOLDER, item)
        dst = os.path.join(ROOT_DIR, item)
        
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                log(f"[OK] Restored File: {item}")
                restored_count += 1
            except Exception as e:
                log(f"[X] Failed to restore {item}: {e}")
        else:
            log(f" Missing Source in Vault Subfolder: {item}")
            
    log(f"Stitch Pass 4 Complete. Restored {restored_count} components.")

if __name__ == "__main__":
    perform_stitch_4()
