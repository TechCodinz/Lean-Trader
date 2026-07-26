#!/usr/bin/env python3
"""
DYNAMIC ENGINE ACTIVATOR

Auto-discovers and initializes ALL engines from DISCOVERED_ENGINES.txt
No manual coding needed - discovers and activates everything!
"""

import logging
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger(__name__)

# All possible module locations to search
SEARCH_MODULES = [
    '',  # Root
    'elite_stack.core',
    'elite_stack',
    'pitch_bent.core',
    'engines',
    'core',
    'extracted_engines',
]

def parse_discovered_engines():
    """Parse DISCOVERED_ENGINES.txt for unique engine classes"""
    try:
        with open('DISCOVERED_ENGINES.txt', 'r') as f:
            content = f.read()
        
        # Extract unique engine classes section
        if 'UNIQUE ENGINE CLASSES:' in content:
            classes_section = content.split('UNIQUE ENGINE CLASSES:')[1]
            classes = [line.strip() for line in classes_section.split('\n') 
                      if line.strip() and 'Engine' in line]
            return classes
        return []
    except Exception as e:
        logger.error(f"Could not parse discovered engines: {e}")
        return []

def dynamic_import(class_name):
    """Try to import a class from various possible locations"""
    
    # Try direct import from file matching class name
    possible_files = [
        class_name,
        f"{class_name.upper()}",
        f"{'_'.join([c for c in class_name if c.isupper()])}",
    ]
    
    for file_name in possible_files:
        for search_path in SEARCH_MODULES:
            try:
                if search_path:
                    module_name = f"{search_path}.{file_name}"
                else:
                    module_name = file_name
                
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    return getattr(module, class_name)
            except:
                continue
    
    return None

def initialize_all_engines_dynamic():
    """
    Dynamically initialize ALL engines discovered
    """
    logger.info("=" * 80)
    logger.info("🔥 DYNAMIC ENGINE ACTIVATION - AUTO-DISCOVERING ALL ENGINES")
    logger.info("=" * 80)
    
    all_engines = {}
    
    # Get discovered engine classes
    engine_classes = parse_discovered_engines()
    logger.info(f"\n📊 Found {len(engine_classes)} unique engine classes to activate")
    
    # Initialize each discovered engine
    successful = 0
    failed = 0
    
    for engine_class in engine_classes:
        try:
            logger.info(f"\n[{successful + failed + 1}/{len(engine_classes)}] {engine_class}...")
            
            # Try to import the class
            EngineClass = dynamic_import(engine_class)
            
            if EngineClass:
                # Try to instantiate
                try:
                    engine_instance = EngineClass()
                    all_engines[engine_class.lower()] = engine_instance
                    logger.info(f"  [OK] {engine_class} activated")
                    successful += 1
                except TypeError:
                    # Try with mock arguments if __init__ requires them
                    try:
                        engine_instance = EngineClass(None, None)
                        all_engines[engine_class.lower()] = engine_instance
                        logger.info(f"  [OK] {engine_class} activated (with mock args)")
                        successful += 1
                    except:
                        logger.warning(f"    {engine_class} - could not instantiate")
                        failed += 1
            else:
                logger.warning(f"    {engine_class} - could not import")
                failed += 1
                
        except Exception as e:
            logger.warning(f"    {engine_class} - {str(e)[:100]}")
            failed += 1
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info(f"🔥 DYNAMIC ACTIVATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"  [OK] Successfully activated: {successful}")
    logger.info(f"    Failed to activate: {failed}")
    logger.info(f"  📊 Total engines ready: {len(all_engines)}")
    logger.info("=" * 80)
    
    return all_engines

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engines = initialize_all_engines_dynamic()
    
    print(f"\n[OK] {len(engines)} engines activated!")
    print("\nActivated engines:")
    for name in sorted(engines.keys()):
        print(f"  - {name}")
