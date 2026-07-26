#!/usr/bin/env python3
"""
⏱️ MULTI-TIMEFRAME COORDINATOR ⏱️

Trades ALL timeframes simultaneously:
- 1m: Ultra-fast scalping (0.2-0.5% profits)
- 5m: Fast scalping (0.3-0.8% profits)  
- 15m: Quick swings (0.5-1.5% profits)
- 1h: Swing trades (1-3% profits)
- 4h: Position trades (2-6% profits)

PARALLEL TRADING FOR 5X MORE OPPORTUNITIES!
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MultiTimeframeCoordinator:
    """
    COORDINATES PARALLEL TRADING ACROSS TIMEFRAMES
    
    Features:
    - Each timeframe trades independently
    - 1m for ultra-fast scalps
    - 5m for fast scalps
    - 15m-4h for swings
    - No conflicts (different entry/exit)
    - 5x more opportunities!
    """
    
    def __init__(self):
        # Active timeframes
        self.timeframes = ['1m', '5m', '15m', '1h', '4h']
        
        # Trades per timeframe
        self.active_trades = {tf: [] for tf in self.timeframes}
        
        # Max trades per timeframe
        self.max_per_tf = {
            '1m': 5,   # Up to 5 ultra-fast scalps
            '5m': 10,  # Up to 10 fast scalps
            '15m': 8,  # Up to 8 quick swings
            '1h': 5,   # Up to 5 swings
            '4h': 3    # Up to 3 positions
        }
        
        logger.info("⏱️ MULTI-TIMEFRAME COORDINATOR initialized!")
        logger.info(f"   Active timeframes: {', '.join(self.timeframes)}")
        logger.info(f"   Total capacity: {sum(self.max_per_tf.values())} parallel trades!")
    
    def can_trade_on_timeframe(self, symbol: str, timeframe: str) -> bool:
        """Check if we can open another trade on this timeframe"""
        if timeframe not in self.active_trades:
            return True
        
        # Count active trades on this timeframe for this symbol
        active_count = len([
            t for t in self.active_trades[timeframe] 
            if t['symbol'] == symbol
        ])
        
        max_allowed = self.max_per_tf.get(timeframe, 5)
        
        if active_count >= max_allowed:
            logger.debug(f"   ⏸️ {symbol} on {timeframe}: {active_count}/{max_allowed} trades (limit reached)")
            return False
        
        return True
    
    def get_priority_timeframes(self, signal: Dict) -> List[str]:
        """
        Get priority timeframes for this signal
        
        Returns list ordered by priority
        """
        confidence = signal.get('confidence', 0)
        if confidence > 1:
            confidence = confidence / 100
        
        # High confidence = trade on ALL timeframes!
        if confidence >= 0.80:
            return ['1m', '5m', '15m', '1h']  # Trade 4 timeframes!
        
        # Medium confidence = fast timeframes
        elif confidence >= 0.70:
            return ['1m', '5m', '15m']  # Trade 3 timeframes
        
        # Lower confidence = just 5m
        else:
            return ['5m']
    
    def record_trade(self, symbol: str, timeframe: str, trade_id: str):
        """Record active trade"""
        if timeframe in self.active_trades:
            self.active_trades[timeframe].append({
                'symbol': symbol,
                'trade_id': trade_id,
                'opened_at': datetime.now()
            })
    
    def close_trade(self, symbol: str, timeframe: str, trade_id: str):
        """Remove closed trade"""
        if timeframe in self.active_trades:
            self.active_trades[timeframe] = [
                t for t in self.active_trades[timeframe]
                if t['trade_id'] != trade_id
            ]


# Singleton
_mtf_coordinator = None

def get_mtf_coordinator():
    """Get multi-timeframe coordinator"""
    return _mtf_coordinator

def initialize_mtf_coordinator():
    """Initialize multi-timeframe coordinator"""
    global _mtf_coordinator
    _mtf_coordinator = MultiTimeframeCoordinator()
    return _mtf_coordinator
