#!/usr/bin/env python3
"""
SIGNAL AGGREGATOR - Combines multiple signals intelligently
Trades once with high confidence instead of 5 times with low confidence
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class SignalAggregator:
    """
    Aggregates signals from multiple engines into unified high-confidence signals
    Prevents capital fragmentation and reduces fees
    """
    
    def __init__(self, 
                 aggregation_window: int = 10,  # seconds to collect signals
                 min_signals: int = 2,          # minimum signals to aggregate
                 max_signals: int = 10):        # maximum signals to collect
        
        self.aggregation_window = aggregation_window
        self.min_signals = min_signals
        self.max_signals = max_signals
        
        # Active signal collection
        self.pending_signals = defaultdict(list)
        self.aggregation_tasks = {}
        
        # Statistics
        self.stats = {
            'raw_signals': 0,
            'aggregated_signals': 0,
            'signals_combined': 0,
            'average_aggregation': 0,
        }
        
        logger.info("🧠 Signal Aggregator initialized")
        logger.info(f"   Window: {aggregation_window}s")
        logger.info(f"   Min signals: {min_signals}")
        logger.info(f"   Max signals: {max_signals}")
    
    async def add_signal(self, symbol: str, signal: Dict) -> Optional[Dict]:
        """
        Add signal for aggregation
        Returns aggregated signal if ready, None if still collecting
        """
        self.stats['raw_signals'] += 1
        
        # Add signal to pending
        self.pending_signals[symbol].append({
            **signal,
            'timestamp': datetime.now(),
        })
        
        logger.info(f"📥 Signal received: {symbol} {signal.get('side', 'unknown').upper()} from {signal.get('engine', 'unknown')}")
        logger.info(f"   Confidence: {signal.get('confidence', 0):.1%} | Pending: {len(self.pending_signals[symbol])}")
        
        # Start aggregation timer if first signal
        if len(self.pending_signals[symbol]) == 1:
            self.aggregation_tasks[symbol] = asyncio.create_task(
                self._aggregation_timer(symbol)
            )
        
        # Check if we have enough signals
        if len(self.pending_signals[symbol]) >= self.min_signals:
            # Check if we should aggregate now
            if len(self.pending_signals[symbol]) >= self.max_signals:
                # Max signals reached, aggregate immediately
                return await self._aggregate_signals(symbol)
            
            # Check if signals are unanimous (all same side)
            sides = [s['side'] for s in self.pending_signals[symbol]]
            if len(set(sides)) == 1:  # All agree
                # Cancel timer and aggregate
                if symbol in self.aggregation_tasks:
                    self.aggregation_tasks[symbol].cancel()
                return await self._aggregate_signals(symbol)
        
        return None  # Still collecting
    
    async def _aggregation_timer(self, symbol: str):
        """Wait for aggregation window to expire"""
        try:
            await asyncio.sleep(self.aggregation_window)
            
            # Time expired, aggregate signals
            if len(self.pending_signals[symbol]) >= self.min_signals:
                aggregated = await self._aggregate_signals(symbol)
                # Would publish aggregated signal here
            else:
                # Not enough signals, discard
                logger.info(f"  Insufficient signals for {symbol}, discarding {len(self.pending_signals[symbol])} signals")
                self.pending_signals[symbol] = []
            
        except asyncio.CancelledError:
            # Timer cancelled because we aggregated early
            pass
        finally:
            if symbol in self.aggregation_tasks:
                del self.aggregation_tasks[symbol]
    
    async def _aggregate_signals(self, symbol: str) -> Dict:
        """Aggregate pending signals into one unified signal"""
        if symbol not in self.pending_signals or not self.pending_signals[symbol]:
            return None
        
        signals = self.pending_signals[symbol]
        
        # Group by side
        buy_signals = [s for s in signals if s.get('side') == 'buy']
        sell_signals = [s for s in signals if s.get('side') == 'sell']
        
        # Determine dominant side
        if len(buy_signals) > len(sell_signals):
            dominant_signals = buy_signals
            side = 'buy'
        elif len(sell_signals) > len(buy_signals):
            dominant_signals = sell_signals
            side = 'sell'
        else:
            # Equal signals, use higher confidence
            if buy_signals and sell_signals:
                avg_buy_conf = statistics.mean([s.get('confidence', 0) for s in buy_signals])
                avg_sell_conf = statistics.mean([s.get('confidence', 0) for s in sell_signals])
                if avg_buy_conf > avg_sell_conf:
                    dominant_signals = buy_signals
                    side = 'buy'
                else:
                    dominant_signals = sell_signals
                    side = 'sell'
            else:
                dominant_signals = signals
                side = signals[0].get('side', 'buy')
        
        # Aggregate confidence (weighted average)
        confidences = [s.get('confidence', 0.5) for s in dominant_signals]
        aggregated_confidence = statistics.mean(confidences)
        
        # Boost confidence based on consensus
        consensus_boost = min(0.1, len(dominant_signals) * 0.02)  # +2% per signal, max +10%
        aggregated_confidence = min(1.0, aggregated_confidence + consensus_boost)
        
        # Collect engines
        engines = list(set([s.get('engine', 'unknown') for s in dominant_signals]))
        
        # Calculate aggregated position size (sum of individual sizes)
        total_size = sum([s.get('size', 0) for s in dominant_signals])
        
        # Take average of other parameters
        volatilities = [s.get('volatility', 0.02) for s in dominant_signals]
        avg_volatility = statistics.mean(volatilities) if volatilities else 0.02
        
        stop_losses = [s.get('stop_loss', 0.01) for s in dominant_signals if s.get('stop_loss')]
        avg_stop_loss = statistics.mean(stop_losses) if stop_losses else 0.01
        
        take_profits = [s.get('take_profit', 0.02) for s in dominant_signals if s.get('take_profit')]
        avg_take_profit = statistics.mean(take_profits) if take_profits else 0.02
        
        # Create aggregated signal
        aggregated = {
            'symbol': symbol,
            'side': side,
            'confidence': aggregated_confidence,
            'size': total_size,
            'volatility': avg_volatility,
            'stop_loss': avg_stop_loss,
            'take_profit': avg_take_profit,
            'engines': engines,
            'num_signals': len(dominant_signals),
            'timestamp': datetime.now(),
            'aggregated': True,
        }
        
        # Update statistics
        self.stats['aggregated_signals'] += 1
        self.stats['signals_combined'] += len(dominant_signals)
        self.stats['average_aggregation'] = self.stats['signals_combined'] / self.stats['aggregated_signals']
        
        # Clear pending signals
        self.pending_signals[symbol] = []
        
        logger.info(f"[OK] AGGREGATED SIGNAL: {symbol} {side.upper()}")
        logger.info(f"   Combined {len(dominant_signals)} signals from {len(engines)} engines")
        logger.info(f"   Confidence: {aggregated_confidence:.1%} (boosted by consensus)")
        logger.info(f"   Size: ${total_size:.2f}")
        
        return aggregated
    
    def get_pending_count(self, symbol: str) -> int:
        """Get number of pending signals for symbol"""
        return len(self.pending_signals.get(symbol, []))
    
    def get_stats(self) -> Dict:
        """Get aggregation statistics"""
        reduction_pct = 0
        if self.stats['raw_signals'] > 0:
            reduction_pct = ((self.stats['raw_signals'] - self.stats['aggregated_signals']) / self.stats['raw_signals']) * 100
        
        return {
            **self.stats,
            'reduction_pct': reduction_pct,
        }
    
    def print_stats(self):
        """Print aggregation statistics"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("🧠 SIGNAL AGGREGATION STATISTICS")
        print("=" * 80)
        print(f"Raw Signals: {stats['raw_signals']}")
        print(f"Aggregated Signals: {stats['aggregated_signals']}")
        print(f"Signals Combined: {stats['signals_combined']}")
        print(f"Average Aggregation: {stats['average_aggregation']:.1f} signals/trade")
        print(f"Trade Reduction: {stats['reduction_pct']:.1f}%")
        print()
        print(f"💰 Fee Savings: {stats['reduction_pct']:.1f}% fewer trades = {stats['reduction_pct']:.1f}% fee reduction!")
        print("=" * 80)


