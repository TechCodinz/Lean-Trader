#!/usr/bin/env python3
"""
DUPLICATE BACKUP SYSTEM
Archives ALL duplicates safely before any organization
NOTHING IS DELETED - everything is preserved
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
AUDIT_JSON = os.path.join(ROOT_DIR, "COMPLETE_AUDIT_REPORT.json")
DUPLICATES_ARCHIVE = os.path.join(ROOT_DIR, "_DUPLICATES_BACKUP")
MANIFEST_FILE = "DUPLICATES_MANIFEST.txt"

def log(msg):
    print(f"[DUPLICATE_BACKUP] {msg}")

def load_audit_data():
    """Load the audit JSON"""
    if not os.path.exists(AUDIT_JSON):
        log(f"ERROR: Audit file not found: {AUDIT_JSON}")
        return None
    
    with open(AUDIT_JSON, "r", encoding='utf-8') as f:
        return json.load(f)

def backup_duplicates(audit_data):
    """
    Backup ALL duplicate files to archive
    Keep the 'best' one in original location
    """
    log("=" * 80)
    log("BACKING UP ALL DUPLICATES - ZERO DELETION POLICY")
    log("=" * 80)
    
    os.makedirs(DUPLICATES_ARCHIVE, exist_ok=True)
    
    local_inv = audit_data["inventories"]["local"]
    duplicates = audit_data["analysis"].get("local_duplicates", [])
    
    if not duplicates:
        log("No duplicates found in audit data")
        return
    
    log(f"Found {len(duplicates)} duplicate sets to backup")
    
    manifest = []
    total_backed_up = 0
    
    for i, dupe_set in enumerate(duplicates, 1):
        hash_val = dupe_set["hash"]
        files = dupe_set["files"]
        count = dupe_set["count"]
        
        log(f"\n[{i}/{len(duplicates)}] Duplicate Set: {count} copies")
        log(f"   Hash: {hash_val[:12]}...")
        
        # Find full file info for each duplicate
        file_infos = []
        for file_rel_path in files:
            # Find this file in inventory
            for file_info in local_inv["files"]:
                if file_info["rel_path"] == file_rel_path:
                    file_infos.append(file_info)
                    break
        
        if not file_infos:
            log("   ⚠️ Could not find file infos in inventory")
            continue
        
        # Determine which to keep (largest, or newest if same size)
        file_infos.sort(key=lambda f: (f["size"], f["abs_path"]), reverse=True)
        keeper = file_infos[0]
        to_backup = file_infos[1:]
        
        log(f"   KEEPING: {keeper['name']} ({keeper['size']} bytes)")
        log(f"   BACKING UP: {len(to_backup)} copies")
        
        # Backup the duplicates
        for dup in to_backup:
            src = dup["abs_path"]
            
            # Create meaningful backup path
            # Use relative path structure in backup
            rel_path = dup["rel_path"]
            backup_path = os.path.join(DUPLICATES_ARCHIVE, rel_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            try:
                # MOVE (not delete) to backup
                shutil.move(src, backup_path)
                log(f"     ✅ Backed up: {dup['name']}")
                total_backed_up += 1
                
                # Record in manifest
                manifest.append({
                    "original_path": src,
                    "backup_path": backup_path,
                    "kept_version": keeper["abs_path"],
                    "hash": hash_val,
                    "size": dup["size"]
                })
                
            except Exception as e:
                log(f"     ❌ Failed to backup {dup['name']}: {e}")
    
    # Write manifest
    manifest_path = os.path.join(DUPLICATES_ARCHIVE, MANIFEST_FILE)
    with open(manifest_path, "w", encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DUPLICATES BACKUP MANIFEST\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Backed Up: {total_backed_up} files\n")
        f.write("=" * 80 + "\n\n")
        
        for item in manifest:
            f.write(f"Original: {item['original_path']}\n")
            f.write(f"Backup:   {item['backup_path']}\n")
            f.write(f"Kept:     {item['kept_version']}\n")
            f.write(f"Hash:     {item['hash']}\n")
            f.write(f"Size:     {item['size']} bytes\n")
            f.write("-" * 80 + "\n")
    
    log("\n" + "=" * 80)
    log(f"✅ BACKUP COMPLETE: {total_backed_up} duplicates safely archived")
    log(f"   Location: {DUPLICATES_ARCHIVE}")
    log(f"   Manifest: {manifest_path}")
    log("=" * 80)
    log("\n⚠️ IMPORTANT: NO FILES DELETED - All duplicates moved to _DUPLICATES_BACKUP")
    log("   You can restore any file if needed from the backup")

def main():
    log("🛡️ DUPLICATE BACKUP SYSTEM - ZERO DELETION POLICY")
    log("   Loading audit data...")
    
    audit_data = load_audit_data()
    if not audit_data:
        return
    
    backup_duplicates(audit_data)

if __name__ == "__main__":
    main()
