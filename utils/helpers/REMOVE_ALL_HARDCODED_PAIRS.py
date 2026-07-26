#!/usr/bin/env python3
"""
REMOVE ALL HARDCODED PAIRS
Replaces hardcoded pair lists with dynamic discovery across ALL engines
"""

import re
from pathlib import Path

print("\n" + "="*80)
print("🔧 REMOVING ALL HARDCODED PAIRS")
print("="*80 + "\n")

# Files to fix
files_to_fix = [
    'COMPLETE_ULTIMATE_ORCHESTRATOR.py',
    'COMPLETE_UNIFIED_ORCHESTRATOR.py',
    'AGGRESSIVE_SCALPING_ENGINE.py',
    'SMART_SCALPING_ENGINE.py',
    'SESSION_AWARE_TRADING.py',
    'HEDGE_FUND_ARSENAL.py',
    'MONEY_PRINTER_ULTRA_RARE.py',
    'CROSS_EXCHANGE_ARBITRAGE.py',
    'SINGLE_EXCHANGE_ARBITRAGE.py',
]

# Replacement patterns
def replace_hardcoded_pairs(content: str) -> str:
    """Replace all hardcoded pair lists with dynamic fetching"""
    
    # Replace simple hardcoded lists
    patterns = [
        # Pattern: ['BTC/USDT', 'ETH/USDT', ...]
        (r"\[[\s\n]*['\"]BTC/USDT['\"][\s\n]*,[\s\n]*['\"]ETH/USDT['\"][\s\n]*,[^\]]+\]",
         "await self._get_dynamic_pairs()"),
        
        # Pattern: symbols = ['BTC/USDT', ...]
        (r"symbols\s*=\s*\[[\s\n]*['\"]BTC/USDT['\"][^\]]+\]",
         "symbols = await self._get_dynamic_pairs()"),
        
        # Pattern: self.pairs = ['...']
        (r"self\.pairs\s*=\s*\[[\s\n]*['\"][A-Z]+/USDT['\"][^\]]+\]",
         "self.pairs = await self._get_dynamic_pairs()"),
        
        # Pattern: crypto_pairs = ['...']
        (r"crypto_pairs\s*=\s*\[[\s\n]*['\"][A-Z]+/USDT['\"][^\]]+\]",
         "crypto_pairs = await self._get_dynamic_pairs()"),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def add_dynamic_pair_method(content: str) -> str:
    """Add dynamic pair fetching method to class"""
    
    # Check if method already exists
    if '_get_dynamic_pairs' in content:
        return content
    
    method_code = '''
    async def _get_dynamic_pairs(self, min_volume_24h: float = 50000, limit: int = None) -> List[str]:
        """
        Get dynamic trading pairs from pair discovery
        Falls back to fetching from exchange if discovery not available
        """
        # Try to get from dynamic pair discovery first
        if hasattr(self, 'pair_discovery') and self.pair_discovery:
            try:
                await self.pair_discovery.refresh_if_needed()
                all_pairs = self.pair_discovery.get_all_active_pairs()
                if all_pairs:
                    return all_pairs[:limit] if limit else all_pairs
            except Exception as e:
                logger.debug(f"Could not get pairs from discovery: {e}")
        
        # Fallback: Fetch directly from exchange
        try:
            if hasattr(self, 'exchange') and self.exchange:
                tickers = await asyncio.to_thread(self.exchange.fetch_tickers)
                
                pairs = []
                for symbol, ticker in tickers.items():
                    # Only USDT pairs
                    if not symbol.endswith('/USDT'):
                        continue
                    
                    # Skip futures/perps
                    if any(x in symbol for x in ['PERP', ':', '_']):
                        continue
                    
                    # Check volume
                    volume = ticker.get('quoteVolume', 0) or 0
                    if volume < min_volume_24h:
                        continue
                    
                    pairs.append(symbol)
                
                # Sort by volume
                pairs_with_vol = []
                for pair in pairs:
                    vol = tickers[pair].get('quoteVolume', 0) or 0
                    pairs_with_vol.append((pair, vol))
                
                pairs_with_vol.sort(key=lambda x: x[1], reverse=True)
                sorted_pairs = [p[0] for p in pairs_with_vol]
                
                logger.info(f"[OK] Fetched {len(sorted_pairs)} dynamic pairs from exchange")
                return sorted_pairs[:limit] if limit else sorted_pairs
        
        except Exception as e:
            logger.error(f"Could not fetch pairs from exchange: {e}")
        
        # Last resort fallback - top 10 only
        return ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
                'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT']
'''
    
    # Find a class definition to add method to
    class_match = re.search(r'class\s+\w+.*?:\s*\n', content)
    if class_match:
        insert_pos = class_match.end()
        # Find next method or end of class
        next_method = re.search(r'\n\s{4}def\s+', content[insert_pos:])
        if next_method:
            insert_pos += next_method.start()
        
        content = content[:insert_pos] + method_code + content[insert_pos:]
    
    return content

# Process each file
fixed_count = 0
for filename in files_to_fix:
    filepath = Path(filename)
    
    if not filepath.exists():
        print(f"  {filename} - Not found, skipping")
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace hardcoded pairs
        content = replace_hardcoded_pairs(content)
        
        # Add dynamic pair method if it changed
        if content != original_content:
            content = add_dynamic_pair_method(content)
            
            # Backup
            backup_path = filepath.with_suffix('.py.hardcoded_backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed version
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[OK] {filename} - Fixed and backed up")
            fixed_count += 1
        else:
            print(f"✓  {filename} - No hardcoded pairs found")
    
    except Exception as e:
        print(f"[X] {filename} - Error: {e}")

print("\n" + "="*80)
print(f"[OK] FIXED {fixed_count} FILES")
print("="*80)
print("\nBackups created with .hardcoded_backup extension")
print("\nNow pairs will be discovered dynamically!")
print("="*80 + "\n")
