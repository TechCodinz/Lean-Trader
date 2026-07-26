#!/usr/bin/env python3
"""
💧 LIQUIDITY ENGINE 💧

Market-maker level liquidity management!

Calculates:
- Order book depth
- Spread costs
- Market impact (Almgren-Chriss model)
- Liquidity scores
- Safe position sizes

TRADES LIKE A $100B MARKET MAKER!
"""

import logging
import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LiquiditySnapshot:
    """Complete liquidity snapshot"""
    bid: float
    ask: float
    bid_volume: float
    ask_volume: float
    depth_1pct: float  # Volume within 1% of mid
    adv_24h: float  # Average daily volume
    spread_pct: float  # Spread as %
    liquidity_score: float  # Overall score (0-100)
    timestamp: datetime


class LiquidityEngine:
    """
    LIQUIDITY MANAGEMENT SYSTEM
    
    Features:
    - Real-time order book analysis
    - Market impact prediction (Almgren-Chriss)
    - Liquidity scoring
    - Safe size calculation
    - Slippage estimation
    
    PROFESSIONAL MARKET MAKING!
    """
    
    def __init__(self, impact_factor: float = 0.1):
        """
        Initialize liquidity engine
        
        Args:
            impact_factor: Almgren constant for impact calculation
        """
        self.impact_factor = impact_factor
        
        # Historical data
        self.liquidity_history = {}  # {symbol: [LiquiditySnapshot]}
        self.slippage_history = {}   # {symbol: [actual_slippage]}
        
        logger.info("💧 LIQUIDITY ENGINE initialized!")
        logger.info(f"   Impact factor: {impact_factor}")
    
    async def fetch_orderbook(self, exchange, symbol: str, depth: int = 20) -> Dict:
        """
        Fetch order book from exchange
        
        Args:
            exchange: Exchange instance
            symbol: Trading pair
            depth: Number of levels
        
        Returns:
            Order book dict
        """
        try:
            orderbook = await exchange.fetch_order_book(symbol, limit=depth)
            return orderbook
        except Exception as e:
            logger.debug(f"Orderbook fetch failed for {symbol}: {e}")
            return {}
    
    def calculate_liquidity(self, orderbook: Dict, adv_24h: float, 
                           current_price: float) -> LiquiditySnapshot:
        """
        Calculate comprehensive liquidity metrics
        
        Args:
            orderbook: Order book data
            adv_24h: Average daily volume (24h)
            current_price: Current market price
        
        Returns:
            Complete liquidity snapshot
        """
        if not orderbook or 'bids' not in orderbook or 'asks' not in orderbook:
            # Return empty snapshot
            return LiquiditySnapshot(
                bid=current_price,
                ask=current_price,
                bid_volume=0,
                ask_volume=0,
                depth_1pct=0,
                adv_24h=adv_24h,
                spread_pct=100.0,
                liquidity_score=0.0,
                timestamp=datetime.now()
            )
        
        # Extract bids and asks
        bids = orderbook.get('bids', [])[:10]
        asks = orderbook.get('asks', [])[:10]
        
        if not bids or not asks:
            return LiquiditySnapshot(
                current_price, current_price, 0, 0, 0, adv_24h, 100, 0, datetime.now()
            )
        
        # Best bid/ask
        bid_price, bid_volume = bids[0]
        ask_price, ask_volume = asks[0]
        
        # Mid price
        mid_price = (bid_price + ask_price) / 2
        
        # Spread
        spread_pct = ((ask_price - bid_price) / mid_price) * 100 if mid_price > 0 else 100
        
        # Depth within 1% of mid
        depth_1pct = 0
        for price, volume in bids:
            if (mid_price - price) / mid_price <= 0.01:
                depth_1pct += volume * price  # USD value
        
        for price, volume in asks:
            if (price - mid_price) / mid_price <= 0.01:
                depth_1pct += volume * price
        
        # Liquidity score (0-100)
        # High score = tight spread + deep book
        if spread_pct > 0:
            liquidity_score = min(100, (1 / (spread_pct / 100)) * (depth_1pct / 10000))
        else:
            liquidity_score = 100
        
        snapshot = LiquiditySnapshot(
            bid=bid_price,
            ask=ask_price,
            bid_volume=bid_volume,
            ask_volume=ask_volume,
            depth_1pct=depth_1pct,
            adv_24h=adv_24h,
            spread_pct=spread_pct,
            liquidity_score=liquidity_score,
            timestamp=datetime.now()
        )
        
        # Store history
        if symbol not in self.liquidity_history:
            self.liquidity_history[symbol] = []
        self.liquidity_history[symbol].append(snapshot)
        
        # Keep last 100
        if len(self.liquidity_history[symbol]) > 100:
            self.liquidity_history[symbol].pop(0)
        
        return snapshot
    
    def expected_impact_cost(self, size_usd: float, adv_24h: float, 
                            volatility_pct: float) -> float:
        """
        Calculate expected market impact using Almgren-Chriss model
        
        Impact = impact_factor × volatility × sqrt(size / ADV)
        
        Args:
            size_usd: Order size in USD
            adv_24h: Average daily volume
            volatility_pct: Daily volatility %
        
        Returns:
            Expected impact as % of price
        """
        if adv_24h == 0:
            return 1.0  # 100% impact if no liquidity!
        
        sigma = volatility_pct / 100  # Convert to decimal
        impact = self.impact_factor * sigma * np.sqrt(size_usd / adv_24h)
        
        return float(impact)
    
    def max_safe_size(self, liquidity: LiquiditySnapshot, 
                     risk_budget_pct: float = 0.01) -> float:
        """
        Calculate maximum safe order size
        
        Uses min of:
        - 1% depth
        - risk_budget % of ADV
        
        Args:
            liquidity: Liquidity snapshot
            risk_budget_pct: Max % of ADV to trade (1% default)
        
        Returns:
            Max safe size in USD
        """
        max_from_depth = liquidity.depth_1pct
        max_from_adv = liquidity.adv_24h * risk_budget_pct
        
        max_size = min(max_from_depth, max_from_adv)
        
        return float(max_size)
    
    def should_use_twap(self, size_usd: float, liquidity: LiquiditySnapshot) -> bool:
        """
        Determine if order should use TWAP
        
        Large orders (>50% of depth) should use TWAP
        """
        if liquidity.depth_1pct == 0:
            return True  # No liquidity, use TWAP
        
        size_vs_depth = size_usd / liquidity.depth_1pct
        
        # Use TWAP if order is >50% of depth
        return size_vs_depth > 0.5


# Singleton
_liquidity_engine = None

def get_liquidity_engine():
    """Get liquidity engine"""
    return _liquidity_engine

def initialize_liquidity_engine(impact_factor=0.1):
    """Initialize liquidity engine"""
    global _liquidity_engine
    _liquidity_engine = LiquidityEngine(impact_factor)
    return _liquidity_engine
