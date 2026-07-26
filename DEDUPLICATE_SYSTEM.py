#!/usr/bin/env python3
"""
PROFESSIONAL DEDUPLICATION SYSTEM
Keeps only the BEST single version of each file
Moves all duplicates to archive with full traceability
"""

import os
import shutil
import hashlib
from collections import defaultdict
from pathlib import Path
import time

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
DUPLICATES_ARCHIVE = os.path.join(ROOT_DIR, "_DUPLICATES_ARCHIVE")
DEDUP_LOG = "DEDUPLICATION_LOG.txt"
DEDUP_MANIFEST = "DEDUPLICATION_MANIFEST.txt"

# Directories to EXCLUDE from deduplication
EXCLUDE_DIRS = [
    "_BACKUP", "_VPS", ".git", "__pycache__", 
    "_DUPLICATES", "venv", "site-packages"
]

def log(msg):
    print(f"[DEDUP] {msg}")
    try:
        with open(DEDUP_LOG, "a", encoding='utf-8') as f:
            f.write(f"{msg}\n")
    except:
        pass

def should_exclude(path):
    """Check if path should be excluded"""
    for exclude in EXCLUDE_DIRS:
        if exclude in path:
            return True
    return False

def get_file_hash(filepath):
    """Calculate MD5 hash"""
    try:
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except:
        return None

def scan_all_files():
    """Scan all Python files and group by filename"""
    log("=" * 70)
    log("SCANNING FOR DUPLICATES...")
    log("=" * 70)
    
    # Group files by filename
    files_by_name = defaultdict(list)
    
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip excluded directories
        if should_exclude(root):
            continue
            
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                file_stat = os.stat(full_path)
                
                files_by_name[file].append({
                    'path': full_path,
                    'size': file_stat.st_size,
                    'mtime': file_stat.st_mtime,
                    'hash': get_file_hash(full_path)
                })
    
    log(f"Found {len(files_by_name)} unique filenames")
    
    # Identify duplicates
    duplicates = {}
    for filename, file_list in files_by_name.items():
        if len(file_list) > 1:
            duplicates[filename] = file_list
    
    log(f"Found {len(duplicates)} files with duplicates")
    
    return files_by_name, duplicates

def choose_best_version(file_list):
    """
    Choose the best version to keep
    Priority: 1) Largest size, 2) Most recent
    """
    # Sort by size (desc), then by mtime (desc)
    sorted_files = sorted(file_list, key=lambda f: (f['size'], f['mtime']), reverse=True)
    return sorted_files[0]

def deduplicate():
    """Main deduplication logic"""
    log("\n" + "=" * 70)
    log("STARTING PROFESSIONAL DEDUPLICATION")
    log("=" * 70)
    
    os.makedirs(DUPLICATES_ARCHIVE, exist_ok=True)
    
    # Scan files
    all_files, duplicates = scan_all_files()
    
    if not duplicates:
        log("\nNo duplicates found! System is already clean.")
        return
    
    # Process duplicates
    manifest_entries = []
    total_removed = 0
    total_kept = 0
    
    log(f"\nProcessing {len(duplicates)} duplicate sets...")
    
    for i, (filename, file_list) in enumerate(duplicates.items(), 1):
        # Choose best version
        best = choose_best_version(file_list)
        to_archive = [f for f in file_list if f['path'] != best['path']]
        
        log(f"\n[{i}/{len(duplicates)}] {filename}")
        log(f"  Copies found: {len(file_list)}")
        log(f"  KEEPING: {best['path']}")
        log(f"           Size: {best['size']} bytes, Modified: {time.ctime(best['mtime'])}")
        
        # Archive duplicates
        for dup in to_archive:
            try:
                # Create meaningful archive path
                rel_path = os.path.relpath(dup['path'], ROOT_DIR)
                archive_path = os.path.join(DUPLICATES_ARCHIVE, rel_path)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                
                # Move to archive
                shutil.move(dup['path'], archive_path)
                total_removed += 1
                
                log(f"  ARCHIVED: {dup['path']}")
                
                # Record in manifest
                manifest_entries.append({
                    'filename': filename,
                    'archived_from': dup['path'],
                    'archived_to': archive_path,
                    'kept_version': best['path'],
                    'size': dup['size']
                })
                
            except Exception as e:
                log(f"  ERROR archiving {dup['path']}: {e}")
        
        total_kept += 1
        
        if i % 10 == 0:
            log(f"\nProgress: {i}/{len(duplicates)} processed, {total_removed} archived")
    
    # Write manifest
    write_manifest(manifest_entries, total_kept, total_removed)
    
    log("\n" + "=" * 70)
    log("DEDUPLICATION COMPLETE")
    log(f"  Unique files kept: {total_kept}")
    log(f"  Duplicates archived: {total_removed}")
    log(f"  Archive location: {DUPLICATES_ARCHIVE}")
    log("=" * 70)

def write_manifest(entries, kept, removed):
    """Write detailed manifest"""
    with open(DEDUP_MANIFEST, "w", encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("DEDUPLICATION MANIFEST\n")
        f.write("=" * 70 + "\n")
        f.write(f"Total Files Kept: {kept}\n")
        f.write(f"Total Duplicates Archived: {removed}\n")
        f.write("=" * 70 + "\n\n")
        
        for entry in entries:
            f.write(f"File: {entry['filename']}\n")
            f.write(f"  Kept:     {entry['kept_version']}\n")
            f.write(f"  Archived: {entry['archived_from']}\n")
            f.write(f"  To:       {entry['archived_to']}\n")
            f.write(f"  Size:     {entry['size']} bytes\n")
            f.write("-" * 70 + "\n")

if __name__ == "__main__":
    deduplicate()
