import os
import re
import ast

MANIFEST_FILE = "DEDUPLICATION_MANIFEST.txt"
REPORT_FILE = "CHERRY_PICK_REPORT.txt"

def log(msg):
    print(msg)
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def get_functions_and_classes(filepath):
    """Extract set of function and class names from a file"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        tree = ast.parse(content)
        definitions = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                definitions.add(node.name)
        return definitions, len(content.splitlines())
    except Exception as e:
        return set(), 0

def check_for_keywords(filepath, keywords):
    """Check if file contains specific high-value keywords"""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().upper()
        found = [k for k in keywords if k in content]
        return set(found)
    except:
        return set()

def parse_manifest():
    """Parse the deduplication manifest to find pairs"""
    entries = []
    current_entry = {}
    
    if not os.path.exists(MANIFEST_FILE):
        print("Manifest not found!")
        return []

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("File:"):
                current_entry = {"filename": line.split(": ")[1]}
            elif line.startswith("Kept:"):
                current_entry["kept"] = line.split(": ")[1]
            elif line.startswith("To:"):
                current_entry["archived"] = line.split(": ")[1]
            elif line.startswith("Size:"):
                line_val = line.split(":", 1)[1].strip()
                current_entry["size"] = int(line_val.split(" ")[0])
            elif line.startswith("---") and "kept" in current_entry:
                entries.append(current_entry)
                current_entry = {}
    return entries

def smart_audit():
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("SMART CHERRY PICK AUDIT REPORT\n")
        f.write("==============================\n")
    
    entries = parse_manifest()
    log(f"Auditing {len(entries)} archived pairs...\n")
    
    critical_keywords = ["GOD_MODE", "UNLIMITED", "NO_LIMIT", "BYPASS", "SECRET", "PROFIT_FACTOR"]
    
    potential_loss_count = 0
    
    for entry in entries:
        kept_path = entry.get("kept")
        archived_path = entry.get("archived")
        
        if not kept_path or not archived_path or not os.path.exists(kept_path) or not os.path.exists(archived_path):
            continue
            
        # Analysis 1: Ast Definitions
        kept_defs, kept_lines = get_functions_and_classes(kept_path)
        arch_defs, arch_lines = get_functions_and_classes(archived_path)
        
        # Check if Archived has definitions NOT in Kept
        unique_to_archive = arch_defs - kept_defs
        
        # Analysis 2: Keywords
        kept_keys = check_for_keywords(kept_path, critical_keywords)
        arch_keys = check_for_keywords(archived_path, critical_keywords)
        lost_keys = arch_keys - kept_keys
        
        # Flagging Logic
        flags = []
        if unique_to_archive:
            flags.append(f"Unique Logic: {len(unique_to_archive)} definitions missing in kept version ({', '.join(list(unique_to_archive)[:3])}...)")
        
        if lost_keys:
            flags.append(f"Lost Keywords: {lost_keys}")
            
        if arch_lines > kept_lines * 1.5:
             flags.append(f"Size Mismatch: Archived is significantly larger ({arch_lines} vs {kept_lines} lines)")

        if flags:
            potential_loss_count += 1
            log(f"⚠️  FLAGGED: {entry['filename']}")
            log(f"   Kept: {kept_path} ({kept_lines} lines)")
            log(f"   Archived: {archived_path} ({arch_lines} lines)")
            for flag in flags:
                log(f"   - {flag}")
            log("-" * 50)

    log(f"\nAudit Complete. Found {potential_loss_count} files with potential unique value.")

if __name__ == "__main__":
    smart_audit()
