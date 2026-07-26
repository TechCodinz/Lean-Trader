#!/usr/bin/env python3
"""
🧠 SENTIENT INTEGRATION - MASTER COORDINATOR 🧠
Integrates all ultra-sophisticated systems into one sentient trader

This is the missing piece that makes everything work together:
- Sentient decision making
- Fee-aware execution
- Perfect timing
- Ultra-sophisticated algorithms
- Dynamic pair discovery
- Cross-engine consensus
- Compounding growth
- Pattern shuffling
- Zero waste

Deploy this to make your bot truly sentient.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

# Import all the new systems
try:
    from SENTIENT_TRADER_ULTIMATE import (
        initialize_sentient_trader,
        process_signal_sentient,
        record_trade_result,
        SentientOrchestrator
    )
    SENTIENT_AVAILABLE = True
except ImportError:
    SENTIENT_AVAILABLE = False
    logging.warning(" SENTIENT_TRADER_ULTIMATE not found")

try:
    from PERFECT_EXECUTION_SYSTEM import (
        PerfectEntryTimer,
        ActivePositionMonitor,
        DynamicPairDiscovery,
        CrossEngineConsensus
    )
    EXECUTION_AVAILABLE = True
except ImportError:
    EXECUTION_AVAILABLE = False
    logging.warning(" PERFECT_EXECUTION_SYSTEM not found")

try:
    from ULTRA_SOPHISTICATED_ALGORITHMS import (
        AlgorithmMaster
    )
    ALGORITHMS_AVAILABLE = True
except ImportError:
    ALGORITHMS_AVAILABLE = False
    logging.warning(" ULTRA_SOPHISTICATED_ALGORITHMS not found")

logger = logging.getLogger(__name__)


class SentientIntegration:
    """
    Master coordinator for all sentient systems
    """
    
    def __init__(self, exchange, initial_balance: float = 20.0):
        self.exchange = exchange
        self.initial_balance = initial_balance
        
        # Initialize components
        self.sentient_orchestrator = None
        self.entry_timer = None
        self.position_monitor = None
        self.pair_discovery = None
        self.consensus_engine = None
        self.algorithm_master = None
        
        # Stats
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        self.current_balance = initial_balance
        
        # Initialize all systems
        self._initialize_systems()
        
    def _initialize_systems(self):
        """Initialize all sophisticated systems"""
        logger.info("=" * 80)
        logger.info("🧠 SENTIENT INTEGRATION INITIALIZING")
        logger.info("=" * 80)
        
        if SENTIENT_AVAILABLE:
            self.sentient_orchestrator = initialize_sentient_trader(self.initial_balance)
            logger.info("[OK] Sentient Orchestrator")
        else:
            logger.warning("[X] Sentient Orchestrator UNAVAILABLE")
        
        if EXECUTION_AVAILABLE:
            self.entry_timer = PerfectEntryTimer()
            self.position_monitor = ActivePositionMonitor()
            self.pair_discovery = DynamicPairDiscovery()
            self.consensus_engine = CrossEngineConsensus(min_engines_required=2)
            logger.info("[OK] Perfect Execution System")
        else:
            logger.warning("[X] Perfect Execution System UNAVAILABLE")
        
        if ALGORITHMS_AVAILABLE:
            self.algorithm_master = AlgorithmMaster()
            logger.info("[OK] Ultra-Sophisticated Algorithms")
        else:
            logger.warning("[X] Ultra-Sophisticated Algorithms UNAVAILABLE")
        
        logger.info("=" * 80)
        
        # Log status
        available_count = sum([
            SENTIENT_AVAILABLE,
            EXECUTION_AVAILABLE,
            ALGORITHMS_AVAILABLE
        ])
        
        if available_count == 3:
            logger.info(">> ALL SYSTEMS ONLINE - FULL SENTIENT MODE")
        elif available_count >= 2:
            logger.info("⚡ PARTIAL SYSTEMS ONLINE - ENHANCED MODE")
        else:
            logger.info(" LIMITED SYSTEMS - FALLBACK MODE")
        
        logger.info("=" * 80)
    
    async def discover_best_pairs(self) -> List[str]:
        """Discover best trading pairs dynamically"""
        if not self.pair_discovery:
            # Fallback to common pairs
            return ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
        
        pairs = await self.pair_discovery.discover_best_pairs(
            self.exchange,
            min_volume_24h=50000,  # $50k min volume
            min_volatility=0.01,   # 1% min volatility
            max_pairs=30           # Top 30 pairs
        )
        
        return pairs if pairs else ['BTC/USDT', 'ETH/USDT']
    
    async def process_signal(
        self,
        signal: Dict,
        prices: Optional[List[float]] = None,
        returns: Optional[List[float]] = None
    ) -> Optional[Dict]:
        """
        Process signal through all systems
        
        Returns enhanced signal or None if should skip
        """
        symbol = signal.get('symbol', 'UNKNOWN')
        
        # 1. Get current balance
        try:
            balance = await asyncio.to_thread(self.exchange.fetch_balance)
            usdt_balance = balance.get('USDT', {}).get('free', self.current_balance)
            self.current_balance = usdt_balance
        except:
            usdt_balance = self.current_balance
        
        # 2. Run sophisticated algorithms
        algorithm_boost = 0.0
        if self.algorithm_master and prices and returns:
            try:
                algo_analysis = self.algorithm_master.comprehensive_analysis(
                    symbol=symbol,
                    prices=prices,
                    returns=returns,
                    signal=signal
                )
                algorithm_boost = algo_analysis.get('total_confidence_boost', 0.0)
                signal['algorithm_analysis'] = algo_analysis
            except Exception as e:
                logger.debug(f"Algorithm analysis error: {e}")
        
        # 3. Apply algorithm boost to signal
        base_confidence = signal.get('confidence', 0.75)
        signal['confidence'] = min(base_confidence + algorithm_boost, 0.98)
        
        # 4. Process through sentient orchestrator
        if self.sentient_orchestrator:
            enhanced_signal = await process_signal_sentient(
                signal=signal,
                current_balance=usdt_balance,
                market_data={
                    'price_change_1h': signal.get('price_change', 0.0),
                    'volume_ratio': signal.get('volume_ratio', 1.0),
                    'volatility': signal.get('volatility', 0.02)
                }
            )
            
            if not enhanced_signal:
                logger.debug(f"[X] {symbol} filtered by sentient orchestrator")
                return None
            
            return enhanced_signal
        
        # Fallback if sentient not available
        return signal
    
    async def execute_trade(self, signal: Dict) -> Optional[Dict]:
        """
        Execute trade with perfect timing
        """
        symbol = signal['symbol']
        side = signal['side']
        position_size = signal['position_size']
        
        try:
            # 1. Get current price
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            target_price = ticker['last']
            
            # 2. Wait for perfect entry (if enabled)
            if self.entry_timer:
                perfect_price = await self.entry_timer.wait_for_perfect_entry(
                    exchange=self.exchange,
                    symbol=symbol,
                    target_price=target_price,
                    side=side,
                    max_wait=30  # 30 second max wait
                )
                
                if perfect_price:
                    target_price = perfect_price
            
            # 3. Calculate quantity
            quantity = position_size / target_price
            
            # Get market info for minimum
            markets = await asyncio.to_thread(self.exchange.load_markets)
            market = markets.get(symbol)
            
            if market:
                min_amount = market['limits']['amount']['min']
                if quantity < min_amount:
                    logger.warning(f"[X] {symbol}: Quantity {quantity} below minimum {min_amount}")
                    return None
            
            # 4. Execute order
            logger.info(f"🎯 EXECUTING: {side} {quantity:.6f} {symbol} @ ${target_price:.6f}")
            
            order = await asyncio.to_thread(
                self.exchange.create_market_order,
                symbol=symbol,
                side=side.lower(),
                amount=quantity
            )
            
            # 5. Add to position monitor
            if self.position_monitor:
                position = {
                    'entry_price': target_price,
                    'side': side,
                    'position_size': position_size,
                    'quantity': quantity,
                    'profit_target_pct': signal.get('profit_target_pct', 0.01),
                    'stop_loss_pct': signal.get('stop_loss_pct', 0.005),
                    'patterns_detected': signal.get('patterns_detected', []),
                    'max_hold_seconds': 300 if signal.get('speed') == 'ultra_fast' else 600
                }
                self.position_monitor.add_position(symbol, position)
            
            logger.info(f"[OK] Order executed: {order.get('id', 'UNKNOWN')}")
            
            return order
            
        except Exception as e:
            logger.error(f"[X] Execution failed for {symbol}: {e}")
            return None
    
    async def monitor_and_close_positions(self):
        """Monitor all positions and close when appropriate"""
        if not self.position_monitor:
            return
        
        close_signals = await self.position_monitor.monitor_all_positions(self.exchange)
        
        for close_signal in close_signals:
            symbol = close_signal['symbol']
            position = close_signal['position']
            
            try:
                # Close position
                logger.info(f"🔒 CLOSING: {symbol} - {close_signal['reason']}")
                
                side = 'sell' if position['side'].upper() == 'BUY' else 'buy'
                quantity = position['quantity']
                
                close_order = await asyncio.to_thread(
                    self.exchange.create_market_order,
                    symbol=symbol,
                    side=side,
                    amount=quantity
                )
                
                # Record result
                result = self.position_monitor.close_position(
                    symbol=symbol,
                    exit_price=close_signal['current_price'],
                    reason=close_signal['reason']
                )
                
                # Update stats
                self.total_trades += 1
                if result['profit_usd'] > 0:
                    self.winning_trades += 1
                self.total_profit += result['profit_usd']
                
                # Record for learning
                if self.sentient_orchestrator:
                    record_trade_result(
                        symbol=symbol,
                        patterns=result['patterns'],
                        profit=result['profit_usd'],
                        fees=result['position_size'] * 0.004  # Estimate
                    )
                
                logger.info(f"[OK] Closed: ${result['profit_usd']:.4f} profit")
                
            except Exception as e:
                logger.error(f"[X] Failed to close {symbol}: {e}")
    
    def get_stats(self) -> Dict:
        """Get trading statistics"""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'current_balance': self.current_balance,
            'roi': (self.current_balance / self.initial_balance - 1) * 100 if self.initial_balance > 0 else 0
        }
    
    async def run_monitoring_loop(self):
        """Run continuous position monitoring"""
        logger.info("👁️ Starting position monitoring loop")
        
        while True:
            try:
                await self.monitor_and_close_positions()
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(10)


# Global instance
_sentient_integration = None

def initialize_sentient_integration(exchange, initial_balance: float = 20.0) -> SentientIntegration:
    """Initialize sentient integration"""
    global _sentient_integration
    _sentient_integration = SentientIntegration(exchange, initial_balance)
    return _sentient_integration

def get_sentient_integration() -> Optional[SentientIntegration]:
    """Get global sentient integration instance"""
    return _sentient_integration

# Export
__all__ = [
    'SentientIntegration',
    'initialize_sentient_integration',
    'get_sentient_integration',
    'SENTIENT_AVAILABLE',
    'EXECUTION_AVAILABLE',
    'ALGORITHMS_AVAILABLE'
]

logger.info("🧠 SENTIENT INTEGRATION loaded - Ready to coordinate all systems!")
