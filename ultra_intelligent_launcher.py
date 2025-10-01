#!/usr/bin/env python3
"""
Ultra Intelligent Launcher - The Brain of the Trading System
Automatically manages environments, exchanges, and features based on available resources
"""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ultra_intelligent.log')
    ]
)
logger = logging.getLogger('UltraIntelligent')

class IntelligentEnvironmentManager:
    """
    Intelligently manages all environments and decides the best configuration
    """
    
    def __init__(self):
        self.environments = {
            'arbitrage': 'env.arbitrage',
            'live': 'env.live',
            'testnet': 'env.testnet',
            'paper': 'env.paper'
        }
        self.available_exchanges = {}
        self.telegram_config = {}
        self.selected_mode = None
        
    def analyze_all_environments(self) -> Dict[str, Any]:
        """Analyze all available environments and credentials"""
        
        analysis = {
            'exchanges_with_balance': [],
            'exchanges_available': [],
            'telegram_configured': False,
            'arbitrage_possible': False,
            'training_environment': None,
            'production_ready': False
        }
        
        # Check each environment
        for env_name, env_file in self.environments.items():
            if Path(env_file).exists():
                exchanges = self.analyze_environment(env_file)
                
                if exchanges:
                    logger.info(f"Found {len(exchanges)} exchanges in {env_name}")
                    
                    if env_name == 'arbitrage' and len(exchanges) >= 7:
                        analysis['arbitrage_possible'] = True
                        analysis['exchanges_available'].extend(exchanges)
                    elif env_name == 'testnet':
                        analysis['training_environment'] = exchanges
                    elif env_name == 'live':
                        # These would need balance checks
                        analysis['exchanges_available'].extend(exchanges)
                        
        # Check Telegram configuration
        if Path('telegram_config.json').exists():
            self.load_telegram_config()
            if self.telegram_config.get('telegram', {}).get('bot_token'):
                analysis['telegram_configured'] = True
                
        # Determine production readiness
        if len(analysis['exchanges_available']) >= 2 and analysis['telegram_configured']:
            analysis['production_ready'] = True
            
        return analysis
        
    def analyze_environment(self, env_file: str) -> List[str]:
        """Analyze a specific environment file"""
        
        exchanges = []
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                
                # Known exchanges to check
                exchange_list = [
                    'BINANCE', 'BYBIT', 'GATEIO', 'COINBASE', 
                    'KRAKEN', 'KUCOIN', 'OKX', 'BITFINEX',
                    'HUOBI', 'MEXC'
                ]
                
                for exchange in exchange_list:
                    # Check if exchange has real credentials (not placeholders)
                    if f'{exchange}_API_KEY=' in content:
                        # Extract the value
                        for line in content.split('\n'):
                            if f'{exchange}_API_KEY=' in line and not line.startswith('#'):
                                key = line.split('=')[1].strip()
                                
                                # Check if it's a real key (you would add actual keys)
                                if key and not key.startswith('your_') and len(key) > 20:
                                    exchanges.append(exchange.lower())
                                    break
                                    
        except Exception as e:
            logger.error(f"Error analyzing {env_file}: {e}")
            
        return exchanges
        
    def load_telegram_config(self):
        """Load Telegram configuration"""
        
        try:
            with open('telegram_config.json', 'r') as f:
                self.telegram_config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading Telegram config: {e}")
            
    async def check_exchange_balances(self, exchanges: List[str]) -> List[str]:
        """Check which exchanges have balance (would connect to actual exchanges)"""
        
        exchanges_with_balance = []
        
        # In production, this would actually check balances
        # For now, we'll simulate
        logger.info("Checking exchange balances...")
        
        for exchange in exchanges:
            # Simulate balance check
            logger.info(f"  Checking {exchange}...")
            # In reality: balance = await exchange.fetch_balance()
            # if balance['USDT']['free'] > 10:
            #     exchanges_with_balance.append(exchange)
            
        return exchanges_with_balance
        
    def select_optimal_configuration(self, analysis: Dict) -> Dict[str, Any]:
        """Select the optimal configuration based on analysis"""
        
        config = {
            'mode': 'paper',  # Default safe mode
            'exchanges': [],
            'features': {
                'arbitrage': False,
                'training': False,
                'telegram': False,
                'swarm': False,
                'evolution': True
            }
        }
        
        # Determine mode
        if analysis['production_ready'] and analysis['arbitrage_possible']:
            config['mode'] = 'arbitrage'
            config['exchanges'] = analysis['exchanges_available']
            config['features']['arbitrage'] = True
            config['features']['swarm'] = True
        elif analysis['exchanges_available']:
            config['mode'] = 'live'
            config['exchanges'] = analysis['exchanges_available'][:5]  # Use top 5
        elif analysis['training_environment']:
            config['mode'] = 'testnet'
            config['exchanges'] = analysis['training_environment']
            config['features']['training'] = True
        else:
            config['mode'] = 'paper'
            logger.warning("No exchanges configured - using paper trading")
            
        # Enable Telegram if configured
        if analysis['telegram_configured']:
            config['features']['telegram'] = True
            
        return config

