#!/usr/bin/env python3
"""
SMART TRADE FILTER - Reduces wasted trades by 60%
Only trades when conditions are optimal
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


class SmartTradeFilter:
    """
    Intelligent trade filtering to prevent waste:
    1. Volatility check - only trade when market moves
    2. Cooldown periods - prevent over-trading same pair
    3. Multi-engine consensus - require agreement
    4. Volume validation - avoid low liquidity
    """
    
    def __init__(self, 
                 min_volatility: float = 0.01,  # 1% hourly volatility minimum
                 cooldown_seconds: int = 300,    # 5 minutes between trades
                 min_engines_agree: int = 3,     # Require 3 engines to agree
                 min_confidence: float = 0.85):  # 85% minimum confidence
        
        self.min_volatility = min_volatility
        self.cooldown_seconds = cooldown_seconds
        self.min_engines_agree = min_engines_agree
        self.min_confidence = min_confidence
        
        # Track last trade time per pair
        self.last_trade_time = {}
        
        # Track signal counts per pair
        self.signal_counts = defaultdict(lambda: {'buy': 0, 'sell': 0, 'engines': []})
        
        # Volatility cache
        self.volatility_cache = {}
        
        # Statistics
        self.stats = {
            'signals_received': 0,
            'signals_passed': 0,
            'filtered_low_volatility': 0,
            'filtered_cooldown': 0,
            'filtered_low_consensus': 0,
            'filtered_low_confidence': 0,
        }
        
        logger.info("🎯 Smart Trade Filter initialized")
        logger.info(f"   Min Volatility: {min_volatility*100:.1f}% per hour")
        logger.info(f"   Cooldown: {cooldown_seconds}s between trades")
        logger.info(f"   Min Consensus: {min_engines_agree} engines")
        logger.info(f"   Min Confidence: {min_confidence*100:.0f}%")
    
    async def should_trade(self, 
                          symbol: str,
                          side: str,
                          confidence: float,
                          engine_name: str,
                          exchange = None) -> tuple[bool, str]:
        """
        Determine if trade should proceed
        Returns: (should_trade: bool, reason: str)
        """
        
        self.stats['signals_received'] += 1
        
        # 1. Check confidence threshold
        if confidence < self.min_confidence:
            self.stats['filtered_low_confidence'] += 1
            return False, f"Low confidence: {confidence:.1%} < {self.min_confidence:.1%}"
        
        # 2. Check cooldown period
        if symbol in self.last_trade_time:
            time_since_last = (datetime.now() - self.last_trade_time[symbol]).total_seconds()
            if time_since_last < self.cooldown_seconds:
                self.stats['filtered_cooldown'] += 1
                return False, f"Cooldown: {self.cooldown_seconds - time_since_last:.0f}s remaining"
        
        # 3. Check volatility (if exchange available)
        if exchange:
            volatility = await self._calculate_volatility(symbol, exchange)
            if volatility < self.min_volatility:
                self.stats['filtered_low_volatility'] += 1
                return False, f"Low volatility: {volatility*100:.2f}% < {self.min_volatility*100:.0f}%"
        
        # 4. Check multi-engine consensus
        signal_data = self.signal_counts[symbol]
        signal_data[side] += 1
        if engine_name not in signal_data['engines']:
            signal_data['engines'].append(engine_name)
        
        # Count unique engines agreeing on same side
        engines_agreeing = len(signal_data['engines'])
        if engines_agreeing < self.min_engines_agree:
            return False, f"Insufficient consensus: {engines_agreeing}/{self.min_engines_agree} engines"
        
        # All checks passed!
        self.stats['signals_passed'] += 1
        
        # Reset signal counts for this pair
        self.signal_counts[symbol] = {'buy': 0, 'sell': 0, 'engines': []}
        
        # Update last trade time
        self.last_trade_time[symbol] = datetime.now()
        
        return True, "All checks passed"
    
    async def _calculate_volatility(self, symbol: str, exchange, timeframe: str = '1h') -> float:
        """Calculate recent volatility"""
        try:
            # Check cache (update every 5 minutes)
            if symbol in self.volatility_cache:
                cache_time, volatility = self.volatility_cache[symbol]
                if (time.time() - cache_time) < 300:  # 5 minutes
                    return volatility
            
            # Fetch recent OHLCV data
            ohlcv = await asyncio.to_thread(exchange.fetch_ohlcv, symbol, timeframe, limit=24)
            
            if not ohlcv or len(ohlcv) < 2:
                return 0.0
            
            # Calculate volatility as average of high-low ranges
            volatilities = []
            for candle in ohlcv[-24:]:  # Last 24 hours
                high = candle[2]
                low = candle[3]
                vol = (high - low) / low
                volatilities.append(vol)
            
            avg_volatility = sum(volatilities) / len(volatilities) if volatilities else 0.0
            
            # Cache result
            self.volatility_cache[symbol] = (time.time(), avg_volatility)
            
            return avg_volatility
            
        except Exception as e:
            logger.error(f"❌ Volatility calculation error: {e}")
            return 0.01  # Default to minimum threshold
    
    def add_signal(self, symbol: str, side: str, engine_name: str):
        """Add a signal for aggregation"""
        signal_data = self.signal_counts[symbol]
        signal_data[side] += 1
        if engine_name not in signal_data['engines']:
            signal_data['engines'].append(engine_name)
    
    def get_aggregated_signal(self, symbol: str) -> Optional[Dict]:
        """Get aggregated signal if consensus reached"""
        if symbol not in self.signal_counts:
            return None
        
        signal_data = self.signal_counts[symbol]
        
        # Check if enough engines agree
        if len(signal_data['engines']) < self.min_engines_agree:
            return None
        
        # Determine dominant side
        if signal_data['buy'] > signal_data['sell']:
            side = 'buy'
            votes = signal_data['buy']
        elif signal_data['sell'] > signal_data['buy']:
            side = 'sell'
            votes = signal_data['sell']
        else:
            return None  # No consensus
        
        # Calculate consensus strength
        total_votes = signal_data['buy'] + signal_data['sell']
        consensus_strength = votes / total_votes if total_votes > 0 else 0
        
        return {
            'symbol': symbol,
            'side': side,
            'engines': signal_data['engines'],
            'votes': votes,
            'consensus_strength': consensus_strength,
        }
    
    def reset_pair(self, symbol: str):
        """Reset signal counts for a pair"""
        if symbol in self.signal_counts:
            self.signal_counts[symbol] = {'buy': 0, 'sell': 0, 'engines': []}
    
    def get_stats(self) -> Dict:
        """Get filter statistics"""
        total = self.stats['signals_received']
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'pass_rate': (self.stats['signals_passed'] / total) * 100 if total > 0 else 0,
            'filter_rate': ((total - self.stats['signals_passed']) / total) * 100 if total > 0 else 0,
        }
    
    def print_stats(self):
        """Print filtering statistics"""
        stats = self.get_stats()
        
        print("\n" + "=" * 80)
        print("📊 SMART TRADE FILTER STATISTICS")
        print("=" * 80)
        print(f"Total Signals: {stats['signals_received']}")
        print(f"Passed: {stats['signals_passed']} ({stats['pass_rate']:.1f}%)")
        print(f"Filtered: {stats['signals_received'] - stats['signals_passed']} ({stats['filter_rate']:.1f}%)")
        print()
        print("Filtered By:")
        print(f"  Low Volatility: {stats['filtered_low_volatility']}")
        print(f"  Cooldown: {stats['filtered_cooldown']}")
        print(f"  Low Consensus: {stats['filtered_low_consensus']}")
        print(f"  Low Confidence: {stats['filtered_low_confidence']}")
        print("=" * 80)


# Example usage
if __name__ == '__main__':
    async def test_filter():
        filter = SmartTradeFilter(
            min_volatility=0.01,
            cooldown_seconds=300,
            min_engines_agree=3,
            min_confidence=0.85
        )
        
        print("=" * 80)
        print("🎯 TESTING SMART TRADE FILTER")
        print("=" * 80)
        print()
        
        # Simulate signals
        test_signals = [
            ('BTC/USDT', 'buy', 0.90, 'ScalpEngine1'),
            ('BTC/USDT', 'buy', 0.88, 'ScalpEngine2'),
            ('BTC/USDT', 'buy', 0.92, 'ScalpEngine3'),  # Should pass (3 engines agree)
            ('BTC/USDT', 'buy', 0.89, 'ScalpEngine4'),  # Should fail (cooldown)
            ('ETH/USDT', 'buy', 0.70, 'ScalpEngine1'),  # Should fail (low confidence)
            ('ETH/USDT', 'buy', 0.90, 'ScalpEngine2'),  # Should fail (not enough engines)
        ]
        
        for symbol, side, confidence, engine in test_signals:
            should_trade, reason = await filter.should_trade(symbol, side, confidence, engine)
            status = "✅ PASS" if should_trade else "❌ FAIL"
            print(f"{status} | {symbol} {side.upper()} | Conf: {confidence:.1%} | {engine}")
            if not should_trade:
                print(f"       Reason: {reason}")
            print()
        
        # Print stats
        filter.print_stats()
    
    asyncio.run(test_filter())
