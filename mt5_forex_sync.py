#!/usr/bin/env python3
"""
🌍💱 BYBIT MT5 FOREX PAIRS INTEGRATION SYSTEM 💱🌍

COMPLETE AUTOMATED SYSTEM FOR BYBIT MT5 FOREX PAIRS

FEATURES:
1. Scrapes Bybit MT5 forex pairs from official docs
2. Stores to bybit_mt5_pairs.json
3. Merges with existing forex_pairs.json
4. Auto-updates every 24 hours
5. Integrates with trading engine
6. Validates and logs all changes

RESULT: Bot NEVER misses a tradable MT5 pair!
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Web scraping
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    logging.warning("⚠️  requests or beautifulsoup4 not available - scraping disabled")

logger = logging.getLogger(__name__)


class MT5ForexSync:
    """
    🌍 Complete MT5 Forex Synchronization System
    
    Scrapes, merges, and auto-updates Bybit MT5 forex pairs
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.bybit_mt5_file = self.data_dir / "bybit_mt5_pairs.json"
        self.forex_pairs_file = self.data_dir / "forex_pairs.json"
        self.merged_file = self.data_dir / "merged_forex_pairs.json"
        self.update_log_file = self.data_dir / "mt5_sync_log.txt"
        
        # Bybit MT5 help center URL
        self.bybit_mt5_url = "https://www.bybit.com/en/help-center/article/Contracts-Available-on-MT5-and-Specifications"
        
        # Alternative: Direct API endpoint if available
        self.bybit_api_url = "https://api.bybit.com/v5/market/instruments-info"
        
        # Last update tracking
        self.last_update = None
        self.update_interval = 24 * 3600  # 24 hours in seconds
        
        logger.info("=" * 80)
        logger.info("🌍 MT5 FOREX SYNC INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   Data directory: {self.data_dir}")
        logger.info(f"   Update interval: 24 hours")
        logger.info(f"   Scraping available: {SCRAPING_AVAILABLE}")
        logger.info("=" * 80)
    
    async def scrape_bybit_mt5_pairs(self) -> List[Dict]:
        """
        STEP 1: Scrape Bybit MT5 forex pairs from help center
        
        Returns list of pairs with metadata
        """
        logger.info("🔍 STEP 1: Scraping Bybit MT5 forex pairs...")
        
        if not SCRAPING_AVAILABLE:
            logger.warning("⚠️  Scraping not available - using fallback hardcoded pairs")
            return self._get_fallback_mt5_pairs()
        
        pairs = []
        
        try:
            # Try scraping help center page
            logger.info(f"   Fetching: {self.bybit_mt5_url}")
            response = requests.get(self.bybit_mt5_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find tables with forex pairs
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all('td')
                        
                        if len(cells) >= 2:
                            # Extract pair symbol
                            symbol_text = cells[0].get_text(strip=True)
                            
                            # Check if it ends with '+'
                            if symbol_text.endswith('+'):
                                pair_data = {
                                    'symbol': symbol_text,
                                    'base_symbol': symbol_text.replace('+', ''),
                                    'description': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                                    'contract_size': cells[2].get_text(strip=True) if len(cells) > 2 else '100000',
                                    'leverage': cells[3].get_text(strip=True) if len(cells) > 3 else '100',
                                    'currency': cells[4].get_text(strip=True) if len(cells) > 4 else 'USD',
                                    'source': 'bybit_mt5_help_center',
                                    'last_updated': datetime.now().isoformat()
                                }
                                pairs.append(pair_data)
                                logger.debug(f"      ✅ {symbol_text}")
                
                logger.info(f"   ✅ Scraped {len(pairs)} MT5 pairs from help center")
            
            else:
                logger.warning(f"   ⚠️  Help center returned {response.status_code}")
                raise Exception("Help center unavailable")
        
        except Exception as e:
            logger.warning(f"   ⚠️  Scraping help center failed: {e}")
            logger.info("   📡 Trying API endpoint...")
            
            # Fallback: Try API
            try:
                response = requests.get(
                    self.bybit_api_url,
                    params={'category': 'linear', 'limit': 1000},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    instruments = data.get('result', {}).get('list', [])
                    
                    for inst in instruments:
                        symbol = inst.get('symbol', '')
                        
                        # Filter for forex pairs
                        if any(fx in symbol for fx in ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']):
                            pair_data = {
                                'symbol': symbol,
                                'base_symbol': symbol.replace('+', ''),
                                'description': inst.get('name', ''),
                                'contract_size': inst.get('lotSizeFilter', {}).get('minOrderQty', '100000'),
                                'leverage': inst.get('leverageFilter', {}).get('maxLeverage', '100'),
                                'currency': 'USD',
                                'source': 'bybit_api',
                                'last_updated': datetime.now().isoformat()
                            }
                            pairs.append(pair_data)
                    
                    logger.info(f"   ✅ Got {len(pairs)} forex pairs from API")
                
            except Exception as api_error:
                logger.error(f"   ❌ API also failed: {api_error}")
        
        # If scraping completely failed, use fallback
        if not pairs:
            logger.warning("   ⚠️  All scraping methods failed - using fallback")
            pairs = self._get_fallback_mt5_pairs()
        
        logger.info(f"✅ STEP 1 COMPLETE: {len(pairs)} MT5 pairs collected")
        return pairs
    
    def _get_fallback_mt5_pairs(self) -> List[Dict]:
        """
        Fallback: Hardcoded common MT5 forex pairs
        Used if scraping fails
        """
        common_pairs = [
            'EURUSD+', 'GBPUSD+', 'USDJPY+', 'USDCHF+', 'USDCAD+', 'AUDUSD+', 'NZDUSD+',
            'EURJPY+', 'EURGBP+', 'EURCHF+', 'GBPJPY+', 'AUDJPY+', 'AUDNZD+', 'CADJPY+',
            'CHFJPY+', 'EURAUD+', 'EURCAD+', 'EURNZD+', 'GBPAUD+', 'GBPCAD+', 'GBPCHF+',
            'GBPNZD+', 'NZDJPY+', 'AUDCAD+', 'AUDCHF+', 'CADCHF+', 'NZDCAD+', 'NZDCHF+'
        ]
        
        return [{
            'symbol': pair,
            'base_symbol': pair.replace('+', ''),
            'description': f'{pair.replace("+", "")} Forex Pair',
            'contract_size': '100000',
            'leverage': '100',
            'currency': 'USD',
            'source': 'fallback',
            'last_updated': datetime.now().isoformat()
        } for pair in common_pairs]
    
    async def save_bybit_mt5_pairs(self, pairs: List[Dict]) -> bool:
        """
        STEP 2: Save scraped pairs to bybit_mt5_pairs.json
        """
        logger.info("💾 STEP 2: Saving Bybit MT5 pairs...")
        
        try:
            with open(self.bybit_mt5_file, 'w') as f:
                json.dump(pairs, f, indent=2)
            
            logger.info(f"   ✅ Saved {len(pairs)} pairs to {self.bybit_mt5_file}")
            return True
        
        except Exception as e:
            logger.error(f"   ❌ Failed to save: {e}")
            return False
    
    def load_existing_forex_pairs(self) -> List[Dict]:
        """
        Load existing forex_pairs.json if it exists
        """
        if not self.forex_pairs_file.exists():
            logger.info("   ℹ️  No existing forex_pairs.json - starting fresh")
            return []
        
        try:
            with open(self.forex_pairs_file, 'r') as f:
                pairs = json.load(f)
            logger.info(f"   ✅ Loaded {len(pairs)} existing forex pairs")
            return pairs
        
        except Exception as e:
            logger.error(f"   ❌ Failed to load existing pairs: {e}")
            return []
    
    async def merge_pairs(self, bybit_pairs: List[Dict]) -> Dict:
        """
        STEP 3: Merge Bybit MT5 pairs with existing forex pairs
        
        Returns merged data + statistics
        """
        logger.info("🔀 STEP 3: Merging MT5 pairs with existing forex pairs...")
        
        # Load existing pairs
        existing_pairs = self.load_existing_forex_pairs()
        
        # Create lookup by symbol
        existing_symbols = {p['symbol']: p for p in existing_pairs}
        bybit_symbols = {p['symbol']: p for p in bybit_pairs}
        
        # Also check base_symbol for matching
        existing_base = {p.get('base_symbol', p['symbol']): p for p in existing_pairs}
        
        # Track changes
        added = []
        updated = []
        unchanged = []
        
        # Merge
        merged = []
        all_symbols = set(existing_symbols.keys()) | set(bybit_symbols.keys())
        
        for symbol in sorted(all_symbols):
            if symbol in bybit_symbols:
                bybit_pair = bybit_symbols[symbol]
                
                if symbol in existing_symbols:
                    # Pair exists - merge metadata
                    existing = existing_symbols[symbol]
                    merged_pair = {**existing, **bybit_pair}  # Bybit takes precedence
                    merged_pair['sources'] = list(set(
                        existing.get('sources', [existing.get('source', 'manual')]) +
                        [bybit_pair['source']]
                    ))
                    updated.append(symbol)
                else:
                    # New pair from Bybit
                    merged_pair = bybit_pair
                    merged_pair['sources'] = [bybit_pair['source']]
                    added.append(symbol)
                
                merged.append(merged_pair)
            
            elif symbol in existing_symbols:
                # Exists but not in Bybit - keep it
                merged.append(existing_symbols[symbol])
                unchanged.append(symbol)
        
        # Statistics
        stats = {
            'total_merged': len(merged),
            'from_bybit_mt5': len(bybit_pairs),
            'from_existing': len(existing_pairs),
            'newly_added': len(added),
            'updated': len(updated),
            'unchanged': len(unchanged),
            'added_symbols': added,
            'updated_symbols': updated,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"   ✅ Merged pairs:")
        logger.info(f"      Total: {stats['total_merged']}")
        logger.info(f"      Newly added: {stats['newly_added']}")
        logger.info(f"      Updated: {stats['updated']}")
        logger.info(f"      Unchanged: {stats['unchanged']}")
        
        if added:
            logger.info(f"   🆕 New pairs added:")
            for symbol in added[:10]:  # Show first 10
                logger.info(f"      • {symbol}")
            if len(added) > 10:
                logger.info(f"      ... and {len(added) - 10} more")
        
        return {'merged_pairs': merged, 'stats': stats}
    
    async def save_merged_pairs(self, merged_data: Dict) -> bool:
        """
        Save merged pairs to merged_forex_pairs.json
        """
        logger.info("💾 STEP 3b: Saving merged pairs...")
        
        try:
            merged_pairs = merged_data['merged_pairs']
            stats = merged_data['stats']
            
            # Save merged pairs
            with open(self.merged_file, 'w') as f:
                json.dump(merged_pairs, f, indent=2)
            
            logger.info(f"   ✅ Saved {len(merged_pairs)} pairs to {self.merged_file}")
            
            # Log the update
            self._log_update(stats)
            
            return True
        
        except Exception as e:
            logger.error(f"   ❌ Failed to save merged pairs: {e}")
            return False
    
    def _log_update(self, stats: Dict):
        """
        Log update to update log file
        """
        try:
            with open(self.update_log_file, 'a') as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"MT5 FOREX SYNC UPDATE\n")
                f.write(f"Timestamp: {stats['timestamp']}\n")
                f.write(f"{'=' * 80}\n")
                f.write(f"Total merged pairs: {stats['total_merged']}\n")
                f.write(f"From Bybit MT5: {stats['from_bybit_mt5']}\n")
                f.write(f"From existing: {stats['from_existing']}\n")
                f.write(f"Newly added: {stats['newly_added']}\n")
                f.write(f"Updated: {stats['updated']}\n")
                f.write(f"Unchanged: {stats['unchanged']}\n")
                
                if stats['added_symbols']:
                    f.write(f"\nNewly added symbols:\n")
                    for sym in stats['added_symbols']:
                        f.write(f"  • {sym}\n")
                
                if stats['updated_symbols']:
                    f.write(f"\nUpdated symbols:\n")
                    for sym in stats['updated_symbols'][:20]:  # First 20
                        f.write(f"  • {sym}\n")
                    if len(stats['updated_symbols']) > 20:
                        f.write(f"  ... and {len(stats['updated_symbols']) - 20} more\n")
                
                f.write(f"{'=' * 80}\n")
        
        except Exception as e:
            logger.error(f"❌ Failed to write log: {e}")
    
    async def full_sync(self) -> bool:
        """
        Complete sync: Scrape → Save → Merge → Save
        
        Returns True if successful
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("🔄 STARTING FULL MT5 FOREX SYNC")
        logger.info("=" * 80)
        logger.info("")
        
        # Step 1: Scrape
        bybit_pairs = await self.scrape_bybit_mt5_pairs()
        
        if not bybit_pairs:
            logger.error("❌ No pairs scraped - aborting sync")
            return False
        
        # Step 2: Save Bybit pairs
        await self.save_bybit_mt5_pairs(bybit_pairs)
        
        # Step 3: Merge
        merged_data = await self.merge_pairs(bybit_pairs)
        
        # Step 3b: Save merged
        success = await self.save_merged_pairs(merged_data)
        
        if success:
            self.last_update = datetime.now()
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ FULL MT5 FOREX SYNC COMPLETE!")
            logger.info("=" * 80)
            logger.info(f"   Total pairs: {merged_data['stats']['total_merged']}")
            logger.info(f"   File: {self.merged_file}")
            logger.info("")
        
        return success
    
    async def auto_update_loop(self):
        """
        STEP 4: Auto-update every 24 hours
        
        Runs in background, continuously updating pairs
        """
        logger.info("=" * 80)
        logger.info("🔄 AUTO-UPDATE SYSTEM STARTED")
        logger.info("=" * 80)
        logger.info(f"   Update interval: 24 hours")
        logger.info(f"   Next update: {(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')}")
        logger.info("=" * 80)
        logger.info("")
        
        while True:
            try:
                # Do full sync
                await self.full_sync()
                
                # Wait 24 hours
                logger.info(f"⏳ Next update in 24 hours ({(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')})")
                await asyncio.sleep(self.update_interval)
            
            except Exception as e:
                logger.error(f"❌ Auto-update error: {e}")
                # Wait 1 hour and retry
                logger.info("   ⏳ Retrying in 1 hour...")
                await asyncio.sleep(3600)
    
    def get_merged_pairs(self) -> List[Dict]:
        """
        Get merged forex pairs for trading engine
        """
        if not self.merged_file.exists():
            logger.warning(f"⚠️  {self.merged_file} not found - run sync first!")
            return []
        
        try:
            with open(self.merged_file, 'r') as f:
                pairs = json.load(f)
            return pairs
        
        except Exception as e:
            logger.error(f"❌ Failed to load merged pairs: {e}")
            return []
    
    def get_tradable_symbols(self) -> List[str]:
        """
        Get list of tradable symbols (for trading engine)
        """
        pairs = self.get_merged_pairs()
        return [p['symbol'] for p in pairs]
    
    def get_pair_metadata(self, symbol: str) -> Optional[Dict]:
        """
        Get metadata for a specific pair
        """
        pairs = self.get_merged_pairs()
        
        for pair in pairs:
            if pair['symbol'] == symbol or pair.get('base_symbol') == symbol:
                return pair
        
        return None
    
    def validate_and_log(self):
        """
        STEP 6: Validation and logging
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 MT5 FOREX SYNC VALIDATION")
        logger.info("=" * 80)
        
        # Load all files
        bybit_pairs = []
        if self.bybit_mt5_file.exists():
            with open(self.bybit_mt5_file, 'r') as f:
                bybit_pairs = json.load(f)
        
        existing_pairs = []
        if self.forex_pairs_file.exists():
            with open(self.forex_pairs_file, 'r') as f:
                existing_pairs = json.load(f)
        
        merged_pairs = self.get_merged_pairs()
        
        # Statistics
        logger.info(f"   Bybit MT5 pairs: {len(bybit_pairs)}")
        logger.info(f"   Existing forex pairs: {len(existing_pairs)}")
        logger.info(f"   Total merged pairs: {len(merged_pairs)}")
        logger.info("")
        
        if merged_pairs:
            # Sample pairs
            logger.info("   Sample pairs:")
            for pair in merged_pairs[:10]:
                logger.info(f"      • {pair['symbol']} ({pair.get('description', 'N/A')})")
            if len(merged_pairs) > 10:
                logger.info(f"      ... and {len(merged_pairs) - 10} more")
            
            # Currency breakdown
            currencies = defaultdict(int)
            for pair in merged_pairs:
                currencies[pair.get('currency', 'USD')] += 1
            
            logger.info("")
            logger.info("   Currency breakdown:")
            for curr, count in currencies.items():
                logger.info(f"      {curr}: {count} pairs")
            
            # Leverage ranges
            leverages = [int(p.get('leverage', '100').replace(':', '').replace('x', '')) 
                        for p in merged_pairs 
                        if p.get('leverage')]
            
            if leverages:
                logger.info("")
                logger.info(f"   Leverage range: {min(leverages)}x - {max(leverages)}x")
        
        logger.info("=" * 80)
        logger.info("")


# Singleton
_mt5_sync = None

def get_mt5_forex_sync():
    """Get or create MT5 forex sync instance"""
    global _mt5_sync
    if _mt5_sync is None:
        _mt5_sync = MT5ForexSync()
    return _mt5_sync


async def initialize_mt5_forex_sync():
    """
    Initialize and run first sync
    
    Call this when bot starts
    """
    sync = get_mt5_forex_sync()
    
    # Run first sync
    success = await sync.full_sync()
    
    if success:
        sync.validate_and_log()
    
    return sync


async def start_mt5_auto_update():
    """
    Start auto-update background task
    
    Call this to enable 24-hour auto-updates
    """
    sync = get_mt5_forex_sync()
    await sync.auto_update_loop()


if __name__ == '__main__':
    # Test
    async def test():
        print("=" * 80)
        print("🧪 MT5 FOREX SYNC TEST")
        print("=" * 80)
        print()
        
        # Initialize
        sync = await initialize_mt5_forex_sync()
        
        # Get tradable symbols
        symbols = sync.get_tradable_symbols()
        print(f"\n✅ {len(symbols)} tradable MT5 forex symbols")
        
        print("\nSample symbols:")
        for sym in symbols[:15]:
            meta = sync.get_pair_metadata(sym)
            print(f"  • {sym} - {meta.get('description', 'N/A')}")
        
        if len(symbols) > 15:
            print(f"  ... and {len(symbols) - 15} more!")
        
        print("\n✅ MT5 Forex Sync System Ready!")
        print("\nTo enable auto-updates:")
        print("  asyncio.create_task(start_mt5_auto_update())")
    
    asyncio.run(test())
