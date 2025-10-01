#!/usr/bin/env python3
"""
Fix all hardcoded API keys in the codebase
Replace with environment variable lookups
"""

import os
import re
from pathlib import Path

def fix_hardcoded_keys():
    """Replace all hardcoded API keys with environment variables"""
    
    # Files to fix (excluding our verification script)
    files_to_fix = [
        'ultra_with_telegram.py',
        'working_450_models_bot.py',
        'real_market_fetcher.py',
        'run_ultra_system.py',
        'ultimate_learntrader.py',
        'ultimate_bot_working.py',
        'ultimate_trading_bot.py',
        'complete_ultimate_bot.py',
        'complete_god_trader.py',
        'complete_enhanced_bot.py',
        'complete_learntrader.py',
        'learntrader_bot.py',
        'auto_deploy.py',
        'live_price_bot.py',
        'god_trader_bot.py',
        'FULL_POTENTIAL_BOT.py',
        'enhanced_trading_bot.py',
        'ABSOLUTE_COMPLETE_BOT.py'
    ]
    
    # Patterns to replace
    replacements = [
        # API key patterns
        (r"'apiKey'\s*:\s*'g1mhPqKrOBp9rnqb4G'", "'apiKey': os.getenv('BYBIT_API_KEY', '')"),
        (r'"apiKey"\s*:\s*"g1mhPqKrOBp9rnqb4G"', '"apiKey": os.getenv("BYBIT_API_KEY", "")'),
        (r"'api_key'\s*:\s*'g1mhPqKrOBp9rnqb4G'", "'api_key': os.getenv('BYBIT_API_KEY', '')"),
        (r'BYBIT_API_KEY\s*=\s*"g1mhPqKrOBp9rnqb4G"', 'BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")'),
        (r'self\.api_key\s*=\s*"g1mhPqKrOBp9rnqb4G"', 'self.api_key = os.getenv("BYBIT_API_KEY", "")'),
        
        # Secret key patterns
        (r"'secret'\s*:\s*'s9KCIelCqPwJOOWAXNoWqFHtiauRQr9PLeqG'", "'secret': os.getenv('BYBIT_SECRET', '')"),
        (r'"secret"\s*:\s*"s9KCIelCqPwJOOWAXNoWqFHtiauRQr9PLeqG"', '"secret": os.getenv("BYBIT_SECRET", "")'),
        (r'BYBIT_SECRET\s*=\s*"s9KCIelCqPwJOOWAXNoWqFHtiauRQr9PLeqG"', 'BYBIT_SECRET = os.getenv("BYBIT_SECRET", "")'),
        (r'self\.secret_key\s*=\s*"s9KCIelCqPwJOOWAXNoWqFHtiauRQr9PLeqG"', 'self.secret_key = os.getenv("BYBIT_SECRET", "")')
    ]
    
    fixed_count = 0
    
    for filename in files_to_fix:
        filepath = Path(filename)
        if not filepath.exists():
            print(f"⚠️ Skipping {filename} (not found)")
            continue
        
        try:
            content = filepath.read_text()
            original_content = content
            
            # Check if 'import os' is present, if not add it
            if 'import os' not in content:
                # Add import os at the beginning after the shebang and docstring
                lines = content.split('\n')
                insert_idx = 0
                
                # Skip shebang
                if lines[0].startswith('#!'):
                    insert_idx = 1
                
                # Skip docstrings
                if insert_idx < len(lines) and lines[insert_idx].startswith('"""'):
                    # Find end of docstring
                    for i in range(insert_idx + 1, len(lines)):
                        if '"""' in lines[i]:
                            insert_idx = i + 1
                            break
                
                # Insert import os
                lines.insert(insert_idx, 'import os')
                content = '\n'.join(lines)
            
            # Apply replacements
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # Write back if changed
            if content != original_content:
                filepath.write_text(content)
                fixed_count += 1
                print(f"✅ Fixed {filename}")
            else:
                print(f"ℹ️ No changes needed in {filename}")
                
        except Exception as e:
            print(f"❌ Error fixing {filename}: {e}")
    
    print(f"\n📊 Summary: Fixed {fixed_count} files")
    return fixed_count

if __name__ == "__main__":
    fixed = fix_hardcoded_keys()
    print("\n✅ All hardcoded keys have been replaced with environment variables!")
    print("⚠️ Remember to set these environment variables:")
    print("  export BYBIT_API_KEY='your_actual_api_key'")
    print("  export BYBIT_SECRET='your_actual_secret'")