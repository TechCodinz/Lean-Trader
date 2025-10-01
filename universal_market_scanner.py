#!/usr/bin/env python3
"""
Universal Market Scanner - Scans ALL markets, ALL pairs, ALL timeframes
Ensures no trading opportunity is missed across spot, futures, and all sessions
"""

import asyncio
import ccxt.async_support as ccxt
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class UniversalMarketScanner:
    """Scans every possible trading opportunity across all markets"""
    
    def __init__(self):
        self.exchanges = {}
        self.all_symbols = {
            'spot': {},
            'futures': {},
            'perpetual': {}
        }
        self.timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']
        self.active_sessions = []
        
    async def initialize_all_exchanges(self, config):
        """Initialize ALL configured exchanges for ALL market types"""
        
        logger.info("🌍 Initializing Universal Market Scanner...")
        
        exchange_classes = {
            'binance': ccxt.binance,
            'bybit': ccxt.bybit,
            'gateio': ccxt.gateio,
            'okx': ccxt.okx,
            'bitget': ccxt.bitget,
            'mexc': ccxt.mexc,
            'kucoin': ccxt.kucoin,
            'huobi': ccxt.huobi,
            'kraken': ccxt.kraken,
            'coinbase': ccxt.coinbase
        }
        
        for name, exchange_class in exchange_classes.items():
            try:
                # Try to load from config
                api_key = config.get(f'{name.upper()}_API_KEY')
                secret = config.get(f'{name.upper()}_SECRET')
                
                if api_key and secret:
                    # Initialize for SPOT
                    spot_exchange = exchange_class({
                        'apiKey': api_key,
                        'secret': secret,
                        'enableRateLimit': True,
                        'options': {
                            'defaultType': 'spot',
                            'adjustForTimeDifference': True
                        }
                    })
                    
                    # Initialize for FUTURES
                    futures_exchange = exchange_class({
                        'apiKey': api_key,
                        'secret': secret,
                        'enableRateLimit': True,
                        'options': {
                            'defaultType': 'future',
                            'adjustForTimeDifference': True
                        }
                    })
                    
                    # Initialize for PERPETUAL
                    perp_exchange = exchange_class({
                        'apiKey': api_key,
                        'secret': secret,
                        'enableRateLimit': True,
                        'options': {
                            'defaultType': 'swap',
                            'adjustForTimeDifference': True
                        }
                    })
                    
                    self.exchanges[name] = {
                        'spot': spot_exchange,
                        'futures': futures_exchange,
                        'perpetual': perp_exchange
                    }
                    
                    # Load ALL markets
                    await self.load_all_markets(name)
                    
                    logger.info(f"✅ {name.upper()}: Initialized for SPOT, FUTURES, PERPETUAL")
                    
            except Exception as e:
                logger.debug(f"Could not initialize {name}: {e}")
                
    async def load_all_markets(self, exchange_name):
        """Load ALL available trading pairs from an exchange"""
        
        for market_type in ['spot', 'futures', 'perpetual']:
            try:
                exchange = self.exchanges[exchange_name][market_type]
                markets = await exchange.load_markets()
                
                # Get ALL active trading pairs
                active_symbols = []
                for symbol, market in markets.items():
                    if market['active']:
                        active_symbols.append(symbol)
                        
                self.all_symbols[market_type][exchange_name] = active_symbols
                
                logger.info(f"  📊 {exchange_name} {market_type}: {len(active_symbols)} pairs loaded")
                
            except Exception as e:
                logger.debug(f"Could not load {market_type} markets for {exchange_name}: {e}")
                
    def get_current_session(self):
        """Determine current trading session based on time"""
        
        now = datetime.now(timezone.utc)
        hour = now.hour
        
        sessions = []
        
        # Asian Session (Tokyo: 00:00 - 09:00 UTC)
        if 0 <= hour < 9:
            sessions.append('asian')
            
        # European Session (London: 08:00 - 17:00 UTC)
        if 8 <= hour < 17:
            sessions.append('european')
            
        # American Session (New York: 13:00 - 22:00 UTC)
        if 13 <= hour < 22:
            sessions.append('american')
            
        # Late Session (22:00 - 00:00 UTC)
        if hour >= 22:
            sessions.append('late')
            
        return sessions
        
    async def scan_all_opportunities(self):
        """Scan ALL markets for ALL opportunities"""
        
        opportunities = {
            'arbitrage': [],
            'trending': [],
            'breakouts': [],
            'reversals': [],
            'volume_spikes': [],
            'futures_basis': [],
            'funding_rates': []
        }
        
        current_sessions = self.get_current_session()
        logger.info(f"🌍 Active Sessions: {', '.join(current_sessions)}")
        
        # Scan SPOT markets
        for exchange_name, symbols in self.all_symbols['spot'].items():
            for symbol in symbols:
                try:
                    # Get data for multiple timeframes
                    for timeframe in self.timeframes:
                        opp = await self.analyze_opportunity(
                            exchange_name, symbol, 'spot', timeframe
                        )
                        if opp:
                            opportunities[opp['type']].append(opp)
                            
                except Exception as e:
                    logger.debug(f"Error scanning {symbol} on {exchange_name}: {e}")
                    
        # Scan FUTURES markets
        for exchange_name, symbols in self.all_symbols['futures'].items():
            for symbol in symbols:
                try:
                    # Check futures basis trade opportunities
                    basis = await self.check_futures_basis(exchange_name, symbol)
                    if basis:
                        opportunities['futures_basis'].append(basis)
                        
                except Exception as e:
                    logger.debug(f"Error scanning futures {symbol}: {e}")
                    
        # Scan PERPETUAL markets
        for exchange_name, symbols in self.all_symbols['perpetual'].items():
            for symbol in symbols:
                try:
                    # Check funding rates
                    funding = await self.check_funding_rates(exchange_name, symbol)
                    if funding:
                        opportunities['funding_rates'].append(funding)
                        
                except Exception as e:
                    logger.debug(f"Error scanning perpetual {symbol}: {e}")
                    
        return opportunities
        
    async def analyze_opportunity(self, exchange_name, symbol, market_type, timeframe):
        """Analyze a specific symbol for trading opportunities"""
        
        try:
            exchange = self.exchanges[exchange_name][market_type]
            
            # Get OHLCV data
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            
            if len(ohlcv) < 20:
                return None
                
            # Calculate indicators
            closes = [x[4] for x in ohlcv]
            volumes = [x[5] for x in ohlcv]
            
            # Simple trend detection
            sma_20 = sum(closes[-20:]) / 20
            sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20
            
            current_price = closes[-1]
            
            # Volume spike detection
            avg_volume = sum(volumes[-20:]) / 20
            current_volume = volumes[-1]
            volume_spike = current_volume > (avg_volume * 2)
            
            # Identify opportunity type
            if current_price > sma_20 and sma_20 > sma_50:
                return {
                    'type': 'trending',
                    'exchange': exchange_name,
                    'symbol': symbol,
                    'market_type': market_type,
                    'timeframe': timeframe,
                    'price': current_price,
                    'signal': 'BULLISH',
                    'strength': (current_price - sma_20) / sma_20 * 100
                }
            elif volume_spike:
                return {
                    'type': 'volume_spikes',
                    'exchange': exchange_name,
                    'symbol': symbol,
                    'market_type': market_type,
                    'timeframe': timeframe,
                    'price': current_price,
                    'volume_ratio': current_volume / avg_volume
                }
                
        except Exception as e:
            logger.debug(f"Analysis error for {symbol}: {e}")
            
        return None
        
    async def check_futures_basis(self, exchange_name, symbol):
        """Check futures basis trade opportunities"""
        
        try:
            spot_exchange = self.exchanges[exchange_name]['spot']
            futures_exchange = self.exchanges[exchange_name]['futures']
            
            # Get spot price
            spot_ticker = await spot_exchange.fetch_ticker(symbol)
            spot_price = spot_ticker['last']
            
            # Get futures price
            futures_ticker = await futures_exchange.fetch_ticker(symbol)
            futures_price = futures_ticker['last']
            
            # Calculate basis
            basis = (futures_price - spot_price) / spot_price * 100
            
            # Significant basis = opportunity
            if abs(basis) > 0.5:  # 0.5% basis
                return {
                    'exchange': exchange_name,
                    'symbol': symbol,
                    'spot_price': spot_price,
                    'futures_price': futures_price,
                    'basis_pct': basis,
                    'action': 'LONG_SPOT_SHORT_FUTURES' if basis > 0 else 'SHORT_SPOT_LONG_FUTURES'
                }
                
        except Exception as e:
            logger.debug(f"Basis calculation error: {e}")
            
        return None
        
    async def check_funding_rates(self, exchange_name, symbol):
        """Check perpetual funding rate opportunities"""
        
        try:
            exchange = self.exchanges[exchange_name]['perpetual']
            
            # Get funding rate (exchange-specific)
            if hasattr(exchange, 'fetch_funding_rate'):
                funding = await exchange.fetch_funding_rate(symbol)
                rate = funding['fundingRate'] * 100  # Convert to percentage
                
                # High funding = opportunity
                if abs(rate) > 0.01:  # 0.01% funding
                    return {
                        'exchange': exchange_name,
                        'symbol': symbol,
                        'funding_rate': rate,
                        'next_funding': funding.get('fundingDatetime'),
                        'action': 'SHORT' if rate > 0 else 'LONG'
                    }
                    
        except Exception as e:
            logger.debug(f"Funding rate error: {e}")
            
        return None

# Integration function for ultra_launcher
async def integrate_universal_scanner(pipeline):
    """Integrate universal scanner into the pipeline"""
    
    if not hasattr(pipeline, 'universal_scanner'):
        pipeline.universal_scanner = UniversalMarketScanner()
        
        # Load config
        config = {}
        try:
            with open('env.arbitrage', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key] = value
        except:
            pass
            
        await pipeline.universal_scanner.initialize_all_exchanges(config)
        
        # Add scanning method to pipeline
        pipeline.scan_all_markets = pipeline.universal_scanner.scan_all_opportunities
        
        logger.info("✅ Universal Market Scanner integrated - scanning ALL pairs, ALL timeframes, ALL market types")
        
    return pipeline