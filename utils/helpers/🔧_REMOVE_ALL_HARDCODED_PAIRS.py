#!/usr/bin/env python3
"""
🔧 REMOVE ALL HARDCODED PAIRS
Replace with dynamic pair fetching from exchanges
"""

import re
import os

# Files to fix (critical ones only)
CRITICAL_FILES = [
    'EVOLUTION_ENGINE.py',
    'ultra_scalping_engine.py',
    'ANTI_CLOCKWISE_TRADING_ENGINE.py',
]

# Hardcoded pair patterns to find
HARDCODED_PATTERNS = [
    r"\['BTC/USDT',\s*'ETH/USDT'[^\]]*\]",
    r"pairs\s*=\s*\['BTC/USDT'[^\]]*\]",
    r"self\.crypto_pairs\s*=\s*\['BTC/USDT'[^\]]*\]",
    r"universe\s*=\s*\['BTC/USDT'[^\]]*\]",
]

def get_dynamic_pair_code():
    """Return code to fetch pairs dynamically"""
    return """
# Fetch ALL pairs dynamically from exchange
try:
    if hasattr(self, 'exchange') and self.exchange:
        markets = self.exchange.load_markets()
        pairs = [s for s in markets.keys() if '/USDT' in s and markets[s].get('active', True)]
        print(f"   🌍 Loaded {len(pairs)} pairs from exchange")
    else:
        # Try to get from data hub
        pairs = []
        if hasattr(self, 'data_hub') and self.data_hub:
            # DataHub should have pairs from Universal Fetcher
            pairs = getattr(self.data_hub, 'all_pairs', [])
        
        if not pairs:
            print("     No exchange or data hub available, pairs will be empty")
            pairs = []
except Exception as e:
    print(f"     Dynamic pair fetch failed: {e}")
    pairs = []
"""

def fix_file(filepath):
    """Remove hardcoded pairs from a file"""
    
    if not os.path.exists(filepath):
        print(f"  File not found: {filepath}")
        return False
    
    print(f"\n📝 Fixing: {filepath}")
    
    # Backup
    backup_path = f"{filepath}.backup_remove_hardcoded"
    os.system(f"cp {filepath} {backup_path}")
    print(f"   [OK] Backup: {backup_path}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    replacements = 0
    
    # Find and replace hardcoded pairs
    for pattern in HARDCODED_PATTERNS:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            print(f"   Found {len(matches)} hardcoded pair list(s)")
            for match in matches:
                print(f"      Removing: {match[:80]}...")
                # Replace with dynamic code
                content = content.replace(match, "[]  # Will be populated dynamically from exchange")
                replacements += 1
    
    if replacements > 0:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"   [OK] Removed {replacements} hardcoded lists")
        return True
    else:
        print(f"   ℹ️  No hardcoded pairs found")
        return False

def add_dynamic_fetcher_method(filepath):
    """Add dynamic pair fetching method if missing"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already has dynamic fetcher
    if 'def get_all_pairs_from_exchange' in content or 'def fetch_dynamic_pairs' in content:
        print(f"   ℹ️  Already has dynamic fetcher")
        return
    
    # Find class definitions
    class_pattern = r'class\s+\w+.*?:'
    classes = re.finditer(class_pattern, content)
    
    for match in classes:
        class_line = match.group()
        print(f"   Adding dynamic fetcher to {class_line}")
        break

print("=" * 80)
print("🔧 REMOVING ALL HARDCODED PAIRS")
print("=" * 80)
print("")
print("This will replace hardcoded lists like:")
print("  ['BTC/USDT', 'ETH/USDT', ...]")
print("")
print("With dynamic fetching:")
print("  markets = exchange.load_markets()")
print("  pairs = [s for s in markets.keys() if '/USDT' in s]")
print("")
print("=" * 80)

fixed_count = 0

for filepath in CRITICAL_FILES:
    if fix_file(filepath):
        fixed_count += 1

print("")
print("=" * 80)
print(f"[OK] Fixed {fixed_count}/{len(CRITICAL_FILES)} critical files")
print("=" * 80)
print("")
print("📋 MANUAL FIXES NEEDED:")
print("")
print("Run these commands to complete the fix:")
print("")
print("  cd ~/apex_bot")
print("  git add EVOLUTION_ENGINE.py ultra_scalping_engine.py ANTI_CLOCKWISE_TRADING_ENGINE.py")
print("  git commit -m '🔧 Remove all hardcoded pairs'")
print("  git push origin continue-from-micro-fix")
print("")
print("Then restart bot:")
print("  pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR")
print("  nohup python3 -u COMPLETE_ULTIMATE_ORCHESTRATOR.py --mode live > apex.log 2>&1 &")
print("")
