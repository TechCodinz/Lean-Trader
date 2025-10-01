#!/usr/bin/env python3
"""
Intelligent Pair Selector - Selects best pairs to trade based on multiple factors
Instead of trading ALL pairs blindly
"""

import asyncio
import logging
from typing import List, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

class IntelligentPairSelector:
    """Selects the best trading pairs based on multiple criteria"""
    
    def __init__(self, balance: float = 48):
        self.balance = balance
        self.min_volume_24h = 100000  # $100k minimum daily volume
        self.max_pairs = self.calculate_max_pairs()
        
    def calculate_max_pairs(self) -> int:
        """Calculate optimal number of pairs based on balance"""
        
        if self.balance < 50:
            return 2  # Focus on 2 pairs
        elif self.balance < 100:
            return 3
        elif self.balance < 500:
            return 5
        elif self.balance < 1000:
            return 8
        else:
            return 10
            
    async def select_best_pairs(self, exchange) -> List[str]:
        """Select the best pairs to trade"""
        
        logger.info(f"🎯 Selecting best pairs for ${self.balance} balance...")
        
        try:
            # Get all markets
            markets = await exchange.load_markets()
            
            # Filter and score pairs
            pair_scores = {}
            
            for symbol, market in markets.items():
                # Basic filters
                if not market['active']:
                    continue
                if not symbol.endswith('/USDT'):
                    continue
                if market['type'] != 'spot':
                    continue
                    
                # Calculate score
                score = await self.score_pair(exchange, symbol, market)
                if score > 0:
                    pair_scores[symbol] = score
                    
            # Sort by score and select top pairs
            sorted_pairs = sorted(pair_scores.items(), key=lambda x: x[1], reverse=True)
            selected_pairs = [pair for pair, score in sorted_pairs[:self.max_pairs]]
            
            logger.info(f"✅ Selected {len(selected_pairs)} pairs: {', '.join(selected_pairs)}")
            
            return selected_pairs
            
        except Exception as e:
            logger.error(f"Pair selection error: {e}")
            # Fallback to default pairs
            return self.get_default_pairs()
            
    async def score_pair(self, exchange, symbol: str, market: Dict) -> float:
        """Score a trading pair based on multiple factors"""
        
        score = 0
        
        try:
            # Get ticker for volume and price info
            ticker = await exchange.fetch_ticker(symbol)
            
            # Volume score (most important for small balance)
            volume_24h = ticker.get('quoteVolume', 0)
            if volume_24h < self.min_volume_24h:
                return 0  # Skip low volume pairs
                
            volume_score = min(volume_24h / 1000000, 10)  # Cap at 10
            score += volume_score * 3  # Weight: 3x
            
            # Volatility score (good for small balance)
            if ticker.get('high') and ticker.get('low'):
                daily_range = (ticker['high'] - ticker['low']) / ticker['low']
                volatility_score = min(daily_range * 100, 10)  # Cap at 10
                score += volatility_score * 2  # Weight: 2x
                
            # Spread score (lower is better)
            if ticker.get('bid') and ticker.get('ask'):
                spread = (ticker['ask'] - ticker['bid']) / ticker['bid']
                spread_score = max(10 - (spread * 1000), 0)  # Lower spread = higher score
                score += spread_score * 1  # Weight: 1x
                
            # Popularity score (top coins)
            popular_coins = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'DOGE', 'ADA', 'MATIC']
            base_currency = symbol.split('/')[0]
            if base_currency in popular_coins:
                popularity_index = popular_coins.index(base_currency)
                popularity_score = 10 - popularity_index
                score += popularity_score * 1.5  # Weight: 1.5x
                
            # Price score (can we afford meaningful positions?)
            price = ticker.get('last', 0)
            if price > 0:
                position_size = self.balance * 0.2  # 20% per position
                units_affordable = position_size / price
                
                if units_affordable < 0.001:  # Can't buy meaningful amount
                    score *= 0.5  # Penalize
                    
        except Exception as e:
            logger.debug(f"Error scoring {symbol}: {e}")
            return 0
            
        return score
        
    def get_default_pairs(self) -> List[str]:
        """Get default pairs when selection fails"""
        
        if self.balance < 100:
            return ['BTC/USDT', 'ETH/USDT']
        else:
            return ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
            
    async def filter_pairs_for_session(self, pairs: List[str], session: str) -> List[str]:
        """Filter pairs based on trading session"""
        
        session_preferences = {
            'asian': {
                'preferred': ['BTC', 'ETH', 'BNB'],  # Asian markets prefer these
                'avoid': ['EUR', 'GBP']
            },
            'european': {
                'preferred': ['BTC', 'ETH', 'EUR', 'GBP'],
                'avoid': ['JPY', 'KRW']
            },
            'american': {
                'preferred': ['BTC', 'ETH', 'SOL', 'DOGE'],  # US loves memes
                'avoid': ['EUR', 'GBP']
            }
        }
        
        prefs = session_preferences.get(session, {})
        
        if not prefs:
            return pairs
            
        filtered_pairs = []
        
        for pair in pairs:
            base = pair.split('/')[0]
            
            # Prioritize preferred
            if any(pref in base for pref in prefs.get('preferred', [])):
                filtered_pairs.insert(0, pair)  # Add to front
            # Avoid non-preferred
            elif not any(avoid in base for avoid in prefs.get('avoid', [])):
                filtered_pairs.append(pair)
                
        return filtered_pairs[:self.max_pairs]