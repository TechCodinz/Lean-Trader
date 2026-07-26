
import os
import re

ROOT_DIR = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix"

# Map of Module Name -> New Package Path (dot notation)
# This allows converting "import X" to "from path.to import X"
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
    "WEBSOCKET_DATA_FEED": "data.feeds",
    # Add common utilities if needed
}

def log(msg):
    print(f"[FIX_IMPORTS] {msg}")

def fix_imports_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        modified = False
        
        # Strategy: Replace "import X" with "from path import X"
        # Strategy: Replace "from X import Y" with "from path.X import Y"
        
        for module, pkg_path in MODULE_MAP.items():
            # Regex for "import MODULE" -> "from PKG import MODULE"
            # Look for lines that start with import or follow ;
            # Handle "import MODULE"
            pattern_import = r'(?m)^(?:import\s+)' + re.escape(module) + r'(?:\s|$)'
            if re.search(pattern_import, content):
                content = re.sub(pattern_import, f'from {pkg_path} import {module}', content)
                modified = True
                
            # Handle "from MODULE import ..." -> "from PKG.MODULE import ..."
            pattern_from = r'(?m)^(?:from\s+)' + re.escape(module) + r'(?:\s+import)'
            if re.search(pattern_from, content):
                content = re.sub(pattern_from, f'from {pkg_path}.{module} import', content)
                modified = True
                
        # Also need to fix relative imports if files moved deep
        # But for now, let's focus on the absolute imports of Key Modules
        
        if modified and content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            # log(f"Fixed imports in: {os.path.basename(filepath)}")
            return True
            
    except Exception as e:
        log(f"Error processing {filepath}: {e}")
        return False

def main():
    log("🚀 STARTING GLOBAL IMPORT REPAIR")
    
    count = 0
    # Walk all files
    for root, dirs, files in os.walk(ROOT_DIR):
        if "_BACKUP" in root or ".git" in root: continue
        
        for file in files:
            if file.endswith(".py"):
                if fix_imports_in_file(os.path.join(root, file)):
                    count += 1
                    
    log(f"✅ REPAIR COMPLETE. Updated imports in {count} files.")

if __name__ == "__main__":
    main()