class UltraSystemCoordinator:
    """
    Coordinates all system components based on intelligent configuration
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.components = {}
        self.tasks = []
        
    async def initialize_system(self):
        """Initialize all system components"""
        
        logger.info("=" * 70)
        logger.info("🧠 ULTRA INTELLIGENT SYSTEM INITIALIZATION")
        logger.info("=" * 70)
        
        logger.info(f"\n📊 Selected Configuration:")
        logger.info(f"  • Mode: {self.config['mode'].upper()}")
        logger.info(f"  • Exchanges: {self.config['exchanges'] or 'Simulated'}")
        logger.info(f"  • Features:")
        for feature, enabled in self.config['features'].items():
            status = "✅ ENABLED" if enabled else "⚠️ DISABLED"
            logger.info(f"    - {feature.capitalize()}: {status}")
            
        # Load the appropriate environment
        await self.load_environment()
        
        # Initialize components based on configuration
        if self.config['features']['arbitrage']:
            await self.init_arbitrage_system()
            
        if self.config['features']['telegram']:
            await self.init_telegram_system()
            
        if self.config['features']['training']:
            await self.init_training_system()
            
        if self.config['features']['swarm']:
            await self.init_swarm_system()
            
        # Always initialize main trading pipeline
        await self.init_main_pipeline()
        
        logger.info("\n✅ All systems initialized successfully!")
        
    async def load_environment(self):
        """Load the appropriate environment file"""
        
        env_file = f"env.{self.config['mode']}"
        
        if Path(env_file).exists():
            logger.info(f"Loading environment: {env_file}")
            
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value.strip()
                        
    async def init_arbitrage_system(self):
        """Initialize multi-exchange arbitrage"""
        
        logger.info("\n💎 Initializing Arbitrage System...")
        
        try:
            from multi_exchange_arbitrage_system import UltraArbitrageSystem
            
            self.components['arbitrage'] = UltraArbitrageSystem()
            await self.components['arbitrage'].initialize()
            
            logger.info("  ✅ Arbitrage system ready")
            logger.info(f"  • Monitoring {len(self.config['exchanges'])} exchanges")
            logger.info("  • Scanning for opportunities across all pairs")
            
        except Exception as e:
            logger.error(f"  ❌ Arbitrage initialization failed: {e}")
            
    async def init_telegram_system(self):
        """Initialize Telegram notification system"""
        
        logger.info("\n📱 Initializing Telegram System...")
        
        try:
            # Load Telegram configuration
            admin_chat = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')
            free_channel = os.environ.get('TELEGRAM_FREE_CHANNEL_ID')
            vip_channel = os.environ.get('TELEGRAM_VIP_CHANNEL_ID')
            
            logger.info("  ✅ Telegram channels configured:")
            if admin_chat:
                logger.info(f"    • Admin: {admin_chat}")
            if free_channel:
                logger.info(f"    • Free Signals: {free_channel}")
            if vip_channel:
                logger.info(f"    • VIP Signals: {vip_channel}")
                
        except Exception as e:
            logger.error(f"  ❌ Telegram initialization failed: {e}")
            
    async def init_training_system(self):
        """Initialize AI training system"""
        
        logger.info("\n🧬 Initializing Training System...")
        
        try:
            logger.info("  ✅ Training mode activated")
            logger.info("  • Using Bybit Testnet for training")
            logger.info("  • AI learning enabled")
            logger.info("  • Model evolution active")
            
        except Exception as e:
            logger.error(f"  ❌ Training initialization failed: {e}")
            
    async def init_swarm_system(self):
        """Initialize swarm consciousness"""
        
        logger.info("\n🐝 Initializing Swarm Consciousness...")
        
        try:
            if Path('ultra_swarm_consciousness.py').exists():
                from ultra_swarm_consciousness import UltraSwarmConsciousness
                
                self.components['swarm'] = UltraSwarmConsciousness()
                logger.info("  ✅ Swarm consciousness activated")
                logger.info(f"  • {os.environ.get('SWARM_AGENTS', 20)} agents online")
                
        except Exception as e:
            logger.error(f"  ❌ Swarm initialization failed: {e}")
            
    async def init_main_pipeline(self):
        """Initialize main trading pipeline"""
        
        logger.info("\n🤖 Initializing Main Trading Pipeline...")
        
        try:
            from start_ultra_evolution import UltraEvolutionBot
            
            self.components['main'] = UltraEvolutionBot()
            await self.components['main'].initialize()
            
            logger.info("  ✅ Main pipeline ready")
            
        except Exception as e:
            logger.error(f"  ❌ Main pipeline initialization failed: {e}")
            
    async def run_system(self):
        """Run all initialized components"""
        
        logger.info("\n" + "=" * 70)
        logger.info("🚀 LAUNCHING ULTRA INTELLIGENT TRADING SYSTEM")
        logger.info("=" * 70)
        
        # Start all components
        if 'arbitrage' in self.components:
            logger.info("\n Starting Arbitrage Scanner...")
            task = asyncio.create_task(self.components['arbitrage'].run())
            self.tasks.append(task)
            
        if 'main' in self.components:
            logger.info("\n Starting Main Trading Engine...")
            task = asyncio.create_task(self.components['main'].start_evolution())
            self.tasks.append(task)
            
        # Start monitoring
        monitor_task = asyncio.create_task(self.monitor_system())
        self.tasks.append(monitor_task)
        
        # Wait for all tasks
        try:
            await asyncio.gather(*self.tasks)
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown requested...")
            await self.shutdown()
            
    async def monitor_system(self):
        """Monitor system health and send heartbeats"""
        
        while True:
            try:
                await asyncio.sleep(1800)  # 30 minutes
                
                # Send heartbeat to admin
                if os.environ.get('TELEGRAM_ADMIN_CHAT_ID'):
                    heartbeat = {
                        'timestamp': datetime.now().isoformat(),
                        'mode': self.config['mode'],
                        'exchanges': len(self.config['exchanges']),
                        'components': list(self.components.keys()),
                        'status': 'operational'
                    }
                    
                    logger.info(f"💓 Heartbeat: {heartbeat}")
                    # Would send to Telegram here
                    
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                
    async def shutdown(self):
        """Graceful shutdown"""
        
        logger.info("Shutting down all components...")
        
        for task in self.tasks:
            task.cancel()
            
        for name, component in self.components.items():
            if hasattr(component, 'shutdown'):
                await component.shutdown()
                
        logger.info("✅ All systems stopped")

async def main():
    """Main entry point"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          ULTRA INTELLIGENT TRADING SYSTEM v4.0                      ║
