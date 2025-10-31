#!/usr/bin/env python3
"""
ENHANCED AGGRESSIVE MICRO SCALPER
Uses ALL engine analysis to make ultra-fast scalping decisions
Designed to grow micro balances ($3-50) quickly
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class EnhancedAggressiveMicroScalper:
    """
    Aggressive micro scalper that:
    - Uses signals from ALL engines
    - Trades ONLY hot/fast pairs from dynamic discovery
    - Takes rapid 0.3-1% profits
    - Uses full available balance per trade
    - Exits losers quickly (<0.5% loss)
    """
    
    def __init__(self, profit_system, pair_discovery, tier_coordinator):
        self.profit_system = profit_system
        self.pair_discovery = pair_discovery
        self.tier_coordinator = tier_coordinator
        
        # Engine signal aggregation
        self.engine_signals: Dict[str, List[Dict]] = {}
        self.signal_weights = {
            'BRAIN_ADVISOR': 0.20,
            'HIVEMIND': 0.20,
            'SENTIENT': 0.15,
            'NEWS': 0.15,
            'OPPORTUNITY_SCANNER': 0.10,
            'SESSION_AWARE': 0.10,
            'QUANTUM': 0.05,
            'EVOLUTION': 0.05
        }
        
        # Scalping config
        self.min_confidence = 0.60  # Lower for micro - need more trades
        self.quick_profit_target = 0.003  # 0.3%
        self.normal_profit_target = 0.008  # 0.8%
        self.stop_loss = 0.005  # 0.5%
        
        # Execution tracking
        self.scalps_executed = 0
        self.scalps_won = 0
        self.total_profit = 0.0
        
        # Recent scalps (track performance)
        self.recent_scalps = deque(maxlen=100)
        
        logger.info("⚡ Enhanced Aggressive Micro Scalper initialized")
        logger.info("   Strategy: ALL-ENGINE consensus + dynamic pairs")
        logger.info("   Target: 0.3-0.8% profits, <0.5% losses")
    
    async def receive_engine_signal(self, engine_name: str, signal: Dict):
        """Receive signal from any engine"""
        if engine_name not in self.engine_signals:
            self.engine_signals[engine_name] = deque(maxlen=50)
        
        # Add timestamp
        signal['timestamp'] = datetime.now()
        signal['engine'] = engine_name
        
        self.engine_signals[engine_name].append(signal)
    
    async def aggregate_signals(self, symbol: str) -> Optional[Dict]:
        """
        Aggregate signals from ALL engines for a symbol
        Returns consensus decision with confidence
        """
        buy_votes = 0
        sell_votes = 0
        total_weight = 0
        confidence_sum = 0
        
        reasons = []
        
        # Check each engine's latest signal for this symbol
        for engine_name, signals in self.engine_signals.items():
            # Get most recent signal for this symbol
            for signal in reversed(signals):
                if signal.get('symbol') == symbol:
                    # Check age (only last 5 minutes)
                    age = (datetime.now() - signal['timestamp']).seconds
                    if age > 300:
                        break
                    
                    weight = self.signal_weights.get(engine_name, 0.05)
                    side = signal.get('side', '').lower()
                    conf = signal.get('confidence', 0.5)
                    
                    if side == 'buy':
                        buy_votes += weight
                        confidence_sum += conf * weight
                        reasons.append(f"{engine_name}:BUY({conf:.0%})")
                    elif side == 'sell':
                        sell_votes += weight
                        confidence_sum += conf * weight
                        reasons.append(f"{engine_name}:SELL({conf:.0%})")
                    
                    total_weight += weight
                    break  # Only use most recent signal
        
        # No signals?
        if total_weight == 0:
            return None
        
        # Calculate consensus
        if buy_votes > sell_votes * 1.5:
            side = 'buy'
            confidence = buy_votes / total_weight
        elif sell_votes > buy_votes * 1.5:
            side = 'sell'
            confidence = sell_votes / total_weight
        else:
            return None  # No clear consensus
        
        # Average confidence from engines
        avg_confidence = confidence_sum / total_weight if total_weight > 0 else 0.5
        final_confidence = (confidence + avg_confidence) / 2
        
        if final_confidence < self.min_confidence:
            return None
        
        return {
            'symbol': symbol,
            'side': side,
            'confidence': final_confidence,
            'engine_count': len([r for r in reasons]),
            'reasons': reasons[:5],  # Top 5 reasons
            'buy_votes': buy_votes,
            'sell_votes': sell_votes
        }
    
    async def find_best_scalp_opportunity(self) -> Optional[Dict]:
        """
        Find the BEST scalp opportunity right now
        Uses dynamic pair discovery + engine signals
        """
        # Get top opportunities from pair discovery
        opportunities = await self.pair_discovery.get_top_opportunities(limit=30)
        
        if not opportunities:
            return None
        
        # Score each opportunity with engine signals
        scored_opps = []
        
        for opp in opportunities:
            symbol = opp['symbol']
            
            # Get engine consensus
            consensus = await self.aggregate_signals(symbol)
            
            if not consensus:
                continue
            
            # Calculate total score
            score = opp['score']  # Base score from pair discovery
            score += consensus['confidence'] * 50  # Engine confidence
            score += consensus['engine_count'] * 5  # More engines = better
            
            # Bonus for fast movers
            if abs(opp['change_24h']) > 3:
                score += 20
            
            scored_opps.append({
                **opp,
                'consensus': consensus,
                'final_score': score
            })
        
        if not scored_opps:
            return None
        
        # Return highest scored
        scored_opps.sort(key=lambda x: x['final_score'], reverse=True)
        return scored_opps[0]
    
    async def execute_micro_scalp(self, opportunity: Dict) -> bool:
        """Execute a micro scalp trade"""
        try:
            symbol = opportunity['symbol']
            consensus = opportunity['consensus']
            side = consensus['side']
            confidence = consensus['confidence']
            
            logger.info("")
            logger.info("⚡" + "="*60)
            logger.info(f"   MICRO SCALP: {side.upper()} {symbol}")
            logger.info(f"   Confidence: {confidence:.1%}")
            logger.info(f"   Engine votes: {consensus['engine_count']}")
            logger.info(f"   Reasons: {', '.join(consensus['reasons'][:3])}")
            logger.info(f"   Pair score: {opportunity['score']}")
            logger.info("   " + "="*60)
            
            # Get recommended position size from tier coordinator
            position_size = self.tier_coordinator.get_recommended_position_size()
            
            # For micro tier, use ALL available balance
            if self.tier_coordinator.current_tier in ['nano', 'micro']:
                balance = await self.profit_system.get_current_balance()
                position_size = max(balance * 0.95, 3.0)  # 95% or $3 min
            
            # Create signal for profit system
            signal = {
                'symbol': symbol,
                'side': side,
                'confidence': confidence,
                'source': 'ENHANCED_MICRO_SCALPER',
                'position_size': position_size,
                'target': self.quick_profit_target,  # Quick 0.3% target
                'stop': self.stop_loss,
                'metadata': {
                    'engines': consensus['engine_count'],
                    'category': opportunity.get('category', 'UNKNOWN'),
                    'volume_24h': opportunity.get('volume_24h', 0),
                    'change_24h': opportunity.get('change_24h', 0)
                }
            }
            
            # Execute through profit system
            result = await self.profit_system.execute_signal(signal)
            
            if result and result.get('success'):
                self.scalps_executed += 1
                
                # Track scalp
                self.recent_scalps.append({
                    'symbol': symbol,
                    'side': side,
                    'confidence': confidence,
                    'timestamp': datetime.now(),
                    'position_size': position_size
                })
                
                logger.info("✅ MICRO SCALP EXECUTED!")
                return True
            else:
                logger.warning(f"⚠️  Scalp execution failed: {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Micro scalp error: {e}")
            return False
    
    async def run_aggressive_scalping_loop(self):
        """
        Main aggressive scalping loop
        Constantly searches for and executes micro scalps
        """
        logger.info("⚡ Starting AGGRESSIVE MICRO SCALPING LOOP...")
        logger.info("   Scanning every 5 seconds for opportunities")
        logger.info("   Using ALL engine signals + dynamic pairs")
        logger.info("")
        
        scan_interval = 5  # Scan every 5 seconds
        
        while True:
            try:
                # Check if we should be running
                if not self.tier_coordinator.should_engine_run('AGGRESSIVE_MICRO_SCALPER'):
                    logger.debug("Micro scalper paused (tier deactivation)")
                    await asyncio.sleep(30)
                    continue
                
                # Refresh pairs if needed
                await self.pair_discovery.refresh_if_needed()
                
                # Find best opportunity
                opportunity = await self.find_best_scalp_opportunity()
                
                if opportunity:
                    logger.info(f"🎯 Found opportunity: {opportunity['symbol']} (score: {opportunity['final_score']:.0f})")
                    
                    # Check if we already have a position
                    if not await self.profit_system.has_open_position(opportunity['symbol']):
                        # Execute!
                        await self.execute_micro_scalp(opportunity)
                        
                        # Wait a bit after execution
                        await asyncio.sleep(10)
                    else:
                        logger.debug(f"Already in position: {opportunity['symbol']}")
                
                # Wait before next scan
                await asyncio.sleep(scan_interval)
                
            except Exception as e:
                logger.error(f"Scalping loop error: {e}")
                await asyncio.sleep(15)
    
    def get_statistics(self) -> Dict:
        """Get scalper statistics"""
        win_rate = (self.scalps_won / self.scalps_executed * 100) if self.scalps_executed > 0 else 0
        
        return {
            'scalps_executed': self.scalps_executed,
            'scalps_won': self.scalps_won,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'recent_scalps': len(self.recent_scalps),
            'engine_signals': len(self.engine_signals)
        }


# Global instance
_micro_scalper = None

def initialize_micro_scalper(profit_system, pair_discovery, tier_coordinator):
    """Initialize global micro scalper"""
    global _micro_scalper
    _micro_scalper = EnhancedAggressiveMicroScalper(profit_system, pair_discovery, tier_coordinator)
    return _micro_scalper

def get_micro_scalper():
    """Get global micro scalper"""
    return _micro_scalper