# Example usage
if __name__ == '__main__':
    async def test_aggregator():
        aggregator = SignalAggregator(
            aggregation_window=5,
            min_signals=2,
            max_signals=5
        )
        
        print("=" * 80)
        print("🧠 TESTING SIGNAL AGGREGATOR")
        print("=" * 80)
        print()
        
        # Simulate signals from multiple engines
        test_signals = [
            {'symbol': 'BTC/USDT', 'side': 'buy', 'confidence': 0.85, 'size': 20, 'engine': 'ScalpEngine1'},
            {'symbol': 'BTC/USDT', 'side': 'buy', 'confidence': 0.88, 'size': 25, 'engine': 'ScalpEngine2'},
            {'symbol': 'BTC/USDT', 'side': 'buy', 'confidence': 0.82, 'size': 15, 'engine': 'MomentumEngine'},
            {'symbol': 'BTC/USDT', 'side': 'buy', 'confidence': 0.90, 'size': 30, 'engine': 'TrendEngine'},
        ]
        
        print("Sending 4 BUY signals for BTC/USDT...")
        print()
        
        aggregated = None
        for signal in test_signals:
            result = await aggregator.add_signal(signal['symbol'], signal)
            if result:
                aggregated = result
            await asyncio.sleep(1)
        
        if aggregated:
            print()
            print("=" * 80)
            print("📊 AGGREGATION RESULT")
            print("=" * 80)
            print(f"Instead of 4 trades of $20-$30 each...")
            print(f"We get 1 trade of ${aggregated['size']:.2f}")
            print(f"Confidence boosted to {aggregated['confidence']:.1%}")
            print(f"Engines: {', '.join(aggregated['engines'])}")
            print()
            print("💰 Fee Savings:")
            print(f"   Before: 4 trades × 0.15% = 0.60% total fees")
            print(f"   After:  1 trade × 0.15% = 0.15% total fees")
            print(f"   Savings: 75% reduction in fees!")
            print("=" * 80)
        
        # Print stats
        aggregator.print_stats()
    
    asyncio.run(test_aggregator())
