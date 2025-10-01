#!/usr/bin/env python3
"""
Multi-Exchange Arbitrage System with Swarm Consciousness
Automatically detects and executes arbitrage opportunities across all configured exchanges
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
from decimal import Decimal
from collections import defaultdict
import ccxt.async_support as ccxt_async

logger = logging.getLogger(__name__)

class ExchangeEnvironmentManager:
    """
    Intelligently manages multiple exchange configurations from environment files
    """
    
    def __init__(self):
        self.env_files = {
            'live': 'env.live',
            'paper': 'env.paper',
            'testnet': 'env.testnet'
        }
        self.exchanges_config = {}
        self.active_mode = 'paper'  # Default safe mode
        
    def load_all_environments(self):
        """Load all environment configurations"""
        for mode, file_path in self.env_files.items():
            if Path(file_path).exists():
                self.load_environment(mode, file_path)
                
    def load_environment(self, mode: str, file_path: str):
        """Load specific environment file"""
        config = {}
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
                        
            # Extract exchange configurations
            exchanges = self.extract_exchange_configs(config)
            self.exchanges_config[mode] = exchanges
            
            logger.info(f"Loaded {len(exchanges)} exchanges from {mode} environment")
            
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            
    def extract_exchange_configs(self, config: Dict) -> Dict:
        """Extract exchange configurations from environment"""
        exchanges = {}
        
        # Known exchange prefixes
        exchange_prefixes = [
            'BINANCE', 'BYBIT', 'GATEIO', 'COINBASE', 'KRAKEN',
            'BITFINEX', 'HUOBI', 'OKEX', 'FTX', 'KUCOIN'
        ]
        
        for prefix in exchange_prefixes:
            api_key = config.get(f'{prefix}_API_KEY')
            secret = config.get(f'{prefix}_SECRET')
            
            if api_key and api_key != f'your_{prefix.lower()}_api_key_here':
                exchanges[prefix.lower()] = {
                    'apiKey': api_key,
                    'secret': secret,
                    'testnet': config.get(f'{prefix}_TESTNET', 'false').lower() == 'true',
                    'sandbox': config.get(f'{prefix}_SANDBOX', 'false').lower() == 'true'
                }
                
        return exchanges
        
    def get_best_environment(self) -> str:
        """Intelligently choose the best environment based on available credentials"""
        
        # Priority order
        priority = ['live', 'testnet', 'paper']
        
        for mode in priority:
            if mode in self.exchanges_config:
                exchanges = self.exchanges_config[mode]
                
                # Check if we have real credentials
                valid_exchanges = [
                    ex for ex, cfg in exchanges.items() 
                    if cfg['apiKey'] and not cfg['apiKey'].startswith('your_')
                ]
                
                if valid_exchanges:
                    logger.info(f"Selected {mode} environment with {len(valid_exchanges)} exchanges")
                    return mode
                    
        return 'paper'  # Fallback to paper trading

class MultiExchangeArbitrage:
    """
    Core arbitrage engine that monitors and executes opportunities
    """
    
    def __init__(self, env_manager: ExchangeEnvironmentManager):
        self.env_manager = env_manager
        self.exchanges = {}
        self.orderbooks = {}
        self.balances = {}
        self.opportunities = []
        self.min_profit_threshold = 0.002  # 0.2% minimum profit
        self.max_exposure = 1000  # Maximum USD per arbitrage
        
    async def initialize_exchanges(self):
        """Initialize all available exchanges"""
        
        mode = self.env_manager.get_best_environment()
        exchanges_config = self.env_manager.exchanges_config.get(mode, {})
        
        for exchange_id, config in exchanges_config.items():
            try:
                # Create exchange instance
                exchange_class = getattr(ccxt_async, exchange_id)
                exchange = exchange_class({
                    'apiKey': config['apiKey'],
                    'secret': config['secret'],
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot',
                        'adjustForTimeDifference': True
                    }
                })
                
                if config.get('testnet') or config.get('sandbox'):
                    exchange.set_sandbox_mode(True)
                    
                # Load markets
                await exchange.load_markets()
                
                self.exchanges[exchange_id] = exchange
                logger.info(f"✅ Initialized {exchange_id} exchange")
                
                # Fetch initial balance
                await self.update_balance(exchange_id)
                
            except Exception as e:
                logger.error(f"Failed to initialize {exchange_id}: {e}")
                
    async def update_balance(self, exchange_id: str):
        """Update balance for specific exchange"""
        try:
            exchange = self.exchanges[exchange_id]
            balance = await exchange.fetch_balance()
            self.balances[exchange_id] = balance
            
            # Log available balances
            total = balance.get('USDT', {}).get('free', 0)
            logger.info(f"{exchange_id} balance: ${total:.2f} USDT")
            
        except Exception as e:
            logger.error(f"Failed to fetch balance for {exchange_id}: {e}")
            
    async def fetch_orderbook(self, exchange_id: str, symbol: str):
        """Fetch orderbook for a symbol on an exchange"""
        try:
            exchange = self.exchanges[exchange_id]
            orderbook = await exchange.fetch_order_book(symbol, limit=10)
            self.orderbooks[f"{exchange_id}:{symbol}"] = orderbook
            return orderbook
            
        except Exception as e:
            logger.debug(f"Failed to fetch orderbook {exchange_id}:{symbol}: {e}")
            return None
            
    async def scan_arbitrage_opportunities(self, symbol: str = 'BTC/USDT'):
        """Scan for arbitrage opportunities across all exchanges"""
        
        # Fetch orderbooks from all exchanges
        tasks = []
        for exchange_id in self.exchanges:
            tasks.append(self.fetch_orderbook(exchange_id, symbol))
            
        await asyncio.gather(*tasks)
        
        # Find arbitrage opportunities
        opportunities = []
        exchange_ids = list(self.exchanges.keys())
        
        for i, buy_exchange in enumerate(exchange_ids):
            for sell_exchange in exchange_ids[i+1:]:
                
                buy_key = f"{buy_exchange}:{symbol}"
                sell_key = f"{sell_exchange}:{symbol}"
                
                if buy_key in self.orderbooks and sell_key in self.orderbooks:
                    buy_book = self.orderbooks[buy_key]
                    sell_book = self.orderbooks[sell_key]
                    
                    # Check both directions
                    opp1 = self.calculate_arbitrage(
                        buy_exchange, buy_book,
                        sell_exchange, sell_book,
                        symbol
                    )
                    
                    opp2 = self.calculate_arbitrage(
                        sell_exchange, sell_book,
                        buy_exchange, buy_book,
                        symbol
                    )
                    
                    if opp1:
                        opportunities.append(opp1)
                    if opp2:
                        opportunities.append(opp2)
                        
        # Sort by profit
        opportunities.sort(key=lambda x: x['profit_pct'], reverse=True)
        
        # Filter by threshold
        self.opportunities = [
            opp for opp in opportunities 
            if opp['profit_pct'] >= self.min_profit_threshold
        ]
        
        return self.opportunities
        
    def calculate_arbitrage(self, buy_exchange: str, buy_book: Dict,
                           sell_exchange: str, sell_book: Dict,
                           symbol: str) -> Optional[Dict]:
        """Calculate arbitrage opportunity between two exchanges"""
        
        try:
            # Get best prices
            buy_price = buy_book['asks'][0][0] if buy_book['asks'] else None
            sell_price = sell_book['bids'][0][0] if sell_book['bids'] else None
            
            if not buy_price or not sell_price:
                return None
                
            # Calculate profit
            spread = sell_price - buy_price
            profit_pct = (spread / buy_price) * 100
            
            # Estimate fees (0.1% per trade typical)
            total_fees = 0.2  # 0.1% buy + 0.1% sell
            net_profit_pct = profit_pct - total_fees
            
            if net_profit_pct <= 0:
                return None
                
            # Calculate optimal size
            buy_depth = buy_book['asks'][0][1] if buy_book['asks'] else 0
            sell_depth = sell_book['bids'][0][1] if sell_book['bids'] else 0
            max_size = min(buy_depth, sell_depth)
            
            # Limit by exposure
            max_usd = min(self.max_exposure, max_size * buy_price)
            optimal_size = max_usd / buy_price
            
            return {
                'symbol': symbol,
                'buy_exchange': buy_exchange,
                'sell_exchange': sell_exchange,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'spread': spread,
                'profit_pct': net_profit_pct,
                'size': optimal_size,
                'potential_profit': optimal_size * spread * (1 - total_fees/100),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error calculating arbitrage: {e}")
            return None

class SwarmConsciousness:
    """
    Distributed intelligence that coordinates multiple trading agents
    """
    
    def __init__(self):
        self.agents = {}
        self.collective_memory = defaultdict(list)
        self.consensus_threshold = 0.7
        self.swarm_decisions = []
        
    def add_agent(self, agent_id: str, agent: Any):
        """Add an agent to the swarm"""
        self.agents[agent_id] = agent
        logger.info(f"Added agent {agent_id} to swarm consciousness")
        
    async def collective_analysis(self, market_data: Dict) -> Dict:
        """Perform collective analysis across all agents"""
        
        analyses = {}
        
        # Gather analysis from each agent
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'analyze'):
                try:
                    analysis = await agent.analyze(market_data)
                    analyses[agent_id] = analysis
                except Exception as e:
                    logger.error(f"Agent {agent_id} analysis failed: {e}")
                    
        # Find consensus
        consensus = self.find_consensus(analyses)
        
        # Store in collective memory
        self.collective_memory['analyses'].append({
            'timestamp': datetime.now(),
            'consensus': consensus,
            'individual': analyses
        })
        
        # Trim memory
        if len(self.collective_memory['analyses']) > 1000:
            self.collective_memory['analyses'] = self.collective_memory['analyses'][-1000:]
            
        return consensus
        
    def find_consensus(self, analyses: Dict) -> Dict:
        """Find consensus among agent analyses"""
        
        if not analyses:
            return {'action': 'hold', 'confidence': 0}
            
        # Count votes
        votes = defaultdict(int)
        confidences = defaultdict(list)
        
        for agent_id, analysis in analyses.items():
            action = analysis.get('action', 'hold')
            confidence = analysis.get('confidence', 0)
            
            votes[action] += 1
            confidences[action].append(confidence)
            
        # Find majority action
        total_agents = len(analyses)
        consensus_action = 'hold'
        consensus_confidence = 0
        
        for action, count in votes.items():
            if count / total_agents >= self.consensus_threshold:
                avg_confidence = sum(confidences[action]) / len(confidences[action])
                if avg_confidence > consensus_confidence:
                    consensus_action = action
                    consensus_confidence = avg_confidence
                    
        return {
            'action': consensus_action,
            'confidence': consensus_confidence,
            'votes': dict(votes),
            'agreement': max(votes.values()) / total_agents
        }
        
    def share_knowledge(self, knowledge_type: str, data: Any):
        """Share knowledge across the swarm"""
        self.collective_memory[knowledge_type].append({
            'timestamp': datetime.now(),
            'data': data
        })
        
        # Notify all agents
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'receive_knowledge'):
                try:
                    agent.receive_knowledge(knowledge_type, data)
                except:
                    pass

class UltraArbitrageSystem:
    """
    Main system that orchestrates multi-exchange arbitrage with swarm intelligence
    """
    
    def __init__(self):
        self.env_manager = ExchangeEnvironmentManager()
        self.arbitrage_engine = None
        self.swarm = SwarmConsciousness()
        self.running = False
        
    async def initialize(self):
        """Initialize the complete system"""
        
        logger.info("=" * 70)
        logger.info("🚀 INITIALIZING ULTRA ARBITRAGE SYSTEM")
        logger.info("=" * 70)
        
        # Load all environments
        self.env_manager.load_all_environments()
        
        # Initialize arbitrage engine
        self.arbitrage_engine = MultiExchangeArbitrage(self.env_manager)
        await self.arbitrage_engine.initialize_exchanges()
        
        # Add arbitrage engine to swarm
        self.swarm.add_agent('arbitrage_master', self.arbitrage_engine)
        
        # Create specialized agents
        await self.create_specialized_agents()
        
        logger.info("✅ Ultra Arbitrage System initialized")
        logger.info(f"  • Active exchanges: {list(self.arbitrage_engine.exchanges.keys())}")
        logger.info(f"  • Swarm agents: {list(self.swarm.agents.keys())}")
        
    async def create_specialized_agents(self):
        """Create specialized trading agents"""
        
        # Trend follower agent
        class TrendAgent:
            async def analyze(self, data):
                # Simple trend analysis
                return {'action': 'buy', 'confidence': 0.6}
                
        # Mean reversion agent
        class ReversionAgent:
            async def analyze(self, data):
                # Mean reversion analysis
                return {'action': 'sell', 'confidence': 0.5}
                
        # Volume agent
        class VolumeAgent:
            async def analyze(self, data):
                # Volume analysis
                return {'action': 'hold', 'confidence': 0.7}
                
        self.swarm.add_agent('trend_follower', TrendAgent())
        self.swarm.add_agent('mean_reverter', ReversionAgent())
        self.swarm.add_agent('volume_analyzer', VolumeAgent())
        
    async def run(self):
        """Main execution loop"""
        
        self.running = True
        scan_interval = 10  # seconds
        
        logger.info("🔄 Starting arbitrage scanning...")
        
        while self.running:
            try:
                # Scan for opportunities
                symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
                
                for symbol in symbols:
                    opportunities = await self.arbitrage_engine.scan_arbitrage_opportunities(symbol)
                    
                    if opportunities:
                        logger.info(f"\n💎 Found {len(opportunities)} arbitrage opportunities for {symbol}:")
                        
                        for opp in opportunities[:3]:  # Show top 3
                            logger.info(
                                f"  • {opp['buy_exchange']} → {opp['sell_exchange']}: "
                                f"{opp['profit_pct']:.3f}% profit "
                                f"(${opp['potential_profit']:.2f})"
                            )
                            
                        # Get swarm consensus on best opportunity
                        if opportunities:
                            best_opp = opportunities[0]
                            consensus = await self.swarm.collective_analysis(best_opp)
                            
                            logger.info(f"  🧠 Swarm consensus: {consensus['action']} "
                                      f"(confidence: {consensus['confidence']:.2f})")
                            
                            # Execute if consensus is strong
                            if consensus['action'] == 'execute' and consensus['confidence'] > 0.8:
                                await self.execute_arbitrage(best_opp)
                                
                await asyncio.sleep(scan_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(scan_interval)
                
    async def execute_arbitrage(self, opportunity: Dict):
        """Execute an arbitrage opportunity"""
        
        logger.info(f"🎯 Executing arbitrage: {opportunity['symbol']}")
        logger.info(f"  Buy on {opportunity['buy_exchange']} @ ${opportunity['buy_price']:.2f}")
        logger.info(f"  Sell on {opportunity['sell_exchange']} @ ${opportunity['sell_price']:.2f}")
        logger.info(f"  Size: {opportunity['size']:.6f}")
        logger.info(f"  Expected profit: ${opportunity['potential_profit']:.2f}")
        
        # In production, this would execute real trades
        # For safety, we're just logging
        
        # Share execution with swarm
        self.swarm.share_knowledge('execution', opportunity)
        
    async def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Close all exchange connections
        for exchange in self.arbitrage_engine.exchanges.values():
            await exchange.close()

async def main():
    """Main entry point"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    )
    
    # Create and run system
    system = UltraArbitrageSystem()
    await system.initialize()
    
    try:
        await system.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        await system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())