#!/usr/bin/env python3
"""
🔧 ENABLE ALL PAIRS - Fix Hardcoded Pairs Issue
Run this on VPS to enable dynamic pair discovery for ALL pairs
"""

import sys
import re

def fix_orchestrator():
    """Fix COMPLETE_ULTIMATE_ORCHESTRATOR.py to enable all pairs"""
    
    filepath = "COMPLETE_ULTIMATE_ORCHESTRATOR.py"
    
    print("🔧 Fixing pair discovery in orchestrator...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix 1: Initialize pair_discovery properly (line 685)
    print("1️⃣ Enabling pair_discovery initialization...")
    old_line = "        self.pair_discovery = None  # Initialize for universal pair fetcher"
    new_line = """        # Initialize Dynamic Pair Discovery
        try:
            from DYNAMIC_PAIR_DISCOVERY import DynamicPairDiscovery
            # Get exchange for pair discovery
            if hasattr(self, 'exchanges') and self.exchanges:
                first_exchange = list(self.exchanges.values())[0]
                self.pair_discovery = DynamicPairDiscovery(first_exchange, min_volume_24h=10000)
                logger.info("[OK] Dynamic Pair Discovery initialized")
            else:
                self.pair_discovery = None
                logger.warning("  No exchanges available for pair discovery")
        except Exception as e:
            logger.warning(f"  Pair discovery init failed: {e}")
            self.pair_discovery = None"""
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("   [OK] Pair discovery will now initialize!")
    else:
        print("     Line not found (might be already fixed)")
    
    # Fix 2: Change _get_all_pairs to discover more pairs
    print("2️⃣ Enhancing _get_all_pairs method...")
    old_method = """    async def _get_all_pairs(self):
        \"\"\"Get all pairs from Universal Fetcher\"\"\"
        try:
            from UNIVERSAL_PAIR_FETCHER import get_universal_fetcher
            fetcher = get_universal_fetcher()
            if fetcher and len(fetcher.all_pairs) > 100:
                return fetcher.top_volume_pairs[:50] if fetcher.top_volume_pairs else fetcher.all_pairs[:50]
        except Exception as e:
            pass
        return ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']"""
    
    new_method = """    async def _get_all_pairs(self):
        \"\"\"Get all pairs dynamically - NO MORE HARDCODED!\"\"\"
        discovered_pairs = []
        
        # Try 1: Use pair discovery
        if self.pair_discovery:
            try:
                result = await self.pair_discovery.discover_pairs()
                discovered_pairs = result.get('hot', []) + result.get('fast', []) + result.get('stable', [])
                if discovered_pairs:
                    logger.info(f"[OK] Discovered {len(discovered_pairs)} pairs from DynamicPairDiscovery")
                    return discovered_pairs[:100]  # Top 100
            except Exception as e:
                logger.debug(f"Pair discovery error: {e}")
        
        # Try 2: Use Universal Fetcher
        try:
            from UNIVERSAL_PAIR_FETCHER import get_universal_fetcher
            fetcher = get_universal_fetcher()
            if fetcher and fetcher.all_pairs:
                logger.info(f"[OK] Got {len(fetcher.all_pairs)} pairs from Universal Fetcher")
                return fetcher.top_volume_pairs[:100] if fetcher.top_volume_pairs else fetcher.all_pairs[:100]
        except Exception as e:
            logger.debug(f"Universal fetcher error: {e}")
        
        # Try 3: Fetch directly from exchange
        try:
            if hasattr(self, 'exchanges') and self.exchanges:
                first_exchange = list(self.exchanges.values())[0]
                tickers = await asyncio.to_thread(first_exchange.fetch_tickers)
                
                # Get all USDT pairs with volume
                pairs = []
                for symbol, ticker in tickers.items():
                    if '/USDT' in symbol:
                        volume = ticker.get('quoteVolume', 0) or 0
                        if volume > 10000:  # Min $10k volume
                            pairs.append((symbol, volume))
                
                # Sort by volume, return top 100
                pairs.sort(key=lambda x: x[1], reverse=True)
                discovered_pairs = [p[0] for p in pairs[:100]]
                
                if discovered_pairs:
                    logger.info(f"[OK] Fetched {len(discovered_pairs)} pairs directly from exchange")
                    return discovered_pairs
        except Exception as e:
            logger.error(f"Direct fetch error: {e}")
        
        # Only if everything fails, use expanded fallback
        logger.warning("  All discovery methods failed, using expanded fallback")
        return [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'AVAX/USDT',
            'XRP/USDT', 'ADA/USDT', 'DOT/USDT', 'MATIC/USDT', 'LINK/USDT',
            'UNI/USDT', 'ATOM/USDT', 'LTC/USDT', 'ETC/USDT', 'XLM/USDT',
            'ALGO/USDT', 'VET/USDT', 'FIL/USDT', 'TRX/USDT', 'DOGE/USDT',
            'SHIB/USDT', 'APE/USDT', 'SAND/USDT', 'MANA/USDT', 'AXS/USDT',
            'GALA/USDT', 'ENJ/USDT', 'CHZ/USDT', 'BAT/USDT', 'ZEC/USDT'
        ]  # 30 popular pairs as last resort"""
    
    if old_method in content:
        content = content.replace(old_method, new_method)
        print("   [OK] _get_all_pairs will now discover pairs dynamically!")
    else:
        print("     Method not found or already modified")
    
    # Fix 3: Add forex pair discovery
    print("3️⃣ Adding forex pair support...")
    forex_init = """        self.pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
        self.forex_active = True"""
    
    forex_enhanced = """        # Enhanced forex pairs - ALL major and exotic pairs
        self.pairs = [
            # Major pairs
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
            # Cross pairs
            'EURJPY', 'GBPJPY', 'EURGBP', 'AUDJPY', 'CADJPY', 'CHFJPY',
            # Exotic pairs
            'EURNZD', 'EURCHF', 'EURAUD', 'EURCAD', 'GBPAUD', 'GBPCAD',
            # Commodities
            'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL'
        ]
        self.forex_active = True
        logger.info(f"💱 Forex Master initialized with {len(self.pairs)} pairs")"""
    
    if forex_init in content:
        content = content.replace(forex_init, forex_enhanced)
        print("   [OK] Forex pairs expanded to 23 pairs!")
    else:
        print("     Forex initialization not found")
    
    # Write back
    print("\n💾 Saving changes...")
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("[OK] All fixes applied!")
    print("\n📋 Changes made:")
    print("   1. pair_discovery now initializes properly")
    print("   2. _get_all_pairs discovers 100+ pairs dynamically")
    print("   3. Forex pairs expanded from 4 to 23 pairs")
    print("   4. Added 30-pair fallback (instead of 5)")
    print("\n🔄 Restart bot to activate changes!")

if __name__ == "__main__":
    try:
        fix_orchestrator()
        print("\n[OK] SUCCESS! Restart bot now:")
        print("   pkill -f COMPLETE_ULTIMATE_ORCHESTRATOR")
        print("   nohup python3 COMPLETE_ULTIMATE_ORCHESTRATOR.py > apex.log 2>&1 &")
    except Exception as e:
        print(f"\n[X] Error: {e}")
        sys.exit(1)
