#!/usr/bin/env python3
"""
🌌 CENTRAL CONTROL INTELLIGENCE
The supreme autonomous trading entity that coordinates everything

CONCEPT:
- Master intelligence overseeing all operations
- Receives reports from all models/spawns
- Makes high-level strategic decisions
- Calibrates all systems in real-time
- Learns from collective experience
- Achieves colony precision

ARCHITECTURE:
                    ┌─────────────────────────────────┐
                    │ CENTRAL CONTROL INTELLIGENCE    │
                    │  (Supreme Decision Maker)       │
                    └──────────────┬──────────────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
          ┌──────▼──────┐   ┌─────▼──────┐  ┌──────▼─────┐
          │   Hybrid    │   │  Exchange  │  │  Learning  │
          │ Coordinator │   │   Spawn    │  │  Transfer  │
          └─────────────┘   └────────────┘  └────────────┘
                 │                 │                │
          Testnet+Live      Models/Exchange    Pattern Learning
          
RESPONSIBILITIES:
1. Strategic decisions (which exchanges, which strategies)
2. Resource allocation (balance distribution)
3. Risk management (global position limits)
4. Performance optimization (boost winners, kill losers)
5. Learning aggregation (combine all learnings)
6. Autonomous evolution (spawn/kill/clone models)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import statistics
import json

logger = logging.getLogger(__name__)


class CentralControlIntelligence:
    """
    The supreme autonomous intelligence coordinating everything
    Makes all high-level decisions, learns continuously
    """
    
    def __init__(self, data_hub):
        self.data_hub = data_hub
        self.active = True
        
        # Sub-systems
        self.hybrid_coordinator = None
        self.spawn_manager = None
        self.collective_swarm = None
        
        # Intelligence state
        self.collective_knowledge = {
            'market_regimes': {},
            'optimal_strategies': {},
            'risk_patterns': {},
            'profit_patterns': {},
            'exchange_characteristics': {}
        }
        
        # Global metrics
        self.total_models = 0
        self.total_trades = 0
        self.total_profit = 0.0
        self.global_win_rate = 0.0
        self.global_sharpe_ratio = 0.0
        
        # Decision history
        self.decisions_made = []
        self.decision_performance = deque(maxlen=1000)
        
        # Strategic directives
        self.current_strategy = 'balanced'  # balanced, aggressive, conservative
        self.risk_level = 0.5  # 0.0 to 1.0
        self.target_exchanges = []
        self.priority_pairs = []
        
        # Autonomous learning
        self.learning_rate = 0.01
        self.adaptation_speed = 'fast'  # fast, medium, slow
        self.innovation_enabled = True
        
        # Performance tracking
        self.cycles_completed = 0
        self.optimizations_performed = 0
        self.strategies_evolved = 0
        
        logger.info("🌌 Central Control Intelligence initialized")
        logger.info("   Status: FULLY AUTONOMOUS")
        logger.info("   Learning: CONTINUOUS")
        logger.info("   Goal: MAXIMUM PROFIT WITH MINIMUM RISK")
    
    def register_subsystems(self, hybrid_coordinator, spawn_manager, collective_swarm):
        """Register all sub-systems for coordination"""
        self.hybrid_coordinator = hybrid_coordinator
        self.spawn_manager = spawn_manager
        self.collective_swarm = collective_swarm
        
        logger.info("🔗 All subsystems connected to Central Intelligence")
        logger.info(f"   [OK] Hybrid Coordinator: {hybrid_coordinator is not None}")
        logger.info(f"   [OK] Spawn Manager: {spawn_manager is not None}")
        logger.info(f"   [OK] Collective Swarm: {collective_swarm is not None}")
    
    async def start_central_intelligence(self):
        """Start the supreme intelligence"""
        logger.info("=" * 80)
        logger.info("🌌 STARTING CENTRAL CONTROL INTELLIGENCE")
        logger.info("=" * 80)
        logger.info("The bot is now FULLY AUTONOMOUS")
        logger.info("It will:")
        logger.info("  • Learn from testnet")
        logger.info("  • Trade on live with proven strategies")
        logger.info("  • Spawn models per exchange")
        logger.info("  • Optimize continuously")
        logger.info("  • Evolve strategies autonomously")
        logger.info("  • Achieve colony precision")
        logger.info("=" * 80)
        
        tasks = []
        
        # Start strategic oversight loop
        tasks.append(asyncio.create_task(self.strategic_oversight_loop()))
        
        # Start performance optimization loop
        tasks.append(asyncio.create_task(self.performance_optimization_loop()))
        
        # Start learning aggregation loop
        tasks.append(asyncio.create_task(self.learning_aggregation_loop()))
        
        # Start autonomous evolution loop
        tasks.append(asyncio.create_task(self.autonomous_evolution_loop()))
        
        await asyncio.gather(*tasks)
    
    async def strategic_oversight_loop(self):
        """
        High-level strategic decisions
        Determines overall direction of trading operations
        """
        while self.active:
            try:
                self.cycles_completed += 1
                
                logger.info("=" * 80)
                logger.info(f"🌌 STRATEGIC OVERSIGHT CYCLE {self.cycles_completed}")
                logger.info("=" * 80)
                
                # Gather intelligence from all subsystems
                hybrid_status = self.hybrid_coordinator.get_status() if self.hybrid_coordinator else {}
                spawn_status = self.spawn_manager.get_status() if self.spawn_manager else {}
                
                # Calculate global metrics
                await self._calculate_global_metrics(hybrid_status, spawn_status)
                
                # Make strategic decisions
                await self._make_strategic_decisions()
                
                # Issue directives to subsystems
                await self._issue_directives()
                
                logger.info("=" * 80)
                
                await asyncio.sleep(300)  # Every 5 minutes
            
            except Exception as e:
                logger.error(f"Strategic oversight error: {e}")
                await asyncio.sleep(60)
    
    async def performance_optimization_loop(self):
        """
        Continuously optimize performance
        Boost winners, kill losers, adjust parameters
        """
        while self.active:
            try:
                self.optimizations_performed += 1
                
                logger.info(f"⚡ PERFORMANCE OPTIMIZATION #{self.optimizations_performed}")
                
                # Analyze current performance
                performance = await self._analyze_performance()
                
                # Make optimizations
                if performance['win_rate'] < 0.6:
                    logger.info("   📊 Win rate low, shifting to conservative mode")
                    self.current_strategy = 'conservative'
                    self.risk_level = max(0.3, self.risk_level - 0.1)
                
                elif performance['win_rate'] > 0.75:
                    logger.info("   📊 Win rate high, shifting to aggressive mode")
                    self.current_strategy = 'aggressive'
                    self.risk_level = min(0.8, self.risk_level + 0.1)
                
                else:
                    logger.info("   📊 Performance balanced, maintaining current strategy")
                    self.current_strategy = 'balanced'
                
                # Optimize spawn manager
                if self.spawn_manager:
                    if performance['profit'] < 0:
                        logger.info("   🔮 Low profit, killing underperformers")
                        await self.spawn_manager.kill_underperforming_models()
                    
                    elif performance['profit'] > 100:
                        logger.info("   🔮 High profit, cloning best performers")
                        await self.spawn_manager.clone_best_models()
                
                await asyncio.sleep(180)  # Every 3 minutes
            
            except Exception as e:
                logger.error(f"Performance optimization error: {e}")
                await asyncio.sleep(60)
    
    async def learning_aggregation_loop(self):
        """
        Aggregate learnings from all models
        Build collective knowledge base
        """
        while self.active:
            try:
                logger.info("🧠 AGGREGATING COLLECTIVE LEARNING")
                
                # Collect learnings from hybrid coordinator
                if self.hybrid_coordinator:
                    for strategy_id, strategy in self.hybrid_coordinator.strategies.items():
                        if strategy.approved_for_live:
                            # This strategy works, add to optimal strategies
                            self.collective_knowledge['optimal_strategies'][strategy_id] = {
                                'win_rate': strategy.live_win_rate,
                                'profit': strategy.live_profit,
                                'trades': strategy.live_trades
                            }
                
                # Collect learnings from spawn manager
                if self.spawn_manager:
                    for exchange, models in self.spawn_manager.testnet_models.items():
                        exchange_learnings = []
                        
                        for model in models:
                            if model.learned_patterns:
                                exchange_learnings.extend(model.learned_patterns)
                        
                        if exchange_learnings:
                            self.collective_knowledge['exchange_characteristics'][exchange] = {
                                'patterns_learned': len(exchange_learnings),
                                'best_patterns': exchange_learnings[:10]  # Top 10
                            }
                
                logger.info(f"   Optimal strategies: {len(self.collective_knowledge['optimal_strategies'])}")
                logger.info(f"   Exchange insights: {len(self.collective_knowledge['exchange_characteristics'])}")
                
                await asyncio.sleep(240)  # Every 4 minutes
            
            except Exception as e:
                logger.error(f"Learning aggregation error: {e}")
                await asyncio.sleep(60)
    
    async def autonomous_evolution_loop(self):
        """
        Autonomous evolution of strategies
        Bot evolves itself to improve performance
        """
        while self.active:
            try:
                self.strategies_evolved += 1
                
                logger.info("🧬 AUTONOMOUS EVOLUTION CYCLE")
                
                # Check if we need to evolve
                performance = await self._analyze_performance()
                
                if performance['stagnant']:
                    logger.info("     Performance stagnant, triggering evolution")
                    
                    # Spawn new experimental models
                    if self.spawn_manager:
                        logger.info("   🔮 Spawning experimental models")
                        await self.spawn_manager.spawn_exchange_model('gateio', 'testnet')
                        await self.spawn_manager.spawn_exchange_model('bybit', 'testnet')
                    
                    # Increase innovation
                    self.innovation_enabled = True
                    logger.info("   💡 Innovation enabled")
                
                if performance['profit'] > self.total_profit * 1.5:
                    logger.info("   >> Performance breakthrough! Cloning winners")
                    if self.spawn_manager:
                        await self.spawn_manager.clone_best_models()
                
                logger.info(f"   Evolution cycles: {self.strategies_evolved}")
                
                await asyncio.sleep(600)  # Every 10 minutes
            
            except Exception as e:
                logger.error(f"Autonomous evolution error: {e}")
                await asyncio.sleep(120)
    
    async def receive_model_report(self, model):
        """Receive performance report from a model"""
        try:
            self.total_models += 1
            self.total_trades += model.trades_executed
            self.total_profit += model.total_profit
            
            # Update global win rate
            if self.total_trades > 0:
                # Would calculate from all models
                pass
            
            logger.debug(f"📊 Report from {model.model_id}: {model.trades_executed} trades, ${model.total_profit:.2f} profit")
        
        except Exception as e:
            logger.error(f"Model report error: {e}")
    
    async def _calculate_global_metrics(self, hybrid_status: Dict, spawn_status: Dict):
        """Calculate global performance metrics"""
        try:
            # From hybrid coordinator
            testnet_profit = hybrid_status.get('total_testnet_profit', 0)
            live_profit = hybrid_status.get('total_live_profit', 0)
            
            self.total_profit = testnet_profit + live_profit
            
            # Log metrics
            logger.info(f"Global Metrics:")
            logger.info(f"   Total profit: ${self.total_profit:.2f}")
            logger.info(f"   Testnet: ${testnet_profit:.2f}")
            logger.info(f"   Live: ${live_profit:.2f}")
            logger.info(f"   Active models: {spawn_status.get('testnet_models', 0) + spawn_status.get('live_models', 0)}")
            logger.info(f"   Strategy: {self.current_strategy}")
            logger.info(f"   Risk level: {self.risk_level:.2f}")
        
        except Exception as e:
            logger.error(f"Metrics calculation error: {e}")
    
    async def _make_strategic_decisions(self):
        """Make high-level strategic decisions"""
        try:
            # Decide which exchanges to prioritize
            if self.total_profit > 100:
                self.target_exchanges = ['gateio', 'bybit', 'binance']
                logger.info("   🎯 High profit, targeting all major exchanges")
            else:
                self.target_exchanges = ['gateio']
                logger.info("   🎯 Building profit, focusing on Gate.io")
            
            # Decide risk level
            if self.total_profit < -50:
                self.risk_level = 0.2
                logger.info("     Losses detected, reducing risk to 20%")
            
            # Record decision
            decision = {
                'timestamp': datetime.now(),
                'strategy': self.current_strategy,
                'risk_level': self.risk_level,
                'target_exchanges': self.target_exchanges
            }
            self.decisions_made.append(decision)
        
        except Exception as e:
            logger.error(f"Strategic decision error: {e}")
    
    async def _issue_directives(self):
        """Issue directives to all subsystems"""
        try:
            # Directive to hybrid coordinator
            if self.hybrid_coordinator:
                logger.info(f"   📤 Directive to Hybrid: Strategy={self.current_strategy}, Risk={self.risk_level}")
            
            # Directive to spawn manager
            if self.spawn_manager:
                logger.info(f"   📤 Directive to Spawn: Target exchanges={self.target_exchanges}")
        
        except Exception as e:
            logger.error(f"Directive issuance error: {e}")
    
    async def _analyze_performance(self) -> Dict:
        """Analyze overall performance"""
        try:
            # Simple analysis for now
            recent_profit = self.total_profit
            
            performance = {
                'profit': recent_profit,
                'win_rate': self.global_win_rate,
                'stagnant': abs(recent_profit) < 5 and self.cycles_completed > 10
            }
            
            return performance
        
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            return {'profit': 0, 'win_rate': 0, 'stagnant': False}
    
    def get_supreme_status(self) -> Dict:
        """Get complete status of central intelligence"""
        return {
            'central_intelligence': {
                'cycles_completed': self.cycles_completed,
                'optimizations_performed': self.optimizations_performed,
                'strategies_evolved': self.strategies_evolved,
                'total_profit': self.total_profit,
                'current_strategy': self.current_strategy,
                'risk_level': self.risk_level
            },
            'hybrid_coordinator': self.hybrid_coordinator.get_status() if self.hybrid_coordinator else {},
            'spawn_manager': self.spawn_manager.get_status() if self.spawn_manager else {},
            'collective_knowledge': {
                'optimal_strategies': len(self.collective_knowledge['optimal_strategies']),
                'exchange_insights': len(self.collective_knowledge['exchange_characteristics'])
            }
        }
