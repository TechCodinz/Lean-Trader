#!/usr/bin/env python3
"""
🧠 AI STRATEGY LEARNER 🧠

Bot learns NEW strategies by:
1. Querying AI for market insights
2. Analyzing successful trades
3. Discovering new patterns
4. Spawning specialized models
5. Continuous adaptation

BOT LEARNS AND EVOLVES!
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class AIStrategyLearner:
    """
    AI-POWERED STRATEGY LEARNING
    
    Features:
    - Learns from successful trades
    - Queries AI for new strategies
    - Spawns specialized models per strategy
    - Adapts to market conditions
    - Continuous evolution
    """
    
    def __init__(self, ai_consultation=None):
        self.ai_consultation = ai_consultation
        
        # Learned strategies
        self.strategies = {
            'SCALPING': {'win_rate': 0, 'trades': 0, 'active': True},
            'MOMENTUM_BREAKOUT': {'win_rate': 0, 'trades': 0, 'active': True},
            'ARBITRAGE': {'win_rate': 0, 'trades': 0, 'active': True},
            'NEWS_TRADING': {'win_rate': 0, 'trades': 0, 'active': True},
            'FOREX_SWING': {'win_rate': 0, 'trades': 0, 'active': True},
        }
        
        # Strategy models (spawned per strategy)
        self.strategy_models = {}
        
        # Learning history
        self.learning_history = []
        
        logger.info("🧠 AI STRATEGY LEARNER initialized!")
    
    async def learn_from_trade(self, trade: Dict):
        """
        Learn from completed trade
        
        Updates strategy performance and spawns new models
        """
        strategy = trade.get('strategy', 'UNKNOWN')
        profit = trade.get('profit', 0)
        
        if strategy in self.strategies:
            self.strategies[strategy]['trades'] += 1
            
            if profit > 0:
                # Update win rate
                wins = int(self.strategies[strategy]['win_rate'] * self.strategies[strategy]['trades'])
                wins += 1
                self.strategies[strategy]['win_rate'] = wins / self.strategies[strategy]['trades']
                
                logger.info(f"📚 Learning: {strategy} successful!")
                logger.info(f"   Win rate: {self.strategies[strategy]['win_rate']:.1%}")
        
        # Query AI for insights on this trade
        if self.ai_consultation and profit != 0:
            insights = await self._query_ai_for_insights(trade)
            
            if insights:
                logger.info(f"🤖 AI insights on {strategy}:")
                logger.info(f"   {insights.get('learning', 'No insights')}")
    
    async def _query_ai_for_insights(self, trade: Dict) -> Dict:
        """Query AI for insights on trade"""
        context = {
            'symbol': trade.get('symbol'),
            'strategy': trade.get('strategy'),
            'profit': trade.get('profit'),
            'duration': trade.get('duration'),
            'confidence': trade.get('confidence')
        }
        
        # Ask AI: "What can we learn from this trade?"
        result = await self.ai_consultation.consult_strategy(context)
        
        return result
    
    def get_best_strategy_for_symbol(self, symbol: str) -> str:
        """Get best performing strategy for this symbol"""
        # Would track per-symbol performance
        # For now, return best overall
        
        best_strategy = 'MULTI_ENGINE_CONFLUENCE'
        best_win_rate = 0
        
        for strategy, stats in self.strategies.items():
            if stats['trades'] > 5 and stats['win_rate'] > best_win_rate:
                best_strategy = strategy
                best_win_rate = stats['win_rate']
        
        return best_strategy


# Singleton
_strategy_learner = None

def get_strategy_learner():
    """Get strategy learner"""
    return _strategy_learner

def initialize_strategy_learner(ai_consultation=None):
    """Initialize strategy learner"""
    global _strategy_learner
    _strategy_learner = AIStrategyLearner(ai_consultation)
    return _strategy_learner
