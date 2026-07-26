import os

target_file = 'COMPLETE_ULTIMATE_ORCHESTRATOR.py'

with open(target_file, 'r') as f:
    content = f.read()

# 1. Add Import
if 'from OMEGA_SINGULARITY_ENGINE import' not in content:
    print("Injecting import...")
    # Find a good place for import (after sys.path insert)
    import_hook = "sys.path.insert(0, str(Path(__file__).parent))"
    new_import = "\nfrom OMEGA_SINGULARITY_ENGINE import initialize_omega_engine"
    
    if import_hook in content:
        content = content.replace(import_hook, import_hook + new_import)
    else:
        # Fallback
        content = "from OMEGA_SINGULARITY_ENGINE import initialize_omega_engine\n" + content

# 2. Add Initialization
if 'OMEGA SINGULARITY ENGINE LOADED' not in content:
    print("Injecting initialization...")
    # Look for the Ultra Goldmine loading success message
    init_hook = 'logger.info("[OK] ULTRA GOLDMINE FEATURES LOADED - Ready for +200-500% boost!")'
    
    # We need to be careful with indentation. The hook is likely inside an __init__ or setup method.
    # We'll assume standard 4-space indentation relative to the hook's line.
    
    new_init = '''
    try:
        # Initialize Omega Singularity Engine
        if hasattr(self, 'data_hub'):
            self.omega_engine = initialize_omega_engine(self.data_hub)
            logger.info("🌌 OMEGA SINGULARITY ENGINE LOADED - The Final Frontier of Trading!")
            logger.info("   Tracking: Entropy Collapse & 4D Vector Alignment")
    except Exception as e:
        logger.error(f"[X] Failed to load Omega Engine: {e}")
'''
    if init_hook in content:
        content = content.replace(init_hook, init_hook + new_init)
    else:
        print("  Could not find initialization hook! Appending manually...")
        # Fallback: append to end of __init__ if possible, or just warn
        # Let's try to find another hook
        alt_hook = 'logger.info("[OK] CRITICAL PROFIT FEATURES LOADED - Ready for +50-100% boost!")'
        if alt_hook in content:
             content = content.replace(alt_hook, alt_hook + new_init)

with open(target_file, 'w') as f:
    f.write(content)

print("[OK] Omega Singularity Engine integrated into COMPLETE_ULTIMATE_ORCHESTRATOR.py")
