#!/usr/bin/env python3
import re

# Read orchestrator
with open('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
    content = f.read()

# Find and replace the engine collection section
old_pattern = r"all_engines = \{\}.*?collective_consensus = initialize_collective_consensus\(all_engines\)"

new_code = """
            # 🔥 COLLECT ALL ENGINES - COMPREHENSIVE SYSTEM
            from ALL_ENGINES_INITIALIZER import initialize_all_engines
            
            # Initialize ALL engines (39+ working engines)
            all_engines = initialize_all_engines()
            
            logger.info(f"   🔥 Initialized {len(all_engines)} engines via ALL_ENGINES_INITIALIZER")
            
            # Add orchestrator's existing engine instances
            if hasattr(self, 'trading_engines'):
                for name, engine in self.trading_engines.items():
                    all_engines[f"trading_{name}"] = engine
            
            if hasattr(self, 'advanced_systems'):
                for name, system in self.advanced_systems.items():
                    all_engines[f"advanced_{name}"] = system
            
            # Add specific high-value instances
            if hasattr(self, 'evolution_engine'): all_engines['evolution'] = self.evolution_engine
            if hasattr(self, 'brain_system'): all_engines['brain_system'] = self.brain_system
            if hasattr(self, 'hivemind'): all_engines['hivemind_coord'] = self.hivemind
            if hasattr(self, 'revolutionary_master'): all_engines['revolutionary'] = self.revolutionary_master
            if hasattr(self, 'ultra_rare_orchestrator'): all_engines['ultra_rare'] = self.ultra_rare_orchestrator
            if hasattr(self, 'divine_intelligence'): all_engines['divine'] = self.divine_intelligence
            if hasattr(self, 'supreme_consciousness'): all_engines['supreme'] = self.supreme_consciousness
            
            logger.info(f"   📊 Total engines after orchestrator merging: {len(all_engines)}")

            
            # Initialize collective consensus
            collective_consensus = initialize_collective_consensus(all_engines)"""

# Replace
new_content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

# Write back
with open('/root/bot/COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'w') as f:
    f.write(new_content)

print("[OK] Patch applied successfully!")
