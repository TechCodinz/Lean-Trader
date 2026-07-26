#!/usr/bin/env python3
"""
WEBSOCKET DATA FEED - Real-time market data
10-100x faster than REST API polling
"""

import asyncio
import json
import logging
from typing import Dict, List, Callable, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)

try:
    import ccxt.pro as ccxtpro
    CCXT_PRO_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  ccxt.pro not available - install with: pip install ccxt[async]")
    CCXT_PRO_AVAILABLE = False


class WebSocketDataFeed:
    """
    Real-time WebSocket data feed for multiple exchanges
    Provides millisecond-latency market data
    """
    
    def __init__(self, exchanges: Dict[str, any] = None):
        self.exchanges = exchanges or {}
        self.subscribers = {
            'ticker': {},
            'trades': {},
            'orderbook': {},
            'ohlcv': {},
        }
        self.running = False
        self.data_cache = {
            'tickers': {},
            'orderbooks': {},
            'trades': {},
        }
        
        logger.info("🌐 WebSocket Data Feed initialized")
    
    async def connect_exchange_websocket(self, exchange_name: str, api_key: str = None, secret: str = None):
        """Connect to exchange WebSocket"""
        try:
            if not CCXT_PRO_AVAILABLE:
                logger.warning(f"⚠️  ccxt.pro not available for {exchange_name}")
                return False
            
            # Initialize ccxt.pro exchange
            exchange_class = getattr(ccxtpro, exchange_name)
            config = {
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            }
            
            if api_key and secret:
                config['apiKey'] = api_key
                config['secret'] = secret
            
            exchange = exchange_class(config)
            self.exchanges[exchange_name] = exchange
            
            logger.info(f"✅ WebSocket connected: {exchange_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed for {exchange_name}: {e}")
            return False
    
    def subscribe_ticker(self, symbol: str, callback: Callable):
        """Subscribe to real-time ticker updates"""
        if symbol not in self.subscribers['ticker']:
            self.subscribers['ticker'][symbol] = []
        self.subscribers['ticker'][symbol].append(callback)
        logger.info(f"📊 Subscribed to ticker: {symbol}")
    
    def subscribe_orderbook(self, symbol: str, callback: Callable):
        """Subscribe to real-time orderbook updates"""
        if symbol not in self.subscribers['orderbook']:
            self.subscribers['orderbook'][symbol] = []
        self.subscribers['orderbook'][symbol].append(callback)
        logger.info(f"📖 Subscribed to orderbook: {symbol}")
    
    def subscribe_trades(self, symbol: str, callback: Callable):
        """Subscribe to real-time trade stream"""
        if symbol not in self.subscribers['trades']:
            self.subscribers['trades'][symbol] = []
        self.subscribers['trades'][symbol].append(callback)
        logger.info(f"💹 Subscribed to trades: {symbol}")
    
    async def watch_ticker(self, exchange_name: str, symbol: str):
        """Watch ticker updates via WebSocket"""
        if exchange_name not in self.exchanges:
            logger.warning(f"⚠️  Exchange {exchange_name} not connected")
            return
        
        exchange = self.exchanges[exchange_name]
        
        try:
            while self.running:
                ticker = await exchange.watch_ticker(symbol)
                
                # Update cache
                self.data_cache['tickers'][symbol] = {
                    'symbol': symbol,
                    'bid': ticker.get('bid'),
                    'ask': ticker.get('ask'),
                    'last': ticker.get('last'),
                    'volume': ticker.get('baseVolume'),
                    'timestamp': ticker.get('timestamp'),
                    'datetime': ticker.get('datetime'),
                }
                
                # Notify subscribers
                if symbol in self.subscribers['ticker']:
                    for callback in self.subscribers['ticker'][symbol]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(self.data_cache['tickers'][symbol])
                            else:
                                callback(self.data_cache['tickers'][symbol])
                        except Exception as e:
                            logger.error(f"❌ Ticker callback error: {e}")
                
        except Exception as e:
            logger.error(f"❌ Watch ticker error for {symbol}: {e}")
    
    async def watch_orderbook(self, exchange_name: str, symbol: str):
        """Watch orderbook updates via WebSocket"""
        if exchange_name not in self.exchanges:
            logger.warning(f"⚠️  Exchange {exchange_name} not connected")
            return
        
        exchange = self.exchanges[exchange_name]
        
        try:
            while self.running:
                orderbook = await exchange.watch_order_book(symbol)
                
                # Update cache
                self.data_cache['orderbooks'][symbol] = {
                    'symbol': symbol,
                    'bids': orderbook['bids'][:10],  # Top 10 bids
                    'asks': orderbook['asks'][:10],  # Top 10 asks
                    'timestamp': orderbook.get('timestamp'),
                    'datetime': orderbook.get('datetime'),
                }
                
                # Notify subscribers
                if symbol in self.subscribers['orderbook']:
                    for callback in self.subscribers['orderbook'][symbol]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(self.data_cache['orderbooks'][symbol])
                            else:
                                callback(self.data_cache['orderbooks'][symbol])
                        except Exception as e:
                            logger.error(f"❌ Orderbook callback error: {e}")
                
        except Exception as e:
            logger.error(f"❌ Watch orderbook error for {symbol}: {e}")
    
    async def watch_trades(self, exchange_name: str, symbol: str):
        """Watch trade stream via WebSocket"""
        if exchange_name not in self.exchanges:
            logger.warning(f"⚠️  Exchange {exchange_name} not connected")
            return
        
        exchange = self.exchanges[exchange_name]
        
        try:
            while self.running:
                trades = await exchange.watch_trades(symbol)
                
                # Process recent trades
                if trades:
                    latest_trade = trades[-1]
                    trade_data = {
                        'symbol': symbol,
                        'price': latest_trade.get('price'),
                        'amount': latest_trade.get('amount'),
                        'side': latest_trade.get('side'),
                        'timestamp': latest_trade.get('timestamp'),
                        'datetime': latest_trade.get('datetime'),
                    }
                    
                    # Update cache
                    if symbol not in self.data_cache['trades']:
                        self.data_cache['trades'][symbol] = []
                    self.data_cache['trades'][symbol].append(trade_data)
                    # Keep last 100 trades
                    self.data_cache['trades'][symbol] = self.data_cache['trades'][symbol][-100:]
                    
                    # Notify subscribers
                    if symbol in self.subscribers['trades']:
                        for callback in self.subscribers['trades'][symbol]:
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(trade_data)
                                else:
                                    callback(trade_data)
                            except Exception as e:
                                logger.error(f"❌ Trade callback error: {e}")
                
        except Exception as e:
            logger.error(f"❌ Watch trades error for {symbol}: {e}")
    
    def get_latest_ticker(self, symbol: str) -> Optional[Dict]:
        """Get latest cached ticker data"""
        return self.data_cache['tickers'].get(symbol)
    
    def get_latest_orderbook(self, symbol: str) -> Optional[Dict]:
        """Get latest cached orderbook"""
        return self.data_cache['orderbooks'].get(symbol)
    
    def get_recent_trades(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get recent trades"""
        trades = self.data_cache['trades'].get(symbol, [])
        return trades[-limit:]
    
    async def start(self, pairs: List[str], exchange_name: str = 'binance'):
        """Start WebSocket feeds for given pairs"""
        self.running = True
        
        logger.info(f"🚀 Starting WebSocket feeds for {len(pairs)} pairs on {exchange_name}")
        
        tasks = []
        for pair in pairs:
            # Watch ticker
            tasks.append(asyncio.create_task(self.watch_ticker(exchange_name, pair)))
            # Watch orderbook
            tasks.append(asyncio.create_task(self.watch_orderbook(exchange_name, pair)))
            # Watch trades
            tasks.append(asyncio.create_task(self.watch_trades(exchange_name, pair)))
        
        logger.info(f"✅ {len(tasks)} WebSocket streams started")
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
    
    async def stop(self):
        """Stop all WebSocket feeds"""
        self.running = False
        
        for exchange in self.exchanges.values():
            try:
                await exchange.close()
            except:
                pass
        
        logger.info("🛑 WebSocket feeds stopped")


# Fallback: Simulated WebSocket using REST API (for exchanges without WebSocket)
class SimulatedWebSocket:
    """
    Simulates WebSocket behavior using fast REST API polling
    Used when ccxt.pro is not available
    """
    
    def __init__(self, exchange):
        self.exchange = exchange
        self.subscribers = {'ticker': {}}
        self.running = False
        logger.info("⚡ Simulated WebSocket initialized (REST polling)")
    
    def subscribe_ticker(self, symbol: str, callback: Callable):
        """Subscribe to ticker updates"""
        if symbol not in self.subscribers['ticker']:
            self.subscribers['ticker'][symbol] = []
        self.subscribers['ticker'][symbol].append(callback)
    
    async def watch_ticker(self, symbol: str, interval: float = 1.0):
        """Simulate watching ticker with fast polling"""
        while self.running:
            try:
                ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
                
                ticker_data = {
                    'symbol': symbol,
                    'bid': ticker.get('bid'),
                    'ask': ticker.get('ask'),
                    'last': ticker.get('last'),
                    'volume': ticker.get('baseVolume'),
                    'timestamp': ticker.get('timestamp'),
                }
                
                # Notify subscribers
                if symbol in self.subscribers['ticker']:
                    for callback in self.subscribers['ticker'][symbol]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(ticker_data)
                            else:
                                callback(ticker_data)
                        except Exception as e:
                            logger.error(f"❌ Simulated ticker callback error: {e}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Simulated ticker error: {e}")
                await asyncio.sleep(interval * 2)
    
    async def start(self, pairs: List[str]):
        """Start simulated feeds"""
        self.running = True
        logger.info(f"⚡ Starting simulated WebSocket for {len(pairs)} pairs")
        
        tasks = []
        for pair in pairs:
            tasks.append(asyncio.create_task(self.watch_ticker(pair, interval=1.0)))
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """Stop simulated feeds"""
        self.running = False


# Example usage
if __name__ == '__main__':
    async def on_ticker_update(ticker):
        print(f"📊 {ticker['symbol']}: ${ticker['last']:.2f} | Bid: ${ticker['bid']:.2f} | Ask: ${ticker['ask']:.2f}")
    
    async def main():
        ws = WebSocketDataFeed()
        
        # Connect to exchange
        await ws.connect_exchange_websocket('binance')
        
        # Subscribe to tickers
        ws.subscribe_ticker('BTC/USDT', on_ticker_update)
        ws.subscribe_ticker('ETH/USDT', on_ticker_update)
        
        # Start feeds
        await ws.start(['BTC/USDT', 'ETH/USDT'], 'binance')
    
    print("=" * 80)
    print("🌐 WEBSOCKET DATA FEED TEST")
    print("=" * 80)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
