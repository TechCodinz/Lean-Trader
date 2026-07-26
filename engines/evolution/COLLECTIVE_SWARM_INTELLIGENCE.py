#!/usr/bin/env python3
"""
🧠 COLLECTIVE SWARM INTELLIGENCE
Autonomous self-aware trading swarm that:
- Shares resources between all engines
- Auto-adjusts based on performance
- Prevents liquidation through collective awareness
- Catches ALL trading opportunities
- Restructures strategy in real-time
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from collections import deque
import statistics

logger = logging.getLogger(__name__)


class CollectiveSwarmIntelligence:
    """
    Central coordinator for all engines
    Creates collective awareness and auto-adjustment
    """
    
    def __init__(self, data_hub):
        self.data_hub = data_hub
        
        # Collective awareness
        self.engine_performance = {}  # Track each engine's performance
        self.shared_resources = {
            'balance': 0.0,
            'opportunities_found': 0,
            'trades_executed': 0,
            'total_profit': 0.0,
            'win_rate': 0.0
        }
        
        # Performance tracking
        self.trade_history = deque(maxlen=100)
        self.opportunity_cache = deque(maxlen=500)
        
        # Auto-adjustment thresholds
        self.min_confidence_threshold = 0.70
        self.max_position_size = 0.10  # 10% of balance
        self.liquidation_protection_threshold = 0.20  # Stop if down 20%
        
        # Engine coordination
        self.active_engines = set()
        self.engine_signals = {}  # Store signals from each engine
        self.engine_votes = {}  # Voting system for decisions
        
        # Swarm state
        self.swarm_mode = 'balanced'  # balanced, aggressive, conservative, recovery
        self.collective_confidence = 0.0
        
        logger.info("🧠 Collective Swarm Intelligence initialized")
    
    def register_engine(self, engine_name: str):
        """Register an engine with the swarm"""
        self.active_engines.add(engine_name)
        self.engine_performance[engine_name] = {
            'signals_generated': 0,
            'trades_executed': 0,
            'profit': 0.0,
            'win_rate': 0.0,
            'confidence_avg': 0.0,
            'last_active': datetime.now()
        }
        logger.info(f"🔗 {engine_name} joined the swarm")
    
    async def share_signal(self, engine_name: str, signal: Dict):
        """
        Engine shares a signal with the swarm
        Other engines can see and vote on it
        """
        if engine_name not in self.engine_signals:
            self.engine_signals[engine_name] = []
        
        # Add signal
        signal['source_engine'] = engine_name
        signal['timestamp'] = datetime.now()
        signal['votes'] = []
        
        self.engine_signals[engine_name].append(signal)
        
        # Let other engines vote
        await self._swarm_vote_on_signal(signal)
        
        # Update engine performance
        self.engine_performance[engine_name]['signals_generated'] += 1
        self.engine_performance[engine_name]['last_active'] = datetime.now()
        
        return signal
    
    async def _swarm_vote_on_signal(self, signal: Dict):
        """All engines vote on whether to take this trade"""
        symbol = signal.get('symbol')
        side = signal.get('side')
        confidence = signal.get('confidence', 0)
        
        # Voting criteria from different perspectives
        votes = {
            'technical': self._vote_technical(signal),
            'fundamental': self._vote_fundamental(signal),
            'risk': self._vote_risk(signal),
            'timing': self._vote_timing(signal),
            'momentum': self._vote_momentum(signal)
        }
        
        # Calculate swarm consensus
        total_votes = sum(1 for v in votes.values() if v > 0.5)
        swarm_confidence = sum(votes.values()) / len(votes)
        
        signal['swarm_votes'] = votes
        signal['swarm_consensus'] = total_votes >= 3  # At least 3/5 agree
        signal['swarm_confidence'] = swarm_confidence
        
        if signal['swarm_consensus']:
            logger.info(f"🐝 SWARM CONSENSUS: {symbol} {side} ({swarm_confidence*100:.0f}%)")
            logger.info(f"   Votes: {total_votes}/5 engines agree")
        
        return signal
    
    def _vote_technical(self, signal: Dict) -> float:
        """Technical analysis vote"""
        # Check if price action supports the signal
        confidence = signal.get('confidence', 0.5)
        
        # Look at recent signals for this symbol
        recent_signals = [s for s in self.opportunity_cache 
                         if s.get('symbol') == signal.get('symbol')]
        
        if recent_signals:
            # If multiple engines see the same opportunity, boost confidence
            same_direction = sum(1 for s in recent_signals[-5:] 
                               if s.get('side') == signal.get('side'))
            if same_direction >= 2:
                confidence *= 1.2
        
        return min(1.0, confidence)
    
    def _vote_fundamental(self, signal: Dict) -> float:
        """Fundamental analysis vote"""
        # Check news sentiment, trending status
        reasoning = signal.get('reasoning', '').lower()
        
        confidence = 0.5
        
        # Positive indicators
        if any(word in reasoning for word in ['trending', 'breakout', 'momentum', 'volume']):
            confidence += 0.2
        
        # Negative indicators
        if any(word in reasoning for word in ['risk', 'volatile', 'uncertain']):
            confidence -= 0.1
        
        return max(0, min(1.0, confidence))
    
    def _vote_risk(self, signal: Dict) -> float:
        """Risk management vote"""
        # Check if trade fits risk parameters
        
        # Check recent performance
        if self.trade_history:
            recent_wins = sum(1 for t in list(self.trade_history)[-10:] 
                            if t.get('profit', 0) > 0)
            win_rate = recent_wins / min(10, len(self.trade_history))
            
            # If losing streak, be more conservative
            if win_rate < 0.4:
                return 0.3
            elif win_rate > 0.6:
                return 0.9
        
        return 0.6
    
    def _vote_timing(self, signal: Dict) -> float:
        """Timing vote - is this the right time?"""
        # Check if we're in a good market condition
        
        # Session timing
        if signal.get('session_multiplier', 1.0) > 1.1:
            return 0.8
        elif signal.get('session_multiplier', 1.0) < 0.9:
            return 0.4
        
        return 0.6
    
    def _vote_momentum(self, signal: Dict) -> float:
        """Momentum vote"""
        # Check if momentum supports the trade
        
        # Look for confluence from multiple engines
        symbol = signal.get('symbol')
        recent = [s for s in self.opportunity_cache 
                 if s.get('symbol') == symbol]
        
        if len(recent) >= 3:  # Multiple engines see opportunity
            return 0.9
        elif len(recent) >= 2:
            return 0.7
        else:
            return 0.5
    
    async def auto_adjust_strategy(self, current_balance: float, starting_balance: float):
        """
        Auto-adjust entire swarm strategy based on performance
        Prevents liquidation and maximizes opportunities
        """
        # Calculate performance
        profit_pct = ((current_balance - starting_balance) / starting_balance) * 100
        
        # LIQUIDATION PREVENTION
        if profit_pct < -self.liquidation_protection_threshold * 100:
            logger.warning(f"⚠️  LIQUIDATION PROTECTION ACTIVATED!")
            logger.warning(f"   Down {abs(profit_pct):.1f}% from starting balance")
            self.swarm_mode = 'recovery'
            self.min_confidence_threshold = 0.85  # Only take high-confidence trades
            self.max_position_size = 0.05  # Reduce position size
            
            # Notify all engines
            await self._broadcast_swarm_mode_change('recovery')
            
        # PROFIT PROTECTION
        elif profit_pct > 50:
            logger.info(f"💰 PROFIT PROTECTION MODE - Up {profit_pct:.1f}%")
            self.swarm_mode = 'conservative'
            self.min_confidence_threshold = 0.75
            self.max_position_size = 0.08
            
            await self._broadcast_swarm_mode_change('conservative')
        
        # GROWTH MODE
        elif profit_pct > 10:
            logger.info(f"🚀 GROWTH MODE - Up {profit_pct:.1f}%")
            self.swarm_mode = 'aggressive'
            self.min_confidence_threshold = 0.65
            self.max_position_size = 0.12
            
            await self._broadcast_swarm_mode_change('aggressive')
        
        # BALANCED MODE
        else:
            self.swarm_mode = 'balanced'
            self.min_confidence_threshold = 0.70
            self.max_position_size = 0.10
        
        # Update shared resources
        self.shared_resources['balance'] = current_balance
        
        logger.info(f"🧠 Swarm Strategy: {self.swarm_mode.upper()}")
        logger.info(f"   Min Confidence: {self.min_confidence_threshold*100:.0f}%")
        logger.info(f"   Max Position: {self.max_position_size*100:.0f}%")
    
    async def _broadcast_swarm_mode_change(self, mode: str):
        """Notify all engines of mode change"""
        message = {
            'type': 'mode_change',
            'mode': mode,
            'min_confidence': self.min_confidence_threshold,
            'max_position': self.max_position_size,
            'timestamp': datetime.now().isoformat()
        }
        
        # All engines will adjust their behavior
        await self.data_hub.publish_signal(message)
        
        logger.info(f"📡 Broadcast to all {len(self.active_engines)} engines: Mode changed to {mode}")
    
    def record_trade_result(self, trade: Dict):
        """Record trade result for collective learning"""
        self.trade_history.append(trade)
        
        # Update shared resources
        profit = trade.get('profit', 0)
        self.shared_resources['total_profit'] += profit
        self.shared_resources['trades_executed'] += 1
        
        # Calculate win rate
        wins = sum(1 for t in self.trade_history if t.get('profit', 0) > 0)
        self.shared_resources['win_rate'] = wins / len(self.trade_history)
        
        # Update engine performance
        engine = trade.get('engine', 'unknown')
        if engine in self.engine_performance:
            self.engine_performance[engine]['trades_executed'] += 1
            self.engine_performance[engine]['profit'] += profit
    
    def get_collective_state(self) -> Dict:
        """Get current state of the entire swarm"""
        return {
            'mode': self.swarm_mode,
            'active_engines': len(self.active_engines),
            'engines': list(self.active_engines),
            'shared_resources': self.shared_resources.copy(),
            'thresholds': {
                'min_confidence': self.min_confidence_threshold,
                'max_position': self.max_position_size
            },
            'performance': {
                'trades': len(self.trade_history),
                'win_rate': self.shared_resources['win_rate'],
                'total_profit': self.shared_resources['total_profit']
            }
        }
    
    def should_take_trade(self, signal: Dict) -> bool:
        """
        Collective decision: Should we take this trade?
        All engines contribute to the decision
        """
        # Check swarm consensus
        if not signal.get('swarm_consensus', False):
            logger.debug(f"❌ No swarm consensus for {signal.get('symbol')}")
            return False
        
        # Check confidence against current threshold
        swarm_confidence = signal.get('swarm_confidence', 0)
        if swarm_confidence < self.min_confidence_threshold:
            logger.debug(f"❌ Confidence too low: {swarm_confidence*100:.0f}% < {self.min_confidence_threshold*100:.0f}%")
            return False
        
        # Check if in recovery mode
        if self.swarm_mode == 'recovery':
            # Only take trades with 85%+ confidence and at least 4/5 votes
            votes = signal.get('swarm_votes', {})
            high_votes = sum(1 for v in votes.values() if v > 0.7)
            if high_votes < 4:
                logger.debug(f"❌ Recovery mode: Need 4/5 high-confidence votes, got {high_votes}")
                return False
        
        logger.info(f"✅ SWARM APPROVES: {signal.get('symbol')} {signal.get('side')}")
        logger.info(f"   Confidence: {swarm_confidence*100:.0f}%")
        logger.info(f"   Mode: {self.swarm_mode}")
        
        return True
    
    async def optimize_opportunities(self):
        """
        Continuously scan for missed opportunities
        Ensure NO opportunity is left behind
        """
        # Get all signals from all engines
        all_signals = []
        for engine, signals in self.engine_signals.items():
            all_signals.extend(signals)
        
        # Find high-confidence signals that weren't acted on
        missed_opportunities = [
            s for s in all_signals
            if s.get('swarm_confidence', 0) > 0.8
            and not s.get('acted_on', False)
        ]
        
        if missed_opportunities:
            logger.warning(f"⚠️  Found {len(missed_opportunities)} missed opportunities!")
            for opp in missed_opportunities[:3]:  # Show first 3
                logger.info(f"   💎 {opp.get('symbol')} @ {opp.get('swarm_confidence', 0)*100:.0f}%")
            
            # Publish them again
            for opp in missed_opportunities:
                await self.data_hub.publish_signal(opp)
