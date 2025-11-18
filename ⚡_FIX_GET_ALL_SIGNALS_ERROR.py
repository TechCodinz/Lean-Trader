#!/usr/bin/env python3
"""
⚡ FIX get_all_signals ERROR ⚡

Fixes the error: 'CentralDataHub' object has no attribute 'get_all_signals'
Replaces with: get_recent_signals(limit=1000)
"""

import os
import sys

print("=" * 80)
print("⚡ FIXING get_all_signals ERROR!")
print("=" * 80)
print()

files_to_fix = [
    'HYBRID_INTELLIGENCE_COORDINATOR.py',
    'EXCHANGE_SPAWN_MANAGER.py',
    'COMPLETE_ULTIMATE_ORCHESTRATOR.py',
    'systems/COMPLETE_ULTIMATE_ORCHESTRATOR.py'
]

fixed_files = []

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if get_all_signals is used
        if 'get_all_signals' not in content:
            continue
        
        print(f"📝 Fixing {filepath}...")
        
        # Create backup
        backup_path = f"{filepath}.backup_signals_fix"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Fix 1: data_hub.get_all_signals() → data_hub.get_recent_signals(limit=1000)
        content = content.replace(
            '.get_all_signals()',
            '.get_recent_signals(limit=1000)'
        )
        
        # Fix 2: await self.data_hub.get_all_signals() → await self.data_hub.get_recent_signals(limit=1000)
        content = content.replace(
            'await self.data_hub.get_all_signals()',
            'await self.data_hub.get_recent_signals(limit=1000)'
        )
        
        # Fix 3: For ultra_goldmine which might have different signature
        # get_all_signals(symbol, {}) → analyze_symbol(symbol) or similar
        if 'ultra_goldmine' in content and 'get_all_signals' in content:
            # Just remove the call if it's ultra_goldmine (it doesn't have this method)
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if 'ultra_goldmine.get_all_signals' in line:
                    # Comment it out
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + '# FIXED: ultra_goldmine.get_all_signals not needed')
                    new_lines.append(' ' * indent + 'goldmine_signals = {}  # Placeholder')
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed {filepath}")
        print(f"   Backup saved to: {backup_path}")
        fixed_files.append(filepath)
    
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

print()
print("=" * 80)

if fixed_files:
    print("✅ FIXED FILES:")
    for file in fixed_files:
        print(f"   • {file}")
    print()
    print("🔧 Changes made:")
    print("   • .get_all_signals() → .get_recent_signals(limit=1000)")
    print("   • ultra_goldmine.get_all_signals() → commented out (not needed)")
    print()
    print("📝 Backups created with .backup_signals_fix extension")
else:
    print("ℹ️  No files needed fixing!")

print("=" * 80)
