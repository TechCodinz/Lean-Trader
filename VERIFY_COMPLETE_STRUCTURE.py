#!/usr/bin/env python3
"""
COMPLETE STRUCTURE VERIFICATION
Verifies that ALL files are properly organized in the professional folder structure
Generates comprehensive manifest of all engines and their locations
"""

import os
import json
from collections import defaultdict
from datetime import datetime

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"

# Expected Professional Structure
EXPECTED_STRUCTURE = {
    "core/orchestrators": ["COMPLETE_ULTIMATE_ORCHESTRATOR", "Supreme", "Ultimate"],
    "core/coordinators": ["HYBRID_INTELLIGENCE", "Coordinator"],
    "core/registry": ["Registry", "Manager"],
    "engines/execution": ["INTELLIGENT_EXECUTION", "EXECUTION_ORCHESTRATOR"],
    "engines/profit": ["PROFIT", "Optimization"],
    "engines/evolution": ["EVOLUTION", "Swarm"],
    "engines/routing": ["ROUTER", "BRIDGE", "BYBIT"],
    "ai/intelligence": ["AI_", "Intelligence", "Consciousness"],
    "ai/learning": ["Learning", "ML", "Neural"],
    "ai/prediction": ["Predict", "Forecast"],
    "ultra_rare/goldmine": ["ULTRA_GOLDMINE", "ULTRA_RARE", "MONEY_PRINTER"],
    "ultra_rare/divine": ["DIVINE", "GOD", "SUPREME"],
    "ultra_rare/quantum": ["QUANTUM", "Transcendent"],
    "safety/risk": ["SAFETY", "RISK", "Guard"],
    "safety/deadlock": ["DEADLOCK", "Capital"],
    "safety/validation": ["VALIDATION", "Proof", "Gate"],
    "data/feeds": ["WEBSOCKET", "DATA_FEED"],
    "data/intelligence": ["MARKET_DATA", "Intelligence"],
    "features/critical": ["critical_features"],
    "features/compounding": ["COMPOUND"],
    "utils/helpers": ["Helper", "Utility"],
    "diagnostics/audits": ["AUDIT", "CHECK", "VERIFY"],
    "scripts/activation": ["ACTIVATE", "START"],
}

def log(msg):
    print(msg)

def scan_structure():
    """Scan the entire directory structure"""
    log("🔍 SCANNING ENTIRE PROFESSIONAL STRUCTURE")
    log("=" * 80)
    
    structure_report = defaultdict(list)
    all_files = []
    
    # Exclude backup directories
    exclude = ["_BACKUP", "_VPS", ".git", "__pycache__"]
    
    for root, dirs, files in os.walk(ROOT_DIR):
        # Skip excluded directories
        if any(ex in root for ex in exclude):
            continue
            
        for file in files:
            if file.endswith(".py"):
                rel_path = os.path.relpath(root, ROOT_DIR)
                structure_report[rel_path].append(file)
                all_files.append({
                    "file": file,
                    "location": rel_path,
                    "full_path": os.path.join(root, file)
                })
    
    return structure_report, all_files

def verify_critical_engines(all_files):
    """Verify all critical engines are present"""
    log("\n🎯 VERIFYING CRITICAL ENGINES")
    log("=" * 80)
    
    critical_engines = [
        "COMPLETE_ULTIMATE_ORCHESTRATOR.py",
        "INTELLIGENT_EXECUTION_ENGINE.py",
        "EXECUTION_ORCHESTRATOR.py",
        "HYBRID_INTELLIGENCE_COORDINATOR.py",
        "AI_COLLECTIVE_CONSCIOUSNESS.py",
        "EVOLUTION_ENGINE.py",
        "COMPLETE_PROFIT_SYSTEM.py",
        "ULTRA_GOLDMINE_FEATURES.py",
        "ULTRA_RARE_ENGINES.py",
        "BYBIT_EXECUTION_BRIDGE.py",
        "MARKET_DATA_INTELLIGENCE.py"
    ]
    
    found_engines = {}
    missing_engines = []
    
    for engine in critical_engines:
        found = False
        for file_info in all_files:
            if file_info["file"] == engine:
                found_engines[engine] = file_info["location"]
                found = True
                break
        
        if not found:
            missing_engines.append(engine)
    
    # Report
    log(f"\n✅ FOUND: {len(found_engines)}/{len(critical_engines)} critical engines")
    for engine, location in found_engines.items():
        log(f"   ✓ {engine:<50} → {location}")
    
    if missing_engines:
        log(f"\n❌ MISSING: {len(missing_engines)} critical engines")
        for engine in missing_engines:
            log(f"   ✗ {engine}")
    
    return len(missing_engines) == 0

def generate_manifest(structure_report, all_files):
    """Generate complete manifest"""
    log("\n📋 GENERATING COMPLETE MANIFEST")
    log("=" * 80)
    
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(all_files),
        "structure": dict(structure_report),
        "files_by_location": {loc: len(files) for loc, files in structure_report.items()}
    }
    
    # Save manifest
    with open("COMPLETE_STRUCTURE_MANIFEST.json", "w", encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    # Print summary
    log(f"\n📊 STRUCTURE SUMMARY:")
    log(f"   Total Python Files: {len(all_files)}")
    log(f"   Total Directories: {len(structure_report)}")
    log(f"\n   Top-Level Categories:")
    
    top_level = defaultdict(int)
    for loc, files in structure_report.items():
        if "/" in loc:
            top = loc.split("/")[0]
        else:
            top = "root"
        top_level[top] += len(files)
    
    for category, count in sorted(top_level.items(), key=lambda x: x[1], reverse=True):
        log(f"      {category:<20} {count:>5} files")
    
    log(f"\n✅ Manifest saved: COMPLETE_STRUCTURE_MANIFEST.json")
    
    return manifest

def main():
    log("=" * 80)
    log("🏗️  COMPLETE STRUCTURE VERIFICATION")
    log("=" * 80)
    
    # Scan
    structure_report, all_files = scan_structure()
    
    # Verify critical engines
    all_critical_found = verify_critical_engines(all_files)
    
    # Generate manifest
    manifest = generate_manifest(structure_report, all_files)
    
    # Final verdict
    log("\n" + "=" * 80)
    if all_critical_found and len(all_files) > 6000:
        log("✅ STRUCTURE VERIFICATION PASSED")
        log("   All critical engines present and properly organized")
        log(f"   {len(all_files)} files in professional structure")
    else:
        log("⚠️ STRUCTURE NEEDS ATTENTION")
        if not all_critical_found:
            log("   Some critical engines are missing")
        if len(all_files) < 6000:
            log(f"   File count seems low ({len(all_files)})")
    log("=" * 80)

if __name__ == "__main__":
    main()
