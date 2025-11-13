#!/usr/bin/env python3
"""
📊 TRANSACTION COST ANALYSIS (TCA) ENGINE 📊

Professional execution analysis like Citadel!

Measures:
- Realized spread (cost vs mid)
- Slippage (cost vs expected)
- Impact cost (moved market)
- Timing cost (vs VWAP)
- Total transaction costs

PROFESSIONAL EXECUTION QUALITY!
"""

import logging
import numpy as np
from typing import Dict
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TCABreakdown:
    """Complete TCA breakdown"""
    realized_spread_bps: float
    slippage_bps: float
    impact_cost_bps: float
    timing_cost_bps: float
    total_cost_bps: float
    vwap_improvement: float
    timestamp: datetime


class TCAEngine:
    """
    TRANSACTION COST ANALYSIS
    
    Analyzes every trade:
    - Pre-trade: Snapshot mid price, VWAP
    - Post-trade: Calculate all cost components
    - Report: Detailed cost breakdown
    - Learn: Optimize future executions
    
    PROFESSIONAL EXECUTION ANALYTICS!
    """
    
    def __init__(self):
        # Pre-trade snapshots
        self.pre_trade_mid = {}  # {symbol: mid_price}
        self.vwap_reference = {}  # {symbol: vwap}
        
        # TCA history
        self.tca_history = []  # List of TCABreakdown
        self.avg_costs_bps = 0.0
        
        logger.info("📊 TCA ENGINE initialized!")
    
    def pre_trade_snapshot(self, symbol: str, orderbook: Dict):
        """
        Take pre-trade snapshot
        
        Args:
            symbol: Trading pair
            orderbook: Current order book
        """
        if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
            return
        
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        
        if not bids or not asks:
            return
        
        # Mid price
        mid = (bids[0][0] + asks[0][0]) / 2
        self.pre_trade_mid[symbol] = mid
        
        # VWAP reference
        vwap = self.calculate_vwap(orderbook, depth=5)
        self.vwap_reference[symbol] = vwap
        
        logger.debug(f"📸 Pre-trade snapshot: {symbol}")
        logger.debug(f"   Mid: ${mid:.6f}")
        logger.debug(f"   VWAP: ${vwap:.6f}")
    
    def post_trade_analysis(self, symbol: str, exec_price: float, 
                           size: float, side: str, orderbook: Dict) -> TCABreakdown:
        """
        Analyze execution quality
        
        Returns complete cost breakdown in basis points
        """
        # Get pre-trade references
        pre_mid = self.pre_trade_mid.get(symbol, exec_price)
        pre_vwap = self.vwap_reference.get(symbol, exec_price)
        
        # Post-trade mid
        if orderbook and 'bids' in orderbook and 'asks' in orderbook:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            if bids and asks:
                post_mid = (bids[0][0] + asks[0][0]) / 2
            else:
                post_mid = exec_price
        else:
            post_mid = exec_price
        
        # Calculate costs in basis points (1 bp = 0.01%)
        
        # 1. Realized Spread (paid spread)
        realized_spread_bps = abs(exec_price - pre_mid) / pre_mid * 10000
        
        # 2. Slippage (vs mid)
        slippage = (exec_price - pre_mid) / pre_mid
        if side == 'sell':
            slippage = -slippage
        slippage_bps = slippage * 10000
        
        # 3. Impact Cost (moved market)
        impact_bps = abs(post_mid - pre_mid) / pre_mid * 10000
        
        # 4. Timing Cost (vs VWAP)
        timing_bps = (exec_price - pre_vwap) / pre_vwap * 10000 if pre_vwap > 0 else 0
        
        # 5. Total Cost
        total_bps = realized_spread_bps + abs(slippage_bps) + impact_bps + abs(timing_bps)
        
        # 6. VWAP Improvement (negative = better than VWAP)
        vwap_improvement = (pre_vwap - exec_price) / pre_vwap * 10000 if pre_vwap > 0 else 0
        
        tca = TCABreakdown(
            realized_spread_bps=float(realized_spread_bps),
            slippage_bps=float(slippage_bps),
            impact_cost_bps=float(impact_bps),
            timing_cost_bps=float(timing_bps),
            total_cost_bps=float(total_bps),
            vwap_improvement=float(vwap_improvement),
            timestamp=datetime.now()
        )
        
        # Store history
        self.tca_history.append(tca)
        
        # Keep last 1000
        if len(self.tca_history) > 1000:
            self.tca_history.pop(0)
        
        # Update average
        self.avg_costs_bps = np.mean([t.total_cost_bps for t in self.tca_history[-100:]])
        
        # Log if significant
        if total_bps > 5.0:  # >5 bps is notable
            logger.warning(f"⚠️ High TCA: {symbol} = {total_bps:.1f} bps")
        elif total_bps < 1.0:  # <1 bp is excellent
            logger.info(f"✅ Excellent execution: {symbol} = {total_bps:.1f} bps")
        
        return tca
    
    def calculate_vwap(self, orderbook: Dict, depth: int = 5) -> float:
        """Calculate Volume-Weighted Average Price"""
        if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
            return 0.0
        
        bids = orderbook.get('bids', [])[:depth]
        asks = orderbook.get('asks', [])[:depth]
        
        if not bids and not asks:
            return 0.0
        
        total_volume = sum(v for _, v in bids) + sum(v for _, v in asks)
        
        if total_volume == 0:
            return 0.0
        
        vwap = (sum(p * v for p, v in bids) + sum(p * v for p, v in asks)) / total_volume
        
        return float(vwap)
    
    def get_performance_stats(self) -> Dict:
        """Get TCA performance statistics"""
        if not self.tca_history:
            return {'avg_cost_bps': 0, 'total_trades': 0}
        
        return {
            'avg_cost_bps': self.avg_costs_bps,
            'total_trades': len(self.tca_history),
            'best_execution_bps': min(t.total_cost_bps for t in self.tca_history),
            'worst_execution_bps': max(t.total_cost_bps for t in self.tca_history),
            'avg_slippage_bps': np.mean([t.slippage_bps for t in self.tca_history]),
            'avg_impact_bps': np.mean([t.impact_cost_bps for t in self.tca_history])
        }


# Singleton
_tca_engine = None

def get_tca_engine():
    """Get TCA engine"""
    return _tca_engine

def initialize_tca_engine():
    """Initialize TCA engine"""
    global _tca_engine
    _tca_engine = TCAEngine()
    return _tca_engine
