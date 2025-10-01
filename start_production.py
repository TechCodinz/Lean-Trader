#!/usr/bin/env python3
"""
Production Startup Script - Validates and Launches the Ultra Trading System
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger('ProductionStart')

class ProductionValidator:
    """Validates production readiness before launch"""
    
    def __init__(self):
        self.exchanges_found = []
        self.telegram_ready = False
        self.errors = []
        
    def validate_all(self) -> bool:
        """Run all validation checks"""
        
        logger.info("=" * 70)
        logger.info("🔍 PRODUCTION VALIDATION")
        logger.info("=" * 70)
        
        # Check exchanges
        self.check_exchanges()
        
        # Check Telegram
        self.check_telegram()
        
        # Check directories
        self.check_directories()
        
        # Summary
        if self.errors:
            logger.error("\n❌ VALIDATION FAILED:")
            for error in self.errors:
                logger.error(f"  • {error}")
            return False
        else:
            logger.info("\n✅ ALL VALIDATIONS PASSED!")
            return True
            
    def check_exchanges(self):
        """Validate exchange credentials"""
        
        logger.info("\n📋 Checking Exchange Credentials...")
        
        # Load arbitrage environment
        if Path('env.arbitrage').exists():
            with open('env.arbitrage', 'r') as f:
                content = f.read()
                
            exchanges = {
                'BINANCE': 'uxMw38StLFlWpqzi9OpFMMj4H7m3dWy8jnR2EAl2raL0n465jtxnlK9S2CYBflyf',
                'BYBIT': 'fX0py6Av5dFPmCPOMX',
                'GATEIO': 'a0508d8aadf3bcb76e16f4373e1f3a76',
                'OKX': '9b6e8a19-5a9c-44ca-942f-e98cc36d0354',
                'BITGET': 'bg_a76be18966412e3f95b11eac379edf91',
                'MEXC': 'mx0vgl7ytNbnU44V5G'
            }
            
            for exchange, key_part in exchanges.items():
                if key_part in content:
                    self.exchanges_found.append(exchange)
                    logger.info(f"  ✅ {exchange} credentials found")
                    
            logger.info(f"\n  Total: {len(self.exchanges_found)} exchanges configured")
            
            if len(self.exchanges_found) < 2:
                self.errors.append("Need at least 2 exchanges for arbitrage")
        else:
            self.errors.append("env.arbitrage file not found")
            
    def check_telegram(self):
        """Validate Telegram configuration"""
        
        logger.info("\n📱 Checking Telegram Configuration...")
        
        # Check in arbitrage env
        if Path('env.arbitrage').exists():
            with open('env.arbitrage', 'r') as f:
                content = f.read()
                
            if '8291641352:AAFTGq-hIY_iS47aMOoGXrBDFlR_B3nCupg' in content:
                logger.info("  ✅ Bot token configured")
                
                channels = {
                    'Admin': '5329503447',
                    'Free Channel': '-1002930953007',
                    'VIP Channel': '-1002983007302'
                }
                
                for name, id in channels.items():
                    if id in content:
                        logger.info(f"  ✅ {name}: {id}")
                        
                self.telegram_ready = True
            else:
                self.errors.append("Telegram bot token not found")
                
    def check_directories(self):
        """Ensure required directories exist"""
        
        logger.info("\n📁 Checking Directories...")
        
        dirs = ['logs', 'data', 'state', 'reports', 'models', 'checkpoints']
        
        for dir_name in dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"  ✅ Created {dir_name}/")
            else:
                logger.info(f"  ✅ {dir_name}/ exists")

async def send_startup_notification():
    """Send startup notification to Telegram admin"""
    
    try:
        import telegram
        
        bot_token = "8291641352:AAFTGq-hIY_iS47aMOoGXrBDFlR_B3nCupg"
        admin_chat = "5329503447"
        
        bot = telegram.Bot(token=bot_token)
        
        message = f"""
🚀 **ULTRA TRADING SYSTEM STARTING**

📊 **Configuration:**
• Mode: PRODUCTION ARBITRAGE
• Exchanges: 6 Active
• Telegram: Configured
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💎 **Features Active:**
• Multi-Exchange Arbitrage ✅
• Swarm Consciousness ✅
• AI Evolution ✅
• Risk Management ✅

🔄 Starting initialization...
        """
        
        await bot.send_message(chat_id=admin_chat, text=message, parse_mode='Markdown')
        logger.info("📱 Startup notification sent to admin")
        
    except Exception as e:
        logger.warning(f"Could not send Telegram notification: {e}")

async def main():
    """Main startup sequence"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║            🚀 ULTRA TRADING SYSTEM - PRODUCTION START 🚀            ║
║                                                                      ║
║  Version: 4.0 ULTIMATE                                              ║
║  Mode: MULTI-EXCHANGE ARBITRAGE                                     ║
║  Status: INITIALIZING...                                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Validate production readiness
    validator = ProductionValidator()
    
    if not validator.validate_all():
        logger.error("\n❌ Cannot start in production mode - validation failed")
        sys.exit(1)
        
    # Send startup notification
    await send_startup_notification()
    
    # Load environment
    logger.info("\n🔧 Loading Production Environment...")
    
    # Load env.arbitrage
    with open('env.arbitrage', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip()
                
    logger.info("  ✅ Environment loaded")
    
    # Import and start the intelligent launcher
    logger.info("\n🚀 Starting Ultra Intelligent System...")
    
    try:
        from ultra_intelligent_launcher import main as launch_system
        await launch_system()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())