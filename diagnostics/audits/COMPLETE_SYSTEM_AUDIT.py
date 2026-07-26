#!/usr/bin/env python3
"""
COMPLETE SYSTEM AUDIT - PROFESSIONAL PRECISION
Systematically catalogs every file, checks for duplicates, and validates architecture integrity
"""

import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VAULT_DIR = os.path.join(ROOT_DIR, "_BACKUP_VAULT_BEFORE_STITCH")
VPS_BACKUP = os.path.join(ROOT_DIR, "_VPS_BACKUP_RAW")

def get_file_hash(filepath):
    """Calculate MD5 hash for duplicate detection"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def categorize_file(filename):
    """Categorize files by their role in the architecture"""
    name_upper = filename.upper()
    
    # Core System Categories
    if "ORCHESTRATOR" in name_upper or "SUPREME" in name_upper or "ULTIMATE" in name_upper:
        return "CORE_ORCHESTRATORS"
    elif "EXECUTION" in name_upper and ("ENGINE" in name_upper or "SYSTEM" in name_upper):
        return "EXECUTION_ENGINES"
    elif "PROFIT" in name_upper or "OPTIMIZATION" in name_upper:
        return "PROFIT_SYSTEMS"
    elif "INTELLIGENCE" in name_upper or "AI" in name_upper or "CONSCIOUSNESS" in name_upper:
        return "AI_INTELLIGENCE"
    elif "EVOLUTION" in name_upper or "SWARM" in name_upper or "COLLECTIVE" in name_upper:
        return "EVOLUTION_SWARM"
    elif "ULTRA" in name_upper or "RARE" in name_upper or "GOLDMINE" in name_upper:
        return "ULTRA_RARE_ENGINES"
    elif "SAFETY" in name_upper or "RISK" in name_upper or "DEADLOCK" in name_upper:
        return "SAFETY_SYSTEMS"
    elif "DATA" in name_upper or "MARKET" in name_upper or "FEED" in name_upper:
        return "DATA_SYSTEMS"
    elif "ROUTER" in name_upper or "EXCHANGE" in name_upper or "BRIDGE" in name_upper:
        return "ROUTING_EXCHANGE"
    elif "DIVINE" in name_upper or "GOD" in name_upper or "NOBEL" in name_upper:
        return "DIVINE_ADVANCED"
    elif name_upper.startswith("PITCH"):
        return "PITCH_BENT_SYSTEM"
    else:
        return "UTILITIES_OTHER"

def scan_directory(directory, label):
    """Scan a directory and return detailed file inventory"""
    print(f"\n🔍 Scanning: {label}")
    print(f"   Path: {directory}")
    
    inventory = {
        "label": label,
        "path": directory,
        "scan_time": datetime.now().isoformat(),
        "files": [],
        "by_hash": defaultdict(list),
        "by_category": defaultdict(list),
        "stats": {
            "total_files": 0,
            "total_py_files": 0,
            "total_size_bytes": 0,
            "duplicates_found": 0
        }
    }
    
    if not os.path.exists(directory):
        print(f"   ⚠️ Directory not found!")
        return inventory
    
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ and .git
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
        
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, directory)
            
            try:
                file_size = os.path.getsize(filepath)
                file_hash = get_file_hash(filepath) if file.endswith('.py') else None
                
                file_info = {
                    "name": file,
                    "rel_path": rel_path,
                    "abs_path": filepath,
                    "size": file_size,
                    "hash": file_hash,
                    "category": categorize_file(file) if file.endswith('.py') else "NON_PYTHON"
                }
                
                inventory["files"].append(file_info)
                inventory["stats"]["total_files"] += 1
                inventory["stats"]["total_size_bytes"] += file_size
                
                if file.endswith('.py'):
                    inventory["stats"]["total_py_files"] += 1
                    inventory["by_category"][file_info["category"]].append(file_info)
                    
                    if file_hash:
                        inventory["by_hash"][file_hash].append(file_info)
                        
            except Exception as e:
                print(f"   ⚠️ Error scanning {file}: {e}")
    
    # Count duplicates
    for hash_val, file_list in inventory["by_hash"].items():
        if len(file_list) > 1:
            inventory["stats"]["duplicates_found"] += len(file_list) - 1
    
    print(f"   ✅ Found {inventory['stats']['total_py_files']} Python files")
    print(f"   ⚠️ Duplicates: {inventory['stats']['duplicates_found']}")
    
    return inventory

def generate_audit_report(local_inv, vps_inv, vault_inv):
    """Generate comprehensive audit report"""
    
    report = {
        "audit_timestamp": datetime.now().isoformat(),
        "inventories": {
            "local": local_inv,
            "vps": vps_inv,
            "vault": vault_inv
        },
        "analysis": {}
    }
    
    # Find duplicates WITHIN local
    print("\n📊 ANALYZING DUPLICATES IN LOCAL SYSTEM...")
    local_dupes = []
    for hash_val, file_list in local_inv["by_hash"].items():
        if len(file_list) > 1:
            local_dupes.append({
                "hash": hash_val,
                "count": len(file_list),
                "files": [f["rel_path"] for f in file_list],
                "size": file_list[0]["size"]
            })
    
    report["analysis"]["local_duplicates"] = local_dupes
    print(f"   Found {len(local_dupes)} duplicate sets in local")
    
    # Find VPS-unique files
    if vps_inv["files"]:
        print("\n📊 ANALYZING VPS UNIQUE FILES...")
        local_names = {f["name"] for f in local_inv["files"]}
        vps_unique = [f for f in vps_inv["files"] if f["name"] not in local_names]
        report["analysis"]["vps_unique"] = vps_unique
        print(f"   Found {len(vps_unique)} files unique to VPS")
    
    # Category breakdown for local
    print("\n📊 CATEGORIZING LOCAL ARCHITECTURE...")
    category_summary = {}
    for category, files in local_inv["by_category"].items():
        category_summary[category] = {
            "count": len(files),
            "total_size": sum(f["size"] for f in files),
            "files": [f["name"] for f in files]
        }
    report["analysis"]["local_categories"] = category_summary
    
    for cat, info in sorted(category_summary.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"   {cat}: {info['count']} files")
    
    # Save detailed JSON
    with open("COMPLETE_AUDIT_REPORT.json", "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Generate human-readable report
    with open("COMPLETE_AUDIT_REPORT.txt", "w", encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPLETE SYSTEM AUDIT REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("🏗️ LOCAL SYSTEM INVENTORY\n")
        f.write(f"Total Python Files: {local_inv['stats']['total_py_files']}\n")
        f.write(f"Total Size: {local_inv['stats']['total_size_bytes'] / 1024 / 1024:.2f} MB\n")
        f.write(f"Duplicates: {len(local_dupes)} sets\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("📁 ARCHITECTURE BY CATEGORY\n")
        f.write("-" * 80 + "\n")
        for cat, info in sorted(category_summary.items(), key=lambda x: x[1]["count"], reverse=True):
            f.write(f"\n{cat} ({info['count']} files):\n")
            for fname in sorted(info["files"]):
                f.write(f"  - {fname}\n")
        
        if local_dupes:
            f.write("\n" + "-" * 80 + "\n")
            f.write("⚠️ DUPLICATE FILES IN LOCAL\n")
            f.write("-" * 80 + "\n")
            for dupe in local_dupes:
                f.write(f"\nDuplicate Set ({dupe['count']} copies, {dupe['size']} bytes each):\n")
                for fpath in dupe["files"]:
                    f.write(f"  - {fpath}\n")
        
        if vps_inv["files"] and "vps_unique" in report["analysis"]:
            f.write("\n" + "-" * 80 + "\n")
            f.write("🌍 VPS-ONLY FILES (Not in Local)\n")
            f.write("-" * 80 + "\n")
            for vps_file in report["analysis"]["vps_unique"]:
                f.write(f"  - {vps_file['rel_path']} ({vps_file['size']} bytes)\n")
    
    print("\n✅ Audit reports generated:")
    print("   - COMPLETE_AUDIT_REPORT.json (detailed)")
    print("   - COMPLETE_AUDIT_REPORT.txt (human-readable)")

def main():
    print("=" * 80)
    print("🔬 COMPLETE SYSTEM AUDIT - PROFESSIONAL PRECISION")
    print("=" * 80)
    
    # Scan all three locations
    local_inventory = scan_directory(ROOT_DIR, "LOCAL GOLDEN SYSTEM")
    vps_inventory = scan_directory(VPS_BACKUP, "VPS BACKUP")
    vault_inventory = scan_directory(VAULT_DIR, "VAULT BACKUP")
    
    # Generate comprehensive report
    generate_audit_report(local_inventory, vps_inventory, vault_inventory)
    
    print("\n" + "=" * 80)
    print("✅ AUDIT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
