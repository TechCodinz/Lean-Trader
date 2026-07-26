#!/usr/bin/env python3
"""
PHASE 7.5: EXECUTION HOT PATH

Fast-track execution for:
- Scalping trades
- Arbitrage opportunities  
- Momentum breakouts

Bypasses non-essential logging while preserving safety checks
"""

from typing import Dict, Any
import logging
import time

logger = logging.getLogger(__name__)

class ExecutionHotPath:
    """
    Phase 7.5: Ultra-fast execution path for time-sensitive trades
    
    Hot path criteria:
    - Scalping (quick in/out)
    - Arbitrage (price discrepancies)
    - Momentum breakouts (fast moves)
    
    Bypasses:
    - Verbose logging
    - Non-essential analysis
    - Attribution tracking (done post-trade)
    
    Preserves:
    - Balance checks
    - Market existence checks
    - Error handling
    """
    
    def __init__(self):
        self.hot_path_count = 0
        self.normal_path_count = 0
        self.latency_samples = []
        
    def is_hot_path_eligible(self, signal: Dict[str, Any]) -> bool:
        """
        Determine if signal qualifies for hot path
        
        Hot path trades:
        - Scalping (timeframe 1m, 5m)
        - Arbitrage (strategy contains 'arb')
        - Momentum breakouts (high confidence + breakout strategy)
        """
        strategy = str(signal.get('strategy', '')).lower()
        timeframe = str(signal.get('timeframe', '')).lower()
        confidence = signal.get('confidence', 0)
        
        # Arbitrage - always hot path
        if 'arb' in strategy:
            return True
        
        # Scalping - 1m/5m timeframes
        if timeframe in ['1m', '5m'] and 'scalp' in strategy:
            return True
        
        # Momentum breakouts - high confidence
        if 'momentum' in strategy or 'breakout' in strategy:
            if confidence > 0.7:
                return True
        
        # Flash trades
        if 'flash' in strategy or 'instant' in strategy:
            return True
        
        return False
    
    async def execute_hot_path(self, signal: Dict, exchange, balance: float):
        """
        HOT PATH: Minimal latency execution
        
        Flow:
        1. Quick validation (balance, market)
        2. Execute immediately
        3. Log post-trade (async)
        
        Returns: (success: bool, trade_id: str)
        """
        start_time = time.time()
        self.hot_path_count += 1
        
        symbol = signal.get('symbol') or signal.get('pair')
        side = signal.get('side', signal.get('direction', 'BUY'))
        size = signal.get('size', 5.0)
        
        # FAST VALIDATION (no verbose logging)
        # 1. Balance check
        if size > balance:
            return False, None
        
        # 2. Market exists (minimal check)
        try:
            ticker = await exchange.fetch_ticker(symbol)
            if not ticker or not ticker.get('last'):
                return False, None
        except:
            return False, None
        
        # HOT PATH EXECUTION
        try:
            # Direct market order (fastest execution)
            order = await exchange.create_market_order(
                symbol=symbol,
                side=side.lower(),
                amount=size / ticker['last'] if side.lower() == 'buy' else size
            )
            
            trade_id = order.get('id')
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            self.latency_samples.append(latency_ms)
            
            # Minimal success log (async later)
            logger.info(f"⚡ HOT PATH: {symbol} {side} ${size:.2f} [{latency_ms:.0f}ms]")
            
            return True, trade_id
            
        except Exception as e:
            # Minimal error log
            logger.error(f"⚡ HOT PATH FAIL: {symbol} - {e}")
            return False, None
    
    def get_metrics(self):
        """Get hot path performance metrics"""
        if not self.latency_samples:
            return {}
        
        return {
            'hot_path_count': self.hot_path_count,
            'normal_path_count': self.normal_path_count,
            'hot_path_ratio': self.hot_path_count / (self.hot_path_count + self.normal_path_count) if (self.hot_path_count + self.normal_path_count) > 0 else 0,
            'avg_latency_ms': sum(self.latency_samples) / len(self.latency_samples),
            'min_latency_ms': min(self.latency_samples),
            'max_latency_ms': max(self.latency_samples),
            'total_hot_trades': self.hot_path_count
        }
    
    def save_metrics(self, filepath='/root/bot/logs/hot_path_latency_metrics.json'):
        """Save metrics to file"""
        import json
        try:
            metrics = self.get_metrics()
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"📊 Hot path metrics saved: {filepath}")
        except Exception as e:
            logger.warning(f"Could not save hot path metrics: {e}")
