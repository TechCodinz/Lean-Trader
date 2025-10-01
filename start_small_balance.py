#!/usr/bin/env python3
"""
Small Balance Startup Script - Optimized for $48 → $1000
This ensures all settings are configured for maximum growth from small balance
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)
logger = logging.getLogger('SmallBalanceStart')

def configure_for_small_balance():
    """Configure environment for small balance trading"""
    
    # Set optimal environment variables
    small_balance_settings = {
        # Account
        'INITIAL_BALANCE': '48',
        'TARGET_BALANCE': '1000',
        
        # Position Sizing - AGGRESSIVE
        'RISK_PER_TRADE': '0.15',      # 15% per trade
        'MAX_POSITIONS': '5',           # 5 concurrent positions
        'MIN_POSITION_SIZE': '5',       # $5 minimum
        'MAX_POSITION_SIZE': '15',      # $15 maximum initially
        'COMPOUND_PROFITS': 'true',     # Reinvest everything
        
        # Risk Management - OPTIMIZED
        'STOP_LOSS_PCT': '0.04',        # 4% stop loss (wider)
        'TAKE_PROFIT_PCT': '0.015',     # 1.5% take profit (quick)
        'TRAILING_STOP': 'true',
        'TRAILING_DISTANCE': '0.02',    # 2% trailing
        'MAX_DAILY_LOSS': '0.20',       # 20% daily loss limit
        
        # Arbitrage - AGGRESSIVE
        'MIN_ARBITRAGE_PROFIT_PCT': '0.0008',  # 0.08% minimum
        'ARBITRAGE_AGGRESSIVE': 'true',
        'ARBITRAGE_FREQUENCY': 'maximum',
        'EXECUTE_IMMEDIATELY': 'true',
        
        # Features - ALL ENABLED
        'ENABLE_SCALPING': 'true',
        'ENABLE_MICRO_TRADES': 'true',
        'ENABLE_LEVERAGE': 'true',
        'MAX_LEVERAGE': '3',            # 3x leverage max
        'USE_ALL_OPPORTUNITIES': 'true',
        
        # Performance
        'SCAN_INTERVAL': '1',           # Scan every second
        'EXECUTION_SPEED': 'instant',
        'PARALLEL_TRADES': 'true',
        
        # Targets
        'DAILY_TARGET_PCT': '5',        # 5% daily target
        'WEEKLY_TARGET_PCT': '40',      # 40% weekly
        'MONTHLY_TARGET_PCT': '200',    # 200% monthly (3x)
    }
    
    # Apply settings
    for key, value in small_balance_settings.items():
        os.environ[key] = value
        
    logger.info("✅ Small balance configuration applied")
    logger.info(f"   Starting: $48")
    logger.info(f"   Target: $1000")
    logger.info(f"   Strategy: Ultra-aggressive compound growth")
    logger.info(f"   Daily target: 5% ($2.40 initially)")
    logger.info(f"   Risk per trade: 15% ($7.20)")
    logger.info(f"   Timeline: 3-4 months")

def print_growth_plan():
    """Display the growth plan"""
    
    print("\n" + "="*60)
    print("💎 GROWTH PLAN: $48 → $1000")
    print("="*60)
    print("""
WEEK 1-2: Foundation ($48 → $100)
• Focus: Micro arbitrage (0.1%+ profits)
• Trade size: $5-10
• Frequency: 20-30 trades/day
• Daily target: 5-7%

WEEK 3-4: Scaling ($100 → $200)
• Focus: Arbitrage + scalping
• Trade size: $15-25
• Frequency: 30-40 trades/day
• Daily target: 5%

MONTH 2: Acceleration ($200 → $500)
• Focus: All strategies enabled
• Trade size: $30-50
• Frequency: 25-35 trades/day
• Daily target: 4%

MONTH 3-4: Full Power ($500 → $1000+)
• Focus: Larger positions
• Trade size: $50-100
• Frequency: 20-30 trades/day
• Daily target: 3%

KEY SUCCESS FACTORS:
✅ Never withdraw - compound everything
✅ Trade 24/7 - never miss opportunities
✅ Use all 6 exchanges
✅ Take small profits (0.1%+)
✅ Quick trades (minutes, not hours)
✅ Monitor closely first week
    """)
    print("="*60)

async def main():
    """Main startup for small balance"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         💎 ULTRA TRADING BOT - SMALL BALANCE MODE 💎                ║
║                                                                      ║
║         Optimized for: $48 → $1000 in 3-4 months                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Configure environment
    configure_for_small_balance()
    
    # Show growth plan
    print_growth_plan()
    
    # Import and start the launcher
    logger.info("\n🚀 Starting Ultra Trading System...")
    logger.info("   Mode: AGGRESSIVE GROWTH")
    logger.info("   Balance: $48")
    logger.info("   Target: $1000")
    
    try:
        # Import the launcher
        from ultra_launcher import UltraLauncher
        
        # Create launcher with optimized config
        launcher = UltraLauncher()
        
        # Override with small balance settings
        launcher.config['risk_per_trade'] = 0.15
        launcher.config['max_positions'] = 5
        launcher.config['min_profit'] = 0.0008
        launcher.config['aggressive_mode'] = True
        launcher.config['compound_profits'] = True
        
        # Start in live mode
        await launcher.start('live')
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.info("\nFallback: Run directly with:")
        logger.info("  python3 ultra_launcher.py --mode live")

if __name__ == "__main__":
    asyncio.run(main())