
import os
import shutil
import glob

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VAULT_DIR = os.path.join(ROOT_DIR, "_BACKUP_VAULT_BEFORE_STITCH")

def log(msg):
    print(f"[ULTRA_RESTORE] {msg}")

def restore_ultras():
    log(">> Initiating MASS RESTORATION of all 'ULTRA' and 'SUPREME' engines...")
    
    # We search recursively in the vault for files matching keywords
    keywords = ["*ULTRA*", "*SUPREME*", "*DIVINE*", "*GOD*", "*RARE*"]
    
    found_files = []
    
    for keyword in keywords:
        # Search in main vault
        pattern = os.path.join(VAULT_DIR, "**", keyword)
        # Recursive glob (requires python 3.10+ generally or recursive=True)
        # glob.glob is simple, let's use os.walk for robust finding to match 'find_by_name' logic
        pass

    # Manual walk to be safe and precise
    count = 0
    for root, dirs, files in os.walk(VAULT_DIR):
        for file in files:
            upper_name = file.upper()
            if any(k.replace("*", "") in upper_name for k in keywords):
                # We found a TREASURE
                src_path = os.path.join(root, file)
                dst_path = os.path.join(ROOT_DIR, file)
                
                # Copy execution
                try:
                    # Don't overwrite if it's already there and size is same (optimization)
                    if os.path.exists(dst_path):
                        if os.path.getsize(src_path) == os.path.getsize(dst_path):
                            # Debug log only if needed
                            # log(f"Skipping duplicate: {file}")
                            continue
                            
                    shutil.copy2(src_path, dst_path)
                    log(f"💎 Restored GEM: {file}")
                    count += 1
                except Exception as e:
                    log(f"[X] Failed to restore {file}: {e}")

    log(f"[OK] RESTORATION COMPLETE. Recovered {count} Ultra/Supreme/Divine artifacts.")

if __name__ == "__main__":
    restore_ultras()
