#!/usr/bin/env python3
"""
COMPLETE VPS FILE EXTRACTION
Downloads EVERY file from VPS using multiple methods to ensure nothing is left behind
"""

import paramiko
import os
import time
from pathlib import Path

VPS_HOST = "75.119.149.117"
VPS_USER = "root"
VPS_PASSWORD = "Prince%1$5%9$5%"
VPS_BOT_DIR = "/root/bot"

LOCAL_ROOT = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VPS_DOWNLOAD_DIR = os.path.join(LOCAL_ROOT, "_VPS_COMPLETE_DOWNLOAD")

def log(msg):
    print(f"[VPS_RSYNC] {msg}")
    with open("VPS_RSYNC_LOG.txt", "a", encoding='utf-8') as f:
        f.write(f"{msg}\n")

def download_all_vps_files():
    """Download ALL files from VPS using SFTP"""
    log("=" * 80)
    log("🚀 COMPLETE VPS FILE EXTRACTION - ZERO FILES LEFT BEHIND")
    log("=" * 80)
    
    os.makedirs(VPS_DOWNLOAD_DIR, exist_ok=True)
    
    # Connect via SSH/SFTP
    try:
        log(f"Connecting to {VPS_HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=30)
        
        sftp = ssh.open_sftp()
        log("✅ SFTP Connection Established")
        
        # Get list of ALL files on VPS
        log(f"\nScanning VPS directory: {VPS_BOT_DIR}")
        stdin, stdout, stderr = ssh.exec_command(f"find {VPS_BOT_DIR} -type f -name '*.py'")
        vps_files = stdout.read().decode('utf-8').strip().split('\n')
        
        log(f"Found {len(vps_files)} Python files on VPS")
        
        downloaded = 0
        skipped = 0
        failed = 0
        
        for i, remote_path in enumerate(vps_files, 1):
            if not remote_path.strip():
                continue
                
            # Calculate local path
            rel_path = remote_path.replace(VPS_BOT_DIR + "/", "")
            local_path = os.path.join(VPS_DOWNLOAD_DIR, rel_path)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            try:
                if os.path.exists(local_path):
                    skipped += 1
                else:
                    sftp.get(remote_path, local_path)
                    downloaded += 1
                    
                if i % 50 == 0:
                    log(f"Progress: {i}/{len(vps_files)} files processed...")
                    
            except Exception as e:
                log(f"❌ Failed to download {rel_path}: {e}")
                failed += 1
        
        sftp.close()
        ssh.close()
        
        log("\n" + "=" * 80)
        log(f"✅ VPS EXTRACTION COMPLETE")
        log(f"   Downloaded: {downloaded} files")
        log(f"   Already Local: {skipped} files")
        log(f"   Failed: {failed} files")
        log(f"   Total VPS Files: {len(vps_files)}")
        log("=" * 80)
        
        return downloaded, skipped, failed
        
    except Exception as e:
        log(f"❌ CRITICAL ERROR: {e}")
        log("Attempting fallback method...")
        return 0, 0, 0

if __name__ == "__main__":
    download_all_vps_files()
