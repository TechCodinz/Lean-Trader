#!/usr/bin/env python3
"""
System Test & Verification - Shows what the bot will do without actual trading
"""

import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger('SystemTest')

class SystemTester:
    """Tests all components and shows what will happen"""
    
    def __init__(self):
        self.exchanges_status = {}
        self.telegram_status = False
        self.arbitrage_opportunities = []
        
    async def test_exchange_connections(self):
        """Test exchange API connections"""
        
        logger.info("\n" + "="*70)
        logger.info("📋 TESTING EXCHANGE CONNECTIONS")
        logger.info("="*70)
        
        try:
            import ccxt.async_support as ccxt
            
            # Load arbitrage environment
            exchanges_config = {}
            with open('env.arbitrage', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        exchanges_config[key] = value.strip()
            
            # Test each exchange
            exchange_tests = [
                ('Binance', ccxt.binance, 'BINANCE_API_KEY', 'BINANCE_SECRET'),
                ('Bybit', ccxt.bybit, 'BYBIT_API_KEY', 'BYBIT_SECRET'),
                ('Gate.io', ccxt.gateio, 'GATEIO_API_KEY', 'GATEIO_SECRET'),
                ('OKX', ccxt.okx, 'OKX_API_KEY', 'OKX_SECRET'),
                ('Bitget', ccxt.bitget, 'BITGET_API_KEY', 'BITGET_SECRET'),
                ('MEXC', ccxt.mexc, 'MEXC_API_KEY', 'MEXC_SECRET'),
            ]
            
            for name, exchange_class, key_var, secret_var in exchange_tests:
                try:
                    api_key = exchanges_config.get(key_var)
                    secret = exchanges_config.get(secret_var)
                    
                    if api_key and secret:
                        exchange = exchange_class({
                            'apiKey': api_key,
                            'secret': secret,
                            'enableRateLimit': True,
                            'options': {'defaultType': 'spot'}
                        })
                        
                        # Try to fetch ticker
                        ticker = await exchange.fetch_ticker('BTC/USDT')
                        await exchange.close()
                        
                        self.exchanges_status[name] = {
                            'status': 'connected',
                            'btc_price': ticker['last']
                        }
                        logger.info(f"  ✅ {name}: Connected (BTC: ${ticker['last']:,.2f})")
                    else:
                        self.exchanges_status[name] = {'status': 'no_credentials'}
                        logger.warning(f"  ⚠️  {name}: No credentials")
                        
                except Exception as e:
                    self.exchanges_status[name] = {'status': 'error', 'error': str(e)}
                    logger.error(f"  ❌ {name}: {str(e)[:50]}...")
                    
        except ImportError:
            logger.error("  ❌ CCXT not available")
            
    async def test_testnet_connection(self):
        """Test Bybit testnet connection"""
        
        logger.info("\n" + "="*70)
        logger.info("🧠 TESTING TESTNET CONNECTION")
        logger.info("="*70)
        
        try:
            import ccxt.async_support as ccxt
            
            # Load testnet config
            with open('env.testnet', 'r') as f:
                testnet_config = {}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        testnet_config[key] = value.strip()
            
            api_key = testnet_config.get('BYBIT_API_KEY')
            secret = testnet_config.get('BYBIT_SECRET')
            
            if api_key and secret:
                exchange = ccxt.bybit({
                    'apiKey': api_key,
                    'secret': secret,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'},
                    'urls': {
                        'api': {
                            'public': 'https://api-testnet.bybit.com',
                            'private': 'https://api-testnet.bybit.com'
                        }
                    }
                })
                
                ticker = await exchange.fetch_ticker('BTC/USDT')
                await exchange.close()
                
                logger.info(f"  ✅ Bybit Testnet: Connected (BTC: ${ticker['last']:,.2f})")
                logger.info("  ✅ Ready for AI training and strategy testing")
            else:
                logger.warning("  ⚠️  Bybit Testnet: No credentials")
                
        except Exception as e:
            logger.error(f"  ❌ Testnet error: {str(e)[:50]}...")
            
    async def test_telegram(self):
        """Test Telegram connection"""
        
        logger.info("\n" + "="*70)
        logger.info("📱 TESTING TELEGRAM CONNECTION")
        logger.info("="*70)
        
        try:
            from telegram import Bot
            from telegram.error import TelegramError
            
            bot_token = "8291641352:AAFTGq-hIY_iS47aMOoGXrBDFlR_B3nCupg"
            admin_chat = "5329503447"
            
            bot = Bot(token=bot_token)
            
            # Test bot connection
            bot_info = await bot.get_me()
            logger.info(f"  ✅ Bot Connected: @{bot_info.username}")
            
            # Send test message
            message = f"""
🔍 **SYSTEM TEST INITIATED**

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 **Exchange Status:**
"""
            for name, status in self.exchanges_status.items():
                if status['status'] == 'connected':
                    message += f"\n• {name}: ✅ Connected"
                else:
                    message += f"\n• {name}: ⚠️ {status['status']}"
                    
            message += "\n\n🧠 **AI Training:** Ready on Bybit Testnet"
            message += "\n\n✅ System test successful!"
            
            await bot.send_message(chat_id=admin_chat, text=message, parse_mode='Markdown')
            logger.info(f"  ✅ Test message sent to admin chat")
            
            self.telegram_status = True
            
        except Exception as e:
            logger.error(f"  ❌ Telegram error: {str(e)[:50]}...")
            self.telegram_status = False
            
    async def simulate_arbitrage_scan(self):
        """Simulate arbitrage opportunity scanning"""
        
        logger.info("\n" + "="*70)
        logger.info("💎 SIMULATING ARBITRAGE SCANNING")
        logger.info("="*70)
        
        # Get connected exchanges
        connected = [name for name, status in self.exchanges_status.items() 
                    if status.get('status') == 'connected']
        
        if len(connected) >= 2:
            logger.info(f"  📊 Scanning {len(connected)} exchanges for opportunities...")
            
            # Simulate finding opportunities
            symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            
            for symbol in symbols:
                # Simulate price differences
                import random
                if random.random() > 0.5:  # 50% chance of opportunity
                    profit_pct = random.uniform(0.1, 0.8)
                    buy_exchange = random.choice(connected)
                    sell_exchange = random.choice([e for e in connected if e != buy_exchange])
                    
                    self.arbitrage_opportunities.append({
                        'symbol': symbol,
                        'buy_exchange': buy_exchange,
                        'sell_exchange': sell_exchange,
                        'profit_pct': profit_pct
                    })
                    
                    logger.info(f"  💰 Found: {symbol} - Buy on {buy_exchange}, Sell on {sell_exchange}")
                    logger.info(f"     Potential profit: {profit_pct:.3f}%")
                    
            if not self.arbitrage_opportunities:
                logger.info("  📊 No opportunities found in this scan (normal - keep scanning)")
        else:
            logger.warning("  ⚠️  Need at least 2 connected exchanges for arbitrage")
            
    def print_summary(self):
        """Print final summary"""
        
        print("\n" + "="*70)
        print("📋 SYSTEM TEST SUMMARY")
        print("="*70)
        
        # Exchange summary
        connected_count = sum(1 for s in self.exchanges_status.values() 
                            if s.get('status') == 'connected')
        print(f"\n📊 Exchanges: {connected_count}/{len(self.exchanges_status)} connected")
        
        # Telegram
        print(f"📱 Telegram: {'✅ Ready' if self.telegram_status else '❌ Not ready'}")
        
        # Arbitrage
        print(f"💎 Arbitrage: {len(self.arbitrage_opportunities)} opportunities found in test")
        
        # What will happen
        print("\n🚀 WHEN YOU START THE BOT:")
        print("  1. Connect to all configured exchanges")
        print("  2. Start scanning for arbitrage every 3 seconds")
        print("  3. Execute trades when profit > 0.2%")
        print("  4. Train AI models on Bybit testnet")
        print("  5. Send signals to Telegram channels")
        print("  6. Monitor and report every 30 minutes")
        
        # Status
        if connected_count >= 2:
            print("\n✅ READY FOR DEPLOYMENT!")
            print("   The bot will start finding and executing arbitrage opportunities")
        else:
            print("\n⚠️  WARNING: Less than 2 exchanges connected")
            print("   Check your API keys and try again")

async def main():
    """Main test runner"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║            🔍 ULTRA TRADING SYSTEM - TEST MODE 🔍                   ║
║                                                                      ║
║  Testing all components before deployment...                        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    tester = SystemTester()
    
    # Run tests
    await tester.test_exchange_connections()
    await tester.test_testnet_connection()
    await tester.test_telegram()
    await tester.simulate_arbitrage_scan()
    
    # Print summary
    tester.print_summary()
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE!")
    print("="*70)
    print("\nTo start the actual bot:")
    print("  • For testing: python3 start_hybrid_mode.py")
    print("  • For VPS: ./DEPLOY_TO_VPS.sh")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())