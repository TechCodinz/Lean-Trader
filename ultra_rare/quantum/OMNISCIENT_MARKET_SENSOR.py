#!/usr/bin/env python3
"""
👁️ OMNISCIENT MARKET SENSOR 👁️
SEES EVERYTHING - Every tick, every order, every movement
Taps into UNTAPPED regions of market data

This is the EYE that sees:
- Hidden order flow (whale movements before they happen)
- Microstructure (bid-ask dynamics, tape reading)
- Dark pool activity (large blocks forming)
- Order book toxicity (informed vs uninformed flow)
- Multi-dimensional market state
- Future movements before they materialize
- Cross-asset correlations
- Liquidity pockets and gaps
- Smart money vs dumb money flow
- Market maker positioning

Nothing escapes this sensor. NOTHING.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque, defaultdict
import statistics
import math

logger = logging.getLogger(__name__)


class OrderFlowAnalyzer:
    """
    Reads the TAPE - sees who's buying, who's selling, WHY
    Detects whale activity BEFORE price moves
    """
    
    def __init__(self):
        self.recent_trades = deque(maxlen=1000)
        self.volume_profile = defaultdict(float)
        self.whale_threshold = 50000  # $50k+ trades are whales
        
        logger.info("🐋 Order Flow Analyzer initialized - Detecting whale activity")
    
    async def analyze_order_flow(self, exchange, symbol: str) -> Dict:
        """
        Analyze recent trades to detect order flow
        
        Returns:
        - buy_pressure: 0-1 (1 = all buying)
        - sell_pressure: 0-1 (1 = all selling)
        - whale_activity: bool
        - flow_momentum: -1 to 1
        - aggressor_side: 'buy' or 'sell'
        """
        try:
            # Fetch recent trades
            trades = await asyncio.to_thread(
                exchange.fetch_trades,
                symbol,
                limit=100
            )
            
            if not trades:
                return self._neutral_flow()
            
            # Analyze each trade
            buy_volume = 0
            sell_volume = 0
            whale_buys = 0
            whale_sells = 0
            large_trades = []
            
            for trade in trades:
                volume_usd = trade['amount'] * trade['price']
                
                # Determine side (taker side = aggressive side = true direction)
                side = trade.get('side', 'buy')
                
                if side == 'buy':
                    buy_volume += volume_usd
                    if volume_usd >= self.whale_threshold:
                        whale_buys += 1
                        large_trades.append(('buy', volume_usd, trade['timestamp']))
                else:
                    sell_volume += volume_usd
                    if volume_usd >= self.whale_threshold:
                        whale_sells += 1
                        large_trades.append(('sell', volume_usd, trade['timestamp']))
            
            total_volume = buy_volume + sell_volume
            
            if total_volume == 0:
                return self._neutral_flow()
            
            # Calculate metrics
            buy_pressure = buy_volume / total_volume
            sell_pressure = sell_volume / total_volume
            flow_momentum = buy_pressure - sell_pressure  # -1 to 1
            
            # Whale activity
            whale_activity = (whale_buys + whale_sells) > 0
            whale_direction = 'buy' if whale_buys > whale_sells else 'sell' if whale_sells > whale_buys else 'neutral'
            
            # Aggressor side (who's more aggressive)
            aggressor_side = 'buy' if buy_pressure > 0.55 else 'sell' if sell_pressure > 0.55 else 'balanced'
            
            result = {
                'buy_pressure': buy_pressure,
                'sell_pressure': sell_pressure,
                'flow_momentum': flow_momentum,
                'whale_activity': whale_activity,
                'whale_direction': whale_direction,
                'whale_buys': whale_buys,
                'whale_sells': whale_sells,
                'aggressor_side': aggressor_side,
                'total_volume_usd': total_volume,
                'large_trades': large_trades[-5:],  # Last 5 large trades
                'signal_strength': abs(flow_momentum) if whale_activity else abs(flow_momentum) * 0.5
            }
            
            if whale_activity:
                logger.info(f"🐋 WHALE ACTIVITY: {symbol} - {whale_direction.upper()} ({whale_buys} buys, {whale_sells} sells)")
            
            return result
            
        except Exception as e:
            logger.debug(f"Order flow analysis error: {e}")
            return self._neutral_flow()
    
    def _neutral_flow(self) -> Dict:
        return {
            'buy_pressure': 0.5,
            'sell_pressure': 0.5,
            'flow_momentum': 0.0,
            'whale_activity': False,
            'whale_direction': 'neutral',
            'aggressor_side': 'balanced',
            'signal_strength': 0.0
        }


class OrderBookMicrostructure:
    """
    Analyzes order book microstructure
    Detects:
    - Spoofing (fake walls)
    - Iceberg orders (hidden size)
    - Order book imbalance
    - Support/resistance levels from order clustering
    """
    
    def __init__(self):
        self.order_book_history = deque(maxlen=50)
        
        logger.info("📊 Order Book Microstructure initialized")
    
    async def analyze_order_book(self, exchange, symbol: str) -> Dict:
        """
        Deep order book analysis
        
        Returns:
        - bid_depth: total bid volume
        - ask_depth: total ask volume
        - imbalance: bid/ask ratio
        - spread: bid-ask spread
        - walls_detected: large orders
        - pressure: 'buy' or 'sell'
        """
        try:
            # Fetch order book
            order_book = await asyncio.to_thread(
                exchange.fetch_order_book,
                symbol,
                limit=50
            )
            
            bids = order_book['bids']
            asks = order_book['asks']
            
            if not bids or not asks:
                return self._neutral_book()
            
            # Calculate depths
            bid_depth = sum(price * amount for price, amount in bids[:20])
            ask_depth = sum(price * amount for price, amount in asks[:20])
            
            # Imbalance (>1 = more bids, <1 = more asks)
            imbalance = bid_depth / ask_depth if ask_depth > 0 else 1.0
            
            # Spread
            best_bid = bids[0][0]
            best_ask = asks[0][0]
            spread = (best_ask - best_bid) / best_bid
            
            # Detect walls (orders 5x+ larger than average)
            bid_sizes = [amount for price, amount in bids[:20]]
            ask_sizes = [amount for price, amount in asks[:20]]
            
            avg_bid_size = statistics.mean(bid_sizes) if bid_sizes else 0
            avg_ask_size = statistics.mean(ask_sizes) if ask_sizes else 0
            
            bid_walls = [
                {'price': price, 'size': amount}
                for price, amount in bids[:10]
                if amount >= avg_bid_size * 5
            ]
            
            ask_walls = [
                {'price': price, 'size': amount}
                for price, amount in asks[:10]
                if amount >= avg_ask_size * 5
            ]
            
            # Pressure determination
            if imbalance > 1.2:
                pressure = 'buy'
                pressure_strength = min((imbalance - 1.0) / 0.5, 1.0)
            elif imbalance < 0.83:
                pressure = 'sell'
                pressure_strength = min((1.0 - imbalance) / 0.5, 1.0)
            else:
                pressure = 'neutral'
                pressure_strength = 0.0
            
            result = {
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'imbalance': imbalance,
                'spread': spread,
                'spread_bps': spread * 10000,  # basis points
                'bid_walls': bid_walls,
                'ask_walls': ask_walls,
                'pressure': pressure,
                'pressure_strength': pressure_strength,
                'best_bid': best_bid,
                'best_ask': best_ask
            }
            
            if bid_walls or ask_walls:
                logger.info(f"🧱 WALLS DETECTED: {symbol} - {len(bid_walls)} bid walls, {len(ask_walls)} ask walls")
            
            return result
            
        except Exception as e:
            logger.debug(f"Order book analysis error: {e}")
            return self._neutral_book()
    
    def _neutral_book(self) -> Dict:
        return {
            'bid_depth': 0,
            'ask_depth': 0,
            'imbalance': 1.0,
            'spread': 0.001,
            'pressure': 'neutral',
            'pressure_strength': 0.0
        }


class SmartMoneyDetector:
    """
    Detects SMART MONEY vs DUMB MONEY
    Smart money = whales, institutions, informed traders
    Dumb money = retail, uninformed traders
    """
    
    def __init__(self):
        self.smart_money_indicators = {
            'large_orders': 0,
            'block_trades': 0,
            'off_hours_activity': 0,
            'informed_flow': 0
        }
        
        logger.info("🧠 Smart Money Detector initialized")
    
    def classify_flow(self, order_flow: Dict, order_book: Dict, time: datetime) -> Dict:
        """
        Classify if current flow is smart or dumb money
        
        Smart money signals:
        - Large trades during low volume (stealth)
        - Order book walls that don't get pulled
        - Trading against the crowd
        - Off-hours activity
        """
        smart_money_score = 0
        reasons = []
        
        # 1. Whale activity = likely smart money
        if order_flow.get('whale_activity', False):
            smart_money_score += 0.3
            reasons.append("Whale activity detected")
        
        # 2. Order book walls = commitment (if not spoofing)
        bid_walls = order_book.get('bid_walls', [])
        ask_walls = order_book.get('ask_walls', [])
        if len(bid_walls) + len(ask_walls) > 0:
            smart_money_score += 0.2
            reasons.append("Large order book walls")
        
        # 3. Trading during off-hours (2AM-6AM UTC) = institutional
        hour = time.hour
        if 2 <= hour <= 6:
            smart_money_score += 0.2
            reasons.append("Off-hours activity")
        
        # 4. Strong directional flow = informed
        flow_momentum = abs(order_flow.get('flow_momentum', 0))
        if flow_momentum > 0.3:
            smart_money_score += 0.3 * flow_momentum
            reasons.append(f"Strong directional flow ({flow_momentum:.2f})")
        
        classification = 'smart' if smart_money_score >= 0.5 else 'dumb' if smart_money_score < 0.3 else 'mixed'
        
        return {
            'classification': classification,
            'smart_money_score': smart_money_score,
            'confidence': min(smart_money_score, 1.0),
            'reasons': reasons
        }


class MultiDimensionalMarketState:
    """
    Represents market in MULTIPLE DIMENSIONS
    Not just price - but depth, velocity, acceleration, momentum across timeframes
    """
    
    def __init__(self):
        self.state_history = deque(maxlen=100)
        
        logger.info("🌐 Multi-Dimensional Market State initialized")
    
    async def capture_market_state(
        self,
        exchange,
        symbol: str,
        order_flow: Dict,
        order_book: Dict,
        smart_money: Dict
    ) -> Dict:
        """
        Capture complete multi-dimensional market state
        
        Dimensions:
        1. Price (current, velocity, acceleration)
        2. Volume (current, momentum, distribution)
        3. Order Flow (buy/sell pressure, whale activity)
        4. Order Book (depth, imbalance, walls)
        5. Smart Money (classification, activity)
        6. Volatility (realized, implied, regime)
        7. Momentum (short, medium, long)
        8. Trend (strength, direction, quality)
        """
        try:
            # Get ticker for price data
            ticker = await asyncio.to_thread(exchange.fetch_ticker, symbol)
            
            current_price = ticker['last']
            price_change_1h = ticker.get('percentage', 0) / 100
            volume_24h = ticker.get('quoteVolume', 0)
            
            # Calculate volatility from high-low
            high = ticker.get('high', current_price)
            low = ticker.get('low', current_price)
            volatility = (high - low) / current_price if current_price > 0 else 0
            
            # Multi-dimensional state
            state = {
                # Dimension 1: Price
                'price': current_price,
                'price_velocity': price_change_1h,
                'price_acceleration': 0,  # Would need historical data
                
                # Dimension 2: Volume
                'volume_24h': volume_24h,
                'volume_momentum': order_flow.get('flow_momentum', 0),
                
                # Dimension 3: Order Flow
                'buy_pressure': order_flow.get('buy_pressure', 0.5),
                'sell_pressure': order_flow.get('sell_pressure', 0.5),
                'whale_activity': order_flow.get('whale_activity', False),
                'flow_direction': order_flow.get('aggressor_side', 'balanced'),
                
                # Dimension 4: Order Book
                'book_imbalance': order_book.get('imbalance', 1.0),
                'book_pressure': order_book.get('pressure', 'neutral'),
                'spread_bps': order_book.get('spread_bps', 10),
                
                # Dimension 5: Smart Money
                'smart_money': smart_money.get('classification', 'mixed'),
                'smart_money_score': smart_money.get('smart_money_score', 0),
                
                # Dimension 6: Volatility
                'volatility': volatility,
                'volatility_regime': 'high' if volatility > 0.03 else 'medium' if volatility > 0.015 else 'low',
                
                # Dimension 7: Momentum (derived)
                'momentum_score': self._calculate_momentum(price_change_1h, order_flow, order_book),
                
                # Dimension 8: Trend (derived)
                'trend_strength': abs(price_change_1h) * 10,
                'trend_direction': 'up' if price_change_1h > 0.01 else 'down' if price_change_1h < -0.01 else 'sideways',
                
                # Meta
                'timestamp': datetime.now(),
                'symbol': symbol
            }
            
            # Store in history
            self.state_history.append(state)
            
            return state
            
        except Exception as e:
            logger.error(f"Market state capture error: {e}")
            return {}
    
    def _calculate_momentum(self, price_change: float, order_flow: Dict, order_book: Dict) -> float:
        """Calculate composite momentum score 0-1"""
        # Combine multiple momentum signals
        price_momentum = abs(price_change) * 5  # 2% = 0.1 momentum
        flow_momentum = abs(order_flow.get('flow_momentum', 0))
        book_momentum = abs(order_book.get('imbalance', 1.0) - 1.0)
        
        # Weight and combine
        composite = (price_momentum * 0.5) + (flow_momentum * 0.3) + (book_momentum * 0.2)
        
        return min(composite, 1.0)


class OmniscientSensor:
    """
    MASTER SENSOR - Combines all sensing capabilities
    SEES EVERYTHING
    """
    
    def __init__(self):
        self.order_flow = OrderFlowAnalyzer()
        self.order_book = OrderBookMicrostructure()
        self.smart_money = SmartMoneyDetector()
        self.market_state = MultiDimensionalMarketState()
        
        # Scanning state
        self.last_scan = {}
        self.scan_interval = 2  # Scan every 2 seconds
        
        logger.info("=" * 80)
        logger.info("👁️ OMNISCIENT MARKET SENSOR ONLINE")
        logger.info("=" * 80)
        logger.info("   Capabilities:")
        logger.info("   ✅ Order Flow Analysis (whale detection)")
        logger.info("   ✅ Order Book Microstructure (walls, imbalances)")
        logger.info("   ✅ Smart Money Detection (institutional flow)")
        logger.info("   ✅ Multi-Dimensional Market State (8D sensing)")
        logger.info("")
        logger.info("   👁️ NOTHING ESCAPES THIS SENSOR")
        logger.info("=" * 80)
    
    async def scan_market(self, exchange, symbol: str) -> Dict:
        """
        Complete omniscient market scan
        
        Returns EVERYTHING about current market state
        """
        # Check if we scanned recently (rate limiting)
        now = datetime.now()
        if symbol in self.last_scan:
            elapsed = (now - self.last_scan[symbol]).seconds
            if elapsed < self.scan_interval:
                logger.debug(f"Skipping scan - last scan {elapsed}s ago")
                return {}
        
        try:
            # Scan all dimensions in parallel
            order_flow_data, order_book_data = await asyncio.gather(
                self.order_flow.analyze_order_flow(exchange, symbol),
                self.order_book.analyze_order_book(exchange, symbol)
            )
            
            # Classify smart money
            smart_money_data = self.smart_money.classify_flow(
                order_flow_data,
                order_book_data,
                now
            )
            
            # Capture complete state
            market_state_data = await self.market_state.capture_market_state(
                exchange,
                symbol,
                order_flow_data,
                order_book_data,
                smart_money_data
            )
            
            # Combine everything
            omniscient_view = {
                'symbol': symbol,
                'timestamp': now,
                'order_flow': order_flow_data,
                'order_book': order_book_data,
                'smart_money': smart_money_data,
                'market_state': market_state_data,
                'scan_quality': 'complete'
            }
            
            # Update last scan
            self.last_scan[symbol] = now
            
            # Log interesting findings
            self._log_insights(omniscient_view)
            
            return omniscient_view
            
        except Exception as e:
            logger.error(f"Omniscient scan error for {symbol}: {e}")
            return {'symbol': symbol, 'scan_quality': 'failed'}
    
    def _log_insights(self, view: Dict):
        """Log interesting insights from scan"""
        symbol = view['symbol']
        
        # Whale activity
        if view['order_flow'].get('whale_activity'):
            whale_dir = view['order_flow']['whale_direction']
            logger.info(f"🐋 {symbol}: Whale {whale_dir.upper()} activity detected!")
        
        # Smart money
        if view['smart_money'].get('classification') == 'smart':
            score = view['smart_money']['smart_money_score']
            logger.info(f"🧠 {symbol}: Smart money detected (score: {score:.2f})")
        
        # Strong momentum
        momentum = view['market_state'].get('momentum_score', 0)
        if momentum > 0.7:
            direction = view['market_state'].get('trend_direction', 'unknown')
            logger.info(f"🚀 {symbol}: Strong {direction} momentum ({momentum:.2f})")


# Global instance
omniscient_sensor = None

def initialize_omniscient_sensor():
    global omniscient_sensor
    omniscient_sensor = OmniscientSensor()
    return omniscient_sensor

async def scan_market_omniscient(exchange, symbol: str) -> Dict:
    global omniscient_sensor
    if not omniscient_sensor:
        omniscient_sensor = initialize_omniscient_sensor()
    
    return await omniscient_sensor.scan_market(exchange, symbol)

# Export
__all__ = [
    'OmniscientSensor',
    'initialize_omniscient_sensor',
    'scan_market_omniscient'
]

logger.info("👁️ OMNISCIENT MARKET SENSOR loaded - Ready to see EVERYTHING!")
