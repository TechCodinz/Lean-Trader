
import os
import shutil

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VAULT_DIR = os.path.join(ROOT_DIR, "_BACKUP_VAULT_BEFORE_STITCH", "Lean-Trader-continue-from-micro-fix")

# The Supreme Engines & Pitch-Bent System
RESTORE_FILES = [
    "COMPLETE_PROFIT_SYSTEM.py",
    "COLLECTIVE_CONSENSUS_ENGINE.py",
    "ENRICHED_SIGNAL_SYSTEM.py",
    "CONSCIOUSNESS_HARMONIZER.py"
]

RESTORE_DIRS = [
    "pitch_bent"
]

def log(msg):
    print(f"[STITCHER_PASS_5] {msg}")

def perform_stitch_5():
    log("Initiating Phase 6: Recovering Supreme Intelligence & Pitch-Bent Systems...")
    
    # Restore Files
    restored_files = 0
    for item in RESTORE_FILES:
        src = os.path.join(VAULT_DIR, item)
        dst = os.path.join(ROOT_DIR, item)
        
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                log(f"[OK] Restored Engine: {item}")
                restored_files += 1
            except Exception as e:
                log(f"[X] Failed to restore {item}: {e}")
        else:
            log(f" Missing Source File: {item}")

    # Restore Directories
    restored_dirs = 0
    for item in RESTORE_DIRS:
        src = os.path.join(VAULT_DIR, item)
        dst = os.path.join(ROOT_DIR, item)
        
        if os.path.exists(src):
            try:
                if os.path.exists(dst):
                    shutil.rmtree(dst) # Clean overwrite
                shutil.copytree(src, dst)
                log(f"[OK] Restored Directory: {item}")
                restored_dirs += 1
            except Exception as e:
                log(f"[X] Failed to restore directory {item}: {e}")
        else:
             log(f" Missing Source Directory: {item}")
            
    log(f"Stitch Pass 5 Complete. Files: {restored_files}, Dirs: {restored_dirs}")

if __name__ == "__main__":
    perform_stitch_5()
