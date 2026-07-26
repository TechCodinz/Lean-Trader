
import os

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"

MODULE_MAP = {
    "COMPLETE_ULTIMATE_ORCHESTRATOR": "core.orchestrators",
    "INTELLIGENT_EXECUTION_ENGINE": "engines.execution",
    "EXECUTION_ORCHESTRATOR": "engines.execution",
    "HYBRID_INTELLIGENCE_COORDINATOR": "core.coordinators",
    "AI_COLLECTIVE_CONSCIOUSNESS": "ai.intelligence",
    "EVOLUTION_ENGINE": "engines.evolution",
    "COMPLETE_PROFIT_SYSTEM": "engines.profit",
    "COLLECTIVE_CONSENSUS_ENGINE": "ai.intelligence",
    "ENRICHED_SIGNAL_SYSTEM": "ai.intelligence",
    "CONSCIOUSNESS_HARMONIZER": "ai.intelligence",
    "ULTRA_GOLDMINE_FEATURES": "ultra_rare.goldmine",
    "ULTRA_RARE_ENGINES": "ultra_rare.goldmine",
    "MARKET_DATA_INTELLIGENCE": "data.intelligence",
    "INTELLIGENT_EXCHANGE_ROUTER": "engines.routing",
    "BYBIT_EXECUTION_BRIDGE": "engines.routing",
    "WEBSOCKET_DATA_FEED": "data.feeds"
}

def log(msg):
    print(f"[FIX_IMPORTS_V2] {msg}")

def fix_imports_simple(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        modified = False
        new_lines = []
        
        for line in lines:
            original_line = line
            
            # Skip comments
            if line.strip().startswith("#"):
                new_lines.append(line)
                continue
                
            for module, pkg in MODULE_MAP.items():
                if module not in line: continue
                
                # Case 1: import MODULE
                if line.strip() == f"import {module}":
                    line = f"from {pkg} import {module}\n"
                    modified = True
                
                # Case 2: from MODULE import ...
                elif line.strip().startswith(f"from {module} import"):
                    line = line.replace(f"from {module} import", f"from {pkg}.{module} import")
                    modified = True
                    
                # Case 3: import MODULE as ...
                elif line.strip().startswith(f"import {module} as"):
                    alias = line.split(" as ")[1].strip()
                    line = f"from {pkg} import {module} as {alias}\n"
                    modified = True
                    
            new_lines.append(line)
            
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        return False
        
    except Exception as e:
        log(f"Error {filepath}: {e}")
        return False

def main():
    log("🚀 STARTING ROBUST IMPORT REPAIR V2")
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        if "_BACKUP" in root or ".git" in root: continue
        for file in files:
            if file.endswith(".py"):
                if fix_imports_simple(os.path.join(root, file)):
                    count += 1
    log(f"✅ V2 REPAIR COMPLETE. Updated {count} files.")

if __name__ == "__main__":
    main()
