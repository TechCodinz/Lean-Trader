
import os
import re

TARGET_FILE = r"C:\Users\User\Downloads\Lean-Trader-continue-from-micro-fix\core\orchestrators\COMPLETE_ULTIMATE_ORCHESTRATOR.py"

def patch_file():
    print(f"Patching {TARGET_FILE}...")
    
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix Imports
    # We use regex to handle indentation and context
    
    # Matches: "    from router import ..."
    content = re.sub(r'from router import', r'from engines.routing.router import', content)
    
    # Matches: "    from market_router import ..."
    content = re.sub(r'from market_router import', r'from engines.routing.market_router import', content)
    
    # Matches: "    from dex_router import ..."
    content = re.sub(r'from dex_router import', r'from engines.routing.dex_router import', content)
    
    # 2. Fix Emojis (UnicodeEncodeError on Windows)
    # Replace common emojis with empty string or text equivalent
    replacements = {
        "\u26a0\ufe0f": "", # Warning sign
        "🚀": ">>",
        "❌": "[X]",
        "✅": "[OK]",
        "⚠️": "",
        "🔌": "",
        "\U0001f3d7\ufe0f": "", # Crane
        "\u274c": "[X]" # Red cross
    }
    
    for emoji, text in replacements.items():
        content = content.replace(emoji, text)
        
    # 3. Fix specifc line found in logs
    content = content.replace(
        "Running without DIVINE INTELLIGENCE - Missing +300-1000% profit potential!",
        "Running without DIVINE INTELLIGENCE - Missing +300-1000 pct profit potential!"
    )
    
    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Patch applied successfully.")

if __name__ == "__main__":
    patch_file()
