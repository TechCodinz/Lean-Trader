#!/usr/bin/env python3
"""
Ultra Trading Bot with Multi-Exchange Arbitrage and Swarm Consciousness
Automatically selects the best available environment and credentials
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
import signal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ultra_arbitrage.log')
    ]
)
logger = logging.getLogger('UltraArbitrage')

class EnvironmentAutoSelector:
    """
    Automatically selects the best environment based on available credentials
    """
    
    @staticmethod
    def detect_available_exchanges():
        """Detect which exchanges have valid credentials"""
        available = []
        
        # Check environment variables and files
        env_files = ['env.live', 'env.paper', 'env.testnet', '.env']
        
        for env_file in env_files:
            if Path(env_file).exists():
                # Load and check
                with open(env_file, 'r') as f:
                    content = f.read()
                    
                    # Check for real API keys (not placeholders)
                    exchanges = ['BINANCE', 'BYBIT', 'GATEIO', 'COINBASE', 'KRAKEN']
                    
                    for exchange in exchanges:
                        if f'{exchange}_API_KEY=' in content:
                            # Extract the key
                            for line in content.split('\n'):
                                if f'{exchange}_API_KEY=' in line:
                                    key = line.split('=')[1].strip()
                                    if key and not key.startswith('your_') and not key.startswith('${'):
                                        available.append((exchange.lower(), env_file))
                                        
        # Also check OS environment
        for exchange in ['BINANCE', 'BYBIT', 'GATEIO', 'COINBASE', 'KRAKEN']:
            key = os.environ.get(f'{exchange}_API_KEY')
            if key and not key.startswith('your_'):
                available.append((exchange.lower(), 'environment'))
                
        return available
    
    @staticmethod
    def select_best_mode():
        """Select the best trading mode based on available credentials"""
        
        available = EnvironmentAutoSelector.detect_available_exchanges()
        
        if not available:
            logger.warning("No valid API credentials found - using PAPER TRADING mode")
            return 'paper', []
            
        # Group by source
        sources = {}
        for exchange, source in available:
            if source not in sources:
                sources[source] = []
            sources[source].append(exchange)
            
        # Prefer live > testnet > paper
        if 'env.live' in sources and len(sources['env.live']) >= 2:
            logger.info(f"Using LIVE environment with exchanges: {sources['env.live']}")
            return 'live', sources['env.live']
        elif 'environment' in sources and len(sources['environment']) >= 2:
            logger.info(f"Using environment variables with exchanges: {sources['environment']}")
            return 'live', sources['environment']
        elif 'env.testnet' in sources:
            logger.info(f"Using TESTNET environment with exchanges: {sources['env.testnet']}")
            return 'testnet', sources['env.testnet']
        else:
            logger.info("Using PAPER TRADING mode (safest option)")
            return 'paper', []

class UltraSystemOrchestrator:
    """
    Orchestrates all components of the Ultra Trading System
    """
    
    def __init__(self):
        self.mode = None
        self.exchanges = []
        self.components = {}
        self.running = False
        
    async def initialize(self):
        """Initialize all system components"""
        
        logger.info("=" * 70)
        logger.info("🚀 ULTRA TRADING SYSTEM - INTELLIGENT INITIALIZATION")
        logger.info("=" * 70)
        
        # Auto-select best environment
        self.mode, self.exchanges = EnvironmentAutoSelector.select_best_mode()
        
        logger.info(f"\n📊 System Configuration:")
        logger.info(f"  • Mode: {self.mode.upper()}")
        logger.info(f"  • Available Exchanges: {self.exchanges if self.exchanges else 'Simulated'}")
        
        # Load appropriate environment file
        if self.mode == 'live' and Path('env.live').exists():
            self.load_env_file('env.live')
        elif self.mode == 'testnet' and Path('env.testnet').exists():
            self.load_env_file('env.testnet')
        elif Path('.env').exists():
            self.load_env_file('.env')
            
        # Initialize components based on available features
        await self.initialize_components()
        
        logger.info("\n✅ System initialization complete!")
        
    def load_env_file(self, filepath: str):
        """Load environment variables from file"""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Only set if not already in environment
                        if not os.environ.get(key):
                            os.environ[key] = value.strip()
                            
            logger.info(f"Loaded environment from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")
            
    async def initialize_components(self):
        """Initialize all trading components"""
        
        # Check what features are enabled
        features = {
            'arbitrage': os.environ.get('ENABLE_ARBITRAGE', 'true').lower() == 'true',
            'swarm': os.environ.get('SWARM_ENABLED', 'true').lower() == 'true',
            'god_mode': os.environ.get('GOD_MODE_ENABLED', 'true').lower() == 'true',
            'moon_spotter': os.environ.get('MOON_SPOTTER_ENABLED', 'true').lower() == 'true',
            'evolution': os.environ.get('EVOLUTION_ENABLED', 'true').lower() == 'true'
        }
        
        logger.info("\n🔧 Initializing components:")
        
        # Initialize based on available exchanges
        if len(self.exchanges) >= 2 and features['arbitrage']:
            logger.info("  ✅ Multi-Exchange Arbitrage: ENABLED")
            await self.init_arbitrage_system()
        else:
            logger.info("  ⚠️ Multi-Exchange Arbitrage: DISABLED (need 2+ exchanges)")
            
        if features['swarm']:
            logger.info("  ✅ Swarm Consciousness: ENABLED")
            await self.init_swarm_consciousness()
        else:
            logger.info("  ⚠️ Swarm Consciousness: DISABLED")
            
        # Initialize standard trading pipeline
        await self.init_trading_pipeline()
        
    async def init_arbitrage_system(self):
        """Initialize arbitrage system"""
        try:
            from multi_exchange_arbitrage_system import UltraArbitrageSystem
            
            self.components['arbitrage'] = UltraArbitrageSystem()
            await self.components['arbitrage'].initialize()
            
            logger.info("    • Arbitrage engine initialized")
            logger.info(f"    • Monitoring {len(self.exchanges)} exchanges")
            
        except Exception as e:
            logger.error(f"Failed to initialize arbitrage: {e}")
            
    async def init_swarm_consciousness(self):
        """Initialize swarm consciousness"""
        try:
            # Import if available
            if Path('ultra_swarm_consciousness.py').exists():
                from ultra_swarm_consciousness import SwarmConsciousness
                
                self.components['swarm'] = SwarmConsciousness()
                logger.info("    • Swarm consciousness activated")
                
        except Exception as e:
            logger.error(f"Failed to initialize swarm: {e}")
            
    async def init_trading_pipeline(self):
        """Initialize main trading pipeline"""
        try:
            from start_ultra_evolution import UltraEvolutionBot
            
            self.components['main_bot'] = UltraEvolutionBot()
            await self.components['main_bot'].initialize()
            
            logger.info("    • Main trading pipeline initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize main pipeline: {e}")
            
    async def run(self):
        """Run all components"""
        
        self.running = True
        tasks = []
        
        logger.info("\n" + "=" * 70)
        logger.info("🚀 STARTING ALL SYSTEMS")
        logger.info("=" * 70)
        
        # Start arbitrage if available
        if 'arbitrage' in self.components:
            logger.info("\n💎 Starting Multi-Exchange Arbitrage...")
            task = asyncio.create_task(self.components['arbitrage'].run())
            tasks.append(task)
            
        # Start main bot
        if 'main_bot' in self.components:
            logger.info("\n🤖 Starting Main Trading Bot...")
            task = asyncio.create_task(self.components['main_bot'].start_evolution())
            tasks.append(task)
            
        # Monitor all tasks
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown requested...")
            self.running = False
            
            # Cancel all tasks
            for task in tasks:
                task.cancel()
                
            # Shutdown components
            for name, component in self.components.items():
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
                    
            logger.info("✅ All systems stopped")

async def main():
    """Main entry point"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        ULTRA TRADING SYSTEM - MULTI-EXCHANGE ARBITRAGE              ║
║                                                                      ║
║  • Automatic environment detection                                  ║
║  • Multi-exchange arbitrage scanning                                ║
║  • Swarm consciousness coordination                                 ║
║  • Intelligent credential management                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Create orchestrator
    orchestrator = UltraSystemOrchestrator()
    
    # Initialize
    await orchestrator.initialize()
    
    # Run
    await orchestrator.run()

if __name__ == "__main__":
    # Handle signals
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run
    asyncio.run(main())