#!/usr/bin/env python3
"""
Professional Trading Bot - Main Entry Point
Advanced ML-powered trading system with real-time learning and risk management
"""

import asyncio
import sys
import os
import signal
from pathlib import Path
import logging

# Setup basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Try to load environment variables if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed, using system environment variables")

# Import bot components
# Import bot components with error handling
try:
    from src.bot import TradingBot
except ImportError:
    logger.error("Could not import TradingBot")
    from trading_bot_stub import TradingBot

try:
    from src.data_collector import DataCollector
except ImportError:
    logger.error("Could not import DataCollector")
    from data_collector_stub import DataCollector

try:
    from src.ml_engine import MLEngine
except ImportError:
    logger.error("Could not import MLEngine")
    from ml_engine_stub import MLEngine

try:
    from src.risk_manager import RiskManager
except ImportError:
    logger.error("Could not import RiskManager")
    from risk_manager_stub import RiskManager

try:
    from src.notification_manager import NotificationManager
except ImportError:
    logger.error("Could not import NotificationManager")
    from notification_manager_stub import NotificationManager

try:
    from src.dashboard import Dashboard
except ImportError:
    logger.error("Could not import Dashboard")
    from dashboard_stub import Dashboard

try:
    from src.database import Database
except ImportError:
    logger.error("Could not import Database")
    from database_stub import Database

class TradingBotOrchestrator:
    """Main orchestrator for the trading bot system"""

    def __init__(self):
        self.bot = None
        self.data_collector = None
        self.ml_engine = None
        self.risk_manager = None
        self.notification_manager = None
        self.dashboard = None
        self.database = None
        self.running = False

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Configure logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Use standard logging instead of loguru if not available
        try:
            from loguru import logger as loguru_logger
            loguru_logger.remove()  # Remove default handler
            loguru_logger.add(
                "logs/trading/trading_bot.log",
                rotation="1 day",
                retention="30 days",
                level=os.getenv("LOG_LEVEL", "INFO"),
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            )
            loguru_logger.add(
                sys.stdout,
                level=os.getenv("LOG_LEVEL", "INFO"),
                format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | {message}",
            )
            global logger
            logger = loguru_logger
        except ImportError:
            # Fallback to standard logging
            log_dir = Path("logs/trading")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_dir / "trading_bot.log")
            file_handler.setLevel(logging.INFO)
            
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

    async def initialize(self):
        """Initialize all bot components"""
        try:
            logger.info("🚀 Initializing Professional Trading Bot...")

            # Initialize database
            self.database = Database()
            await self.database.initialize()

            # Initialize notification manager
            self.notification_manager = NotificationManager()
            await self.notification_manager.initialize()

            # Initialize risk manager
            self.risk_manager = RiskManager(self.database)
            await self.risk_manager.initialize()

            # Initialize ML engine
            self.ml_engine = MLEngine(self.database, self.risk_manager)
            await self.ml_engine.initialize()

            # Initialize data collector
            self.data_collector = DataCollector(self.database)
            await self.data_collector.initialize()

            # Initialize trading bot
            self.bot = TradingBot(
                data_collector=self.data_collector,
                ml_engine=self.ml_engine,
                risk_manager=self.risk_manager,
                notification_manager=self.notification_manager,
                database=self.database,
            )
            await self.bot.initialize()

            # Initialize dashboard
            self.dashboard = Dashboard(self.bot, self.database)
            await self.dashboard.initialize()

            logger.info("✅ All components initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            raise

    async def start(self):
        """Start the trading bot system"""
        try:
            logger.info("🎯 Starting trading bot system...")

            # Send startup notification
            await self.notification_manager.send_notification(
                "🚀 Trading Bot Started",
                f"Professional Trading Bot v{os.getenv('VERSION', '1.0.0')} is now running on {os.getenv('BOT_NAME', 'TradingBot')}",
            )

            self.running = True

            # Start all components concurrently
            tasks = [
                asyncio.create_task(self.data_collector.start()),
                asyncio.create_task(self.ml_engine.start()),
                asyncio.create_task(self.bot.start()),
                asyncio.create_task(self.dashboard.start()),
                asyncio.create_task(self.monitor_system()),
            ]

            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
            await self.notification_manager.send_notification(
                "🚨 Bot Error", f"Critical error occurred: {str(e)}"
            )
            raise

    async def stop(self):
        """Gracefully stop the trading bot system"""
        logger.info("🛑 Stopping trading bot system...")
        self.running = False

        # Stop all components
        if self.bot:
            await self.bot.stop()
        if self.data_collector:
            await self.data_collector.stop()
        if self.ml_engine:
            await self.ml_engine.stop()
        if self.dashboard:
            await self.dashboard.stop()

        logger.info("✅ Trading bot system stopped")

    async def monitor_system(self):
        """Monitor system health and performance"""
        while self.running:
            try:
                # Check system health
                health_status = await self.check_system_health()

                if not health_status["healthy"]:
                    logger.warning(f"⚠️ System health issues: {health_status['issues']}")
                    await self.notification_manager.send_notification(
                        "⚠️ System Health Alert",
                        f"Health issues detected: {', '.join(health_status['issues'])}",
                    )

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(60)

    async def check_system_health(self):
        """Check system health status"""
        issues = []

        try:
            # Check database connection
            if not await self.database.is_healthy():
                issues.append("Database connection issues")

            # Check data collector
            if not await self.data_collector.is_healthy():
                issues.append("Data collector not receiving data")

            # Check ML engine
            if not await self.ml_engine.is_healthy():
                issues.append("ML engine processing issues")

            # Check risk manager
            if not await self.risk_manager.is_healthy():
                issues.append("Risk manager issues")

        except Exception as e:
            issues.append(f"Health check error: {e}")

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "timestamp": asyncio.get_event_loop().time(),
        }

async def main():
    """Main entry point"""
    orchestrator = TradingBotOrchestrator()

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(orchestrator.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize and start the bot
        await orchestrator.initialize()
        await orchestrator.start()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await orchestrator.stop()

if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)

    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
