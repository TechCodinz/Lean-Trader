import os
import shutil

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VAULT_ROOT = os.path.join(ROOT_DIR, "_BACKUP_VAULT_BEFORE_STITCH")

# The Final Missing Pieces (From Vault Root to Root)
RESTORE_LIST = [
    "CROSS_VENUE_CAPITAL_MANAGER.py",
    "PROFIT_OPTIMIZATION_ENGINE.py",
    "BYBIT_EXECUTION_BRIDGE.py",
    "LIVE_VERIFY.py",
    "RESTART_AND_VERIFY.py",
    "FINAL_EXEC_TEST.py",
    "DEEP_TRACE.py"
]

def log(msg):
    print(f"[STITCHER_PASS_3] {msg}")

def perform_stitch_3():
    log("Initiating Phase 4: Recovering Final Engines...")
    
    restored_count = 0
    
    for item in RESTORE_LIST:
        src = os.path.join(VAULT_ROOT, item)
        dst = os.path.join(ROOT_DIR, item)
        
        if os.path.exists(src):
            try:
                shutil.copy2(src, dst)
                log(f"[OK] Restored File: {item}")
                restored_count += 1
            except Exception as e:
                log(f"[X] Failed to restore {item}: {e}")
        else:
            log(f" Missing Source in Vault Root: {item}")
            
    log(f"Stitch Pass 3 Complete. Restored {restored_count} components.")

if __name__ == "__main__":
    perform_stitch_3()
