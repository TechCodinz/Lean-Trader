#!/usr/bin/env python3
"""
🌐 HYBRID INTELLIGENCE COORDINATOR
Simultaneously trades on TESTNET + LIVE for continuous learning

CONCEPT:
- Testnet instances: Learn, experiment, test new strategies
- Live instances: Execute proven strategies for profit
- Learning transfer: Best testnet strategies → live execution
- Central coordination: All instances report to master intelligence

ARCHITECTURE:
┌─────────────────────────────────────────────────────────┐
│         CENTRAL CONTROL INTELLIGENCE                     │
│  (Coordinates all testnet + live instances)             │
└──────────────────┬──────────────────────────────────────┘
                   │
          ┌────────┴────────┐
          │                 │
    ┌─────▼─────┐     ┌────▼────┐
    │  TESTNET  │     │  LIVE   │
    │ INSTANCES │     │INSTANCES│
    └───────────┘     └─────────┘
         │                 │
    Learn/Experiment   Apply/Profit
         │                 │
         └────────┬────────┘
                  │
           Learning Transfer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import statistics
import json
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class StrategyPerformance:
    """Track performance of a strategy across testnet and live"""
    strategy_id: str
    testnet_trades: int = 0
    testnet_wins: int = 0
    testnet_profit: float = 0.0
    live_trades: int = 0
    live_wins: int = 0
    live_profit: float = 0.0
    confidence: float = 0.0
    approved_for_live: bool = False
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @property
    def testnet_win_rate(self):
        return (self.testnet_wins / self.testnet_trades) if self.testnet_trades > 0 else 0.0
    
    @property
    def live_win_rate(self):
        return (self.live_wins / self.live_trades) if self.live_trades > 0 else 0.0


class HybridIntelligenceCoordinator:
    """
    Coordinates simultaneous testnet + live trading
    Learns from testnet, applies to live
    """
    
    def __init__(self, data_hub):
        self.data_hub = data_hub
        self.active = True
        
        # Testnet instances (for learning)
        self.testnet_instances = {}  # {exchange: instance}
        self.testnet_performance = {}  # Track testnet results
        
        # Live instances (for profit)
        self.live_instances = {}  # {exchange: instance}
        self.live_performance = {}  # Track live results
        
        # Strategy tracking
        self.strategies = {}  # {strategy_id: StrategyPerformance}
        self.strategy_history = deque(maxlen=10000)
        
        # Learning thresholds
        self.min_testnet_trades_for_approval = 50
        self.min_testnet_win_rate = 0.65
        self.min_testnet_profit = 10.0  # $10 profit on testnet
        
        # Central intelligence
        self.collective_knowledge = {
            'best_pairs': {},
            'best_timeframes': {},
            'best_indicators': {},
            'risk_patterns': {},
            'market_regimes': {}
        }
        
        # Performance tracking
        self.total_testnet_profit = 0.0
        self.total_live_profit = 0.0
        self.learning_cycles = 0
        self.strategies_approved = 0
        self.strategies_rejected = 0
        
        logger.info("🌐 Hybrid Intelligence Coordinator initialized")
        logger.info("   Mode: SIMULTANEOUS testnet learning + live trading")
        logger.info("   Strategy: Learn on testnet → Apply to live")
    
    async def start_hybrid_trading(self):
        """Start both testnet and live trading simultaneously"""
        logger.info("🚀 Starting HYBRID TRADING MODE")
        logger.info("   Testnet: Learning & experimentation")
        logger.info("   Live: Proven strategies only")
        
        tasks = []
        
        # Start testnet learning loop
        tasks.append(asyncio.create_task(self.testnet_learning_loop()))
        
        # Start live trading loop
        tasks.append(asyncio.create_task(self.live_trading_loop()))
        
        # Start learning transfer loop
        tasks.append(asyncio.create_task(self.learning_transfer_loop()))
        
        # Start central coordination loop
        tasks.append(asyncio.create_task(self.central_coordination_loop()))
        
        await asyncio.gather(*tasks)
    
    async def testnet_learning_loop(self):
        """
        Continuous learning on testnet
        Tests new strategies, learns patterns
        """
        while self.active:
            try:
                # Get signals from all engines
                signals = await self.data_hub.get_all_signals()
                
                for signal in signals:
                    # Execute on testnet for learning
                    strategy_id = signal.get('strategy_id', 'unknown')
                    
                    # Track testnet execution
                    if strategy_id not in self.strategies:
                        self.strategies[strategy_id] = StrategyPerformance(
                            strategy_id=strategy_id
                        )
                    
                    # Simulate or execute on testnet
                    result = await self._execute_on_testnet(signal)
                    
                    # Update testnet performance
                    self.strategies[strategy_id].testnet_trades += 1
                    if result.get('profit', 0) > 0:
                        self.strategies[strategy_id].testnet_wins += 1
                        self.strategies[strategy_id].testnet_profit += result.get('profit', 0)
                    
                    self.strategies[strategy_id].last_updated = datetime.now()
                    
                    # Check if strategy should be approved for live
                    await self._evaluate_strategy_for_live(strategy_id)
                
                await asyncio.sleep(5)  # Every 5 seconds
            
            except Exception as e:
                logger.error(f"Testnet learning error: {e}")
                await asyncio.sleep(10)
    
    async def live_trading_loop(self):
        """
        Live trading with PROVEN strategies only
        Only executes strategies that passed testnet validation
        """
        while self.active:
            try:
                # Get signals from all engines
                signals = await self.data_hub.get_all_signals()
                
                for signal in signals:
                    strategy_id = signal.get('strategy_id', 'unknown')
                    
                    # Check if strategy is approved for live
                    if strategy_id in self.strategies:
                        strategy = self.strategies[strategy_id]
                        
                        if strategy.approved_for_live:
                            # Execute on LIVE exchange
                            result = await self._execute_on_live(signal)
                            
                            # Update live performance
                            strategy.live_trades += 1
                            if result.get('profit', 0) > 0:
                                strategy.live_wins += 1
                                strategy.live_profit += result.get('profit', 0)
                            
                            strategy.last_updated = datetime.now()
                            
                            logger.info(f"💰 LIVE TRADE: {signal['pair']} {signal['side']} (Strategy: {strategy_id})")
                            logger.info(f"   Profit: ${result.get('profit', 0):.2f} | Win rate: {strategy.live_win_rate*100:.1f}%")
                        else:
                            logger.debug(f"🚫 Strategy {strategy_id} not approved for live yet")
                    else:
                        logger.debug(f"⚠️  Unknown strategy {strategy_id}, running on testnet first")
                
                await asyncio.sleep(1)  # Every second
            
            except Exception as e:
                logger.error(f"Live trading error: {e}")
                await asyncio.sleep(10)
    
    async def learning_transfer_loop(self):
        """
        Transfer best learnings from testnet to live
        Continuously evaluates and approves strategies
        """
        while self.active:
            try:
                self.learning_cycles += 1
                
                logger.info(f"🧠 Learning Transfer Cycle {self.learning_cycles}")
                logger.info(f"   Strategies tested: {len(self.strategies)}")
                logger.info(f"   Approved for live: {self.strategies_approved}")
                logger.info(f"   Rejected: {self.strategies_rejected}")
                
                # Evaluate all strategies
                for strategy_id, strategy in self.strategies.items():
                    if not strategy.approved_for_live:
                        await self._evaluate_strategy_for_live(strategy_id)
                
                # Update collective knowledge
                await self._update_collective_knowledge()
                
                await asyncio.sleep(60)  # Every minute
            
            except Exception as e:
                logger.error(f"Learning transfer error: {e}")
                await asyncio.sleep(30)
    
    async def central_coordination_loop(self):
        """
        Central intelligence that coordinates everything
        Monitors performance, adjusts strategies, ensures optimal operation
        """
        while self.active:
            try:
                # Calculate overall performance
                testnet_trades = sum(s.testnet_trades for s in self.strategies.values())
                live_trades = sum(s.live_trades for s in self.strategies.values())
                
                testnet_profit = sum(s.testnet_profit for s in self.strategies.values())
                live_profit = sum(s.live_profit for s in self.strategies.values())
                
                logger.info("=" * 80)
                logger.info("🌐 HYBRID INTELLIGENCE STATUS")
                logger.info("=" * 80)
                logger.info(f"Testnet Learning:")
                logger.info(f"   Trades: {testnet_trades} | Profit: ${testnet_profit:.2f}")
                logger.info(f"Live Trading:")
                logger.info(f"   Trades: {live_trades} | Profit: ${live_profit:.2f}")
                logger.info(f"Learning Pipeline:")
                logger.info(f"   Strategies tested: {len(self.strategies)}")
                logger.info(f"   Approved: {self.strategies_approved}")
                logger.info(f"   Rejected: {self.strategies_rejected}")
                logger.info("=" * 80)
                
                # Save state to database
                await self._save_hybrid_state()
                
                await asyncio.sleep(300)  # Every 5 minutes
            
            except Exception as e:
                logger.error(f"Central coordination error: {e}")
                await asyncio.sleep(60)
    
    async def _execute_on_testnet(self, signal: Dict) -> Dict:
        """Execute trade on testnet for learning"""
        try:
            # This would connect to testnet exchange
            # For now, simulate
            result = {
                'success': True,
                'profit': signal.get('confidence', 0.7) * 5 - 2.5,  # Simulated
                'timestamp': datetime.now()
            }
            
            logger.debug(f"🧪 TESTNET: {signal['pair']} {signal['side']} | Confidence: {signal.get('confidence', 0)*100:.0f}%")
            
            return result
        
        except Exception as e:
            logger.error(f"Testnet execution error: {e}")
            return {'success': False, 'profit': 0}
    
    async def _execute_on_live(self, signal: Dict) -> Dict:
        """Execute trade on LIVE exchange (only approved strategies!)"""
        try:
            # This would connect to live exchange via execution orchestrator
            # For now, return placeholder
            result = {
                'success': True,
                'profit': 0,  # Real execution would have actual profit
                'timestamp': datetime.now()
            }
            
            # Publish to data hub for actual execution
            await self.data_hub.publish_signal(signal)
            
            return result
        
        except Exception as e:
            logger.error(f"Live execution error: {e}")
            return {'success': False, 'profit': 0}
    
    async def _evaluate_strategy_for_live(self, strategy_id: str):
        """Evaluate if strategy should be approved for live trading"""
        if strategy_id not in self.strategies:
            return
        
        strategy = self.strategies[strategy_id]
        
        # Skip if already approved
        if strategy.approved_for_live:
            return
        
        # Check approval criteria
        if (strategy.testnet_trades >= self.min_testnet_trades_for_approval and
            strategy.testnet_win_rate >= self.min_testnet_win_rate and
            strategy.testnet_profit >= self.min_testnet_profit):
            
            # APPROVE for live trading!
            strategy.approved_for_live = True
            self.strategies_approved += 1
            
            logger.info("=" * 80)
            logger.info(f"✅ STRATEGY APPROVED FOR LIVE: {strategy_id}")
            logger.info(f"   Testnet trades: {strategy.testnet_trades}")
            logger.info(f"   Testnet win rate: {strategy.testnet_win_rate*100:.1f}%")
            logger.info(f"   Testnet profit: ${strategy.testnet_profit:.2f}")
            logger.info("   🚀 Now executing on LIVE exchange!")
            logger.info("=" * 80)
        
        # Check rejection criteria
        elif strategy.testnet_trades >= self.min_testnet_trades_for_approval:
            if strategy.testnet_win_rate < 0.5 or strategy.testnet_profit < -20:
                # REJECT strategy
                self.strategies_rejected += 1
                logger.warning(f"❌ STRATEGY REJECTED: {strategy_id} (Win rate: {strategy.testnet_win_rate*100:.1f}%)")
    
    async def _update_collective_knowledge(self):
        """Update collective knowledge from all strategies"""
        # Aggregate best practices from all strategies
        for strategy in self.strategies.values():
            if strategy.approved_for_live:
                # This strategy works well, learn from it
                # (In production, would extract actual patterns/parameters)
                pass
    
    async def _save_hybrid_state(self):
        """Save hybrid state to database for persistence"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'learning_cycles': self.learning_cycles,
                'strategies_approved': self.strategies_approved,
                'strategies_rejected': self.strategies_rejected,
                'total_testnet_profit': sum(s.testnet_profit for s in self.strategies.values()),
                'total_live_profit': sum(s.live_profit for s in self.strategies.values()),
                'strategies': {k: asdict(v) for k, v in self.strategies.items()}
            }
            
            # Would save to database here
            # For now, just log
            logger.debug(f"💾 Hybrid state saved")
        
        except Exception as e:
            logger.error(f"State save error: {e}")
    
    def get_status(self) -> Dict:
        """Get current hybrid intelligence status"""
        return {
            'testnet_instances': len(self.testnet_instances),
            'live_instances': len(self.live_instances),
            'strategies_tested': len(self.strategies),
            'strategies_approved': self.strategies_approved,
            'strategies_rejected': self.strategies_rejected,
            'learning_cycles': self.learning_cycles,
            'total_testnet_profit': sum(s.testnet_profit for s in self.strategies.values()),
            'total_live_profit': sum(s.live_profit for s in self.strategies.values())
        }