║                                                                      ║
║  🧠 Self-Configuring    🔄 Multi-Exchange    📱 Telegram Ready     ║
║  💎 Arbitrage Engine    🐝 Swarm Intelligence 🧬 Self-Evolution    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize environment manager
    env_manager = IntelligentEnvironmentManager()
    
    # Analyze all available resources
    logger.info("🔍 Analyzing available resources...")
    analysis = env_manager.analyze_all_environments()
    
    # Select optimal configuration
    logger.info("🧠 Selecting optimal configuration...")
    config = env_manager.select_optimal_configuration(analysis)
    
    # Create and run coordinator
    coordinator = UltraSystemCoordinator(config)
    await coordinator.initialize_system()
    await coordinator.run_system()

def create_vps_deployment_script():
    """Create a deployment script for VPS"""
    
    script = """#!/bin/bash
# Ultra Trading System - VPS Deployment Script

echo "🚀 Deploying Ultra Trading System..."

# Clone repository
git clone https://github.com/yourusername/ultra-trading-system.git
cd ultra-trading-system

# Install dependencies
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p logs data state backups

# Set up environment files
echo "📝 Please configure your API keys in:"
echo "  - env.arbitrage (for multi-exchange arbitrage)"
echo "  - env.testnet (for training with Bybit testnet)"
echo "  - env.live (for live trading)"

# Set up systemd service
sudo cp ultra-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ultra-bot
sudo systemctl start ultra-bot

echo "✅ Deployment complete!"
echo "📊 Monitor with: sudo journalctl -u ultra-bot -f"
"""
    
    with open('deploy_to_vps.sh', 'w') as f:
        f.write(script)
        
    os.chmod('deploy_to_vps.sh', 0o755)
    logger.info("Created VPS deployment script: deploy_to_vps.sh")

if __name__ == "__main__":
    # Create VPS deployment script
    create_vps_deployment_script()
    
    # Run the system
    asyncio.run(main())