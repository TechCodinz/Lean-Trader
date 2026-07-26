#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VPS Integration - ASCII Only"""

import os
import shutil
import hashlib

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"
VPS_DOWNLOAD = os.path.join(ROOT_DIR, "_VPS_BOT_CODE_ONLY")
INTEGRATION_LOG = "VPS_INTEGRATION_LOG.txt"

CATEGORY_PATTERNS = {
    "core/orchestrators": ["ORCHESTRATOR", "SUPREME", "ULTIMATE", "MASTER", "COMPLETE_ULTIMATE"],
    "core/coordinators": ["COORDINATOR", "HYBRID_INTELLIGENCE"],
    "engines/execution": ["EXECUTION", "INTELLIGENT_EXECUTION", "EXECUTOR"],
    "engines/profit": ["PROFIT", "OPTIMIZATION", "COMPOUND"],
    "engines/evolution": ["EVOLUTION", "SWARM", "GENETIC"],
    "engines/routing": ["ROUTER", "BRIDGE", "BYBIT", "EXCHANGE_SPAWN"],
    "ai/intelligence": ["AI_", "INTELLIGENCE", "CONSCIOUSNESS", "COLLECTIVE", "SENTIMENT"],
    "ai/learning": ["LEARNING", "ML_", "NEURAL", "DEEP_"],
    "ultra_rare/goldmine": ["ULTRA_GOLDMINE", "ULTRA_RARE", "MONEY_PRINTER", "RARE_"],
    "ultra_rare/divine": ["DIVINE", "GOD_MODE", "IMMORTAL", "TRANSCENDENT"],
    "ultra_rare/quantum": ["QUANTUM", "OMNISCIENT"],
    "safety/risk": ["SAFETY", "RISK", "GUARD", "PROTECTION"],
    "safety/deadlock": ["DEADLOCK", "CAPITAL_"],
    "data/feeds": ["WEBSOCKET", "DATA_FEED", "STREAM"],
    "data/intelligence": ["MARKET_DATA", "DATA_HUB"],
    "features/critical": ["critical_features", "CRITICAL_"],
    "scripts/deployment": ["DEPLOY", "INSTALL"],
    "scripts/activation": ["ACTIVATE", "START", "LAUNCH"],
    "diagnostics/audits": ["AUDIT", "CHECK", "VERIFY", "SCAN"],
}

def log(msg):
    print(f"[INTEGRATE] {msg}")
    try:
        with open(INTEGRATION_LOG, "a") as f:
            f.write(f"{msg}\n")
    except:
        pass

def categorize_file(filename):
    name_upper = filename.upper()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in name_upper:
                return category
    return "utils/helpers"

def get_hash(filepath):
    try:
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except:
        return None

def integrate():
    log("=" * 70)
    log("INTEGRATING VPS FILES INTO PROFESSIONAL STRUCTURE")
    log("=" * 70)
    
    if not os.path.exists(VPS_DOWNLOAD):
        log(f"ERROR: VPS download directory not found: {VPS_DOWNLOAD}")
        return
    
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
        category = categorize_file(filename)
        dest_dir = os.path.join(ROOT_DIR, category)
        dest_path = os.path.join(dest_dir, filename)
        
        os.makedirs(dest_dir, exist_ok=True)
        
        if os.path.exists(dest_path):
            vps_hash = get_hash(vps_file)
            local_hash = get_hash(dest_path)
            
            if vps_hash == local_hash:
                duplicates += 1
            else:
                base, ext = os.path.splitext(filename)
                dest_path = os.path.join(dest_dir, f"{base}_vps{ext}")
                shutil.copy2(vps_file, dest_path)
                integrated += 1
        else:
            shutil.copy2(vps_file, dest_path)
            integrated += 1
            
            if integrated % 100 == 0:
                log(f"Progress: {integrated} files integrated")
    
    log("\n" + "=" * 70)
    log(f"INTEGRATION COMPLETE")
    log(f"  Integrated: {integrated} new/unique files")
    log(f"  Duplicates: {duplicates} files (already local)")
    log("=" * 70)

if __name__ == "__main__":
    integrate()
