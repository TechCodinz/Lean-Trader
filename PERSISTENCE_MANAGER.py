#!/usr/bin/env python3
"""
💾 PERSISTENCE MANAGER
Saves and loads all learned knowledge, strategies, performance data

This ensures the bot LEARNS and REMEMBERS across restarts.
Critical for continuous improvement.
"""

import json
import pickle
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PersistenceManager:
    """
    Manages all persistent data for the trading bot
    
    Saves:
    - Strategy evolution data (evolved strategies, fitness scores)
    - Performance history (trades, win rate, profits)
    - Market knowledge (patterns that worked, correlations)
    - Meta-learning data (what features lead to fast learning)
    - Quantum data (entanglements, causal relationships)
    """
    
    def __init__(self, data_dir: str = "bot_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Data files
        self.strategy_file = self.data_dir / "strategies.json"
        self.performance_file = self.data_dir / "performance.json"
        self.market_knowledge_file = self.data_dir / "market_knowledge.json"
        self.meta_learning_file = self.data_dir / "meta_learning.json"
        self.quantum_data_file = self.data_dir / "quantum_data.json"
        self.trades_file = self.data_dir / "trades.jsonl"  # Line-delimited for append
        
        logger.info("=" * 80)
        logger.info("💾 PERSISTENCE MANAGER INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   Data directory: {self.data_dir.absolute()}")
        logger.info(f"   Strategy file: {self.strategy_file.name}")
        logger.info(f"   Performance file: {self.performance_file.name}")
        logger.info(f"   Trades file: {self.trades_file.name}")
        logger.info("")
        logger.info("   💾 BOT WILL LEARN AND REMEMBER")
        logger.info("=" * 80)
    
    # ========================================================================
    # STRATEGY EVOLUTION PERSISTENCE
    # ========================================================================
    
    def save_strategies(self, strategies: List[Dict]) -> bool:
        """
        Save evolved strategies to disk
        
        Args:
            strategies: List of strategy dicts with fitness scores
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'count': len(strategies),
                'strategies': strategies
            }
            
            with open(self.strategy_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Saved {len(strategies)} strategies to disk")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save strategies: {e}")
            return False
    
    def load_strategies(self) -> Optional[List[Dict]]:
        """
        Load evolved strategies from disk
        
        Returns:
            List of strategies or None if file doesn't exist
        """
        try:
            if not self.strategy_file.exists():
                logger.info("📂 No saved strategies found (first run)")
                return None
            
            with open(self.strategy_file, 'r') as f:
                data = json.load(f)
            
            strategies = data.get('strategies', [])
            timestamp = data.get('timestamp', 'unknown')
            
            logger.info(f"✅ Loaded {len(strategies)} strategies from disk")
            logger.info(f"   Last saved: {timestamp}")
            
            return strategies
            
        except Exception as e:
            logger.error(f"❌ Failed to load strategies: {e}")
            return None
    
    # ========================================================================
    # PERFORMANCE DATA PERSISTENCE
    # ========================================================================
    
    def save_performance(self, performance_data: Dict) -> bool:
        """
        Save performance metrics
        
        Args:
            performance_data: Dict with win_rate, total_profit, trade_count, etc.
        """
        try:
            # Load existing data
            if self.performance_file.exists():
                with open(self.performance_file, 'r') as f:
                    history = json.load(f)
            else:
                history = {'entries': []}
            
            # Add new entry
            entry = {
                'timestamp': datetime.now().isoformat(),
                **performance_data
            }
            history['entries'].append(entry)
            
            # Keep last 1000 entries
            history['entries'] = history['entries'][-1000:]
            
            # Save
            with open(self.performance_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.debug(f"💾 Saved performance data")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save performance: {e}")
            return False
    
    def load_performance(self) -> Optional[Dict]:
        """
        Load performance history
        
        Returns:
            Dict with performance history or None
        """
        try:
            if not self.performance_file.exists():
                logger.info("📂 No performance history found (first run)")
                return None
            
            with open(self.performance_file, 'r') as f:
                data = json.load(f)
            
            entries = data.get('entries', [])
            logger.info(f"✅ Loaded {len(entries)} performance entries")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to load performance: {e}")
            return None
    
    # ========================================================================
    # TRADE LOGGING (Append-only for efficiency)
    # ========================================================================
    
    def log_trade(self, trade_data: Dict) -> bool:
        """
        Log a single trade (append-only for efficiency)
        
        Args:
            trade_data: Dict with symbol, side, entry, exit, profit, etc.
        """
        try:
            # Add timestamp
            trade_data['timestamp'] = datetime.now().isoformat()
            
            # Append to file (JSONL format - one JSON per line)
            with open(self.trades_file, 'a') as f:
                f.write(json.dumps(trade_data) + '\n')
            
            logger.debug(f"💾 Logged trade: {trade_data.get('symbol')} {trade_data.get('profit_pct', 0):.2%}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to log trade: {e}")
            return False
    
    def load_trades(self, limit: int = 1000) -> List[Dict]:
        """
        Load recent trades
        
        Args:
            limit: Max number of trades to load (from end)
        
        Returns:
            List of trade dicts
        """
        try:
            if not self.trades_file.exists():
                logger.info("📂 No trade history found (first run)")
                return []
            
            trades = []
            with open(self.trades_file, 'r') as f:
                for line in f:
                    if line.strip():
                        trades.append(json.loads(line))
            
            # Return last N trades
            trades = trades[-limit:]
            
            logger.info(f"✅ Loaded {len(trades)} recent trades")
            return trades
            
        except Exception as e:
            logger.error(f"❌ Failed to load trades: {e}")
            return []
    
    # ========================================================================
    # MARKET KNOWLEDGE PERSISTENCE
    # ========================================================================
    
    def save_market_knowledge(self, knowledge: Dict) -> bool:
        """
        Save market knowledge (patterns, correlations, what works)
        
        Args:
            knowledge: Dict with patterns, symbol performance, etc.
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'knowledge': knowledge
            }
            
            with open(self.market_knowledge_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Saved market knowledge")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save market knowledge: {e}")
            return False
    
    def load_market_knowledge(self) -> Optional[Dict]:
        """Load market knowledge"""
        try:
            if not self.market_knowledge_file.exists():
                logger.info("📂 No market knowledge found (first run)")
                return None
            
            with open(self.market_knowledge_file, 'r') as f:
                data = json.load(f)
            
            knowledge = data.get('knowledge', {})
            timestamp = data.get('timestamp', 'unknown')
            
            logger.info(f"✅ Loaded market knowledge (last updated: {timestamp})")
            return knowledge
            
        except Exception as e:
            logger.error(f"❌ Failed to load market knowledge: {e}")
            return None
    
    # ========================================================================
    # META-LEARNING DATA PERSISTENCE
    # ========================================================================
    
    def save_meta_learning(self, meta_data: Dict) -> bool:
        """
        Save meta-learning data (what features lead to fast learning, etc.)
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'meta_data': meta_data
            }
            
            with open(self.meta_learning_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Saved meta-learning data")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save meta-learning data: {e}")
            return False
    
    def load_meta_learning(self) -> Optional[Dict]:
        """Load meta-learning data"""
        try:
            if not self.meta_learning_file.exists():
                logger.info("📂 No meta-learning data found (first run)")
                return None
            
            with open(self.meta_learning_file, 'r') as f:
                data = json.load(f)
            
            meta_data = data.get('meta_data', {})
            logger.info(f"✅ Loaded meta-learning data")
            return meta_data
            
        except Exception as e:
            logger.error(f"❌ Failed to load meta-learning data: {e}")
            return None
    
    # ========================================================================
    # QUANTUM DATA PERSISTENCE
    # ========================================================================
    
    def save_quantum_data(self, quantum_data: Dict) -> bool:
        """
        Save quantum enhancement data (entanglements, causal graphs, etc.)
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'quantum_data': quantum_data
            }
            
            with open(self.quantum_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Saved quantum data")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save quantum data: {e}")
            return False
    
    def load_quantum_data(self) -> Optional[Dict]:
        """Load quantum enhancement data"""
        try:
            if not self.quantum_data_file.exists():
                logger.info("📂 No quantum data found (first run)")
                return None
            
            with open(self.quantum_data_file, 'r') as f:
                data = json.load(f)
            
            quantum_data = data.get('quantum_data', {})
            logger.info(f"✅ Loaded quantum data")
            return quantum_data
            
        except Exception as e:
            logger.error(f"❌ Failed to load quantum data: {e}")
            return None
    
    # ========================================================================
    # STATISTICS & ANALYSIS
    # ========================================================================
    
    def get_stats(self) -> Dict:
        """
        Get statistics about saved data
        """
        stats = {
            'strategies_saved': self.strategy_file.exists(),
            'performance_history': self.performance_file.exists(),
            'market_knowledge': self.market_knowledge_file.exists(),
            'meta_learning': self.meta_learning_file.exists(),
            'quantum_data': self.quantum_data_file.exists(),
        }
        
        # Count trades
        if self.trades_file.exists():
            with open(self.trades_file, 'r') as f:
                stats['trade_count'] = sum(1 for line in f if line.strip())
        else:
            stats['trade_count'] = 0
        
        return stats
    
    def print_status(self):
        """Print status of persistent data"""
        stats = self.get_stats()
        
        logger.info("=" * 80)
        logger.info("💾 PERSISTENCE STATUS")
        logger.info("=" * 80)
        logger.info(f"   Strategies: {'✅ Saved' if stats['strategies_saved'] else '❌ None'}")
        logger.info(f"   Performance: {'✅ Saved' if stats['performance_history'] else '❌ None'}")
        logger.info(f"   Market Knowledge: {'✅ Saved' if stats['market_knowledge'] else '❌ None'}")
        logger.info(f"   Meta-Learning: {'✅ Saved' if stats['meta_learning'] else '❌ None'}")
        logger.info(f"   Quantum Data: {'✅ Saved' if stats['quantum_data'] else '❌ None'}")
        logger.info(f"   Trades Logged: {stats['trade_count']}")
        logger.info("=" * 80)


# Global instance
_persistence_manager = None

def get_persistence_manager(data_dir: str = "bot_data") -> PersistenceManager:
    """Get or create global persistence manager"""
    global _persistence_manager
    if _persistence_manager is None:
        _persistence_manager = PersistenceManager(data_dir)
    return _persistence_manager


# Module initialization
logger.info("💾 PERSISTENCE MANAGER MODULE LOADED")
logger.info("   Bot will save and load learned knowledge")
