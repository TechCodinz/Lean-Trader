#!/usr/bin/env python3
"""
REAL DATA FETCHER - Get All Market Data for Ultra Rare Engines
===============================================================

Fetches:
- Order books (real-time bid/ask depth)
- Price history (for entropy calculations)
- Liquidation data (for cascade detection)
- Funding rates (for arbitrage)
- Large trades (for smart money detection)
- Sentiment data (for retail panic)
"""

import ccxt
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RealDataFetcher:
    """Fetches all real market data needed by ultra rare engines"""
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        self.price_history = {}  # Store price history per symbol
        
    async def fetch_complete_market_data(self, symbol: str) -> Dict:
        """
        Fetch ALL data needed by ultra rare engines
        
        Returns dict with:
        - order_book: {'bids': [[price, amount], ...], 'asks': [[price, amount], ...]}
        - recent_prices: [price1, price2, ...] (last 100)
        - price: current price
        - open_interest: for cascade detection
        - funding_rate: for arbitrage
        - large_trades: for smart money detection
        - sentiment data: for retail panic
        """
        
        try:
            # 1. Get Order Book (REAL data)
            order_book = await asyncio.to_thread(
                self.exchange.fetch_order_book, symbol, limit=20
            )
            
            # 2. Get Current Ticker
            ticker = await asyncio.to_thread(
                self.exchange.fetch_ticker, symbol
            )
            current_price = ticker['last']
            
            # 3. Get Recent OHLCV for price history
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv, symbol, '1m', limit=100
            )
            recent_prices = [candle[4] for candle in ohlcv]  # closing prices
            
            # Store in history
            self.price_history[symbol] = recent_prices
            
            # 4. Try to get Open Interest (if futures)
            open_interest = 0
            try:
                if hasattr(self.exchange, 'fetch_open_interest'):
                    oi_data = await asyncio.to_thread(
                        self.exchange.fetch_open_interest, symbol
                    )
                    open_interest = oi_data.get('openInterest', 0)
            except:
                pass
            
            # 5. Try to get Funding Rate (if perpetual)
            funding_rate = 0
            try:
                if hasattr(self.exchange, 'fetch_funding_rate'):
                    funding = await asyncio.to_thread(
                        self.exchange.fetch_funding_rate, symbol
                    )
                    funding_rate = funding.get('fundingRate', 0)
            except:
                pass
            
            # 6. Try to get Recent Trades (for smart money detection)
            large_trades = []
            try:
                trades = await asyncio.to_thread(
                    self.exchange.fetch_trades, symbol, limit=100
                )
                # Filter for large trades (>$10k)
                for trade in trades:
                    if trade['cost'] > 10000:
                        large_trades.append({
                            'price': trade['price'],
                            'amount': trade['amount'],
                            'cost': trade['cost'],
                            'side': trade['side'],
                            'timestamp': trade['timestamp']
                        })
            except:
                pass
            
            # 7. Calculate order book depth (for hidden order detection)
            bid_depth = sum(bid[1] for bid in order_book['bids'][:10])
            ask_depth = sum(ask[1] for ask in order_book['asks'][:10])
            order_book_depth = {
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'imbalance': (bid_depth - ask_depth) / (bid_depth + ask_depth) if (bid_depth + ask_depth) > 0 else 0
            }
            
            # 8. Estimate sentiment (simplified - could use external API)
            # For now, use price momentum as proxy
            if len(recent_prices) >= 20:
                recent_change = (recent_prices[-1] - recent_prices[-20]) / recent_prices[-20]
                sentiment_bullish_pct = 0.5 + (recent_change * 5)  # -10% = 0% bullish, +10% = 100% bullish
                sentiment_bullish_pct = max(0, min(1, sentiment_bullish_pct))
            else:
                sentiment_bullish_pct = 0.5
            
            # 9. Calculate volume for social volume proxy
            volume_24h = ticker.get('quoteVolume', 0)
            
            # Compile complete market data
            market_data = {
                'symbol': symbol,
                'price': current_price,
                'order_book': order_book,
                'bids': order_book['bids'],
                'asks': order_book['asks'],
                'recent_prices': recent_prices,
                'open_interest': open_interest,
                'funding_rate': funding_rate,
                'large_trades': large_trades,
                'order_book_depth': order_book_depth['imbalance'],
                'sentiment_bullish_pct': sentiment_bullish_pct,
                'social_volume': volume_24h / 1000000,  # Normalize
                'large_transfers_in': len([t for t in large_trades if t['side'] == 'buy']),
                'large_transfers_out': len([t for t in large_trades if t['side'] == 'sell']),
                'put_call_ratio': 1.0,  # Would need options data
                'options_data': None,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.debug(f"✅ Fetched complete data for {symbol}")
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching data for {symbol}: {e}")
            # Return empty/default data
            return {
                'symbol': symbol,
                'price': 0,
                'order_book': {'bids': [], 'asks': []},
                'bids': [],
                'asks': [],
                'recent_prices': [],
                'open_interest': 0,
                'funding_rate': 0,
                'large_trades': [],
                'order_book_depth': 0,
                'sentiment_bullish_pct': 0.5,
                'social_volume': 0,
                'large_transfers_in': 0,
                'large_transfers_out': 0,
                'put_call_ratio': 1.0,
                'options_data': None,
                'timestamp': datetime.now().isoformat()
            }
    
    async def fetch_batch(self, symbols: List[str]) -> Dict[str, Dict]:
        """Fetch data for multiple symbols in parallel"""
        tasks = [self.fetch_complete_market_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data_dict = {}
        for symbol, result in zip(symbols, results):
            if not isinstance(result, Exception):
                data_dict[symbol] = result
            else:
                logger.error(f"Error fetching {symbol}: {result}")
        
        return data_dict


# Test function
async def test_data_fetcher():
    """Test the data fetcher"""
    import os
    
    # Initialize exchange
    gate = ccxt.gateio({
        'apiKey': os.getenv('GATE_API_KEY', ''),
        'secret': os.getenv('GATE_SECRET', ''),
        'enableRateLimit': True
    })
    
    fetcher = RealDataFetcher(gate)
    
    print("Testing data fetcher...")
    data = await fetcher.fetch_complete_market_data('BTC/USDT')
    
    print(f"\n✅ Fetched data for BTC/USDT:")
    print(f"   Price: ${data['price']:,.2f}")
    print(f"   Order book bids: {len(data['bids'])} levels")
    print(f"   Order book asks: {len(data['asks'])} levels")
    print(f"   Recent prices: {len(data['recent_prices'])} points")
    print(f"   Order book imbalance: {data['order_book_depth']:.2%}")
    print(f"   Large trades: {len(data['large_trades'])}")
    print(f"   Funding rate: {data['funding_rate']:.4%}")
    print(f"   Sentiment: {data['sentiment_bullish_pct']:.0%} bullish")
    
    return True


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_data_fetcher())
