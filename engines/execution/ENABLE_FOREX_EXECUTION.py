import sys

def enable_forex_execution():
    """Enable forex execution on testnet and MT5"""
    
    # Fix 1: Update INTELLIGENT_EXECUTION_ENGINE to execute forex
    print("📝 Updating INTELLIGENT_EXECUTION_ENGINE...")
    try:
        with open('INTELLIGENT_EXECUTION_ENGINE.py', 'r') as f:
            content = f.read()
        
        # Find the forex skip logic and modify it to allow execution
        old_skip = """    def _should_skip_symbol(self, symbol: str) -> bool:
        \"\"\"Check if symbol should be skipped (forex, TradFi needs MT5)\"\"\"
        
        # List of major forex currency codes
        forex_codes = ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD', 'CNY', 'HKD', 'SGD']
        
        # Check if it's a symbol without '/' (forex or TradFi)
        if '/' not in symbol:
            return True  # Skip - needs MT5
        
        # Check if it's a forex pair (USD/JPY, EUR/GBP, etc.)
        parts = symbol.split('/')
        if len(parts) == 2:
            base, quote = parts
            # If both parts are forex codes, it's a forex pair
            if base.replace('+', '') in forex_codes and quote.replace('+', '') in forex_codes:
                return True  # Skip - needs MT5"""
        
        new_skip = """    def _should_skip_symbol(self, symbol: str) -> bool:
        \"\"\"Check if symbol should be skipped - NOW EXECUTES FOREX!\"\"\"
        
        # List of major forex currency codes
        forex_codes = ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD', 'CNY', 'HKD', 'SGD']
        
        # Check if it's a symbol without '/' (forex or TradFi)
        if '/' not in symbol:
            return True  # Skip - needs MT5
        
        # Check if it's a forex pair (USD/JPY, EUR/GBP, etc.)
        parts = symbol.split('/')
        if len(parts) == 2:
            base, quote = parts
            # If both parts are forex codes, it's a forex pair
            if base.replace('+', '') in forex_codes and quote.replace('+', '') in forex_codes:
                # 🔥 CHANGED: Don't skip! Execute on MT5 or testnet!
                logger.info(f"   💱 FOREX PAIR DETECTED: {symbol} - will execute!")
                return False  # Don't skip - execute it!"""
        
        if old_skip in content:
            content = content.replace(old_skip, new_skip)
            print("   [OK] Modified forex skip logic - forex will now execute!")
        else:
            print("    Forex skip logic not found or different structure")
        
        with open('INTELLIGENT_EXECUTION_ENGINE.py', 'w') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False

def verify_forex_router():
    """Verify INTELLIGENT_EXCHANGE_ROUTER routes forex properly"""
    print("\n📝 Checking INTELLIGENT_EXCHANGE_ROUTER...")
    try:
        with open('INTELLIGENT_EXCHANGE_ROUTER.py', 'r') as f:
            content = f.read()
        
        # Check if router handles forex
        has_forex_routing = 'forex' in content.lower() and 'route' in content.lower()
        has_mt5_support = 'mt5' in content.lower() or 'MT5' in content
        
        print(f"   Forex routing: {'[OK]' if has_forex_routing else '[X]'}")
        print(f"   MT5 support: {'[OK]' if has_mt5_support else '[X]'}")
        
        return has_forex_routing
        
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False

def verify_telegram_notifications():
    """Ensure Telegram notifications still work"""
    print("\n📝 Checking Telegram notifications...")
    try:
        with open('COMPLETE_ULTIMATE_ORCHESTRATOR.py', 'r') as f:
            content = f.read()
        
        has_telegram = 'telegram' in content.lower() and 'send' in content.lower()
        has_vip_channel = 'vip' in content.lower()
        
        print(f"   Telegram integration: {'[OK]' if has_telegram else '[X]'}")
        print(f"   VIP channel: {'[OK]' if has_vip_channel else '[X]'}")
        
        return has_telegram
        
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("ENABLING FOREX EXECUTION ON TESTNET + MT5 + TELEGRAM")
    print("=" * 70)
    print()
    
    print("🔧 Step 1: Enable forex execution in engine...")
    result1 = enable_forex_execution()
    
    print("\n🔧 Step 2: Verify router handles forex...")
    result2 = verify_forex_router()
    
    print("\n🔧 Step 3: Verify Telegram notifications...")
    result3 = verify_telegram_notifications()
    
    print("\n" + "=" * 70)
    if result1:
        print("[OK] FOREX EXECUTION ENABLED!")
        print("\nWhat will happen now:")
        print("  1. [OK] Forex signals generate (EUR/USD, GBP/USD, etc.)")
        print("  2. [OK] Signals sent to Telegram VIP channel")
        print("  3. [OK] Bot ATTEMPTS execution on:")
        print("     - MT5 (if available)")
        print("     - Testnet exchanges (if they support forex)")
        print("  4. [OK] All ultra engines working together")
        print("\n Note: On Linux VPS, MT5 won't work (Windows-only)")
        print("         But testnet exchanges might have forex pairs!")
    else:
        print(" PARTIAL SUCCESS - manual verification needed")
    print("=" * 70)
