
import os
import shutil
import json
import hashlib
from datetime import datetime

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
AUDIT_JSON = os.path.join(ROOT_DIR, "COMPLETE_AUDIT_REPORT.json")
MIGRATION_LOG = "MIGRATION_LOG.txt"
BACKUP_DIR = os.path.join(ROOT_DIR, "_PRE_ORG_BACKUP")

# Define Structure Mapping (Category -> Folder)
CATEGORY_MAP = {
    "CORE_ORCHESTRATORS": "core/orchestrators",
    "EXECUTION_ENGINES": "engines/execution",
    "PROFIT_SYSTEMS": "engines/profit",
    "AI_INTELLIGENCE": "ai/intelligence",
    "EVOLUTION_SWARM": "engines/evolution",
    "ULTRA_RARE_ENGINES": "ultra_rare/goldmine",
    "SAFETY_SYSTEMS": "safety/risk",
    "DATA_SYSTEMS": "data/feeds",
    "ROUTING_EXCHANGE": "engines/routing",
    "DIVINE_ADVANCED": "ultra_rare/divine",
    "PITCH_BENT_SYSTEM": "pitch_bent",  # Special case, already a folder usually
    "UTILITIES_OTHER": "utils/helpers", # Default catch-all
    "NON_PYTHON": "utils/resources"
}

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with open(MIGRATION_LOG, "a", encoding='utf-8') as f:
        f.write(entry + "\n")

def create_folders():
    log("Creating folder hierarchy...")
    for folder in CATEGORY_MAP.values():
        path = os.path.join(ROOT_DIR, folder)
        os.makedirs(path, exist_ok=True)
    
    # Create extra specific folders from plan
    extras = [
        "core/coordinators", "core/registry",
        "ai/learning", "ai/prediction", "ai/sentiment",
        "ultra_rare/quantum",
        "safety/deadlock", "safety/circuit_breakers", "safety/validation",
        "data/intelligence", "data/storage",
        "features/critical", "features/compounding", "features/trailing", "features/arbitrage",
        "utils/monitoring", "utils/deployment",
        "diagnostics/audits", "diagnostics/checkers", "diagnostics/fixes",
        "archives/deprecated", "archives/experiments",
        "scripts/activation", "scripts/deployment", "scripts/maintenance",
        "tests/unit", "tests/integration", "tests/verification"
    ]
    for folder in extras:
        os.makedirs(os.path.join(ROOT_DIR, folder), exist_ok=True)

def load_audit():
    if not os.path.exists(AUDIT_JSON):
        log("ERROR: Audit JSON not found!")
        return None
    with open(AUDIT_JSON, "r") as f:
        return json.load(f)

def move_files(audit_data):
    if not audit_data: return

    files = audit_data["inventories"]["local"]["files"]
    log(f"Processing {len(files)} files for migration...")
    
    moved_count = 0
    skipped_count = 0
    
    # Track destination paths to avoid overwriting unique files with same name
    dest_tracker = {} # dest_path -> source_path
    
    for file_info in files:
        # Skip special directories
        if "_BACKUP" in file_info["abs_path"] or "_VPS" in file_info["abs_path"] or ".git" in file_info["abs_path"]:
            continue
            
        src = file_info["abs_path"]
        category = file_info["category"]
        name = file_info["name"]
        
        # Determine destination folder
        dest_folder = CATEGORY_MAP.get(category, "utils/helpers")
        
        # Fine-tune destinations based on keywords
        name_upper = name.upper()
        if "TEST" in name_upper: dest_folder = "tests/unit"
        elif "SCRIPT" in name_upper: dest_folder = "scripts/maintenance"
        elif "DEPLOY" in name_upper: dest_folder = "scripts/deployment"
        elif "AUDIT" in name_upper: dest_folder = "diagnostics/audits"
        elif "FIX" in name_upper: dest_folder = "diagnostics/fixes"
        elif "CHECK" in name_upper: dest_folder = "diagnostics/checkers"
        elif "ARCHIVE" in name_upper: dest_folder = "archives/deprecated"
        
        dest_path = os.path.join(ROOT_DIR, dest_folder, name)
        
        # Skip if already in place
        if os.path.normpath(src) == os.path.normpath(dest_path):
            continue
            
        # Handle Collisions
        if os.path.exists(dest_path):
            # If content matches, we can skip/archive source (it's a duplicate)
            # But wait, we already backed up duplicates. 
            # If we are moving, and dest exists, one version is already there.
            # We move this one to archive just in case
            archive_path = os.path.join(ROOT_DIR, "archives/deprecated", f"{datetime.now().microsecond}_{name}")
            try:
                shutil.move(src, archive_path)
                log(f"Arrived at collision, moved to archive: {name}")
            except: pass
            continue
            
        try:
            shutil.move(src, dest_path)
            moved_count += 1
            if moved_count % 100 == 0:
                print(f"Moved {moved_count} files...", end="\r")
        except Exception as e:
            log(f"Error moving {name}: {e}")
            
    log(f"Migration Complete. Moved {moved_count} files.")

def main():
    log("STARTING ORGANIZATION MIGRATION")
    create_folders()
    
    audit = load_audit()
    move_files(audit)
    
    log("ORGANIZATION FINALIZED.")

if __name__ == "__main__":
    main()
