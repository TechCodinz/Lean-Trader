
import os
import filecmp
import hashlib

LOCAL_ROOT = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VPS_BACKUP = os.path.join(LOCAL_ROOT, "_VPS_BACKUP_RAW")
OUTPUT_FILE = "VPS_COMPARISON_REPORT.txt"

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def compare_remote():
    print("🌍 COMPARISON: VPS Backup vs Local Golden System")
    print(f"   Local: {LOCAL_ROOT}")
    print(f"   VPS:   {VPS_BACKUP}\n")
    
    unique_to_vps = []
    different_content = []
    identical = 0
    
    # Walk VPS backup
    for root, dirs, files in os.walk(VPS_BACKUP):
        for file in files:
            if not file.endswith(".py"): continue
            
            vps_path = os.path.join(root, file)
            # Find relative path
            rel_path = os.path.relpath(vps_path, VPS_BACKUP)
            
            local_path = os.path.join(LOCAL_ROOT, rel_path)
            
            if not os.path.exists(local_path):
                # Check if it exists in root (flat structure on local?)
                local_flat_path = os.path.join(LOCAL_ROOT, file)
                if os.path.exists(local_flat_path):
                    local_path = local_flat_path
                else:
                    unique_to_vps.append((rel_path, os.path.getsize(vps_path)))
                    continue
            
            # Compare hashes
            vps_hash = get_file_hash(vps_path)
            local_hash = get_file_hash(local_path)
            
            if vps_hash == local_hash:
                identical += 1
            else:
                different_content.append((rel_path, os.path.getsize(vps_path), os.path.getsize(local_path)))

    # Generate Report
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        f.write("# VPS COMPARISON REPORT\n\n")
        f.write(f"Identical Files: {identical}\n")
        f.write(f"Unique to VPS:   {len(unique_to_vps)}\n")
        f.write(f"Modified/Diff:   {len(different_content)}\n\n")
        
        f.write("##  UNIQUE TO VPS (Not in Local Golden)\n")
        for p, size in sorted(unique_to_vps):
            f.write(f"- {p} ({size} bytes)\n")
            
        f.write("\n## 📝 DIFFERENT CONTENT (VPS vs Local)\n")
        for p, v_size, l_size in sorted(different_content):
            f.write(f"- {p} (VPS: {v_size}b | Loc: {l_size}b)\n")
            
    print(f"[OK] Report generated: {OUTPUT_FILE}")
    print(f"   Unique VPS Files: {len(unique_to_vps)}")
    print(f"   Differing Files:  {len(different_content)}")

if __name__ == "__main__":
    if not os.path.exists(VPS_BACKUP):
        print(f"[X] VPS Backup not found at {VPS_BACKUP}")
    else:
        compare_remote()
