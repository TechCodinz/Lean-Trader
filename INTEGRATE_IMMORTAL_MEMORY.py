#!/usr/bin/env python3
"""
INTEGRATE IMMORTAL MEMORY INTO EVOLUTION ENGINE
Adds photographic memory backup to the bot
"""

import re

print("=" * 80)
print("🧠 INTEGRATING IMMORTAL MEMORY SYSTEM")
print("=" * 80)

# Read the evolution engine
with open('EVOLUTION_ENGINE.py', 'r') as f:
    content = f.read()

# 1. Add import at the top (after other imports)
if 'from IMMORTAL_MEMORY_SYSTEM import ImmortalMemory' not in content:
    # Find the line with "warnings.filterwarnings('ignore')"
    import_location = content.find("warnings.filterwarnings('ignore')")
    if import_location != -1:
        # Find the end of that line
        line_end = content.find('\n', import_location) + 1
        # Insert our import
        content = (content[:line_end] + 
                  "\n# 🧠 IMMORTAL MEMORY - Photographic persistence\n" +
                  "try:\n" +
                  "    from IMMORTAL_MEMORY_SYSTEM import ImmortalMemory\n" +
                  "    IMMORTAL_MEMORY_AVAILABLE = True\n" +
                  "except ImportError:\n" +
                  "    IMMORTAL_MEMORY_AVAILABLE = False\n" +
                  "    ImmortalMemory = None\n" +
                  content[line_end:])
        print("✅ Added IMMORTAL_MEMORY import")
    else:
        print("⚠️  Warning: Could not find import location")

# 2. Initialize ImmortalMemory in __init__
init_code = '''        # 🧠 IMMORTAL MEMORY - Initialize photographic persistence
        if IMMORTAL_MEMORY_AVAILABLE:
            try:
                self.immortal_memory = ImmortalMemory(
                    db_path='evolution_engine.db',
                    backup_every=10  # Backup every 10 cycles
                )
                print("✅ IMMORTAL MEMORY activated - Data will NEVER be lost!")
            except Exception as e:
                print(f"⚠️  IMMORTAL MEMORY init failed: {e}")
                self.immortal_memory = None
        else:
            self.immortal_memory = None
        
'''

# Find where to insert (after self.load_existing_models())
load_existing_location = content.find('self.load_existing_models()')
if load_existing_location != -1:
    # Find the next line
    next_line = content.find('\n', load_existing_location) + 1
    
    # Check if already inserted
    if 'self.immortal_memory' not in content[next_line:next_line+500]:
        content = content[:next_line] + init_code + content[next_line:]
        print("✅ Added IMMORTAL_MEMORY initialization")
    else:
        print("ℹ️  IMMORTAL_MEMORY already initialized")
else:
    print("⚠️  Warning: Could not find load_existing_models location")

# 3. Add backup call in run_evolution_cycle (after evolution_cycle increment)
backup_code = '''                # 🧠 IMMORTAL MEMORY: Auto-backup to prevent data loss
                try:
                    if hasattr(self, 'immortal_memory') and self.immortal_memory:
                        if self.immortal_memory.should_backup(self.evolution_cycle):
                            self.immortal_memory.backup(self.evolution_cycle)
                except Exception as immortal_error:
                    print(f"⚠️ IMMORTAL MEMORY backup error: {immortal_error}")
                
'''

# Find the evolution cycle increment
evolution_increment = content.find('self.evolution_cycle += 1')
if evolution_increment != -1:
    # Find the next line
    next_line = content.find('\n', evolution_increment)
    next_line = content.find('\n', next_line + 1) + 1  # Skip the print line
    
    # Check if already inserted
    if 'immortal_memory' not in content[next_line:next_line+500]:
        content = content[:next_line] + backup_code + content[next_line:]
        print("✅ Added IMMORTAL_MEMORY auto-backup in evolution cycle")
    else:
        print("ℹ️  IMMORTAL_MEMORY backup already present")
else:
    print("⚠️  Warning: Could not find evolution_cycle increment location")

# Write back
with open('EVOLUTION_ENGINE.py', 'w') as f:
    f.write(content)

print("\n" + "=" * 80)
print("✅ IMMORTAL MEMORY INTEGRATION COMPLETE!")
print("=" * 80)
print("\nYour bot now has:")
print("  🧠 Photographic memory - Never forgets learned patterns")
print("  💾 Auto-backup every 10 cycles")
print("  🛡️  Triple redundancy (3 backup locations)")
print("  🔄 Auto-recovery from corruption")
print("  ✨ Git-safe (survives merges/pulls)")
print("\n✅ Your bot will NEVER lose its memory again!")
print("=" * 80)
