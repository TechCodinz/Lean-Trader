#!/usr/bin/env python3
"""
INTEGRATE VPS FILES INTO PROFESSIONAL STRUCTURE
Takes all downloaded VPS files and properly categorizes them into the professional folder structure
"""

import os
import shutil
import hashlib
from collections import defaultdict

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VPS_DOWNLOAD = os.path.join(ROOT_DIR, "_VPS_COMPLETE_DOWNLOAD")
INTEGRATION_LOG = "VPS_INTEGRATION_LOG.txt"

# Category mapping based on file naming patterns
CATEGORY_PATTERNS = {
    "core/orchestrators": ["ORCHESTRATOR", "SUPREME", "ULTIMATE", "MASTER", "COMPLETE_ULTIMATE"],
    "core/coordinators": ["COORDINATOR", "HYBRID_INTELLIGENCE"],
    "engines/execution": ["EXECUTION", "INTELLIGENT_EXECUTION", "EXECUTOR"],
    "engines/profit": ["PROFIT", "OPTIMIZATION", "COMPOUND"],
    "engines/evolution": ["EVOLUTION", "SWARM", "GENETIC"],
    "engines/routing": ["ROUTER", "BRIDGE", "BYBIT", "EXCHANGE_SPAWN"],
    "ai/intelligence": ["AI_", "INTELLIGENCE", "CONSCIOUSNESS", "COLLECTIVE", "SENTIMENT"],
    "ai/learning": ["LEARNING", "ML_", "NEURAL", "DEEP_"],
    "ai/prediction": ["PREDICT", "FORECAST", "PROPHET"],
    "ultra_rare/goldmine": ["ULTRA_GOLDMINE", "ULTRA_RARE", "MONEY_PRINTER", "RARE_"],
    "ultra_rare/divine": ["DIVINE", "GOD_MODE", "IMMORTAL", "TRANSCENDENT"],
    "ultra_rare/quantum": ["QUANTUM", "OMNISCIENT"],
    "safety/risk": ["SAFETY", "RISK", "GUARD", "PROTECTION"],
    "safety/deadlock": ["DEADLOCK", "CAPITAL_"],
    "safety/circuit_breakers": ["CIRCUIT", "BREAKER", "EMERGENCY"],
    "data/feeds": ["WEBSOCKET", "DATA_FEED", "STREAM"],
    "data/intelligence": ["MARKET_DATA", "DATA_HUB"],
    "features/critical": ["critical_features", "CRITICAL_"],
    "features/compounding": ["COMPOUND", "COMPOUNDING"],
    "features/trailing": ["TRAILING"],
    "scripts/deployment": ["DEPLOY", "INSTALL"],
    "scripts/activation": ["ACTIVATE", "START", "LAUNCH"],
    "diagnostics/audits": ["AUDIT", "CHECK", "VERIFY", "SCAN"],
}

def log(msg):
    print(f"[VPS_INTEGRATE] {msg}")
    with open(INTEGRATION_LOG, "a", encoding='utf-8') as f:
        f.write(f"{msg}\n")

def categorize_file(filename):
    """Determine the best category for a file"""
    name_upper = filename.upper()
    
    # Check each category pattern
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in name_upper:
                return category
    
    # Default
    return "utils/helpers"

def get_file_hash(filepath):
    """Calculate MD5 hash"""
    try:
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def integrate_vps_files():
    """Integrate all VPS files into professional structure"""
    log("=" * 80)
    log("INTEGRATING VPS FILES INTO PROFESSIONAL STRUCTURE")
    log("=" * 80)
    
    if not os.path.exists(VPS_DOWNLOAD):
        log(f"❌ VPS download directory not found: {VPS_DOWNLOAD}")
        return
    
    # Scan VPS download directory
    vps_files = []
    for root, dirs, files in os.walk(VPS_DOWNLOAD):
        for file in files:
            if file.endswith(".py"):
                vps_files.append(os.path.join(root, file))
    
    log(f"Found {len(vps_files)} Python files in VPS download")
    
    integrated = 0
    duplicates = 0
    
    for vps_file in vps_files:
        filename = os.path.basename(vps_file)
        
        # Determine category
        category = categorize_file(filename)
        dest_dir = os.path.join(ROOT_DIR, category)
        dest_path = os.path.join(dest_dir, filename)
        
        # Ensure directory exists
        os.makedirs(dest_dir, exist_ok=True)
        
        # Check if file already exists
        if os.path.exists(dest_path):
            # Compare hashes
            vps_hash = get_file_hash(vps_file)
            local_hash = get_file_hash(dest_path)
            
            if vps_hash == local_hash:
                duplicates += 1
            else:
                # Different content - keep VPS version with suffix
                base, ext = os.path.splitext(filename)
                dest_path = os.path.join(dest_dir, f"{base}_vps{ext}")
                shutil.copy2(vps_file, dest_path)
                integrated += 1
                log(f"   Integrated (different): {filename} → {category}")
        else:
            # New file - copy it
            shutil.copy2(vps_file, dest_path)
            integrated += 1
            
            if integrated % 100 == 0:
                log(f"   Progress: {integrated} files integrated...")
    
    log("\n" + "=" * 80)
    log(f"VPS INTEGRATION COMPLETE")
    log(f"   Integrated: {integrated} new/unique files")
    log(f"   Duplicates: {duplicates} files (already local)")
    log("=" * 80)

if __name__ == "__main__":
    integrate_vps_files()
