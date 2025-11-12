#!/usr/bin/env python3
"""
📊 MARKET DATA INTELLIGENCE SYSTEM 📊

Gets LIVE market data for ALL pairs from ALL sources:
- Live charts (1m, 5m, 15m, 1h, 4h, 1d)
- Order book data (depth, liquidity)
- Recent trades (volume, price action)
- Market trends (momentum, volatility)
- Price action patterns
- Volume profiles

AUTONOMOUS DATA GATHERING - The bot's EYES on the market!
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


class MarketDataIntelligence:
    """
    The bot's MARKET AWARENESS system
    
    Continuously gathers:
    - Live OHLCV data (all timeframes)
    - Order book snapshots
    - Recent trades
    - Market trends
    - Price patterns
    - Volume analysis
    
    FEEDS ALL OTHER SYSTEMS!
    """
    
    def __init__(self, exchanges: Dict[str, Any]):
        """
        Initialize with all available exchanges
        
        Args:
            exchanges: Dict of {'exchange_name': exchange_instance}
        """
        self.exchanges = exchanges
        
        # Market data cache
        self.ohlcv_data = defaultdict(lambda: defaultdict(dict))  # {exchange: {symbol: {tf: data}}}
        self.orderbook_data = defaultdict(dict)  # {exchange: {symbol: orderbook}}
        self.recent_trades = defaultdict(dict)  # {exchange: {symbol: trades}}
        self.market_trends = defaultdict(dict)  # {exchange: {symbol: trend_data}}
        
        # Update tracking
        self.last_ohlcv_update = {}
        self.last_orderbook_update = {}
        self.last_trade_update = {}
        
        # Supported timeframes (from fastest to slowest)
        self.timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        
        # Update intervals (seconds)
        self.update_intervals = {
            '1m': 10,   # Update every 10 seconds
            '5m': 30,   # Every 30 seconds
            '15m': 60,  # Every minute
            '1h': 300,  # Every 5 minutes
            '4h': 900,  # Every 15 minutes
            '1d': 3600  # Every hour
        }
        
        logger.info("📊 MARKET DATA INTELLIGENCE initialized!")
        logger.info(f"   Monitoring {len(exchanges)} exchanges")
        logger.info(f"   Timeframes: {', '.join(self.timeframes)}")
    
    async def start_continuous_data_gathering(self, pairs: List[str]):
        """
        Start CONTINUOUS data gathering for all pairs
        
        This runs forever, constantly updating market data!
        """
        logger.info(f"📊 Starting CONTINUOUS data gathering for {len(pairs)} pairs...")
        
        # Start parallel data gathering tasks
        tasks = []
        
        # OHLCV gathering (all timeframes)
        for tf in self.timeframes:
            tasks.append(self._continuous_ohlcv_updater(pairs, tf))
        
        # Order book gathering
        tasks.append(self._continuous_orderbook_updater(pairs))
        
        # Recent trades gathering
        tasks.append(self._continuous_trades_updater(pairs))
        
        # Trend analysis
        tasks.append(self._continuous_trend_analyzer(pairs))
        
        logger.info(f"📊 Launched {len(tasks)} continuous data gathering tasks!")
        
        # Run all tasks forever
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _continuous_ohlcv_updater(self, pairs: List[str], timeframe: str):
        """Continuously update OHLCV data for timeframe"""
        interval = self.update_intervals[timeframe]
        
        logger.info(f"📊 OHLCV updater started: {timeframe} (every {interval}s)")
        
        while True:
            try:
                # Update OHLCV for all pairs on all exchanges
                for exchange_name, exchange in self.exchanges.items():
                    for symbol in pairs:
                        try:
                            # Fetch OHLCV
                            ohlcv = await asyncio.to_thread(
                                exchange.fetch_ohlcv,
                                symbol,
                                timeframe,
                                limit=100
                            )
                            
                            if ohlcv:
                                self.ohlcv_data[exchange_name][symbol][timeframe] = ohlcv
                                self.last_ohlcv_update[f"{exchange_name}_{symbol}_{timeframe}"] = datetime.now()
                        
                        except Exception as e:
                            # Silently skip unavailable pairs
                            pass
                
                # Wait for next update
                await asyncio.sleep(interval)
            
            except Exception as e:
                logger.error(f"OHLCV updater error ({timeframe}): {e}")
                await asyncio.sleep(interval)
    
    async def _continuous_orderbook_updater(self, pairs: List[str]):
        """Continuously update order book data"""
        logger.info(f"📊 Order book updater started (every 5s)")
        
        while True:
            try:
                for exchange_name, exchange in self.exchanges.items():
                    for symbol in pairs:
                        try:
                            # Fetch order book
                            orderbook = await asyncio.to_thread(
                                exchange.fetch_order_book,
                                symbol,
                                limit=20
                            )
                            
                            if orderbook:
                                # Analyze order book
                                analyzed = self._analyze_orderbook(orderbook)
                                self.orderbook_data[exchange_name][symbol] = analyzed
                                self.last_orderbook_update[f"{exchange_name}_{symbol}"] = datetime.now()
                        
                        except Exception as e:
                            pass
                
                await asyncio.sleep(5)  # Update every 5 seconds
            
            except Exception as e:
                logger.error(f"Order book updater error: {e}")
                await asyncio.sleep(5)
    
    async def _continuous_trades_updater(self, pairs: List[str]):
        """Continuously update recent trades"""
        logger.info(f"📊 Trades updater started (every 10s)")
        
        while True:
            try:
                for exchange_name, exchange in self.exchanges.items():
                    for symbol in pairs:
                        try:
                            # Fetch recent trades
                            trades = await asyncio.to_thread(
                                exchange.fetch_trades,
                                symbol,
                                limit=50
                            )
                            
                            if trades:
                                # Analyze trades
                                analyzed = self._analyze_trades(trades)
                                self.recent_trades[exchange_name][symbol] = analyzed
                                self.last_trade_update[f"{exchange_name}_{symbol}"] = datetime.now()
                        
                        except Exception as e:
                            pass
                
                await asyncio.sleep(10)  # Update every 10 seconds
            
            except Exception as e:
                logger.error(f"Trades updater error: {e}")
                await asyncio.sleep(10)
    
    async def _continuous_trend_analyzer(self, pairs: List[str]):
        """Continuously analyze market trends"""
        logger.info(f"📊 Trend analyzer started (every 30s)")
        
        while True:
            try:
                for exchange_name in self.exchanges.keys():
                    for symbol in pairs:
                        # Analyze trends from OHLCV data
                        trend = self._analyze_market_trend(exchange_name, symbol)
                        if trend:
                            self.market_trends[exchange_name][symbol] = trend
                
                await asyncio.sleep(30)  # Analyze every 30 seconds
            
            except Exception as e:
                logger.error(f"Trend analyzer error: {e}")
                await asyncio.sleep(30)
    
    def _analyze_orderbook(self, orderbook: Dict) -> Dict:
        """Analyze order book for insights"""
        try:
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if not bids or not asks:
                return {}
            
            # Calculate metrics
            best_bid = bids[0][0] if bids else 0
            best_ask = asks[0][0] if asks else 0
            spread = best_ask - best_bid if best_bid and best_ask else 0
            spread_pct = (spread / best_ask) * 100 if best_ask else 0
            
            # Total bid/ask volume
            bid_volume = sum(bid[1] for bid in bids[:10])
            ask_volume = sum(ask[1] for ask in asks[:10])
            
            # Buy/sell pressure
            total_volume = bid_volume + ask_volume
            buy_pressure = (bid_volume / total_volume) * 100 if total_volume else 50
            
            return {
                'best_bid': best_bid,
                'best_ask': best_ask,
                'spread': spread,
                'spread_pct': spread_pct,
                'bid_volume': bid_volume,
                'ask_volume': ask_volume,
                'buy_pressure': buy_pressure,
                'sell_pressure': 100 - buy_pressure,
                'liquidity_score': min(100, (total_volume / 1000) * 100),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Order book analysis error: {e}")
            return {}
    
    def _analyze_trades(self, trades: List[Dict]) -> Dict:
        """Analyze recent trades for insights"""
        try:
            if not trades:
                return {}
            
            # Separate buy/sell trades
            buy_trades = [t for t in trades if t.get('side') == 'buy']
            sell_trades = [t for t in trades if t.get('side') == 'sell']
            
            # Calculate volumes
            buy_volume = sum(t.get('amount', 0) for t in buy_trades)
            sell_volume = sum(t.get('amount', 0) for t in sell_trades)
            total_volume = buy_volume + sell_volume
            
            # Buy/sell ratio
            buy_ratio = (buy_volume / total_volume) * 100 if total_volume else 50
            
            # Average trade size
            avg_trade_size = total_volume / len(trades) if trades else 0
            
            # Price movement
            first_price = trades[0].get('price', 0)
            last_price = trades[-1].get('price', 0)
            price_change = ((last_price - first_price) / first_price) * 100 if first_price else 0
            
            return {
                'total_trades': len(trades),
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'buy_ratio': buy_ratio,
                'avg_trade_size': avg_trade_size,
                'price_change': price_change,
                'momentum': 'bullish' if buy_ratio > 55 else 'bearish' if buy_ratio < 45 else 'neutral',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Trades analysis error: {e}")
            return {}
    
    def _analyze_market_trend(self, exchange_name: str, symbol: str) -> Dict:
        """Analyze market trend from OHLCV data"""
        try:
            # Get 5m and 1h data for trend analysis
            ohlcv_5m = self.ohlcv_data.get(exchange_name, {}).get(symbol, {}).get('5m', [])
            ohlcv_1h = self.ohlcv_data.get(exchange_name, {}).get(symbol, {}).get('1h', [])
            
            if not ohlcv_5m or len(ohlcv_5m) < 20:
                return {}
            
            # Extract closes
            closes = np.array([candle[4] for candle in ohlcv_5m[-50:]])
            
            if len(closes) < 20:
                return {}
            
            # Calculate trend indicators
            sma_20 = np.mean(closes[-20:])
            sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else sma_20
            current_price = closes[-1]
            
            # Volatility
            returns = np.diff(closes) / closes[:-1]
            volatility = np.std(returns) * 100
            
            # Momentum
            momentum_5 = ((closes[-1] - closes[-5]) / closes[-5]) * 100 if len(closes) >= 5 else 0
            momentum_20 = ((closes[-1] - closes[-20]) / closes[-20]) * 100
            
            # Determine trend
            if current_price > sma_20 and sma_20 > sma_50:
                trend = 'strong_uptrend'
            elif current_price > sma_20:
                trend = 'uptrend'
            elif current_price < sma_20 and sma_20 < sma_50:
                trend = 'strong_downtrend'
            elif current_price < sma_20:
                trend = 'downtrend'
            else:
                trend = 'sideways'
            
            return {
                'trend': trend,
                'current_price': float(current_price),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'volatility': float(volatility),
                'momentum_5': float(momentum_5),
                'momentum_20': float(momentum_20),
                'strength': abs(momentum_20),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {}
    
    def get_live_chart_data(self, exchange_name: str, symbol: str, timeframe: str) -> Optional[List]:
        """Get live chart data for pair"""
        return self.ohlcv_data.get(exchange_name, {}).get(symbol, {}).get(timeframe)
    
    def get_market_summary(self, exchange_name: str, symbol: str) -> Dict:
        """
        Get complete market summary for pair
        
        Returns all available data: OHLCV, orderbook, trades, trends
        """
        summary = {
            'exchange': exchange_name,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
        
        # OHLCV data (all timeframes)
        ohlcv_all = {}
        for tf in self.timeframes:
            data = self.ohlcv_data.get(exchange_name, {}).get(symbol, {}).get(tf)
            if data:
                ohlcv_all[tf] = {
                    'candles': len(data),
                    'latest_close': data[-1][4] if data else 0,
                    'latest_volume': data[-1][5] if data else 0
                }
        summary['ohlcv'] = ohlcv_all
        
        # Order book
        orderbook = self.orderbook_data.get(exchange_name, {}).get(symbol)
        if orderbook:
            summary['orderbook'] = orderbook
        
        # Recent trades
        trades = self.recent_trades.get(exchange_name, {}).get(symbol)
        if trades:
            summary['trades'] = trades
        
        # Trend analysis
        trend = self.market_trends.get(exchange_name, {}).get(symbol)
        if trend:
            summary['trend'] = trend
        
        return summary
    
    def get_all_market_summaries(self) -> Dict[str, Dict]:
        """Get summaries for ALL pairs on ALL exchanges"""
        summaries = {}
        
        for exchange_name in self.exchanges.keys():
            for symbol in self.ohlcv_data.get(exchange_name, {}).keys():
                key = f"{exchange_name}:{symbol}"
                summaries[key] = self.get_market_summary(exchange_name, symbol)
        
        return summaries
    
    def get_system_health(self) -> Dict:
        """Get health status of data gathering system"""
        now = datetime.now()
        
        # Count active data streams
        active_ohlcv = len([k for k, v in self.last_ohlcv_update.items() 
                           if (now - v).seconds < 300])
        active_orderbooks = len([k for k, v in self.last_orderbook_update.items() 
                                if (now - v).seconds < 60])
        active_trades = len([k for k, v in self.last_trade_update.items() 
                           if (now - v).seconds < 120])
        
        total_pairs = len(set(
            symbol for exchange_data in self.ohlcv_data.values() 
            for symbol in exchange_data.keys()
        ))
        
        return {
            'status': 'healthy' if active_ohlcv > 0 else 'degraded',
            'total_pairs_monitored': total_pairs,
            'active_ohlcv_streams': active_ohlcv,
            'active_orderbook_streams': active_orderbooks,
            'active_trade_streams': active_trades,
            'total_data_points': (
                sum(len(tf_data) for ex_data in self.ohlcv_data.values() 
                    for sym_data in ex_data.values() 
                    for tf_data in sym_data.values())
            ),
            'last_check': now.isoformat()
        }


# Singleton
_market_data_intelligence = None

def get_market_data_intelligence():
    """Get market data intelligence instance"""
    return _market_data_intelligence

def initialize_market_data_intelligence(exchanges: Dict[str, Any]):
    """Initialize market data intelligence"""
    global _market_data_intelligence
    _market_data_intelligence = MarketDataIntelligence(exchanges)
    return _market_data_intelligence
