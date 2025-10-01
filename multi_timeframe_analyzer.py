#!/usr/bin/env python3
"""
Multi-Timeframe Analyzer - Actually combines multiple timeframes intelligently
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class MultiTimeframeAnalyzer:
    """Analyzes multiple timeframes to get better trading signals"""
    
    def __init__(self):
        self.timeframe_weights = {
            '1m': 0.1,   # Noise filter
            '5m': 0.15,  # Entry timing
            '15m': 0.2,  # Short-term trend
            '1h': 0.25,  # Main trend
            '4h': 0.2,   # Major trend
            '1d': 0.1    # Overall direction
        }
        
    async def analyze_all_timeframes(self, exchange, symbol: str) -> Dict:
        """Analyze symbol across multiple timeframes"""
        
        analyses = {}
        
        for timeframe in self.timeframe_weights.keys():
            try:
                # Fetch data for each timeframe
                ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=100)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # Analyze this timeframe
                analysis = self.analyze_timeframe(df, timeframe)
                analyses[timeframe] = analysis
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol} {timeframe}: {e}")
                
        # Combine all timeframe signals
        combined_signal = self.combine_timeframe_signals(analyses)
        
        return combined_signal
        
    def analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """Analyze a single timeframe"""
        
        if len(df) < 20:
            return {'signal': 'NEUTRAL', 'strength': 0}
            
        # Calculate trend
        sma20 = df['close'].rolling(20).mean().iloc[-1]
        sma50 = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else sma20
        current_price = df['close'].iloc[-1]
        
        # Determine signal
        if current_price > sma20 > sma50:
            signal = 'BUY'
            strength = (current_price - sma20) / sma20
        elif current_price < sma20 < sma50:
            signal = 'SELL'
            strength = (sma20 - current_price) / sma20
        else:
            signal = 'NEUTRAL'
            strength = 0
            
        # Calculate momentum
        momentum = (df['close'].iloc[-1] - df['close'].iloc[-10]) / df['close'].iloc[-10]
        
        # Volume confirmation
        volume_ratio = df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1]
        
        return {
            'timeframe': timeframe,
            'signal': signal,
            'strength': min(abs(strength), 1.0),
            'momentum': momentum,
            'volume_confirmation': volume_ratio > 1.2,
            'price': current_price,
            'sma20': sma20
        }
        
    def combine_timeframe_signals(self, analyses: Dict) -> Dict:
        """Intelligently combine signals from all timeframes"""
        
        if not analyses:
            return {'signal': 'HOLD', 'confidence': 0}
            
        buy_score = 0
        sell_score = 0
        total_weight = 0
        
        # Weight each timeframe's signal
        for timeframe, analysis in analyses.items():
            weight = self.timeframe_weights.get(timeframe, 0.1)
            
            if analysis['signal'] == 'BUY':
                buy_score += weight * analysis['strength']
            elif analysis['signal'] == 'SELL':
                sell_score += weight * analysis['strength']
                
            total_weight += weight
            
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
            
        # Determine final signal
        if buy_score > sell_score and buy_score > 0.3:
            signal = 'BUY'
            confidence = buy_score
        elif sell_score > buy_score and sell_score > 0.3:
            signal = 'SELL'
            confidence = sell_score
        else:
            signal = 'HOLD'
            confidence = 0.5
            
        # Check for alignment
        aligned_timeframes = sum(1 for a in analyses.values() if a['signal'] == signal)
        alignment_score = aligned_timeframes / len(analyses)
        
        return {
            'signal': signal,
            'confidence': confidence,
            'alignment': alignment_score,
            'buy_score': buy_score,
            'sell_score': sell_score,
            'timeframe_signals': {tf: a['signal'] for tf, a in analyses.items()},
            'details': analyses
        }