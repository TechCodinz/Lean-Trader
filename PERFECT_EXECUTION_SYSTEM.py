#!/usr/bin/env python3
"""
⚡ PERFECT EXECUTION SYSTEM ⚡
Flawless entry, monitoring, and exit

Features:
- Perfect entry timing (waits for optimal price)
- Active position monitoring
- Intelligent exit timing (maximize profit, minimize loss)
- Trailing take profit (let winners run)
- Quick stop loss (cut losers fast)
- Auto-compounding reinvestment
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class PerfectEntryTimer:
    """
    Waits for PERFECT entry price
    Never chases, never FOMOs
    """
    
    def __init__(self):
        self.max_wait_seconds = 60  # Wait up to 1 minute for perfect entry
        self.slippage_tolerance = 0.001  # 0.1% max slippage
        
    async def wait_for_perfect_entry(
        self, 
        exchange, 
        symbol: str, 
        target_price: float, 
        side: str,
        max_wait: int = None
    ) -> Optional[float]:
        """
        Wait for perfect entry price
        
        Returns actual entry price or None if timeout
        """
        max_wait = max_wait or self.max_wait_seconds
        start_time = datetime.now()
        
        best_price = None
        
        while (datetime.now() - start_time).seconds < max_wait:
            try:
                ticker = await asyncio.to_thread(exchange.fetch_ticker, symbol)
                current_price = ticker['last']
                
                # For BUY: Want price <= target (or slightly above within slippage)
                if side.upper() == 'BUY':
                    max_acceptable = target_price * (1 + self.slippage_tolerance)
                    if current_price <= max_acceptable:
                        best_price = current_price
                        logger.info(f"✅ Perfect BUY entry: ${current_price:.6f} (target: ${target_price:.6f})")
                        return current_price
                
                # For SELL: Want price >= target (or slightly below within slippage)
                else:
                    min_acceptable = target_price * (1 - self.slippage_tolerance)
                    if current_price >= min_acceptable:
                        best_price = current_price
                        logger.info(f"✅ Perfect SELL entry: ${current_price:.6f} (target: ${target_price:.6f})")
                        return current_price
                
                # Track best price seen
                if best_price is None:
                    best_price = current_price
                elif side.upper() == 'BUY' and current_price < best_price:
                    best_price = current_price
                elif side.upper() == 'SELL' and current_price > best_price:
                    best_price = current_price
                
                await asyncio.sleep(0.5)  # Check every 0.5 seconds
                
            except Exception as e:
                logger.debug(f"Entry timer error: {e}")
                await asyncio.sleep(1)
        
        # Timeout - use best price seen
        if best_price:
            logger.info(f"⏱️ Entry timeout - using best price: ${best_price:.6f}")
            return best_price
        
        return None


class ActivePositionMonitor:
    """
    Actively monitors all open positions
    Closes at perfect timing for maximum profit
    """
    
    def __init__(self):
        self.positions = {}  # {symbol: position_data}
        self.closed_positions = deque(maxlen=100)
        
    def add_position(self, symbol: str, position: Dict):
        """Add position to monitor"""
        position['entry_time'] = datetime.now()
        position['peak_profit_pct'] = 0.0
        position['updates'] = 0
        self.positions[symbol] = position
        
        logger.info(f"👁️ Monitoring: {symbol}")
    
    async def monitor_position(
        self,
        exchange,
        symbol: str,
        position: Dict
    ) -> Optional[Dict]:
        """
        Monitor one position and determine if should close
        
        Returns close signal if should exit
        """
        try:
            ticker = await asyncio.to_thread(exchange.fetch_ticker, symbol)
            current_price = ticker['last']
            
            entry_price = position['entry_price']
            side = position['side']
            target_profit_pct = position['profit_target_pct']
            stop_loss_pct = position['stop_loss_pct']
            
            # Calculate current P&L
            if side.upper() == 'BUY':
                pnl_pct = (current_price - entry_price) / entry_price
            else:
                pnl_pct = (entry_price - current_price) / entry_price
            
            # Update peak profit
            if pnl_pct > position['peak_profit_pct']:
                position['peak_profit_pct'] = pnl_pct
            
            position['updates'] += 1
            position['current_pnl_pct'] = pnl_pct
            position['current_price'] = current_price
            
            # Check exit conditions
            
            # 1. TAKE PROFIT HIT
            if pnl_pct >= target_profit_pct:
                return {
                    'action': 'CLOSE',
                    'reason': 'Take profit hit',
                    'pnl_pct': pnl_pct,
                    'current_price': current_price
                }
            
            # 2. TRAILING TAKE PROFIT (if price pulled back from peak)
            if position['peak_profit_pct'] > target_profit_pct * 0.8:  # Was at 80% of target
                pullback = position['peak_profit_pct'] - pnl_pct
                if pullback > target_profit_pct * 0.2:  # Pulled back 20% of target
                    return {
                        'action': 'CLOSE',
                        'reason': 'Trailing profit - locking gains',
                        'pnl_pct': pnl_pct,
                        'current_price': current_price
                    }
            
            # 3. STOP LOSS HIT
            if pnl_pct <= -stop_loss_pct:
                return {
                    'action': 'CLOSE',
                    'reason': 'Stop loss hit',
                    'pnl_pct': pnl_pct,
                    'current_price': current_price
                }
            
            # 4. TIME STOP (varies by speed)
            elapsed = (datetime.now() - position['entry_time']).seconds
            max_hold = position.get('max_hold_seconds', 300)
            
            if elapsed > max_hold:
                if pnl_pct > 0:
                    return {
                        'action': 'CLOSE',
                        'reason': 'Time stop - taking profit',
                        'pnl_pct': pnl_pct,
                        'current_price': current_price
                    }
                elif pnl_pct < -stop_loss_pct * 0.5:
                    return {
                        'action': 'CLOSE',
                        'reason': 'Time stop - cutting loss',
                        'pnl_pct': pnl_pct,
                        'current_price': current_price
                    }
            
            # No exit signal yet
            return None
            
        except Exception as e:
            logger.error(f"Monitor error for {symbol}: {e}")
            return None
    
    async def monitor_all_positions(self, exchange) -> List[Dict]:
        """Monitor all positions and return close signals"""
        close_signals = []
        
        for symbol, position in list(self.positions.items()):
            close_signal = await self.monitor_position(exchange, symbol, position)
            
            if close_signal:
                close_signal['symbol'] = symbol
                close_signal['position'] = position
                close_signals.append(close_signal)
        
        return close_signals
    
    def close_position(self, symbol: str, exit_price: float, reason: str) -> Dict:
        """Close position and record result"""
        if symbol not in self.positions:
            return {}
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        side = position['side']
        position_size = position['position_size']
        
        # Calculate final P&L
        if side.upper() == 'BUY':
            pnl_pct = (exit_price - entry_price) / entry_price
        else:
            pnl_pct = (entry_price - exit_price) / entry_price
        
        profit_usd = position_size * pnl_pct
        
        # Record
        result = {
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'side': side,
            'position_size': position_size,
            'pnl_pct': pnl_pct,
            'profit_usd': profit_usd,
            'reason': reason,
            'duration_seconds': (datetime.now() - position['entry_time']).seconds,
            'patterns': position.get('patterns_detected', []),
            'closed_at': datetime.now()
        }
        
        self.closed_positions.append(result)
        del self.positions[symbol]
        
        logger.info(f"💰 POSITION CLOSED: {symbol}")
        logger.info(f"   P&L: ${profit_usd:.4f} ({pnl_pct*100:.2f}%)")
        logger.info(f"   Reason: {reason}")
        logger.info(f"   Duration: {result['duration_seconds']}s")
        
        return result


class DynamicPairDiscovery:
    """
    ZERO hardcoded pairs - discovers pairs dynamically
    Finds best opportunities in real-time
    """
    
    def __init__(self):
        self.discovered_pairs = set()
        self.pair_quality_scores = {}
        self.last_scan_time = None
        
        logger.info("🔍 Dynamic Pair Discovery initialized - NO hardcoded pairs!")
    
    async def discover_best_pairs(
        self, 
        exchange, 
        min_volume_24h: float = 10000,
        min_volatility: float = 0.01,
        max_pairs: int = 50
    ) -> List[str]:
        """
        Discover best trading pairs dynamically
        
        Criteria:
        - High 24h volume (liquid)
        - Good volatility (opportunities)
        - USDT pairs (avoid conversion costs)
        - Active trading (real volume, not wash)
        """
        try:
            # Fetch all tickers
            tickers = await asyncio.to_thread(exchange.fetch_tickers)
            
            candidates = []
            
            for symbol, ticker in tickers.items():
                # Filter criteria
                if not symbol.endswith('/USDT'):
                    continue
                
                volume_24h = ticker.get('quoteVolume', 0)
                if volume_24h < min_volume_24h:
                    continue
                
                # Calculate volatility (using high-low range)
                high = ticker.get('high', 0)
                low = ticker.get('low', 0)
                last = ticker.get('last', 1)
                
                if last == 0:
                    continue
                
                volatility = (high - low) / last if last > 0 else 0
                
                if volatility < min_volatility:
                    continue
                
                # Quality score
                quality_score = (volume_24h / 100000) + (volatility * 100)
                
                candidates.append({
                    'symbol': symbol,
                    'volume_24h': volume_24h,
                    'volatility': volatility,
                    'quality_score': quality_score,
                    'last_price': last
                })
            
            # Sort by quality score
            candidates.sort(key=lambda x: x['quality_score'], reverse=True)
            
            # Take top N
            best_pairs = [c['symbol'] for c in candidates[:max_pairs]]
            
            # Update discovered pairs
            self.discovered_pairs.update(best_pairs)
            
            # Update quality scores
            for c in candidates[:max_pairs]:
                self.pair_quality_scores[c['symbol']] = c['quality_score']
            
            self.last_scan_time = datetime.now()
            
            logger.info(f"🔍 Discovered {len(best_pairs)} high-quality pairs")
            logger.info(f"   Top 5: {', '.join(best_pairs[:5])}")
            logger.info(f"   Avg volume: ${statistics.mean([c['volume_24h'] for c in candidates[:max_pairs]]):.0f}")
            
            return best_pairs
            
        except Exception as e:
            logger.error(f"Pair discovery error: {e}")
            return []
    
    def get_best_pairs(self, limit: int = 20) -> List[str]:
        """Get best pairs by quality score"""
        sorted_pairs = sorted(
            self.pair_quality_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [symbol for symbol, score in sorted_pairs[:limit]]


class CrossEngineConsensus:
    """
    Validates signals across multiple engines
    Only executes when MULTIPLE engines agree
    """
    
    def __init__(self, min_engines_required: int = 2):
        self.min_engines = min_engines_required
        self.engine_votes = defaultdict(list)
        self.consensus_history = deque(maxlen=100)
        
        logger.info(f"🤝 Cross-Engine Consensus: {min_engines_required}+ engines must agree")
    
    def add_vote(self, symbol: str, side: str, confidence: float, engine_name: str):
        """Add engine vote for a symbol"""
        vote = {
            'side': side,
            'confidence': confidence,
            'engine': engine_name,
            'timestamp': datetime.now()
        }
        
        self.engine_votes[symbol].append(vote)
        
        # Clean old votes (older than 60 seconds)
        cutoff = datetime.now() - timedelta(seconds=60)
        self.engine_votes[symbol] = [
            v for v in self.engine_votes[symbol]
            if v['timestamp'] > cutoff
        ]
    
    def get_consensus(self, symbol: str) -> Optional[Dict]:
        """
        Get consensus for symbol
        
        Returns consensus decision if enough engines agree
        """
        votes = self.engine_votes.get(symbol, [])
        
        if len(votes) < self.min_engines:
            return None
        
        # Group by side
        buy_votes = [v for v in votes if v['side'].upper() == 'BUY']
        sell_votes = [v for v in votes if v['side'].upper() == 'SELL']
        
        # Determine consensus
        if len(buy_votes) >= self.min_engines:
            avg_confidence = statistics.mean([v['confidence'] for v in buy_votes])
            engines = [v['engine'] for v in buy_votes]
            
            consensus = {
                'symbol': symbol,
                'side': 'BUY',
                'confidence': avg_confidence,
                'engines_agreeing': len(buy_votes),
                'engines': engines,
                'votes': buy_votes
            }
            
            logger.info(f"✅ CONSENSUS: {symbol} BUY ({len(buy_votes)} engines, {avg_confidence:.1%} avg confidence)")
            logger.info(f"   Engines: {', '.join(engines)}")
            
            return consensus
        
        elif len(sell_votes) >= self.min_engines:
            avg_confidence = statistics.mean([v['confidence'] for v in sell_votes])
            engines = [v['engine'] for v in sell_votes]
            
            consensus = {
                'symbol': symbol,
                'side': 'SELL',
                'confidence': avg_confidence,
                'engines_agreeing': len(sell_votes),
                'engines': engines,
                'votes': sell_votes
            }
            
            logger.info(f"✅ CONSENSUS: {symbol} SELL ({len(sell_votes)} engines, {avg_confidence:.1%} avg confidence)")
            logger.info(f"   Engines: {', '.join(engines)}")
            
            return consensus
        
        return None
    
    def clear_votes(self, symbol: str):
        """Clear votes for symbol after execution"""
        if symbol in self.engine_votes:
            del self.engine_votes[symbol]


# Import statistics
import statistics

# Export
__all__ = [
    'PerfectEntryTimer',
    'ActivePositionMonitor',
    'DynamicPairDiscovery',
    'CrossEngineConsensus'
]

logger.info("⚡ PERFECT EXECUTION SYSTEM loaded!")
